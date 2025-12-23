# PowerShell script for git commit
Set-Location C:\eaip

Write-Host "=== GIT STATUS ===" -ForegroundColor Yellow
git status --short

Write-Host "`n=== ADDING FILES ===" -ForegroundColor Yellow
$files = @(
    "ANALYZED_FILES_REPORT.json",
    "CRITICAL_FILES_LIST.md",
    "METHODOLOGY_GUIDE_COMPACT.md",
    "OPERATION_TEMPLATES.md",
    "CONTINUATION_PLAN.md",
    "WAVE1_ANALYSIS_22_FILES.md",
    "WAVE1_REMAINING_18_FILES.json",
    "WAVE1_COMPLETION_STATUS.md",
    "WAVE1_COMBINED_SUMMARY.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        git add $file
        Write-Host "Added: $file" -ForegroundColor Green
    } else {
        Write-Host "Not found: $file" -ForegroundColor Red
    }
}

Write-Host "`n=== COMMITTING ===" -ForegroundColor Yellow
git commit -m "docs: Complete Wave 1 audit (80/80 files)`n`n- Claude: 48+18=66 files analyzed`n- Koda: 14 files analyzed`n- Created handover documentation`n- Identified 20 critical files`n- Detected 5 conflicts`n- Wave 1 complete: 80/80 (100%)`n`nDeliverables:`n- ANALYZED_FILES_REPORT.json (48 files)`n- WAVE1_REMAINING_18_FILES.json (18 files)`n- CRITICAL_FILES_LIST.md (16 protected files)`n- METHODOLOGY_GUIDE_COMPACT.md`n- OPERATION_TEMPLATES.md`n- CONTINUATION_PLAN.md`n- WAVE1_COMPLETION_STATUS.md"

Write-Host "`n=== PUSHING ===" -ForegroundColor Yellow
git push

Write-Host "`n=== DONE ===" -ForegroundColor Green
