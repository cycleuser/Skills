#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_doc.py — build a minimal but real Word 97 binary (.doc) file in pure
Python, for self-verification of the doc2docx converter.

Writes a valid OLE2/Compound-File container by hand (no external libraries)
containing a WordDocument stream and a 0Table stream with a real FIB, piece
table (CLX), CHPX/PAPX FKP pages, a section (PlcfSed/SEPX), a style sheet
(STSH) and a font table (STTBF ffn).

Generated document::

    ¶1 "你好，世界 Hello World"   — bold, 宋体, 16 pt  (font#1, size 32)
    ¶2 "Second paragraph"          — italic, Times New Roman, 12 pt, centered
    a table (2 rows x 2 cols)      — cells A/B/C/D via fInTable/fTtp marks
    page setup                     — A4, 2.54 cm margins

Usage::

    python make_doc.py out.doc
"""

from __future__ import annotations

import struct
import sys

SECTOR = 512
FCMIN = 2048


def u16(x: int) -> bytes:
    return struct.pack("<H", x)


def u32(x: int) -> bytes:
    return struct.pack("<I", x)


def _pad(data: bytes, n: int = SECTOR) -> bytes:
    return data + b"\x00" * ((n - len(data) % n) % n)


# --------------------------------------------------------------------------- #
#  OLE2 / Compound File writer (regular streams only, each >= 4096 B)
# --------------------------------------------------------------------------- #

def build_ole2(streams: list[tuple[str, bytes]]) -> bytes:
    data = []
    for _name, blob in streams:
        if len(blob) < 4096:
            blob = blob + b"\x00" * (4096 - len(blob))
        data.append(_pad(blob))
    sizes = [len(b) for b in data]
    n_sectors = [len(b) // SECTOR for b in data]

    # CFB sector numbers (the header is NOT a numbered sector): the first CFB
    # sector sits at file byte SECTOR (file sector 1).
    cursor = 0
    start = []
    for ns in n_sectors:
        start.append(cursor)
        cursor += ns
    dir_start = cursor
    cursor += 1
    fat_start = cursor
    total = cursor + 2   # CFB sectors 0..fat_start + one trailing slack sector

    fat = [0xFFFFFFFF] * total
    for si, ns in enumerate(n_sectors):
        first = start[si]
        for k in range(ns):
            fat[first + k] = first + k + 1 if k + 1 < ns else 0xFFFFFFFD
    fat[dir_start] = 0xFFFFFFFD
    fat[fat_start] = 0xFFFFFFFD

    # ensure FAT has one entry per sector (including itself)
    fat = fat[: total]
    if fat_start >= len(fat):
        fat.extend([0xFFFFFFFE] * (fat_start + 1 - len(fat)))

    def dir_entry(name, otype, start_sector, size, child=0xFFFFFFFF,
                  left=0xFFFFFFFF, right=0xFFFFFFFF):
        e = bytearray(128)
        nb = name.encode("utf-16-le")
        e[0: len(nb)] = nb
        struct.pack_into("<H", e, 0x40, len(nb) + 2)
        e[0x42] = otype
        e[0x43] = 1
        struct.pack_into("<I", e, 0x44, left)
        struct.pack_into("<I", e, 0x48, right)
        struct.pack_into("<I", e, 0x4C, child)
        struct.pack_into("<I", e, 0x74, start_sector)
        struct.pack_into("<Q", e, 0x78, size)
        return bytes(e)

    d = bytearray()
    d += dir_entry("Root Entry", 5, 0xFFFFFFFE, 0, child=1)
    d += dir_entry("WordDocument", 2, start[0], sizes[0], right=2)
    d += dir_entry("0Table", 2, start[1], sizes[1])
    dir_bytes = _pad(bytes(d))

    hdr = bytearray(512)
    hdr[0:8] = bytes.fromhex("D0CF11E0A1B11AE1")
    struct.pack_into("<H", hdr, 0x1A, 3)
    struct.pack_into("<H", hdr, 0x1C, 0xFFFE)
    struct.pack_into("<H", hdr, 0x1E, 9)
    struct.pack_into("<H", hdr, 0x20, 6)
    struct.pack_into("<I", hdr, 0x2C, 1)
    struct.pack_into("<I", hdr, 0x30, dir_start)
    struct.pack_into("<I", hdr, 0x38, 4096)
    struct.pack_into("<I", hdr, 0x3C, 0xFFFFFFFE)
    struct.pack_into("<I", hdr, 0x44, 0xFFFFFFFE)
    struct.pack_into("<I", hdr, 0x4C, fat_start)

    out = bytearray(_pad(bytes(hdr)))
    for b in data:
        out += b
    out += dir_bytes
    out += _pad(b"".join(u32(v) for v in fat))
    # one extra slack sector after the FAT (olefile reads past the FAT sector)
    out += b"\x00" * SECTOR
    return bytes(out[: SECTOR * (total + 1)])   # header sector + CFB sectors


# --------------------------------------------------------------------------- #
#  sprm helpers
# --------------------------------------------------------------------------- #

def sprm(w: int, op: bytes) -> bytes:
    return u16(w) + op


# --------------------------------------------------------------------------- #
#  Minimal .doc content
# --------------------------------------------------------------------------- #

def build_doc() -> bytes:
    fcMin = FCMIN
    parts = ["你好，世界 Hello World\r",      # p1  19 chars
             "Second paragraph\r",            # p2  18 chars
             "A\x07", "B\x07", "\x07",        # row1 cells + end-of-row
             "C\x07", "D\x07", "\x07"]        # row2 cells + end-of-row
    text = "".join(parts)
    ccpText = len(text)
    fcMac = fcMin + 2 * ccpText
    fcs = [fcMin]
    acc = fcMin
    for part in parts:
        acc += 2 * len(part)
        fcs.append(acc)
    para_fcs = fcs[:-1]

    # ---- CHPX runs ----------------------------------------------------------
    chpx_runs = [
        (para_fcs[0], para_fcs[1],
         sprm(0x0835, b"\x01") + sprm(0x4A43, u16(32)) + sprm(0x4A50, u16(1))),
        (para_fcs[1], para_fcs[2],
         sprm(0x0836, b"\x01") + sprm(0x4A43, u16(24)) + sprm(0x4A4F, u16(0))),
        (para_fcs[2], fcMac, b""),
    ]
    # ---- PAPX runs ----------------------------------------------------------
    tdef = sprm(0xD608, u16(8) + bytes([2]) + u16(0) + u16(1200) + u16(2400))
    papx_runs = [
        (para_fcs[0], sprm(0x2403, b"\x00")),
        (para_fcs[1], sprm(0x2403, b"\x01")),
        (para_fcs[2], sprm(0x2416, b"\x01")),
        (para_fcs[3], sprm(0x2416, b"\x01")),
        (para_fcs[4], sprm(0x2416, b"\x01") + sprm(0x2417, b"\x01") + tdef),
        (para_fcs[5], sprm(0x2416, b"\x01")),
        (para_fcs[6], sprm(0x2416, b"\x01")),
        (para_fcs[7], sprm(0x2416, b"\x01") + sprm(0x2417, b"\x01") + tdef),
    ]

    chpx_fkp = _build_chpx_fkp(chpx_runs)
    papx_fkp = _build_papx_fkp(papx_runs)

    # ---- WordDocument -------------------------------------------------------
    wd = bytearray(4096)
    struct.pack_into("<H", wd, 0, 0xA5EC)
    struct.pack_into("<H", wd, 2, 0x00C1)
    struct.pack_into("<H", wd, 12, 0x00BF)
    struct.pack_into("<I", wd, 24, fcMin)
    struct.pack_into("<I", wd, 28, fcMac)
    struct.pack_into("<H", wd, 32, 14)     # csw
    struct.pack_into("<H", wd, 62, 22)     # cslw
    lw_off = 64
    lw = [0, 0, 0, ccpText, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, fcMac, 0, 0, 0, 0, 0, 0, 0]
    for i, v in enumerate(lw):
        struct.pack_into("<I", wd, lw_off + 4 * i, v)
    fc_lcb_off = lw_off + 22 * 4
    struct.pack_into("<H", wd, fc_lcb_off, 164)
    for i in range(164):
        struct.pack_into("<II", wd, fc_lcb_off + 2 + 8 * i, 0, 0)

    wd[fcMin:fcMac] = text.encode("utf-16-le")
    fkp_off = (fcMac + SECTOR - 1) // SECTOR * SECTOR
    wd[fkp_off:fkp_off + SECTOR] = chpx_fkp
    wd[fkp_off + SECTOR:fkp_off + 2 * SECTOR] = papx_fkp

    # SEPX lives in WordDocument (after the FKP pages)
    sepx_grpprl = (sprm(0xB01F, u16(11906)) + sprm(0xB020, u16(16838))
                   + sprm(0xB021, u16(1800)) + sprm(0xB022, u16(1800))
                   + sprm(0x9023, u16(1440)) + sprm(0x9024, u16(1440)))
    sepx = u16(len(sepx_grpprl)) + sepx_grpprl
    sep_off = fkp_off + 2 * SECTOR
    wd[sep_off:sep_off + len(sepx)] = sepx

    # ---- 0Table -------------------------------------------------------------
    chpx_plcf = _build_plcf(chpx_runs, fkp_off // SECTOR)
    papx_plcf = _build_plcf_papx(papx_runs, (fkp_off // SECTOR) + 1)
    stsh = _build_stsh()
    ffn = _build_ffn(["Times New Roman", "宋体"])
    clx = bytes([0x02]) + u32(16) + u32(0) + u32(ccpText) + u16(0) + u32(fcMin) + u16(0)
    sed = (u32(0) + u32(ccpText)
           + u16(0) + u32(sep_off) + u16(0) + u32(0))

    tbl = bytearray(4096)
    off = 0
    offs = {}
    for name, blob in [("stsh", stsh), ("ffn", ffn), ("chpx", chpx_plcf),
                       ("papx", papx_plcf), ("clx", clx), ("sed", sed)]:
        tbl[off:off + len(blob)] = blob
        offs[name] = off
        off += len(blob)

    def patch(idx, fc, lcb):
        struct.pack_into("<II", wd, fc_lcb_off + 2 + 8 * idx, fc, lcb)

    patch(1, offs["stsh"], len(stsh))
    patch(12, offs["chpx"], len(chpx_plcf))
    patch(13, offs["papx"], len(papx_plcf))
    patch(15, offs["ffn"], len(ffn))
    patch(33, offs["clx"], len(clx))
    patch(6, offs["sed"], len(sed))

    return build_ole2([("WordDocument", bytes(wd)), ("0Table", bytes(tbl))])


# --------------------------------------------------------------------------- #
#  structure builders
# --------------------------------------------------------------------------- #

def _build_chpx_fkp(runs) -> bytes:
    fkp = bytearray(SECTOR)
    crun = len(runs)
    fkp[511] = crun
    for i, (fc0, _fc1, _gp) in enumerate(runs):
        struct.pack_into("<I", fkp, i * 4, fc0)
    struct.pack_into("<I", fkp, crun * 4, runs[-1][1])
    rgb_start = (crun + 1) * 4
    pos = rgb_start + crun
    if pos % 2:
        pos += 1
    for i, (_fc0, _fc1, gp) in enumerate(runs):
        fkp[rgb_start + i] = (pos // 2) & 0xFF
        fkp[pos] = len(gp)
        fkp[pos + 1:pos + 1 + len(gp)] = gp
        pos += 1 + len(gp)
        if pos % 2:
            pos += 1
    return bytes(fkp)


def _build_papx_fkp(runs) -> bytes:
    fkp = bytearray(SECTOR)
    cpara = len(runs)
    fkp[511] = cpara
    for i, (fc0, _gp) in enumerate(runs):
        struct.pack_into("<I", fkp, i * 4, fc0)
    rgb_start = (cpara + 1) * 4
    pos = rgb_start + cpara * 13
    if pos % 2:
        pos += 1
    for i, (_fc0, gp) in enumerate(runs):
        while len(gp) % 2 == 0:
            gp = gp + b"\x00"
        size_byte = (len(gp) + 3) // 2
        entry = (b"\x00" if i == 0 else b"") + bytes([size_byte]) + u16(0) + gp
        fkp[rgb_start + i * 13] = (pos // 2) & 0xFF
        fkp[pos:pos + len(entry)] = entry
        pos += len(entry)
        if pos % 2:
            pos += 1
    return bytes(fkp)


def _build_plcf(runs, fkp_page) -> bytes:
    out = b"".join(u32(fc0) for fc0, _fc1, _gp in runs)
    out += u32(runs[-1][1])
    out += b"".join(u32(fkp_page) for _ in runs)
    return out


def _build_plcf_papx(runs, fkp_page) -> bytes:
    out = b"".join(u32(fc0) for fc0, _gp in runs)
    out += u32(runs[-1][0] + 2)   # end of last paragraph = fcMac
    out += b"".join(u32(fkp_page) for _ in runs)
    return out


def _build_stsh() -> bytes:
    # Normal (paragraph style, istd 0) with a character default (宋体 10.5pt)
    chpx = sprm(0x4A43, u16(21)) + sprm(0x4A50, u16(1))
    upx_pap = u16(5) + u16(0) + sprm(0x2403, b"\x00")   # istd 0 + jc left
    if len(upx_pap) % 2:
        upx_pap += b"\x00"                              # pad to even length
    upx_chp = u16(len(chpx)) + chpx
    name_utf16 = "Normal".encode("utf-16-le")
    name_field = u16(len(name_utf16) // 2) + name_utf16 + u16(0)
    # StdfBase(18): sti(2) type|base(2) cupx|next(2) bchUpe(2) + padding
    type_base = u16((0xFFF << 4) | 1)     # paragraph style, base = none
    cupx_next = u16(2)                    # UpxPapx + UpxChpx
    stdf_base = u16(0) + type_base + cupx_next + u16(0)
    stdf_base += b"\x00" * (18 - len(stdf_base))
    std_body = stdf_base + name_field + upx_pap + upx_chp
    if len(std_body) % 2:
        std_body += b"\x00"
    std = u16(len(std_body)) + std_body
    # STSH header: word[0] = rglpstd_offset - 2 ; cstd@2 ; cbSTDBase@4
    return u16(4) + u16(1) + u16(18) + std


def _build_ffn(fonts) -> bytes:
    out = b""
    for name in fonts:
        nb = name.encode("utf-16-le") + u16(0)
        ffn = bytes([len(nb) + 40 - 1]) + b"\x04" + u16(400) + b"\x00\x00"
        ffn += b"\x00" * 10
        ffn += b"\x00" * 24
        ffn += nb
        out += ffn
    return u16(len(fonts)) + u16(0) + out


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "sample.doc"
    with open(out, "wb") as fh:
        fh.write(build_doc())
    print(f"wrote {out}")
