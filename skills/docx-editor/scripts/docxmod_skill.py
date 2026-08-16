#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docxmod.py — lossless DOCX unpack / edit / repack engine (single-file embed).

A .docx file is a ZIP container of OOXML parts. This module operates directly
on the raw XML with lxml. **Unmodified parts are copied byte-for-byte**; only
the parts you actually edited are re-serialised. Open a document, make an edit,
save it, and every untouched part is guaranteed to be binary-identical to the
original — no formatting drift, no re-normalisation, no surprises.

Design rules (the four guarantees):
  1. Read the package as a ZIP and cache every entry's raw bytes.
  2. Parse an XML part into an lxml tree lazily, only when accessed.
  3. On save, entries you never touched are written back byte-for-byte from
     the cache. Only entries in the *dirty* set are re-serialised.
  4. The original ZIP entry order is preserved.

Public API::

    from docxmod import DocxEditor, unpack, repack
    doc = DocxEditor("report.docx")
    doc.replace_text("2024 edition", "2025 edition")      # global, preserves formatting
    doc.paragraphs[5].set_text("new paragraph text")      # keeps the run's rPr
    doc.tables[0].cell(1, 2).set_text("cell text")        # edit a table cell
    doc.paragraphs[2].insert_paragraph_after("new row")   # clone the paragraph style
    doc.save("report-edited.docx")

    unpack("report.docx", "report_unpacked/")             # extract every part verbatim
    repack("report_unpacked/", "report-rebuilt.docx")     # re-pack a folder into .docx

CLI::

    python -m docxmod unpack report.docx report_unpacked/
    python -m docxmod pack   report_unpacked/ report-rebuilt.docx
    python -m docxmod dump   report.docx
    python -m docxmod replace report.docx "old" "new" -o out.docx
    python -m docxmod set-para  report.docx 3 "new text" -o out.docx
    python -m docxmod set-cell  report.docx 0 1 2 "cell text" -o out.docx
    python -m docxmod parts  report.docx --bytes
    python -m docxmod find   report.docx "keyword"

Dependencies: lxml (required). PySide6 (optional, for the GUI entry point).

Author: cycleuser
License: MIT
"""

from __future__ import annotations

import argparse
import copy
import os
import re
import shutil
import sys
import zipfile

try:
    from lxml import etree
except ImportError as _exc:  # pragma: no cover - import guard
    raise SystemExit(
        "docxmod requires lxml. Install it with: pip install lxml"
    ) from _exc

__version__ = "1.0.0"
__all__ = [
    "DocxEditor", "Paragraph", "Run", "Table", "Cell",
    "unpack", "repack", "w", "main",
]

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W_NS}


def w(tag: str) -> str:
    """Return a Clark-notation tag name in the ``w`` namespace."""
    return f"{{{W_NS}}}{tag}"


# --------------------------------------------------------------------------- #
#  Pack / unpack helpers
# --------------------------------------------------------------------------- #

def unpack(path: str, dest_dir: str) -> str:
    """Unpack a ``.docx`` ZIP container into ``dest_dir``.

    Every entry is extracted verbatim (no XML parsing, no re-encoding), so the
    directory tree mirrors the internal layout of the package exactly.  The
    absolute path of the destination directory is returned.
    """
    os.makedirs(dest_dir, exist_ok=True)
    with zipfile.ZipFile(path) as zf:
        zf.extractall(dest_dir)
    return dest_dir


def repack(src_dir: str, path: str) -> str:
    """Re-pack a directory tree back into a ``.docx`` file.

    ``[Content_Types].xml`` — if present — is always written first so that
    Word recognises the file as a valid OOXML package.  Every other file
    keeps a stable, sorted order which makes the output reproducible.
    """
    files: list[str] = []
    for root, _dirs, names in os.walk(src_dir):
        for name in names:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, src_dir).replace(os.sep, "/")
            files.append(rel)
    files.sort(key=lambda p: (p != "[Content_Types].xml", p))

    tmp = path + ".tmp.docx"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for rel in files:
            full = os.path.join(src_dir, rel)
            with open(full, "rb") as fh:
                zo.writestr(rel, fh.read())
    shutil.move(tmp, path)
    return path


# --------------------------------------------------------------------------- #
#  DocxEditor
# --------------------------------------------------------------------------- #

class DocxEditor:
    """Open a docx, access / edit individual XML parts, then save losslessly.

    A part is considered modified (and thus re-serialised on save) when either
    an editing helper marked it dirty, or you called :meth:`mark_dirty`
    explicitly after poking at the lxml tree returned by :meth:`xml`.
    """

    #: Parts treated as "content" for full-text operations (body, headers,
    #: footers, footnotes, endnotes).
    CONTENT_PART_RE = re.compile(
        r"^word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml$"
    )

    def __init__(self, path: str):
        self.path = path
        self._zip = zipfile.ZipFile(path)
        self._names = self._zip.namelist()          # preserve original order
        self._raw: dict[str, bytes] = {n: self._zip.read(n) for n in self._names}
        self._trees: dict[str, object] = {}         # lazily-parsed lxml roots
        self._dirty: set[str] = set()               # parts needing re-serialise

    # -- dirty tracking ------------------------------------------------------

    def _mark_dirty(self, name: str) -> None:
        self._dirty.add(name)

    def mark_dirty(self, name: str) -> None:
        """Explicitly mark a part as modified so :meth:`save` re-serialises it.

        Use this after editing the lxml tree returned by :meth:`xml` directly
        (e.g. ``t.text = 'x'``); the high-level helpers already do this for you.
        """
        self._dirty.add(name)

    def _dirty_part_of(self, el) -> str | None:
        for name, root in self._trees.items():
            if root is None:
                continue
            if el in root.iter() or el is root:
                return name
        return None

    def _mark_element_dirty(self, el) -> None:
        name = self._dirty_part_of(el)
        if name:
            self._dirty.add(name)

    # -- part-level access ---------------------------------------------------

    @property
    def parts(self) -> list[str]:
        """List of every part name inside the package."""
        return list(self._names)

    def part_bytes(self, name: str) -> bytes:
        """Read the raw bytes of any part (XML, image, font, ...)."""
        if name in self._trees:
            return self._serialize(name)
        return self._raw[name]

    def set_part_bytes(self, name: str, data: bytes) -> None:
        """Replace a part entirely (e.g. swap an image)."""
        self._trees.pop(name, None)
        self._raw[name] = bytes(data)
        self._dirty.add(name)

    def xml(self, name: str):
        """Return the lxml root of an XML part.

        Edits to the returned tree are tracked automatically for the
        high-level helpers; if you edit elements directly, call
        :meth:`mark_dirty` with *name* before saving.
        """
        if name not in self._trees:
            parser = etree.XMLParser(remove_blank_text=False)
            self._trees[name] = etree.fromstring(self._raw[name], parser)
        return self._trees[name]

    def content_parts(self):
        """Iterate ``(name, root)`` for every content part."""
        for name in self._names:
            if self.CONTENT_PART_RE.match(name):
                yield name, self.xml(name)

    # -- paragraphs / tables -------------------------------------------------

    @property
    def body(self):
        return self.xml("word/document.xml").find(w("body"))

    @property
    def paragraphs(self) -> list["Paragraph"]:
        """Body-level paragraphs (not inside tables)."""
        return [Paragraph(p, self) for p in self.body.findall(w("p"))]

    @property
    def tables(self) -> list["Table"]:
        """Body-level tables."""
        return [Table(t, self) for t in self.body.findall(w("tbl"))]

    def all_paragraphs(self) -> list["Paragraph"]:
        """All paragraphs in the document (including those inside tables)."""
        return [Paragraph(p, self) for p in self.body.iter(w("p"))]

    # -- common edits --------------------------------------------------------

    def replace_text(self, old: str, new: str, parts=None) -> int:
        """Global text replacement (across runs, headers, footers, ...).

        Returns the number of replacements performed. Match spans that cross
        run boundaries are handled correctly and each run keeps its formatting.
        """
        count = 0
        targets = parts if parts is not None else [
            n for n in self._names if self.CONTENT_PART_RE.match(n)
        ]
        for name in targets:
            root = self.xml(name)
            part_count = 0
            for p in root.iter(w("p")):
                part_count += _replace_in_paragraph(p, old, new)
            if part_count:
                self._dirty.add(name)
            count += part_count
        return count

    def find(self, keyword: str):
        """Find paragraphs containing ``keyword``.

        Returns ``[(part_name, paragraph_index, Paragraph)]``.
        """
        hits = []
        for name, root in self.content_parts():
            for i, p in enumerate(root.iter(w("p"))):
                if keyword in _para_text(p):
                    hits.append((name, i, Paragraph(p, self)))
        return hits

    # -- save ----------------------------------------------------------------

    def _serialize(self, name: str) -> bytes:
        return etree.tostring(
            self._trees[name],
            xml_declaration=True,
            encoding="UTF-8",
            standalone=True,
        )

    def save(self, path: str | None = None) -> str:
        """Save the document.

        Unmodified parts are copied byte-for-byte; only dirty parts are
        re-serialised.  The ZIP entry order of the original file is preserved.
        When ``path`` is ``None`` the original file is overwritten in place
        (via a temp file + atomic move to avoid corruption on failure).
        """
        out = path or self.path
        tmp = out + ".tmp.docx"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            info_map = {i.filename: i for i in self._zip.infolist()}
            for name in self._names:
                src_info = info_map.get(name)
                info = zipfile.ZipInfo(
                    name,
                    date_time=src_info.date_time if src_info else (1980, 1, 1, 0, 0, 0),
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                if name in self._dirty and name in self._trees and self._trees[name] is not None:
                    data = self._serialize(name)
                else:
                    data = self._raw[name]
                zo.writestr(info, data)
            # Allow brand-new parts added via set_part_bytes().
            for name in self._dirty:
                if name not in self._names:
                    zo.writestr(name, self._raw[name])
        self._zip.close()
        shutil.move(tmp, out)
        self.path = out
        self._zip = zipfile.ZipFile(out)
        self._names = self._zip.namelist()
        self._raw = {n: self._zip.read(n) for n in self._names}
        self._dirty.clear()
        return out

    def close(self) -> None:
        self._zip.close()

    def __enter__(self) -> "DocxEditor":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


# --------------------------------------------------------------------------- #
#  Paragraph-level helpers
# --------------------------------------------------------------------------- #

def _para_text(p) -> str:
    return "".join(t.text or "" for t in p.iter(w("t")))


def _set_t(t, text: str) -> None:
    """Set text on a ``<w:t>`` and toggle ``xml:space="preserve"`` as needed."""
    t.text = text
    if text != text.strip():
        t.set(f"{{{XML_NS}}}space", "preserve")
    elif f"{{{XML_NS}}}space" in t.attrib:
        del t.attrib[f"{{{XML_NS}}}space"]


def _replace_in_paragraph(p, old: str, new: str) -> int:
    """Replace ``old`` -> ``new`` within one paragraph, across runs.

    The replacement text is placed into the first run that intersects the
    match so that run formatting is preserved; subsequent intersecting runs
    have only the matched span removed.
    """
    if not old:
        return 0
    count = 0
    while True:
        ts = list(p.iter(w("t")))
        full = "".join(t.text or "" for t in ts)
        pos = full.find(old)
        if pos < 0:
            return count
        end = pos + len(old)
        cursor = 0
        placed = False
        for t in ts:
            seg = t.text or ""
            seg_start, seg_end = cursor, cursor + len(seg)
            cursor = seg_end
            if seg_end <= pos or seg_start >= end:
                continue
            pre = seg[: max(0, pos - seg_start)]
            post = seg[max(0, min(len(seg), end - seg_start)):]
            if not placed:
                _set_t(t, pre + new + post)
                placed = True
            else:
                _set_t(t, pre + post)
        count += 1


# --------------------------------------------------------------------------- #
#  Wrapper objects
# --------------------------------------------------------------------------- #

class Run:
    """A ``<w:r>`` text run. ``.text`` is read/write; ``rPr`` is preserved."""

    def __init__(self, el, doc: DocxEditor | None = None):
        self.el = el
        self._doc = doc

    def _dirty(self) -> None:
        if self._doc is not None:
            self._doc._mark_element_dirty(self.el)

    @property
    def text(self) -> str:
        return "".join(t.text or "" for t in self.el.findall(w("t")))

    @text.setter
    def text(self, value: str) -> None:
        ts = self.el.findall(w("t"))
        if not ts:
            t = etree.SubElement(self.el, w("t"))
            ts = [t]
        _set_t(ts[0], value)
        for extra in ts[1:]:
            self.el.remove(extra)
        self._dirty()

    @property
    def rpr(self):
        return self.el.find(w("rPr"))


class Paragraph:
    """A ``<w:p>`` paragraph."""

    def __init__(self, el, doc: DocxEditor | None = None):
        self.el = el
        self._doc = doc

    def _dirty(self) -> None:
        if self._doc is not None:
            self._doc._mark_element_dirty(self.el)

    @property
    def text(self) -> str:
        return _para_text(self.el)

    @property
    def runs(self) -> list[Run]:
        return [Run(r, self._doc) for r in self.el.findall(w("r"))]

    @property
    def style(self) -> str | None:
        pstyle = self.el.find(f"{w('pPr')}/{w('pStyle')}")
        return pstyle.get(w("val")) if pstyle is not None else None

    @style.setter
    def style(self, value: str | None) -> None:
        ppr = self.el.find(w("pPr"))
        if ppr is None:
            ppr = etree.Element(w("pPr"))
            self.el.insert(0, ppr)
        pstyle = ppr.find(w("pStyle"))
        if pstyle is None:
            pstyle = etree.Element(w("pStyle"))
            ppr.insert(0, pstyle)
        pstyle.set(w("val"), value)
        self._dirty()

    def set_text(self, text: str) -> None:
        """Replace the whole paragraph text but preserve formatting.

        The new text is written into the first run that already has text;
        all other runs are emptied / removed.
        """
        runs = self.el.findall(w("r"))
        first_with_t = None
        for r in runs:
            if r.find(w("t")) is not None:
                first_with_t = r
                break
        if first_with_t is None:
            r = etree.SubElement(self.el, w("r"))
            t = etree.SubElement(r, w("t"))
            _set_t(t, text)
            self._dirty()
            return
        _set_t(first_with_t.find(w("t")), text)
        for r in runs:
            if r is first_with_t:
                continue
            for t in r.findall(w("t")):
                r.remove(t)
            if len(r) == 0 or all(child.tag in (w("rPr"),) for child in r):
                self.el.remove(r)
        self._dirty()

    def _insert_sibling(self, text: str, after: bool = True, clone: bool = True):
        parent = self.el.getparent()
        if clone:
            new_p = copy.deepcopy(self.el)
            for child in list(new_p):
                if child.tag != w("pPr"):
                    new_p.remove(child)
            r = etree.SubElement(new_p, w("r"))
            first_rpr = self.el.find(f"{w('r')}/{w('rPr')}")
            if first_rpr is not None:
                r.insert(0, copy.deepcopy(first_rpr))
            t = etree.SubElement(r, w("t"))
            _set_t(t, text or "")
        else:
            new_p = etree.Element(w("p"))
            if text:
                r = etree.SubElement(new_p, w("r"))
                t = etree.SubElement(r, w("t"))
                _set_t(t, text)
        idx = list(parent).index(self.el)
        parent.insert(idx + (1 if after else 0), new_p)
        if self._doc is not None:
            self._doc._mark_element_dirty(new_p)
        return Paragraph(new_p, self._doc)

    def insert_paragraph_after(self, text: str = "", clone: bool = True) -> "Paragraph":
        """Insert a new paragraph after this one; clone its style when *clone*."""
        return self._insert_sibling(text, after=True, clone=clone)

    def insert_paragraph_before(self, text: str = "", clone: bool = True) -> "Paragraph":
        return self._insert_sibling(text, after=False, clone=clone)

    def delete(self) -> None:
        """Delete this paragraph.

        If it is the only paragraph inside a table cell, only the text is
        cleared (a table cell must always contain at least one paragraph).
        """
        parent = self.el.getparent()
        if self._doc is not None:
            self._doc._mark_element_dirty(self.el)   # mark before detach
        if parent is not None and parent.tag == w("tc"):
            siblings = parent.findall(w("p"))
            if len(siblings) <= 1:
                self.set_text("")
                return
        if parent is not None:
            parent.remove(self.el)


class Cell:
    """A table cell ``<w:tc>``."""

    def __init__(self, el, doc: DocxEditor | None = None):
        self.el = el
        self._doc = doc

    def _dirty(self) -> None:
        if self._doc is not None:
            self._doc._mark_element_dirty(self.el)

    @property
    def text(self) -> str:
        return "\n".join(_para_text(p) for p in self.el.findall(w("p")))

    @property
    def paragraphs(self) -> list[Paragraph]:
        return [Paragraph(p, self._doc) for p in self.el.findall(w("p"))]

    def set_text(self, text: str) -> None:
        """Write text into the cell (``\\n`` starts a new paragraph).

        The cell's existing paragraph formatting is preserved.
        """
        lines = text.split("\n")
        ps = self.el.findall(w("p"))
        if not ps:
            etree.SubElement(self.el, w("p"))
            ps = self.el.findall(w("p"))
        Paragraph(ps[0], self._doc).set_text(lines[0])
        for i, line in enumerate(lines[1:], start=1):
            if i < len(ps):
                Paragraph(ps[i], self._doc).set_text(line)
            else:
                Paragraph(ps[-1], self._doc).insert_paragraph_after(line)
        for extra in ps[len(lines):]:
            Paragraph(extra, self._doc).delete()
        self._dirty()


class Table:
    """A table ``<w:tbl>``."""

    def __init__(self, el, doc: DocxEditor | None = None):
        self.el = el
        self._doc = doc

    def _dirty(self) -> None:
        if self._doc is not None:
            self._doc._mark_element_dirty(self.el)

    @property
    def rows(self):
        return self.el.findall(w("tr"))

    def row_count(self) -> int:
        return len(self.rows)

    def col_count(self) -> int:
        rows = self.rows
        return max((len(r.findall(w("tc"))) for r in rows), default=0)

    def cell(self, row: int, col: int) -> Cell:
        return Cell(self.rows[row].findall(w("tc"))[col], self._doc)

    def row_texts(self, row: int) -> list[str]:
        return [Cell(tc, self._doc).text for tc in self.rows[row].findall(w("tc"))]

    def add_row(self, clone_last: bool = True):
        """Append a row; clone the last row's formatting when *clone_last*."""
        rows = self.rows
        if not rows:
            raise ValueError("cannot clone a row from an empty table")
        new_tr = copy.deepcopy(rows[-1] if clone_last else rows[0])
        for tc in new_tr.findall(w("tc")):
            Cell(tc, self._doc).set_text("")
        rows[-1].addnext(new_tr)
        self._dirty()
        return new_tr

    def delete_row(self, index: int) -> None:
        self.el.remove(self.rows[index])
        self._dirty()

    def delete_column(self, index: int) -> None:
        """Delete column *index* from every row and from the tblGrid."""
        for tr in self.rows:
            tcs = tr.findall(w("tc"))
            if index < len(tcs):
                tr.remove(tcs[index])
        grid = self.el.find(w("tblGrid"))
        if grid is not None:
            cols = grid.findall(w("gridCol"))
            if index < len(cols):
                grid.remove(cols[index])
        self._dirty()

    def add_column(self, clone_last: bool = True) -> None:
        """Append a column; clone each row's last cell formatting when *clone_last*."""
        for tr in self.rows:
            tcs = tr.findall(w("tc"))
            if not tcs:
                continue
            src = tcs[-1] if clone_last else tcs[0]
            new_tc = copy.deepcopy(src)
            Cell(new_tc, self._doc).set_text("")
            src.addnext(new_tc)
        grid = self.el.find(w("tblGrid"))
        if grid is not None:
            cols = grid.findall(w("gridCol"))
            if cols:
                grid.append(copy.deepcopy(cols[-1]))
        self._dirty()


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="docxmod",
        description="DocxMod — lossless DOCX unpack / edit / repack tool.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_unpack = sub.add_parser("unpack", help="unpack a .docx into a directory")
    p_unpack.add_argument("file")
    p_unpack.add_argument("dest", nargs="?", default=None,
                          help="output directory (default: <file>.unpacked)")

    p_pack = sub.add_parser("pack", help="re-pack a directory into a .docx")
    p_pack.add_argument("src", help="directory to pack")
    p_pack.add_argument("out", help="output .docx path")

    p_dump = sub.add_parser("dump", help="print paragraph & table structure")
    p_dump.add_argument("file")

    p_find = sub.add_parser("find", help="find paragraphs containing a keyword")
    p_find.add_argument("file")
    p_find.add_argument("keyword")

    p_rep = sub.add_parser("replace", help="global text replacement")
    p_rep.add_argument("file")
    p_rep.add_argument("old")
    p_rep.add_argument("new")
    p_rep.add_argument("-o", "--output", default=None)

    p_sp = sub.add_parser("set-para", help="rewrite a body paragraph by index")
    p_sp.add_argument("file")
    p_sp.add_argument("index", type=int)
    p_sp.add_argument("text")
    p_sp.add_argument("-o", "--output", default=None)

    p_sc = sub.add_parser("set-cell", help="rewrite a table cell")
    p_sc.add_argument("file")
    p_sc.add_argument("table", type=int)
    p_sc.add_argument("row", type=int)
    p_sc.add_argument("col", type=int)
    p_sc.add_argument("text")
    p_sc.add_argument("-o", "--output", default=None)

    p_parts = sub.add_parser("parts", help="list every part inside the package")
    p_parts.add_argument("file")
    p_parts.add_argument("--bytes", action="store_true",
                         help="also show the size in bytes of each part")

    return ap


def _cli_main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.cmd == "unpack":
        dest = args.dest or args.file + ".unpacked"
        unpack(args.file, dest)
        print(f"Unpacked {args.file} -> {dest}")
        return 0
    if args.cmd == "pack":
        repack(args.src, args.out)
        print(f"Packed {args.src} -> {args.out}")
        return 0
    if args.cmd == "dump":
        with DocxEditor(args.file) as doc:
            for i, p in enumerate(doc.paragraphs):
                print(f"[P{i:03d}] {p.text}")
            for ti, tb in enumerate(doc.tables):
                print(f"[TABLE {ti}] {tb.row_count()}rows x {tb.col_count()}cols")
                for ri in range(tb.row_count()):
                    print(f"  R{ri}: {tb.row_texts(ri)}")
        return 0
    if args.cmd == "find":
        with DocxEditor(args.file) as doc:
            for part, i, p in doc.find(args.keyword):
                print(f"{part} #{i}: {p.text}")
        return 0
    if args.cmd == "replace":
        with DocxEditor(args.file) as doc:
            n = doc.replace_text(args.old, args.new)
            doc.save(args.output)
        print(f"Replaced {n} occurrence(s); saved to {args.output or args.file}")
        return 0
    if args.cmd == "set-para":
        with DocxEditor(args.file) as doc:
            doc.paragraphs[args.index].set_text(args.text)
            doc.save(args.output)
        print(f"Paragraph {args.index} updated; saved to {args.output or args.file}")
        return 0
    if args.cmd == "set-cell":
        with DocxEditor(args.file) as doc:
            doc.tables[args.table].cell(args.row, args.col).set_text(args.text)
            doc.save(args.output)
        print(f"Cell ({args.table},{args.row},{args.col}) updated; "
              f"saved to {args.output or args.file}")
        return 0
    if args.cmd == "parts":
        with DocxEditor(args.file) as doc:
            for name in doc.parts:
                if args.bytes:
                    print(f"{len(doc.part_bytes(name)):>10}  {name}")
                else:
                    print(name)
        return 0
    return 2


def main() -> int:
    """Console-script entry point (``docxmod``)."""
    return _cli_main()


if __name__ == "__main__":
    sys.exit(main())