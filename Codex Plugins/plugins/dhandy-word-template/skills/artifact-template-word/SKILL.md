---
name: artifact-template-word
description: "Create a document using the 단디메카 Word 표준 포맷 template and its retained reference file. Use when the user selects this template, names 단디메카 Word 표준 포맷, or explicitly invokes $artifact-template-word. 단디메카 기술보고서·설계사양서·URS를 동일한 표지, 문단 계층, 표 및 머리말·바닥글 규칙으로 작성합니다."
---

# 단디메카 Word 표준 포맷

Create a new document from this template. Keep the reference file unchanged.

## Workflow

1. Read `artifact-template.json` and resolve its paths relative to this skill directory.
2. Read `assets/style-guide.md` completely and apply its cover balance, paragraph hierarchy, tables, running elements, and QA gates unless the user explicitly requests a deviation.
3. Load [@documents](plugin://documents@openai-primary-runtime) and invoke its reference/template workflow with the retained file.
4. Treat the user's prompt and available sources as the content input. Do not invent facts merely to fill a template slot.
5. Clone or import the reference instead of replacing its visual system with generic defaults.
6. Apply the prose/list and table contracts before delivery. `Normal`, `Dhandy Body L1/L2/L3`, bullet styles, and numbered styles all use 1.14 line spacing with 0 pt before and 6 pt after. Semantic data-table header/body text is fixed at 9 pt; ID, code, document-number, and revision-number columns must be wide enough for their longest value and must not wrap. Never insert a manual line break into an ID. If space is insufficient, rebalance column widths, split the table, or use a landscape section.
7. Run `python scripts/qa_word_template.py "<output.docx>"` after the final save. Add `--require-id-column` when the document is expected to contain an ID/code table. Do not deliver a file while this structural QA reports a failure.
8. Render every page and visually verify clipping, overlap, abnormal wrapping, and page flow before returning the final artifact.
9. Preserve the embedded Pretendard Regular/Bold font parts. For an externally editable DOCX, verify `embedTrueTypeFonts=true`, `saveSubsetFonts=false`, the `fontTable.xml` relationships, and the `word/fonts` parts after the final save.

## Fidelity

Preserve page setup, sections, styles, lists, tables, headers, footers, and recurring page elements.

Use hierarchical indents for headings and prose, but place ordinary tables, figures, and callouts on the 8 mm object grid. Use the full content width only for deliberately wide objects.

The 9 pt table rule applies to semantic data tables that use `Dhandy Table Header` and `Dhandy Table Body`. Cover, header/footer, metadata, and callout layout tables retain their dedicated styles.

User instructions control requested content and explicit deviations. The retained reference controls layout and formatting where the user has not requested a change.
