"""Create a full-bleed A4 PDF while preserving native Excel rule widths."""

from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream, FloatObject


def render_pdf(pdf: Path, target: Path, pdftoppm: Path, dpi: int) -> list[Path]:
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(pdftoppm), "-r", str(dpi), "-png", str(pdf), str(target)],
        check=True,
    )
    return sorted(target.parent.glob(f"{target.name}-*.png"))


def visible_bbox(image_path: Path, threshold: int = 250) -> tuple[int, int, int, int]:
    image = Image.open(image_path).convert("RGB")
    pixels = image.load()
    width, height = image.size
    left, top, right, bottom = width, height, -1, -1
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if min(r, g, b) < threshold:
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)
    if right < left or bottom < top:
        return 0, 0, width, height
    return left, top, right + 1, bottom + 1


def normalized_rule_width(value: float) -> float:
    """Return the visual print width for an Excel-exported rule."""
    value = abs(value)
    if value <= 1.0:
        return 0.50
    if value <= 2.0:
        return 0.72
    return value


def compensate_rules(page, sx: float, sy: float) -> None:
    """Normalize Excel rules and counter-scale them before page scaling."""
    stream = ContentStream(page.get_contents(), page.pdf)
    for operands, operator in stream.operations:
        op = operator.decode("latin1") if isinstance(operator, bytes) else operator
        if op == "w" and operands:
            # The explicit line shapes in the quotation are horizontal.
            operands[0] = FloatObject(float(operands[0]) / sy)
        elif op == "re" and len(operands) >= 4:
            x, y, width, height = map(float, operands[:4])
            abs_width, abs_height = abs(width), abs(height)
            if 0 < abs_height <= 2.0 and abs_width > 5.0:
                adjusted = math.copysign(normalized_rule_width(abs_height) / sy, height)
                y += (height - adjusted) / 2.0
                height = adjusted
            if 0 < abs_width <= 2.0 and abs_height > 5.0:
                adjusted = math.copysign(normalized_rule_width(abs_width) / sx, width)
                x += (width - adjusted) / 2.0
                width = adjusted
            operands[0] = FloatObject(x)
            operands[1] = FloatObject(y)
            operands[2] = FloatObject(width)
            operands[3] = FloatObject(height)
    page.replace_contents(stream)


def create_full_bleed(
    source: Path,
    output: Path,
    bboxes: list[tuple[int, int, int, int]],
    image_sizes: list[tuple[int, int]],
) -> list[dict]:
    reader = PdfReader(str(source))
    writer = PdfWriter()
    reports = []
    for index, source_page in enumerate(reader.pages):
        writer.add_page(source_page)
        page = writer.pages[-1]
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        left, top, right, bottom = bboxes[index]
        pixel_width, pixel_height = image_sizes[index]
        x0 = left / pixel_width * width
        x1 = right / pixel_width * width
        y0 = (pixel_height - bottom) / pixel_height * height
        y1 = (pixel_height - top) / pixel_height * height
        content_width = max(1.0, x1 - x0)
        content_height = max(1.0, y1 - y0)
        sx = width / content_width
        sy = height / content_height
        compensate_rules(page, sx, sy)
        tx = -x0 * sx
        ty = -y0 * sy
        media = page.mediabox
        page.add_transformation(Transformation().scale(sx, sy).translate(tx, ty))
        page.mediabox = media
        page.cropbox = media
        reports.append(
            {
                "page": index + 1,
                "bbox_px": bboxes[index],
                "image_px": image_sizes[index],
                "scale": (sx, sy),
                "translate_pt": (tx, ty),
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        writer.write(handle)
    return reports


def rule_metrics(pdf: Path) -> list[dict]:
    import pdfplumber

    metrics = []
    with pdfplumber.open(pdf) as document:
        for index, page in enumerate(document.pages, 1):
            strokes = sorted(round(float(line.get("linewidth") or 0), 4) for line in page.lines)
            horizontal_rects = sorted(
                round(abs(float(rect["height"])), 4)
                for rect in page.rects
                if 0 < abs(float(rect["height"])) <= 2.5 and abs(float(rect["width"])) > 5
            )
            vertical_rects = sorted(
                round(abs(float(rect["width"])), 4)
                for rect in page.rects
                if 0 < abs(float(rect["width"])) <= 2.5 and abs(float(rect["height"])) > 5
            )
            metrics.append(
                {
                    "page": index,
                    "stroke_widths": strokes,
                    "horizontal_rule_heights": horizontal_rects,
                    "vertical_rule_widths": vertical_rects,
                }
            )
    return metrics


def compare_metrics(native: list[dict], final: list[dict], tolerance: float = 0.02) -> None:
    for before, after in zip(native, final, strict=True):
        for key in ("stroke_widths", "horizontal_rule_heights", "vertical_rule_widths"):
            a = before[key]
            b = after[key]
            if len(a) != len(b):
                raise AssertionError(f"page {before['page']} {key}: count {len(a)} != {len(b)}")
            expected = a if key == "stroke_widths" else [normalized_rule_width(value) for value in a]
            for index, (left, right) in enumerate(zip(expected, b, strict=True)):
                if not math.isclose(left, right, abs_tol=tolerance):
                    raise AssertionError(
                        f"page {before['page']} {key}[{index}]: {left} != {right}"
                    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--pdftoppm", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="quote-pdf-") as temp_name:
        temp = Path(temp_name)
        native_images = render_pdf(args.source, temp / "native", args.pdftoppm, args.dpi)
        bboxes = [visible_bbox(path) for path in native_images]
        sizes = [Image.open(path).size for path in native_images]
        reports = create_full_bleed(args.source, args.output, bboxes, sizes)
        final_images = render_pdf(args.output, temp / "final", args.pdftoppm, args.dpi)
        final_bboxes = [visible_bbox(path) for path in final_images]
        final_sizes = [Image.open(path).size for path in final_images]

    native_metrics = rule_metrics(args.source)
    final_metrics = rule_metrics(args.output)
    compare_metrics(native_metrics, final_metrics)

    check = PdfReader(str(args.output))
    if len(check.pages) != 2:
        raise AssertionError(f"expected 2 pages, got {len(check.pages)}")
    if not all((page.extract_text() or "").strip() for page in check.pages):
        raise AssertionError("selectable text is missing")
    for bbox, size in zip(final_bboxes, final_sizes, strict=True):
        if bbox != (0, 0, size[0], size[1]):
            raise AssertionError(f"page is not full bleed: bbox={bbox}, size={size}")

    for report in reports:
        print(report)
    print("native_rule_metrics=", native_metrics)
    print("final_rule_metrics=", final_metrics)
    print("final_bboxes=", final_bboxes)
    print("pages=2 selectable_text=true line_width_normalized=true full_bleed=true")


if __name__ == "__main__":
    main()
