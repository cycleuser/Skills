"""Batch OCR with PaddleOCR.

Runs PaddleOCR over a directory of images and PDFs, producing a single
`raw_ocr.json` with per-page text, confidence and provenance so the LLM
refinement step can ingest it.

Usage:
    python batch_ocr.py <input_dir> [--output raw_ocr.json] [--lang ch]
                          [--dpi 200] [--no-angle-cls] [--workers 1]

Exit codes:
    0  success (some or all pages OCR'd)
    2  input_dir missing or empty
    3  PaddleOCR not installed
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable


SUPPORTED_IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}
SUPPORTED_PDF_EXT = {".pdf"}


@dataclass
class OCRItem:
    id: str
    source_file: str
    page: int
    image_path: str
    raw_text: str
    raw_text_lines: list[str]
    confidence: float
    char_count: int
    bbox_count: int
    error: str | None = None


@dataclass
class OCRResult:
    source_dir: str
    timestamp: str
    lang: str
    use_angle_cls: bool
    items: list[OCRItem] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["items"] = [asdict(i) for i in self.items]
        return d


def _import_paddleocr():
    try:
        from paddleocr import PaddleOCR  # type: ignore
        return PaddleOCR
    except ImportError as exc:
        print(
            "[ERROR] paddleocr 未安装。请先运行：\n"
            "    pip install paddlepaddle paddleocr pdf2image\n"
            "并确保 poppler 已加入 PATH（pdf2image 需要它处理 PDF）。",
            file=sys.stderr,
        )
        print(f"        详细错误：{exc}", file=sys.stderr)
        sys.exit(3)


def _import_fitz():
    try:
        import fitz  # type: ignore  # PyMuPDF
        return fitz
    except ImportError:
        print(
            "[ERROR] PyMuPDF (fitz) 未安装。请运行：pip install pymupdf",
            file=sys.stderr,
        )
        sys.exit(3)


def pdf_to_images(pdf_path: Path, out_dir: Path, dpi: int = 200) -> list[Path]:
    """Render every page of a PDF to a PNG and return the image paths."""
    fitz = _import_fitz()
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    paths: list[str] = []
    try:
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out_path = out_dir / f"{pdf_path.stem}_page_{i:03d}.png"
            pix.save(str(out_path))
            paths.append(str(out_path))
    finally:
        doc.close()
    return [Path(p) for p in paths]


def iter_inputs(input_dir: Path) -> Iterable[Path]:
    for p in sorted(input_dir.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() in SUPPORTED_IMG_EXT or p.suffix.lower() in SUPPORTED_PDF_EXT:
            yield p


def run_ocr_on_image(ocr, image_path: Path) -> tuple[str, list[str], float]:
    """Return (joined_text, lines, mean_conf).

    Compatible with PaddleOCR 3.x ``predict`` API which returns a list of
    ``OCRResult`` objects exposing ``rec_texts`` / ``rec_scores``.
    """
    results = ocr.predict(str(image_path))
    lines: list[str] = []
    confs: list[float] = []
    for res in results:
        texts = res.get("rec_texts", []) or []
        scores = res.get("rec_scores", []) or []
        for text, conf in zip(texts, scores):
            text = (text or "").strip()
            if not text:
                continue
            lines.append(text)
            try:
                confs.append(float(conf))
            except (TypeError, ValueError):
                confs.append(0.0)
    return "\n".join(lines), lines, (sum(confs) / len(confs)) if confs else 0.0


def _resolve_device(device_arg: str) -> str:
    """Resolve 'auto' to 'gpu' when a CUDA device is available, else 'cpu'."""
    if device_arg != "auto":
        return device_arg
    try:
        import paddle  # type: ignore
        if paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0:
            return "gpu"
    except Exception:
        pass
    return "cpu"


def process_input(
    input_dir: Path,
    output_path: Path,
    lang: str,
    use_angle_cls: bool,
    dpi: int,
    page_subdir: str,
    device: str = "auto",
    log=print,
) -> OCRResult:
    PaddleOCR = _import_paddleocr()
    resolved_device = _resolve_device(device)
    ocr = PaddleOCR(
        lang=lang,
        use_textline_orientation=use_angle_cls,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        device=resolved_device,
    )
    log(f"[INFO] OCR 设备: {resolved_device}")

    out_root = output_path.parent
    page_dir = out_root / page_subdir
    page_dir.mkdir(parents=True, exist_ok=True)

    result = OCRResult(
        source_dir=str(input_dir.resolve()),
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
        lang=lang,
        use_angle_cls=use_angle_cls,
    )

    inputs = list(iter_inputs(input_dir))
    if not inputs:
        print(f"[ERROR] 在 {input_dir} 找不到可处理的图片或 PDF。", file=sys.stderr)
        sys.exit(2)

    log(f"[INFO] 发现 {len(inputs)} 个输入文件，开始 OCR（首次会下载模型，请耐心等待）…")
    for idx, src in enumerate(inputs, 1):
        log(f"[INFO] ({idx}/{len(inputs)}) {src.name}")
        if src.suffix.lower() in SUPPORTED_PDF_EXT:
            try:
                page_imgs = pdf_to_images(src, page_dir, dpi=dpi)
            except SystemExit:
                raise
            except Exception as exc:
                result.items.append(OCRItem(
                    id=f"{src.stem}_err",
                    source_file=src.name,
                    page=0,
                    image_path="",
                    raw_text="",
                    raw_text_lines=[],
                    confidence=0.0,
                    char_count=0,
                    bbox_count=0,
                    error=f"PDF 拆页失败: {exc}",
                ))
                continue
            for page_idx, img_path in enumerate(page_imgs, 1):
                item_id = f"{src.stem}_page_{page_idx}"
                try:
                    text, lines, conf = run_ocr_on_image(ocr, img_path)
                    result.items.append(OCRItem(
                        id=item_id,
                        source_file=src.name,
                        page=page_idx,
                        image_path=str(img_path.relative_to(out_root)),
                        raw_text=text,
                        raw_text_lines=lines,
                        confidence=round(conf, 4),
                        char_count=len(text),
                        bbox_count=len(lines),
                    ))
                    log(f"        page {page_idx}: {len(text)} 字符, 均置信度 {conf:.3f}")
                except Exception as exc:
                    result.items.append(OCRItem(
                        id=item_id,
                        source_file=src.name,
                        page=page_idx,
                        image_path=str(img_path.relative_to(out_root)),
                        raw_text="",
                        raw_text_lines=[],
                        confidence=0.0,
                        char_count=0,
                        bbox_count=0,
                        error=f"OCR 失败: {exc}",
                    ))
        else:
            item_id = src.stem
            try:
                text, lines, conf = run_ocr_on_image(ocr, src)
                # 同时把原图复制到 page_dir 以便后续校对
                target = page_dir / src.name
                if not target.exists():
                    target.write_bytes(src.read_bytes())
                result.items.append(OCRItem(
                    id=item_id,
                    source_file=src.name,
                    page=1,
                    image_path=str(target.relative_to(out_root)),
                    raw_text=text,
                    raw_text_lines=lines,
                    confidence=round(conf, 4),
                    char_count=len(text),
                    bbox_count=len(lines),
                ))
                log(f"        {len(text)} 字符, 均置信度 {conf:.3f}")
            except Exception as exc:
                result.items.append(OCRItem(
                    id=item_id,
                    source_file=src.name,
                    page=1,
                    image_path=src.name,
                    raw_text="",
                    raw_text_lines=[],
                    confidence=0.0,
                    char_count=0,
                    bbox_count=0,
                    error=f"OCR 失败: {exc}",
                ))

    output_path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log(f"[OK] 写入 {output_path}，共 {len(result.items)} 项。")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Batch OCR with PaddleOCR")
    ap.add_argument("input_dir", help="包含 PNG/JPG/PDF 的目录")
    ap.add_argument("--output", default="raw_ocr.json", help="输出 JSON 路径（默认 raw_ocr.json）")
    ap.add_argument("--lang", default="ch", help="PaddleOCR 语言代码，默认 ch（中文）")
    ap.add_argument("--dpi", type=int, default=200, help="PDF 转图分辨率，默认 200")
    ap.add_argument("--no-angle-cls", action="store_true", help="关闭文字方向分类")
    ap.add_argument("--page-subdir", default="page_images", help="PDF 拆图/单页图片子目录名")
    ap.add_argument("--device", default="auto", choices=["auto", "gpu", "cpu"],
                    help="OCR 推理设备，默认 auto（有 GPU 用 GPU，否则 CPU）")
    args = ap.parse_args(argv)

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"[ERROR] 目录不存在: {input_dir}", file=sys.stderr)
        return 2

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (input_dir / output_path).resolve()

    process_input(
        input_dir=input_dir,
        output_path=output_path,
        lang=args.lang,
        use_angle_cls=not args.no_angle_cls,
        dpi=args.dpi,
        page_subdir=args.page_subdir,
        device=args.device,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())