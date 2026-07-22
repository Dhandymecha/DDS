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
6. Render and verify the finished document, then return the final artifact.
7. Preserve the embedded Pretendard Regular/Bold font parts. For an externally editable DOCX, verify `embedTrueTypeFonts=true`, `saveSubsetFonts=false`, the `fontTable.xml` relationships, and the `word/fonts` parts after the final save.

## Fidelity

Preserve page setup, sections, styles, lists, tables, headers, footers, and recurring page elements.

Use hierarchical indents for headings and prose, but place ordinary tables, figures, and callouts on the 8 mm object grid. Use the full content width only for deliberately wide objects.

User instructions control requested content and explicit deviations. The retained reference controls layout and formatting where the user has not requested a change.
