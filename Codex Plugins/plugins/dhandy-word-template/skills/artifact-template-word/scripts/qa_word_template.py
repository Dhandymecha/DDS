#!/usr/bin/env python3
"""Structural QA for the Dhandy Word template and documents derived from it."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
W = f"{{{W_NS}}}"
R = f"{{{R_NS}}}"
TABLE_FONT_HALF_POINTS = 18  # 9 pt
MIN_ID_WIDTH_DXA = 1800
BODY_LIST_LINE_TWIPS = 274  # 1.14 lines in Word's auto-line unit
BODY_LIST_AFTER_TWIPS = 120  # 6 pt
BODY_LIST_STYLE_NAMES = (
    "Normal",
    "Dhandy Body L1",
    "Dhandy Body L2",
    "Dhandy Body L3",
    "Dhandy Bullet",
    "Dhandy Bullet 2",
    "Dhandy Bullet L1",
    "Dhandy Bullet L2",
    "Dhandy Bullet L3",
    "Dhandy Numbered",
    "Dhandy Numbered 2",
    "Dhandy Numbered L1",
    "Dhandy Numbered L2",
    "Dhandy Numbered L3",
)


def w_attr(name: str) -> str:
    return f"{W}{name}"


def value_is_true(value: str | None) -> bool:
    return value is None or value.lower() not in {"0", "false", "off", "no"}


def style_by_name(styles_root: ET.Element, display_name: str) -> ET.Element | None:
    for style in styles_root.findall(f"{W}style"):
        name = style.find(f"{W}name")
        if name is not None and name.get(w_attr("val")) == display_name:
            return style
    return None


def style_id(style: ET.Element | None) -> str | None:
    return None if style is None else style.get(w_attr("styleId"))


def style_size(style: ET.Element | None) -> int | None:
    if style is None:
        return None
    size = style.find(f"{W}rPr/{W}sz")
    return None if size is None else int(size.get(w_attr("val"), "0"))


def style_is_bold(style: ET.Element | None) -> bool:
    if style is None:
        return False
    bold = style.find(f"{W}rPr/{W}b")
    return bold is not None and value_is_true(bold.get(w_attr("val")))


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


def no_wrap_enabled(cell: ET.Element) -> bool:
    no_wrap = cell.find(f"{W}tcPr/{W}noWrap")
    return no_wrap is not None and value_is_true(no_wrap.get(w_attr("val")))


def table_grid_widths(table: ET.Element) -> list[int]:
    grid = table.find(f"{W}tblGrid")
    if grid is None:
        return []
    return [
        int(column.get(w_attr("w"), "0"))
        for column in grid.findall(f"{W}gridCol")
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--require-id-column", action="store_true")
    args = parser.parse_args()

    checks: list[dict] = []
    failures: list[str] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    try:
        with zipfile.ZipFile(args.docx, "r") as package:
            bad_entry = package.testzip()
            names = set(package.namelist())
            required_parts = {
                "word/document.xml",
                "word/styles.xml",
                "word/settings.xml",
                "word/fontTable.xml",
                "word/_rels/fontTable.xml.rels",
            }
            check("DOCX package", bad_entry is None, f"bad entry={bad_entry}")
            missing = sorted(required_parts - names)
            check("Required OOXML parts", not missing, f"missing={missing}")
            if missing:
                raise ValueError("Required OOXML parts are missing")

            document_root = ET.fromstring(package.read("word/document.xml"))
            styles_root = ET.fromstring(package.read("word/styles.xml"))
            settings_root = ET.fromstring(package.read("word/settings.xml"))
            font_rels_root = ET.fromstring(
                package.read("word/_rels/fontTable.xml.rels")
            )

            header_style = style_by_name(styles_root, "Dhandy Table Header")
            body_style = style_by_name(styles_root, "Dhandy Table Body")
            header_id = style_id(header_style)
            body_id = style_id(body_style)
            check("Table Header style", header_id is not None, f"styleId={header_id}")
            check("Table Body style", body_id is not None, f"styleId={body_id}")
            check(
                "Table Header 9 pt",
                style_size(header_style) == TABLE_FONT_HALF_POINTS,
                f"half-points={style_size(header_style)}",
            )
            check(
                "Table Body 9 pt",
                style_size(body_style) == TABLE_FONT_HALF_POINTS,
                f"half-points={style_size(body_style)}",
            )
            check(
                "Table Header bold",
                style_is_bold(header_style),
                "Dhandy Table Header must be bold",
            )

            spacing_errors = []
            for display_name in BODY_LIST_STYLE_NAMES:
                style = style_by_name(styles_root, display_name)
                spacing = (
                    None
                    if style is None
                    else style.find(f"{W}pPr/{W}spacing")
                )
                if spacing is None:
                    spacing_errors.append(
                        f"{display_name}: spacing definition missing"
                    )
                    continue
                line = int(spacing.get(w_attr("line"), "0"))
                rule = spacing.get(w_attr("lineRule"))
                before = int(spacing.get(w_attr("before"), "0"))
                after = int(spacing.get(w_attr("after"), "0"))
                if (
                    line != BODY_LIST_LINE_TWIPS
                    or rule != "auto"
                    or before != 0
                    or after != BODY_LIST_AFTER_TWIPS
                ):
                    spacing_errors.append(
                        f"{display_name}: line={line}, rule={rule}, "
                        f"before={before}, after={after}"
                    )
            check(
                "Body and list spacing",
                not spacing_errors,
                "; ".join(spacing_errors)
                or "body, bullet, and numbered styles use 1.14 lines / 6 pt after",
            )

            semantic_tables = []
            id_column_count = 0
            direct_size_errors = []
            geometry_errors = []
            id_errors = []

            if header_id and body_id:
                for table_index, table in enumerate(
                    document_root.iter(f"{W}tbl"), start=1
                ):
                    if not semantic_table(table, header_id, body_id):
                        continue
                    semantic_tables.append(table)

                    layout = table.find(f"{W}tblPr/{W}tblLayout")
                    if layout is None or layout.get(w_attr("type")) != "fixed":
                        geometry_errors.append(
                            f"table {table_index}: tblLayout is not fixed"
                        )

                    widths = table_grid_widths(table)
                    tbl_w = table.find(f"{W}tblPr/{W}tblW")
                    declared = (
                        int(tbl_w.get(w_attr("w"), "0")) if tbl_w is not None else 0
                    )
                    if not widths or any(width <= 0 for width in widths):
                        geometry_errors.append(
                            f"table {table_index}: invalid tblGrid"
                        )
                    elif declared != sum(widths):
                        geometry_errors.append(
                            f"table {table_index}: tblW={declared}, grid={sum(widths)}"
                        )

                    for run in table.iter(f"{W}r"):
                        size = run.find(f"{W}rPr/{W}sz")
                        if size is not None and int(size.get(w_attr("val"), "0")) != TABLE_FONT_HALF_POINTS:
                            direct_size_errors.append(
                                f"table {table_index}: direct size "
                                f"{size.get(w_attr('val'))} half-points"
                            )

                    rows = table.findall(f"{W}tr")
                    if not rows:
                        continue
                    header_cells = rows[0].findall(f"{W}tc")
                    for column_index, header_cell in enumerate(header_cells):
                        if not is_id_header(cell_text(header_cell)):
                            continue
                        id_column_count += 1
                        column_cells = [
                            row.findall(f"{W}tc")[column_index]
                            for row in rows
                            if len(row.findall(f"{W}tc")) > column_index
                        ]
                        required_width = required_id_width(column_cells)
                        actual_width = (
                            widths[column_index]
                            if len(widths) > column_index
                            else 0
                        )
                        if actual_width < required_width:
                            id_errors.append(
                                f"table {table_index} column {column_index + 1}: "
                                f"width {actual_width} < required {required_width} DXA"
                            )
                        for row_index, cell in enumerate(column_cells, start=1):
                            if not no_wrap_enabled(cell):
                                id_errors.append(
                                    f"table {table_index} column {column_index + 1} "
                                    f"row {row_index}: noWrap missing"
                                )
                            if cell.find(f".//{W}br") is not None:
                                id_errors.append(
                                    f"table {table_index} column {column_index + 1} "
                                    f"row {row_index}: explicit line break"
                                )

            check(
                "Semantic data tables",
                len(semantic_tables) > 0,
                f"count={len(semantic_tables)}",
            )
            check(
                "Semantic table geometry",
                not geometry_errors,
                "; ".join(geometry_errors) or "fixed geometry is consistent",
            )
            check(
                "Semantic table direct font overrides",
                not direct_size_errors,
                "; ".join(direct_size_errors) or "all direct sizes are 9 pt",
            )
            check(
                "ID columns",
                (id_column_count > 0) if args.require_id_column else True,
                f"count={id_column_count}",
            )
            check(
                "ID column width and no-wrap",
                not id_errors,
                "; ".join(id_errors) or "ID cells are one-line protected",
            )

            embed = settings_root.find(f"{W}embedTrueTypeFonts")
            subset = settings_root.find(f"{W}saveSubsetFonts")
            embed_ok = embed is not None and value_is_true(embed.get(w_attr("val")))
            subset_ok = subset is None or not value_is_true(subset.get(w_attr("val")))
            check(
                "Embedded-font setting",
                embed_ok,
                "embedTrueTypeFonts must be true",
            )
            check(
                "Full-font setting",
                subset_ok,
                "saveSubsetFonts must be false",
            )

            font_parts = sorted(
                name for name in names if name.startswith("word/fonts/")
            )
            font_relationships = [
                rel
                for rel in font_rels_root
                if (rel.get("Type") or "").endswith("/font")
            ]
            check(
                "Embedded font parts",
                len(font_parts) >= 2,
                f"font parts={len(font_parts)}",
            )
            check(
                "Embedded font relationships",
                len(font_relationships) >= 2,
                f"font relationships={len(font_relationships)}",
            )

    except Exception as exc:
        failures.append(f"Unhandled QA error: {exc}")
        checks.append(
            {"name": "Unhandled QA error", "passed": False, "detail": str(exc)}
        )

    result = {
        "passed": not failures,
        "document": str(args.docx.resolve()),
        "table_font_pt": TABLE_FONT_HALF_POINTS / 2,
        "minimum_id_width_dxa": MIN_ID_WIDTH_DXA,
        "body_list_line_multiple": 1.14,
        "body_list_after_pt": BODY_LIST_AFTER_TWIPS / 20,
        "checks": checks,
        "failures": failures,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
