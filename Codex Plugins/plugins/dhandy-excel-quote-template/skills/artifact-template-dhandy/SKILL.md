---
name: artifact-template-dhandy
description: "Create a spreadsheet using the 단디메카 Excel 견적서 표준 포맷 and its retained reference file. Use when the user selects this template, names 단디메카 Excel 견적서 표준 포맷, or explicitly invokes $artifact-template-dhandy."
---

# 단디메카 Excel 견적서 표준 포맷

Create a quotation workbook from the retained company template. Preserve its formulas, print structure, and visual system while replacing the requested quotation data.

## Latest locked standard

The retained reference workbook is the source of truth for the current reusable format. Apply these rules unless the user explicitly requests a project-specific exception:

- Cover sheet: keep row `4` as a white `8 pt` spacer above the `OFFICIAL QUOTE` block and row `8` at `45 pt` to retain breathing room above the main `QUOTATION` title. Keep rows `5:7` at `12 pt` row height. Typography uses integer levels only: `28`, `18`, `10`, and `9 pt`.
- Cover objects: position the logo at `Left 30.75 pt / Top 35 pt` and the stamp at `Left 680.5 pt / Top 36 pt` after all row sizing is complete. Do not move either object by changing row heights.
- Cover summary: use `B:L` with `Code B:C`, `Item D:F`, `Basis G:I`, and `Amount J:L`. Apply one indent level to left-aligned item/basis cells and right-aligned amount cells in body rows.
  - Keep all four summary-header labels centered. In body rows, keep code centered, item/basis left aligned, and amount right aligned.
  - Keep `B:C` unmerged in summary rows and use `Center Across Selection` for the code label. Numbered codes must be numeric values with `0.00` number format; reserve text values for `ADJ.` and `NEG.` only.
  - Apply the pale-orange adjustment fill to every physical cell in `B:L` for rows `32:33`. In particular, do not leave column `C` white merely because `B:C` uses `Center Across Selection`.
  - Do not use cell borders for summary body separators. Clear the top/bottom borders from `B:L` rows `25:33` and use one continuous `0.5 pt` light-gray vector line shape per row, named `COVER_RULE_25` through `COVER_RULE_33`, spanning the full `B:L` width.
  - Keep the header top rule single: row `23` supplies the orange rule and row `24` must not duplicate it.
  - Cover Korean amount: place it below the final supply price, use a white fill, and add a thin gray top rule matching the surrounding design.
  - Keep row `34` as a `12 pt` white separator above the final quotation amount block. Compensate its height in the flexible spacer so the bottom information block and footer remain anchored.
  - Keep row `34` visually blank and resolve its shared boundary with row `35` as one thin orange border. Excel may report the same shared edge as row `34` bottom and row `35` top; do not add a separate line shape or a second medium/thick rule.
  - Anchor payment terms, delivery, installation location, quotation validity, and the disclaimer as a bottom-stacked information block immediately above the company footer. Keep the large flexible blank spacer between VAT and this block, not below the disclaimer.
- Detail sheet: customer-facing print area is `A:K`, with equal blank side-margin columns `A` and `K`. The customer table is `B:J`. Internal analysis begins at `L` and is excluded from customer print output.
- Detail styling: repeat the top orange-to-dark gradient and the light-gray footer frame with orange top rule. Keep the footer inside the customer content area.
- Customer PDF: include sheets `1` and `2` only. Never include the internal labor-rate sheet.

When updating this skill, change only the reusable instructions and `assets/reference.xlsx`; do not modify previously delivered quotation workbooks or PDFs.

## Workflow

1. Read `artifact-template.json` and resolve paths relative to this skill directory.
2. Load [@spreadsheets](plugin://spreadsheets@openai-primary-runtime) and follow its reference/template workflow.
3. Import `assets/reference.xlsx`; do not rebuild the workbook with generic styling.
4. Replace the requested quotation data and formulas while preserving the three-sheet structure.
5. Recalculate in native Excel, verify formulas and key totals, and visually inspect every customer-facing PDF page.
6. Deliver both the editable `.xlsx` workbook and a customer print `.pdf` containing only sheets 1 and 2.

## Workbook Structure

- `1. 견적서`: A4 portrait cover and quotation summary.
- `2. 상세견적`: A4 portrait customer cost breakdown. The customer print area is `A:K`, the customer table is `B:J`, and equal blank safety columns are kept at `A` and `K`. The gray internal analysis area starts at `L` and stays outside the print area.
- `3. 인건비 기준`: A4 portrait internal labor-rate standard with junior `350,000`, intermediate `400,000`, and senior `450,000` KRW per M/D. Keep it in the workbook but exclude it from the customer PDF.

## Cover Rules

- Keep column `A` blank through the quotation-summary block to provide a visible left inset; build the summary table from `B:L`.
- Keep column `M` blank at the same width as column `A` so the main cover content has equal left and right white margins. The full-bleed gradient and footer may extend across `A:M`, but customer content remains within `B:L`.
- Keep the code and item areas separate from the amount area, and preserve the aligned final-price block.
- Center `NEG.` consistently with the other summary codes.
- Keep the company information and quotation-contact information visually separated.
- Preserve the top horizontal orange-to-dark gradient, aligned logo, and A4 bottom company bar.
- Keep a modest white gap between the top gradient and the logo/OFFICIAL QUOTE block; do not crowd those elements against the gradient.
- Keep row `4` as a white `8` pt spacer above the OFFICIAL QUOTE block, row `8` at `45` pt above the main QUOTATION title, and rows `5:7` at the same `12` pt height.
- Position the logo and stamp as shapes with explicit coordinates after row sizing; never create their spacing by changing an unrelated cell height. In the retained reference, the logo is at `Left 30.75 / Top 35` pt and the stamp is at `Left 680.5 / Top 36` pt.
- Use `별도 협의` as the default payment condition unless the user supplies project-specific terms.
- Set the cover cost-summary header and rows to `10` pt, with the black header row at `23` pt height and summary rows at `20` pt height.
- Build the cover summary as `코드 | 항목 | 구성 기준 | 금액` using `B:C | D:F | G:I | J:L`. Use short customer-readable basis text rather than leaving the center of the table empty.
- Apply one Excel indent level to every left-aligned item/basis cell and every right-aligned amount cell in the cover summary.
- Add a Korean amount row directly below the final supply price and before VAT, using the form `일금 [한글 금액]원정`. Always update this text to match the final supply price.
- Keep the Korean amount row white and separate it from the final-price block with a thin gray top rule.
- Keep `ADJ.` and `NEG.` rows as one continuous pale-orange band across `B:L`, including all otherwise empty cells used for center-across-selection or merged display.
- Keep the final-price top accent as one thin orange shared-edge rule. Do not overlay a separate line shape or retain a medium/thick boundary.

## Detail Rules

- Put every hardware component, labor task, and other execution-cost item in its own row.
- Use parent rows only for category or module subtotals.
- Show hierarchical codes with two decimals, such as `10.00`, `11.00`, `11.01`, and `70.01`.
- Give every child item its own item-specific specification or calculation basis. Do not reuse one generic sentence across the list.
- For labor child rows, use `업무단계 - 역할 (등급)` in the item column, `n명 x n일` in the calculation-basis column, `M/D` as the unit, and the matching quantity and rate.
- Labor rates must reference the cells on `3. 인건비 기준`; do not hardcode them.
- When manufacturer, model, or specification is not fixed, include a note that an equivalent-or-better product may be applied after consultation.
- Keep a visible spacer between the customer quotation table and the gray internal analysis panel.
- Avoid orphaned subtotal rows and isolated final/VAT rows when setting page breaks.
- Extend the same orange-to-dark gradient across the full detail print width at the top of every customer-facing detail page.
- Add the same light-gray company footer frame and orange top rule at the bottom of every customer-facing detail page. Keep footer text within the inner `B:J` content area.
- Keep the detail-sheet disclaimer immediately below VAT/totals and use a flexible spacer before the footer so the footer reaches the A4 bottom edge.

## Visual Rules

- Use Pretendard throughout.
- Use exactly four integer typography levels: `28`, `18`, `10`, and `9` pt. Never use a fractional font size.
- Use `28` pt for the cover title, `18` pt for the final amount, `10` pt for section/table emphasis and Korean amount wording, and `9` pt for body, metadata, and notes.
- Major rows such as `10.00`, `20.00`, and `70.00` use a pale-orange full-row fill.
- Reserve strong orange fill for the final supply-price row.
- Black table headers use bold white type at the same `9` pt level as the body.
- Use black as a structural accent while keeping body text readable in dark gray.

## Print And Delivery Rules

- Set all three worksheets to A4 portrait.
- Set top, bottom, left, right, header, and footer print margins to `0` for edge-filling PDF output. Keep readable spacing through the worksheet layout itself rather than printer margins.
- Keep the cover print range at `A1:M50` and at A4 proportions so the company footer reaches the physical bottom edge. Row `47` is the flexible spacer; calculate its height from the current print-range width instead of relying on a fixed value.
- Fit the cover to one page wide by one page tall.
- Fit the detail sheet to one page wide. For a single-page detail, fit it to one A4 portrait page; for longer quotations, repeat the gradient/footer treatment on every exported page and keep VAT, the disclaimer, and the final footer together on the last page.
- Fit the labor-rate sheet to one page wide by one page tall for internal use.
- Export the customer PDF from sheets `1. 견적서` and `2. 상세견적` only, in that order. Never include `3. 인건비 기준` in the external PDF.
- Native Excel PDF export can retain printer-driver hard margins even when every margin is zero. Post-process the exported PDF to remove those hard margins while preserving the A4 media box; do not describe a file as borderless until the rendered cover gradient touches the top/left/right edges and the company footer reaches the bottom edge.
- Measure each native PDF page's non-white pixel bounds after every layout change and map that bounding box back to PDF points.
- Use the raster render only to measure bounds and visually review the result. Never rebuild the delivered PDF from PNG/JPEG pages.
- Apply the measured translation and scale directly to the native PDF content stream so fonts, text selection, search, lines, and vector shapes remain intact while the A4 media box is preserved.
- When the full-bleed transformation scales page content, counter-scale explicit stroke widths and thin horizontal/vertical rule rectangles before applying the page transform. Do not allow page enlargement to thicken Excel rules.
- Compare the native Excel PDF and final full-bleed PDF on every customer page. The counts of explicit line strokes and thin rule rectangles must match, and corresponding physical widths must remain within `0.02 pt`.
- Verify the delivered PDF still exposes extractable text on every page and is not an image-only PDF.
- Whenever a completed quotation is delivered, provide the `.xlsx` file and the matching print-ready `.pdf` together.

## Calculation Rules

- Use formulas for subtotals, management cost, profit, final supply price, and VAT.
- Child rows show unit, quantity, unit price, and amount; parent amounts sum their child rows.
- `견적 단위 조정` is only a small negative won-level adjustment used to align the final amount to a `000` ending.
- Put substantive commercial reductions in a separate negative `협의 할인` row.
- Recalculate in Excel and verify that no formula error exists before delivery.

## Fidelity

Preserve formulas, number formats, merged cells, dimensions, images, print areas, page orientation, and the internal-analysis exclusion. User instructions control explicit deviations; otherwise the retained reference controls layout and formatting.
