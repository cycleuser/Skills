#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docxmod_gui.py — PySide6 GUI for the DocxMod lossless DOCX editor.

Launch with::

    python docxmod_gui.py [file.docx]

Requires PySide6 (``pip install PySide6``). The core engine is in
:mod:`docxmod` (same directory).

Features
  - Open / Save / Save-As docx (in-place overwrite is safe: temp + atomic move)
  - Unpack a docx into a folder; repack a folder back into a docx
  - Paragraph editing: rewrite text (preserving formatting), insert above /
    below, delete, change paragraph style
  - Table editing: edit cells, add / delete rows and columns
  - Global find & replace (covers body, headers, footers, footnotes, endnotes)
  - Raw part browser: view / edit the XML of any part, swap binary parts
"""

from __future__ import annotations

import os
import sys

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction, QKeySequence
    from PySide6.QtWidgets import (
        QApplication, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
        QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow,
        QMessageBox, QPlainTextEdit, QPushButton, QSplitter, QTableWidget,
        QTableWidgetItem, QTabWidget, QTreeWidget, QTreeWidgetItem,
        QVBoxLayout, QWidget,
    )
except ImportError as _exc:  # pragma: no cover - import guard
    raise SystemExit(
        "PySide6 is required for the GUI. Install with: pip install PySide6"
    ) from _exc

# Import the engine from the same directory as this script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docxmod_skill import DocxEditor, _para_text, repack, unpack, w  # noqa: E402


class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Find & Replace")
        form = QFormLayout(self)
        self.old = QLineEdit(); form.addRow("Find:", self.old)
        self.new = QLineEdit(); form.addRow("Replace with:", self.new)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def values(self):
        return self.old.text(), self.new.text()


class PartXmlDialog(QDialog):
    """View / edit the raw XML of a single part."""
    def __init__(self, name, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Part XML: {name}")
        self.resize(800, 600)
        v = QVBoxLayout(self)
        self.edit = QPlainTextEdit()
        self.edit.setPlainText(data.decode("utf-8", errors="replace"))
        v.addWidget(self.edit)
        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        v.addWidget(bb)

    def new_bytes(self) -> bytes:
        return self.edit.toPlainText().encode("utf-8")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocxMod — lossless DOCX editor")
        self.resize(1100, 720)
        self.doc: DocxEditor | None = None
        self.path: str | None = None
        self._loading = False
        self._current_tab = None
        self._modified = False
        self._build_ui()
        self._build_menu()
        self._build_toolbar()

    # ---- UI ----------------------------------------------------------------

    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Outline (paragraphs / tables)"])
        self.tree.setColumnWidth(0, 360)
        self.tree.itemClicked.connect(self._on_select)
        splitter.addWidget(self.tree)

        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(4, 4, 4, 4)
        self.tabs = QTabWidget()

        # Paragraph page
        para_page = QWidget(); pv = QVBoxLayout(para_page)
        self.para_label = QLabel("(select a paragraph)")
        pv.addWidget(self.para_label)
        self.para_edit = QPlainTextEdit(); pv.addWidget(self.para_edit, 1)
        btnrow = QHBoxLayout()
        self.btn_apply = QPushButton("Apply"); self.btn_apply.clicked.connect(self._apply_para)
        self.btn_ins_before = QPushButton("Insert Above")
        self.btn_ins_before.clicked.connect(lambda: self._insert_para(False))
        self.btn_ins_after = QPushButton("Insert Below")
        self.btn_ins_after.clicked.connect(lambda: self._insert_para(True))
        self.btn_del = QPushButton("Delete"); self.btn_del.clicked.connect(self._delete_para)
        for b in (self.btn_apply, self.btn_ins_before, self.btn_ins_after, self.btn_del):
            btnrow.addWidget(b)
        btnrow.addStretch()
        self.style_edit = QLineEdit()
        self.style_edit.setPlaceholderText("paragraph style (e.g. Heading1)")
        btnrow.addWidget(QLabel("Style:")); btnrow.addWidget(self.style_edit)
        self.btn_style = QPushButton("Set Style"); self.btn_style.clicked.connect(self._apply_style)
        btnrow.addWidget(self.btn_style)
        pv.addLayout(btnrow)
        self.tabs.addTab(para_page, "Paragraph")

        # Table page
        tbl_page = QWidget(); tv = QVBoxLayout(tbl_page)
        self.tbl_label = QLabel("(select a table)")
        tv.addWidget(self.tbl_label)
        self.table = QTableWidget(); tv.addWidget(self.table, 1)
        trow = QHBoxLayout()
        self.btn_addrow = QPushButton("+ Row"); self.btn_addrow.clicked.connect(self._add_row)
        self.btn_delrow = QPushButton("- Row"); self.btn_delrow.clicked.connect(self._del_row)
        self.btn_addcol = QPushButton("+ Col"); self.btn_addcol.clicked.connect(self._add_col)
        self.btn_delcol = QPushButton("- Col"); self.btn_delcol.clicked.connect(self._del_col)
        for b in (self.btn_addrow, self.btn_delrow, self.btn_addcol, self.btn_delcol):
            trow.addWidget(b)
        trow.addStretch()
        tv.addLayout(trow)
        self.tabs.addTab(tbl_page, "Table")
        self.table.itemChanged.connect(self._on_cell_changed)

        # Parts page
        parts_page = QWidget(); plv = QVBoxLayout(parts_page)
        plv.addWidget(QLabel("All parts (double-click an XML part to edit it)"))
        self.parts_list = QListWidget(); plv.addWidget(self.parts_list, 1)
        self.parts_list.itemDoubleClicked.connect(self._edit_part_xml)
        self.btn_show_bytes = QPushButton("Show part size")
        self.btn_show_bytes.clicked.connect(self._show_part_info)
        plv.addWidget(self.btn_show_bytes)
        self.tabs.addTab(parts_page, "Parts")

        rv.addWidget(self.tabs)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        self.setCentralWidget(splitter)

    def _build_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("&File")
        self.act_open = QAction("Open…", self); self.act_open.setShortcut(QKeySequence.Open)
        self.act_open.triggered.connect(self.open_file); fm.addAction(self.act_open)
        self.act_save = QAction("Save", self); self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.triggered.connect(self.save_file); fm.addAction(self.act_save)
        self.act_saveas = QAction("Save As…", self); self.act_saveas.setShortcut(QKeySequence.SaveAs)
        self.act_saveas.triggered.connect(self.save_as); fm.addAction(self.act_saveas)
        fm.addSeparator()
        self.act_unpack = QAction("Unpack to Folder…", self)
        self.act_unpack.triggered.connect(self.unpack_file); fm.addAction(self.act_unpack)
        self.act_pack = QAction("Repack from Folder…", self)
        self.act_pack.triggered.connect(self.pack_folder); fm.addAction(self.act_pack)
        fm.addSeparator()
        self.act_close = QAction("Close Document", self)
        self.act_close.triggered.connect(self.close_doc); fm.addAction(self.act_close)
        fm.addSeparator()
        self.act_quit = QAction("Quit", self); self.act_quit.setShortcut(QKeySequence.Quit)
        self.act_quit.triggered.connect(self.close); fm.addAction(self.act_quit)

        em = mb.addMenu("&Edit")
        self.act_find = QAction("Find & Replace…", self); self.act_find.setShortcut(QKeySequence("Ctrl+H"))
        self.act_find.triggered.connect(self.find_replace); em.addAction(self.act_find)

        hm = mb.addMenu("&Help")
        self.act_about = QAction("About", self); self.act_about.triggered.connect(self._about)
        hm.addAction(self.act_about)

    def _build_toolbar(self):
        tb = self.addToolBar("Main"); tb.setMovable(False)
        tb.addAction(self.act_open); tb.addAction(self.act_save); tb.addAction(self.act_saveas)
        tb.addSeparator(); tb.addAction(self.act_unpack); tb.addAction(self.act_pack)
        tb.addSeparator(); tb.addAction(self.act_find)

    # ---- file operations ---------------------------------------------------

    def open_file(self, path=None):
        if path is None:
            path, _ = QFileDialog.getOpenFileName(self, "Open docx", "", "Word Documents (*.docx)")
            if not path:
                return
        self.close_doc()
        try:
            self.doc = DocxEditor(path)
        except Exception as e:
            QMessageBox.critical(self, "Open failed", f"Cannot open file:\n{e}")
            return
        self.path = path
        self._modified = False
        self._refresh_all()
        self._update_title()

    def save_file(self):
        if self.doc is None:
            return
        try:
            self.doc.save(self.path)
            self._modified = False
            self._update_title()
            self.statusBar().showMessage("Saved", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"{e}")

    def save_as(self):
        if self.doc is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Word Documents (*.docx)")
        if not path:
            return
        try:
            self.doc.save(path); self.path = path
            self._modified = False; self._update_title()
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"{e}")

    def unpack_file(self):
        src = self.path
        if src is None:
            src, _ = QFileDialog.getOpenFileName(self, "Select docx to unpack", "",
                                                 "Word Documents (*.docx)")
            if not src:
                return
        default_dir = src + ".unpacked"
        dest = QFileDialog.getExistingDirectory(self, "Choose unpack destination", default_dir)
        if not dest:
            return
        try:
            unpack(src, dest)
            self.statusBar().showMessage(f"Unpacked -> {dest}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Unpack failed", f"{e}")

    def pack_folder(self):
        src = QFileDialog.getExistingDirectory(self, "Select folder to repack", "")
        if not src:
            return
        out, _ = QFileDialog.getSaveFileName(self, "Save packed docx as", "",
                                             "Word Documents (*.docx)")
        if not out:
            return
        try:
            repack(src, out)
            self.statusBar().showMessage(f"Packed -> {out}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Pack failed", f"{e}")

    def close_doc(self):
        if self.doc is not None:
            if self._modified:
                r = QMessageBox.question(self, "Confirm", "Save unsaved changes?")
                if r == QMessageBox.Yes:
                    self.save_file()
            self.doc.close()
            self.doc = None; self.path = None; self._modified = False
            self.tree.clear(); self.parts_list.clear()
            self.table.clear(); self.para_edit.clear()
            self._update_title()

    def _set_modified(self):
        self._modified = True; self._update_title()

    def _update_title(self):
        name = os.path.basename(self.path) if self.path else "(no document)"
        flag = " *" if self._modified else ""
        self.setWindowTitle(f"DocxMod — {name}{flag}")

    # ---- refresh -----------------------------------------------------------

    def _refresh_all(self):
        self._refresh_tree(); self._refresh_parts()

    def _refresh_tree(self):
        self.tree.clear()
        if self.doc is None:
            return
        root = QTreeWidgetItem(self.tree, ["Document"])
        for i, p in enumerate(self.doc.paragraphs):
            txt = p.text.strip().replace("\n", " ")
            if len(txt) > 50:
                txt = txt[:50] + "…"
            it = QTreeWidgetItem(root, [f"[P{i:03d}] {txt}"])
            it.setData(0, Qt.UserRole, ("para", i))
        for ti, tb in enumerate(self.doc.tables):
            it = QTreeWidgetItem(root, [f"[Table {ti}] {tb.row_count()}r × {tb.col_count()}c"])
            it.setData(0, Qt.UserRole, ("table", ti))
            for ri in range(tb.row_count()):
                cells = " | ".join(c[:20] for c in tb.row_texts(ri))
                rit = QTreeWidgetItem(it, [f"R{ri}: {cells}"])
                rit.setData(0, Qt.UserRole, ("table", ti))
        root.setExpanded(True)

    def _refresh_parts(self):
        self.parts_list.clear()
        if self.doc is None:
            return
        for name in self.doc.parts:
            self.parts_list.addItem(name)

    # ---- selection ---------------------------------------------------------

    def _on_select(self, item):
        if self.doc is None:
            return
        data = item.data(0, Qt.UserRole)
        if data is None:
            return
        kind, idx = data
        if kind == "para":
            self.tabs.setCurrentIndex(0); self._load_para(idx)
        elif kind == "table":
            self.tabs.setCurrentIndex(1); self._load_table(idx)

    def _load_para(self, idx):
        self._current_tab = ("para", idx)
        try:
            p = self.doc.paragraphs[idx]
        except IndexError:
            return
        self.para_label.setText(f"Paragraph P{idx:03d}")
        self._loading = True
        self.para_edit.setPlainText(p.text)
        self.style_edit.setText(p.style or "")
        self._loading = False

    def _load_table(self, idx):
        self._current_tab = ("table", idx)
        try:
            tb = self.doc.tables[idx]
        except IndexError:
            return
        self.tbl_label.setText(
            f"Table {idx}: {tb.row_count()} rows × {tb.col_count()} cols "
            "(merged cells shown by actual tc)"
        )
        self._loading = True
        self.table.clear()
        self.table.setRowCount(tb.row_count())
        self.table.setColumnCount(tb.col_count())
        for r in range(tb.row_count()):
            tcs = tb.rows[r].findall(w("tc"))
            for c in range(tb.col_count()):
                text = ""
                if c < len(tcs):
                    try:
                        text = tb.cell(r, c).text
                    except Exception:
                        text = ""
                self.table.setItem(r, c, QTableWidgetItem(text))
        self._loading = False

    # ---- paragraph editing -------------------------------------------------

    def _apply_para(self):
        if self._current_tab and self._current_tab[0] == "para":
            idx = self._current_tab[1]
            self.doc.paragraphs[idx].set_text(self.para_edit.toPlainText())
            self._set_modified(); self._refresh_tree()
            self.statusBar().showMessage("Paragraph updated (format preserved)", 3000)

    def _insert_para(self, after):
        if not self._current_tab or self._current_tab[0] != "para":
            return
        idx = self._current_tab[1]
        p = self.doc.paragraphs[idx]
        if after:
            p.insert_paragraph_after(self.para_edit.toPlainText())
        else:
            p.insert_paragraph_before(self.para_edit.toPlainText())
        self._set_modified(); self._refresh_tree()

    def _delete_para(self):
        if not self._current_tab or self._current_tab[0] != "para":
            return
        idx = self._current_tab[1]
        self.doc.paragraphs[idx].delete()
        self._set_modified(); self._refresh_tree(); self.para_edit.clear()

    def _apply_style(self):
        if not self._current_tab or self._current_tab[0] != "para":
            return
        idx = self._current_tab[1]
        self.doc.paragraphs[idx].style = self.style_edit.text() or None
        self._set_modified()

    # ---- table editing -----------------------------------------------------

    def _on_cell_changed(self, item):
        if self._loading or self.doc is None:
            return
        kind, idx = (self._current_tab or (None, None))
        if kind != "table":
            return
        r, c = item.row(), item.column()
        try:
            self.doc.tables[idx].cell(r, c).set_text(item.text())
            self._set_modified()
        except Exception as e:
            QMessageBox.warning(self, "Write failed", f"{e}")

    def _add_row(self):
        if self._current_tab and self._current_tab[0] == "table":
            self.doc.tables[self._current_tab[1]].add_row()
            self._set_modified(); self._load_table(self._current_tab[1]); self._refresh_tree()

    def _del_row(self):
        if self._current_tab and self._current_tab[0] == "table":
            r = self.table.currentRow()
            if r >= 0:
                self.doc.tables[self._current_tab[1]].delete_row(r)
                self._set_modified(); self._load_table(self._current_tab[1]); self._refresh_tree()

    def _add_col(self):
        if self._current_tab and self._current_tab[0] == "table":
            self.doc.tables[self._current_tab[1]].add_column()
            self._set_modified(); self._load_table(self._current_tab[1]); self._refresh_tree()

    def _del_col(self):
        if self._current_tab and self._current_tab[0] == "table":
            c = self.table.currentColumn()
            if c >= 0:
                self.doc.tables[self._current_tab[1]].delete_column(c)
                self._set_modified(); self._load_table(self._current_tab[1]); self._refresh_tree()

    # ---- find/replace / parts ----------------------------------------------

    def find_replace(self):
        if self.doc is None:
            return
        dlg = FindReplaceDialog(self)
        if dlg.exec():
            old, new = dlg.values()
            if not old:
                return
            n = self.doc.replace_text(old, new)
            if n:
                self._set_modified(); self._refresh_tree()
            QMessageBox.information(self, "Replace done", f"Replaced {n} occurrence(s)")

    def _edit_part_xml(self, item):
        if self.doc is None:
            return
        name = item.text()
        if not name.endswith(".xml"):
            QMessageBox.information(self, "Info", "This part is not XML and cannot be edited as XML.")
            return
        data = self.doc.part_bytes(name)
        dlg = PartXmlDialog(name, data, self)
        if dlg.exec():
            try:
                self.doc.set_part_bytes(name, dlg.new_bytes())
                self._set_modified(); self._refresh_tree()
                self.statusBar().showMessage(f"Updated part {name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Write failed", f"{e}")

    def _show_part_info(self):
        if self.doc is None:
            return
        it = self.parts_list.currentItem()
        if not it:
            return
        name = it.text()
        size = len(self.doc.part_bytes(name))
        QMessageBox.information(self, "Part info", f"{name}\nSize: {size} bytes")

    def _about(self):
        QMessageBox.about(self, "About DocxMod",
            "DocxMod — lossless DOCX unpack / edit / repack toolkit.\n\n"
            "Unmodified parts are preserved byte-for-byte; only edited XML "
            "parts are re-serialised.\n\n"
            "Supports paragraph / table / cell / style editing, global "
            "find-replace, raw part XML editing, and unpack/repack workflows.")

    # ---- close -------------------------------------------------------------

    def closeEvent(self, e):
        self.close_doc()
        super().closeEvent(e)


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        win.open_file(sys.argv[1])
    sys.exit(app.exec())


if __name__ == "__main__":
    main()