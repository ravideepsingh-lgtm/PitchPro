$ErrorActionPreference = "Stop"

$workbookPath = "G:\.shortcut-targets-by-id\1iJjMP2iLsOSP_ZuLA_P96PJqppjOnxoI\BJP (Beyond Just Product) - 10X Productivity\Data Sets\Paid Clients 20260515.xlsb"
$sheetName = "Client Base"
$csvPath = "C:\tmp\paid_clients_client_base.csv"

if (!(Test-Path -LiteralPath $workbookPath)) {
  throw "Workbook not found: $workbookPath"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $csvPath) | Out-Null

$excel = $null
$workbook = $null
$csvWorkbook = $null

try {
  $excel = New-Object -ComObject Excel.Application
  $excel.Visible = $false
  $excel.DisplayAlerts = $false

  $workbook = $excel.Workbooks.Open($workbookPath)
  $worksheet = $workbook.Worksheets.Item($sheetName)
  $worksheet.Copy()

  $csvWorkbook = $excel.ActiveWorkbook
  $csvWorkbook.SaveAs($csvPath, 62)
}
finally {
  if ($csvWorkbook -ne $null) {
    $csvWorkbook.Close($false)
  }

  if ($workbook -ne $null) {
    $workbook.Close($false)
  }

  if ($excel -ne $null) {
    $excel.Quit()
  }
}

python scripts/generate-client-segment-data.py --csv $csvPath --out src/data/clientSegmentData.js
