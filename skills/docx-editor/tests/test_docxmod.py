#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_docxmod.py — self-contained test suite for the docx-editor skill.

Builds a minimal valid .docx on the fly (no external sample needed), then
exercises every editing surface and the losslessness guarantees.

Run with::

    python test_docxmod.py
    pytest test_docxmod.py -v

Exit code is 0 only if every check passes.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import zipfile

# Make the sibling docxmod_skill.py importable when run directly.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from docxmod_skill import DocxEditor, repack, unpack  # noqa: E402

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


# --------------------------------------------------------------------------- #
#  Minimal valid OOXML builder (no external sample required)
# --------------------------------------------------------------------------- #

CONTENT_TYPES = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>
<Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>
</Types>"""

ROOT_RELS = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>
<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>
</Relationships>"""

STYLES = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>
</w:styles>"""

HEADER = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:p><w:r><w:t>Header text</w:t></w:r></w:p>
</w:hdr>"""

FOOTNOTES = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>
<w:footnote w:id="1"><w:p><w:r><w:t>Footnote text</w:t></w:r></w:p></w:footnote>
</w:footnotes>"""

COMMENTS = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:comment w:id="1" w:author="Reviewer"><w:p><w:r><w:t>Comment text</w:t></w:r></w:p></w:comment>
</w:comments>"""

DOC_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<w:body>
<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Test Title</w:t></w:r></w:p>
<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>First paragraph.</w:t></w:r></w:p>
<w:p><w:r><w:t>Second paragraph.</w:t></w:r><w:r><w:t> with more</w:t></w:r></w:p>
<w:tbl>
<w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/></w:tblPr>
<w:tblGrid><w:gridCol w:w="2000"/><w:gridCol w:w="2000"/></w:tblGrid>
<w:tr><w:tc><w:p><w:r><w:t>A1</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>B1</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:p><w:r><w:t>A2</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>B2</w:t></w:r></w:p></w:tc></w:tr>
</w:tbl>
<w:sectPr><w:headerReference w:type="default" r:id="rId2"/><w:pgSz w:w="12240" w:h="15840"/></w:sectPr>
</w:body>
</w:document>"""


def build_sample(path: str) -> str:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", DOC_XML)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/header1.xml", HEADER)
        z.writestr("word/footnotes.xml", FOOTNOTES)
        z.writestr("word/comments.xml", COMMENTS)
    return path


def zip_map(path):
    with zipfile.ZipFile(path) as z:
        return {i.filename: z.read(i.filename) for i in z.infolist()}


# --------------------------------------------------------------------------- #
#  Tests
# --------------------------------------------------------------------------- #

def test_unpack_repack():
    print("\n== unpack / repack byte-identity ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    dest = os.path.join(tmp, "u")
    unpack(src, dest)
    check("unpack creates files", os.path.isfile(os.path.join(dest, "word", "document.xml")))
    out = os.path.join(tmp, "r.docx")
    repack(dest, out)
    a, b = zip_map(src), zip_map(out)
    check("part set identical", set(a) == set(b))
    check("all part bytes identical", all(a[n] == b[n] for n in a))
    shutil.rmtree(tmp)


def test_open_save_no_edits():
    print("\n== open + save (no edits) is byte-identical ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        doc.save(out)
    a, b = zip_map(src), zip_map(out)
    check("part set identical", set(a) == set(b))
    check("all parts byte-identical", all(a[n] == b[n] for n in a))
    shutil.rmtree(tmp)


def test_replace_text():
    print("\n== global text replacement ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        n = doc.replace_text("First", "Number One")
        check("replace hit count >= 1", n >= 1)
        doc.save(out)
    a, b = zip_map(src), zip_map(out)
    changed = {n for n in a if a[n] != b[n]}
    check("only document.xml changed", changed == {"word/document.xml"},
          f"changed={changed}")
    with DocxEditor(out) as doc:
        check("replacement visible", any("Number One" in p.text for p in doc.paragraphs))
    shutil.rmtree(tmp)


def test_replace_across_runs():
    print("\n== replace across run boundaries ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        # "paragraph. with more" spans two runs in paragraph 2
        n = doc.replace_text("paragraph. with", "CHUNK")
        check("cross-run replace hit", n >= 1, f"n={n}")
        doc.save(out)
    with DocxEditor(out) as doc:
        check("cross-run replace applied", "CHUNK" in doc.paragraphs[2].text)
    shutil.rmtree(tmp)


def test_paragraph_set_text():
    print("\n== paragraph rewrite (format preserved) ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        doc.paragraphs[1].set_text("rewritten text")
        doc.save(out)
    with DocxEditor(out) as doc:
        check("paragraph rewritten", doc.paragraphs[1].text == "rewritten text")
    shutil.rmtree(tmp)


def test_paragraph_insert_delete():
    print("\n== insert + delete paragraph ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        n0 = len(doc.paragraphs)
        doc.paragraphs[0].insert_paragraph_after("inserted")
        check("insert +1", len(doc.paragraphs) == n0 + 1)
        doc.paragraphs[1].delete()
        check("delete -1", len(doc.paragraphs) == n0)
        doc.save(out)
    with DocxEditor(out) as doc:
        check("count stable after save", len(doc.paragraphs) == n0)
    shutil.rmtree(tmp)


def test_table_cell():
    print("\n== table cell edit ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        doc.tables[0].cell(0, 0).set_text("XX")
        doc.save(out)
    with DocxEditor(out) as doc:
        check("cell edited", doc.tables[0].cell(0, 0).text == "XX")
    shutil.rmtree(tmp)


def test_table_row_col():
    print("\n== table add/del row & column ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        tb = doc.tables[0]
        r0, c0 = tb.row_count(), tb.col_count()
        tb.add_row();     check("row +1", tb.row_count() == r0 + 1)
        tb.delete_row(r0); check("row -1", tb.row_count() == r0)
        tb.add_column();   check("col +1", tb.col_count() == c0 + 1)
        tb.delete_column(c0); check("col -1", tb.col_count() == c0)
        doc.save(out)
    with DocxEditor(out) as doc:
        check("table restored", doc.tables[0].row_count() == r0 and
              doc.tables[0].col_count() == c0)
    shutil.rmtree(tmp)


def test_paragraph_style():
    print("\n== paragraph style change ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        doc.paragraphs[1].style = "Heading1"
        doc.save(out)
    with DocxEditor(out) as doc:
        check("style set", doc.paragraphs[1].style == "Heading1")
    shutil.rmtree(tmp)


def test_header_edit():
    print("\n== header text edit (non-document part) ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        root = doc.xml("word/header1.xml")
        t = root.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
        check("header text found", t is not None and "Header" in (t.text or ""))
        t.text = "NEW HEADER"
        doc.mark_dirty("word/header1.xml")
        doc.save(out)
    a, b = zip_map(src), zip_map(out)
    changed = {n for n in a if a[n] != b[n]}
    check("only header1.xml changed", changed == {"word/header1.xml"}, f"changed={changed}")
    with DocxEditor(out) as doc:
        root = doc.xml("word/header1.xml")
        t = root.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
        check("header edited", "NEW HEADER" in (t.text or ""))
    shutil.rmtree(tmp)


def test_footnote_edit():
    print("\n== footnote text edit ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        root = doc.xml("word/footnotes.xml")
        for fn in root.findall("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}footnote"):
            if fn.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id") not in ("-1", "0"):
                t = fn.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
                t.text = "NEW FN"
                break
        doc.mark_dirty("word/footnotes.xml")
        doc.save(out)
    a, b = zip_map(src), zip_map(out)
    changed = {n for n in a if a[n] != b[n]}
    check("only footnotes.xml changed", changed == {"word/footnotes.xml"}, f"changed={changed}")
    shutil.rmtree(tmp)


def test_comment_edit():
    print("\n== comment text edit ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        root = doc.xml("word/comments.xml")
        c = root.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}comment")
        t = c.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
        t.text = "NEW COMMENT"
        doc.mark_dirty("word/comments.xml")
        doc.save(out)
    a, b = zip_map(src), zip_map(out)
    changed = {n for n in a if a[n] != b[n]}
    check("only comments.xml changed", changed == {"word/comments.xml"}, f"changed={changed}")
    shutil.rmtree(tmp)


def test_part_bytes_swap():
    print("\n== raw part bytes swap ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        data = doc.part_bytes("word/styles.xml")
        check("styles.xml readable", data.startswith(b"<?xml"))
        new_data = data.replace(b"</w:styles>", b"<!-- X --></w:styles>")
        doc.set_part_bytes("word/styles.xml", new_data)
        doc.save(out)
    with DocxEditor(out) as doc:
        check("swap applied", b"<!-- X -->" in doc.part_bytes("word/styles.xml"))
    shutil.rmtree(tmp)


def test_inplace_save():
    print("\n== in-place save ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    with DocxEditor(src) as doc:
        doc.replace_text("Test", "TEST")
        doc.save()
    with DocxEditor(src) as doc:
        check("in-place edit visible", any("TEST" in p.text for p in doc.paragraphs))
    shutil.rmtree(tmp)


def test_find():
    print("\n== find ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    with DocxEditor(src) as doc:
        hits = doc.find("Second")
        check("find hit", len(hits) == 1)
        check("find part name", hits[0][0] == "word/document.xml")
    shutil.rmtree(tmp)


def test_source_not_mutated():
    print("\n== source not mutated when saving elsewhere ==")
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "s.docx")
    build_sample(src)
    original = zip_map(src)
    out = os.path.join(tmp, "o.docx")
    with DocxEditor(src) as doc:
        doc.replace_text("First", "X")
        doc.save(out)
    check("source intact", zip_map(src) == original)
    shutil.rmtree(tmp)


def main():
    print("=" * 60)
    print("DocxMod skill — self-contained test suite")
    print("=" * 60)
    test_unpack_repack()
    test_open_save_no_edits()
    test_replace_text()
    test_replace_across_runs()
    test_paragraph_set_text()
    test_paragraph_insert_delete()
    test_table_cell()
    test_table_row_col()
    test_paragraph_style()
    test_header_edit()
    test_footnote_edit()
    test_comment_edit()
    test_part_bytes_swap()
    test_inplace_save()
    test_find()
    test_source_not_mutated()
    print(f"\n{'=' * 60}\nResult: {PASS} passed, {FAIL} failed\n{'=' * 60}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())