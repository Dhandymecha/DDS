#!/usr/bin/env python3
"""Apply the Dhandy semantic-table contract to an existing DOCX."""

from __future__ import annotations

import argparse
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import quoteattr


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
ET.register_namespace("w", W_NS)

TABLE_FONT_HALF_POINTS = 18  # 9 pt
MIN_ID_WIDTH_DXA = 1800
MIN_NARRATIVE_WIDTH_DXA = 1800


def w_attr(name: str) -> str:
    return f"{W}{name}"


def child(parent: ET.Element, tag: str) -> ET.Element:
    found = parent.find(f"{W}{tag}")
    if found is None:
        found = ET.SubElement(parent, f"{W}{tag}")
    return found


def style_id_by_name(styles_root: ET.Element, display_name: str) -> str:
    for style in styles_root.findall(f"{W}style"):
        name = style.find(f"{W}name")
        if name is not None and name.get(w_attr("val")) == display_name:
            style_id = style.get(w_attr("styleId"))
            if style_id:
                return style_id
    raise ValueError(f"Required Word style is missing: {display_name}")


def set_style_size(styles_root: ET.Element, display_name: str, half_points: int) -> str:
    for style in styles_root.findall(f"{W}style"):
        name = style.find(f"{W}name")
        if name is None or name.get(w_attr("val")) != display_name:
            continue
        rpr = child(style, "rPr")
        child(rpr, "sz").set(w_attr("val"), str(half_points))
        child(rpr, "szCs").set(w_attr("val"), str(half_points))
        style_id = style.get(w_attr("styleId"))
        if not style_id:
            raise ValueError(f"Style has no styleId: {display_name}")
        return style_id
    raise ValueError(f"Required Word style is missing: {display_name}")


def paragraph_style_id(paragraph: ET.Element) -> str | None:
    style = paragraph.find(f"{W}pPr/{W}pStyle")
    return None if style is None else style.get(w_attr("val"))


def cell_text(cell: ET.Element) -> str:
    return "".join(node.text or "" for node in cell.iter(f"{W}t")).strip()


def normalized_header(text: str) -> str:
    return " ".join(text.strip().lower().replace("_", " ").split())


def is_id_header(text: str) -> bool:
    value = normalized_header(text)
    compact = value.replace(" ", "")
    return (
        compact == "id"
        or compact.endswith("id")
        or "번호" in compact
        or "코드" in compact
        or compact in {"partno", "partno.", "rev", "rev.", "no", "no."}
    )


def required_id_width(cells: list[ET.Element]) -> int:
    longest = max((len(cell_text(cell).replace(" ", "")) for cell in cells), default=0)
    return max(MIN_ID_WIDTH_DXA, 500 + longest * 110)


def semantic_table(
    table: ET.Element, header_style_id: str, body_style_id: str
) -> bool:
    allowed = {header_style_id, body_style_id}
    return any(
        paragraph_style_id(paragraph) in allowed
        for paragraph in table.iter(f"{W}p")
    )


def ensure_fixed_layout(table: ET.Element) -> None:
    tbl_pr = child(table, "tblPr")
    layout = child(tbl_pr, "tblLayout")
    layout.set(w_attr("type"), "fixed")


def set_run_size(run: ET.Element, half_points: int) -> None:
    rpr = run.find(f"{W}rPr")
    if rpr is None:
        rpr = ET.Element(f"{W}rPr")
        run.insert(0, rpr)
    child(rpr, "sz").set(w_attr("val"), str(half_points))
    child(rpr, "szCs").set(w_attr("val"), str(half_points))


def ensure_no_wrap(cell: ET.Element) -> None:
    tc_pr = child(cell, "tcPr")
    no_wrap = tc_pr.find(f"{W}noWrap")
    if no_wrap is None:
        no_wrap = ET.Element(f"{W}noWrap")
        # Word enforces the CT_TcPr schema order. noWrap must precede
        # tcMar/textDirection/tcFitText/vAlign/hideMark/headers.
        following_tags = {
            f"{W}tcMar",
            f"{W}textDirection",
            f"{W}tcFitText",
            f"{W}vAlign",
            f"{W}hideMark",
            f"{W}headers",
        }
        insert_at = len(tc_pr)
        for index, existing in enumerate(tc_pr):
            if existing.tag in following_tags:
                insert_at = index
                break
        tc_pr.insert(insert_at, no_wrap)
    no_wrap.set(w_attr("val"), "1")


def grid_widths(table: ET.Element) -> tuple[ET.Element, list[int]]:
    grid = table.find(f"{W}tblGrid")
    if grid is None:
        raise ValueError("Semantic table is missing tblGrid")
    columns = grid.findall(f"{W}gridCol")
    widths = [int(column.get(w_attr("w"), "0")) for column in columns]
    if not columns or any(width <= 0 for width in widths):
        raise ValueError("Semantic table has invalid tblGrid widths")
    return grid, widths


def rebalance_widths(widths: list[int], id_columns: list[int], targets: dict[int, int]) -> list[int]:
    updated = list(widths)
    for index in id_columns:
        target = targets[index]
        if updated[index] >= target:
            continue
        delta = target - updated[index]
        donors = sorted(
            (i for i in range(len(updated)) if i not in id_columns),
            key=lambda i: updated[i],
            reverse=True,
        )
        remaining = delta
        for donor in donors:
            available = max(0, updated[donor] - MIN_NARRATIVE_WIDTH_DXA)
            take = min(available, remaining)
            updated[donor] -= take
            remaining -= take
            if remaining == 0:
                break
        if remaining:
            raise ValueError(
                f"Cannot widen ID column {index + 1} to {target} DXA without "
                "making another column too narrow"
            )
        updated[index] = target
    return updated


def set_table_widths(table: ET.Element, widths: list[int]) -> None:
    grid = table.find(f"{W}tblGrid")
    if grid is None:
        raise ValueError("Table grid is missing")
    for column, width in zip(grid.findall(f"{W}gridCol"), widths, strict=True):
        column.set(w_attr("w"), str(width))

    rows = table.findall(f"{W}tr")
    for row in rows:
        cells = row.findall(f"{W}tc")
        if len(cells) != len(widths):
            continue
        for cell, width in zip(cells, widths, strict=True):
            tc_pr = child(cell, "tcPr")
            tc_w = child(tc_pr, "tcW")
            tc_w.set(w_attr("type"), "dxa")
            tc_w.set(w_attr("w"), str(width))

    tbl_pr = child(table, "tblPr")
    tbl_w = child(tbl_pr, "tblW")
    tbl_w.set(w_attr("type"), "dxa")
    tbl_w.set(w_attr("w"), str(sum(widths)))


def patch_document(document_root: ET.Element, header_style_id: str, body_style_id: str) -> dict:
    semantic_count = 0
    id_columns_updated = 0
    rows_protected = 0

    for table in document_root.iter(f"{W}tbl"):
        if not semantic_table(table, header_style_id, body_style_id):
            continue
        semantic_count += 1
        ensure_fixed_layout(table)

        for run in table.iter(f"{W}r"):
            set_run_size(run, TABLE_FONT_HALF_POINTS)

        rows = table.findall(f"{W}tr")
        if not rows:
            continue
        header_cells = rows[0].findall(f"{W}tc")
        id_columns = [
            index for index, cell in enumerate(header_cells) if is_id_header(cell_text(cell))
        ]
        if not id_columns:
            continue

        _, widths = grid_widths(table)
        targets = {}
        for index in id_columns:
            column_cells = [
                row.findall(f"{W}tc")[index]
                for row in rows
                if len(row.findall(f"{W}tc")) > index
            ]
            targets[index] = required_id_width(column_cells)
        widths = rebalance_widths(widths, id_columns, targets)
        set_table_widths(table, widths)

        for index in id_columns:
            id_columns_updated += 1
            for row in rows:
                cells = row.findall(f"{W}tc")
                if len(cells) <= index:
                    continue
                ensure_no_wrap(cells[index])
                rows_protected += 1

    if semantic_count == 0:
        raise ValueError("No semantic data tables were found")
    if id_columns_updated == 0:
        raise ValueError("No ID-like columns were found")
    return {
        "semantic_tables": semantic_count,
        "id_columns_updated": id_columns_updated,
        "id_cells_no_wrap": rows_protected,
        "table_font_pt": TABLE_FONT_HALF_POINTS / 2,
    }


def write_package(source: Path, destination: Path, replacements: dict[str, bytes]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f"{destination.stem}-", suffix=".docx", dir=str(destination.parent)
    )
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(source, "r") as zin, zipfile.ZipFile(temp_path, "w") as zout:
            for info in zin.infolist():
                data = replacements.get(info.filename, zin.read(info.filename))
                zout.writestr(info, data)
        os.replace(temp_path, destination)
    finally:
        temp_path.unlink(missing_ok=True)


def parse_xml_part(data: bytes) -> tuple[ET.Element, dict[str, str]]:
    namespaces: dict[str, str] = {}
    for _, declaration in ET.iterparse(io.BytesIO(data), events=("start-ns",)):
        prefix, uri = declaration
        namespaces.setdefault(prefix or "", uri)
    for prefix, uri in namespaces.items():
        if prefix != "xml":
            ET.register_namespace(prefix, uri)
    return ET.fromstring(data), namespaces


def serialize_xml_part(root: ET.Element, namespaces: dict[str, str]) -> bytes:
    serialized = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    declaration_end = serialized.find(b"?>")
    root_start = serialized.find(b"<", declaration_end + 2)
    root_end = serialized.find(b">", root_start)
    if root_start < 0 or root_end < 0:
        raise ValueError("Cannot locate serialized XML root element")

    root_tag = serialized[root_start:root_end]
    missing_declarations: list[bytes] = []
    for prefix, uri in namespaces.items():
        if prefix == "xml":
            continue
        attribute = "xmlns" if not prefix else f"xmlns:{prefix}"
        encoded_attribute = attribute.encode("ascii")
        if encoded_attribute + b"=" in root_tag:
            continue
        missing_declarations.append(
            b" " + encoded_attribute + b"=" + quoteattr(uri).encode("utf-8")
        )
    return (
        serialized[:root_end]
        + b"".join(missing_declarations)
        + serialized[root_end:]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_docx", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    with zipfile.ZipFile(args.input_docx, "r") as package:
        styles_root, styles_namespaces = parse_xml_part(
            package.read("word/styles.xml")
        )
        document_root, document_namespaces = parse_xml_part(
            package.read("word/document.xml")
        )

    header_style_id = set_style_size(
        styles_root, "Dhandy Table Header", TABLE_FONT_HALF_POINTS
    )
    body_style_id = set_style_size(
        styles_root, "Dhandy Table Body", TABLE_FONT_HALF_POINTS
    )
    summary = patch_document(document_root, header_style_id, body_style_id)

    replacements = {
        "word/styles.xml": serialize_xml_part(styles_root, styles_namespaces),
        "word/document.xml": serialize_xml_part(
            document_root, document_namespaces
        ),
    }
    write_package(args.input_docx, args.out, replacements)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
