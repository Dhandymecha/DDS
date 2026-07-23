param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Artifact,
    [Parameter(Mandatory = $true)][string]$Output,
    [Parameter(Mandatory = $true)][string]$NativePdf
)

$ErrorActionPreference = 'Stop'
Copy-Item -LiteralPath $Artifact -Destination $Output -Force

function Copy-PageSetup {
    param($From, $To)

    $properties = @(
        'PrintArea', 'PrintTitleRows', 'PrintTitleColumns',
        'Orientation', 'PaperSize', 'Order',
        'LeftMargin', 'RightMargin', 'TopMargin', 'BottomMargin',
        'HeaderMargin', 'FooterMargin',
        'CenterHorizontally', 'CenterVertically',
        'PrintHeadings', 'PrintGridlines', 'BlackAndWhite', 'Draft',
        'FirstPageNumber'
    )
    foreach ($name in $properties) {
        try { $To.PageSetup.$name = $From.PageSetup.$name } catch { }
    }

    $To.PageSetup.Zoom = $false
    $To.PageSetup.FitToPagesWide = $From.PageSetup.FitToPagesWide
    $To.PageSetup.FitToPagesTall = $From.PageSetup.FitToPagesTall
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $sourceBook = $excel.Workbooks.Open($Source, 0, $true)
    $outputBook = $excel.Workbooks.Open($Output, 0, $false)

    for ($index = 1; $index -le $sourceBook.Worksheets.Count; $index++) {
        Copy-PageSetup $sourceBook.Worksheets.Item($index) $outputBook.Worksheets.Item($index)
    }

    $cover = $outputBook.Worksheets.Item(1)

    # B:C is unmerged and centered across selection. Fill every physical cell.
    $cover.Range('B32:L33').Interior.Color = 15791615

    # Remove the duplicate boundary border and retain one thin final rule.
    $cover.Range('B34:L34').Borders.LineStyle = -4142
    $finalRule = $cover.Range('B35:L36').Borders.Item(8)
    $finalRule.LineStyle = 1
    $finalRule.Weight = 2
    $finalRule.Color = 1331188

    # Horizontal shape rules can become segmented or visually heavier after PDF
    # export. Use one native cell-border rule for every body row instead.
    foreach ($row in 25..33) {
        try { $cover.Shapes.Item("COVER_RULE_$row").Delete() } catch { }
        $rowRange = $cover.Range("B${row}:L${row}")
        $rowRange.Borders.Item(8).LineStyle = -4142
        $rowRange.Borders.Item(9).LineStyle = -4142
    }
    foreach ($row in 25..33) {
        $bottomRule = $cover.Range("B${row}:L${row}").Borders.Item(9)
        $bottomRule.LineStyle = 1
        $bottomRule.Weight = 2
        $bottomRule.Color = 14277081
    }

    # Keep the code column visually stable without merging cells. This applies
    # the same alignment to numeric rows and ADJ./NEG. alike.
    $cover.Range('B25:C33').HorizontalAlignment = 7
    $cover.Range('B25:C33').VerticalAlignment = -4108
    $cover.Range('B24:C24').HorizontalAlignment = 7
    $cover.Range('B24:C24').VerticalAlignment = -4108
    $cover.Range('B24:C24').Font.Underline = -4142
    $cover.Range('B24:L24').Borders.Item(9).LineStyle = -4142

    $detail = $outputBook.Worksheets.Item(2)

    # Keep the table's final boundary within the same standard rule set. Excel
    # stores adjacent top/bottom borders as one shared edge, so the remaining
    # rows retain their native borders and PDF output normalizes the widths.
    $detail.Range('B41:J41').Borders.Item(9).LineStyle = 1
    $detail.Range('B41:J41').Borders.Item(9).Weight = 2
    $detail.Range('B41:J41').Borders.Item(9).Color = 1526512

    $excel.CalculateFullRebuild()
    $outputBook.Save()

    $cover.Select()
    $outputBook.Worksheets.Item(2).Select($false)
    $excel.ActiveSheet.ExportAsFixedFormat(0, $NativePdf, 0, $true, $false)

    $outputBook.Close($true)
    $sourceBook.Close($false)
}
finally {
    $excel.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
