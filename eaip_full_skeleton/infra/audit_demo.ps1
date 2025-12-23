Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# === Paths & URLs ===
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$dataDir = Join-Path $root "data"
$csvPath = Join-Path $dataDir "demo.csv"
$passportPdf = Join-Path $root "passport_demo1_full.pdf"
$forecastCsv = Join-Path $root "forecast_demo.csv"

$uIngest     = "http://127.0.0.1:8001/ingest/files"
$uValidate   = "http://127.0.0.1:8002/validate/run"
$uForecast   = "http://127.0.0.1:8003/analytics/forecast"
$uRecommend  = "http://127.0.0.1:8004/recommend/generate"
$uPassport   = "http://127.0.0.1:8005/reports/passport?format=pdf"

# === 0) Ensure demo data ===
New-Item -ItemType Directory -Force $dataDir | Out-Null
if (-not (Test-Path $csvPath)) {
@"
timestamp,value
2025-10-28T00:00:00,100
2025-10-28T01:00:00,105
2025-10-28T02:00:00,98
"@ | Set-Content $csvPath
}

# === 1) Ingest ===
$ing = Invoke-RestMethod $uIngest -Method Post -Form @{ file = Get-Item $csvPath }
$batchId = $ing.batchId
"INGEST batchId: $batchId"

# === 2) Validate ===
$val = Invoke-RestMethod $uValidate -Method Post -ContentType 'application/json' -Body (@{batchId=$batchId} | ConvertTo-Json)
"VALIDATE passed: $($val.passed)"

# === 3) Analytics (фикс полей) ===
$series = 0..47 | % {
  @{ ts = (Get-Date).AddHours(-$_).ToString("s") + "Z"; value = (Get-Random -Min 95 -Max 110) }
}
$bodyForecast = @{ meterId='demo'; horizon=7; series=$series } | ConvertTo-Json -Depth 6
$fc = Invoke-RestMethod $uForecast -Method Post -ContentType 'application/json' -Body $bodyForecast

# Сохранить прогноз в CSV
$tbl = for ($i=0; $i -lt $fc.forecast.Count; $i++) {
  [pscustomobject]@{
    date  = (Get-Date).Date.AddDays($i).ToString('yyyy-MM-dd')
    value = [double]$fc.forecast[$i]
  }
}
$tbl | Export-Csv -NoTypeInformation $forecastCsv
"ANALYTICS saved: $(Split-Path $forecastCsv -Leaf)"
# === 4) Recommend ===
$rc = Invoke-RestMethod $uRecommend -Method Post -ContentType 'application/json' -Body (@{auditId='demo-1'} | ConvertTo-Json)
"RECOMMEND measures: $($rc.measures.Count)"

# === 5) Reports → Passport PDF (use Accept: application/pdf) ===
Write-Host "Waiting for reports service..."
while (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 8005 -InformationLevel Quiet)) {
    Start-Sleep -Seconds 1
}
Write-Host "Reports service is ready."

$summary = @{ efficiency = 92; savings_usd = 2400 }
$passportBody = @{ auditId='demo-1'; summary=$summary } | ConvertTo-Json
Invoke-WebRequest $uPassport -Method Post -ContentType 'application/json' -Headers @{Accept='application/pdf'} -Body $passportBody -OutFile $passportPdf
"REPORTS pdf: $(Split-Path $passportPdf -Leaf)"

"`nDONE ✅"