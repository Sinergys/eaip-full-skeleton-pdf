# PowerShell script for git commit - FIXED
Set-Location C:\eaip\eaip_full_skeleton

Write-Host "=== GIT STATUS ===" -ForegroundColor Yellow
git status --short

Write-Host "`n=== COPYING FILES TO GIT REPO ===" -ForegroundColor Yellow
$files = @(
    "ANALYZED_FILES_REPORT.json",
    "CRITICAL_FILES_LIST.md",
    "METHODOLOGY_GUIDE_COMPACT.md",
    "OPERATION_TEMPLATES.md",
    "CONTINUATION_PLAN.md",
    "WAVE1_ANALYSIS_22_FILES.md",
    "WAVE1_REMAINING_18_FILES.json",
    "WAVE1_COMPLETION_STATUS.md"
)

foreach ($file in $files) {
    $source = "C:\eaip\$file"
    if (Test-Path $source) {
        Copy-Item $source -Destination . -Force
        Write-Host "Copied: $file" -ForegroundColor Green
    } else {
        Write-Host "Not found: $file" -ForegroundColor Red
    }
}

Write-Host "`n=== ADDING FILES ===" -ForegroundColor Yellow
foreach ($file in $files) {
    if (Test-Path $file) {
        git add $file
        Write-Host "Added: $file" -ForegroundColor Green
    }
}

Write-Host "`n=== COMMITTING ===" -ForegroundColor Yellow
git commit -m "docs: Complete Wave 1 audit (80/80 files)" -m "" -m "- Claude: 48+18=66 files analyzed" -m "- Koda: 14 files analyzed" -m "- Created handover documentation" -m "- Identified 20 critical files" -m "- Detected 5 conflicts" -m "- Wave 1 complete: 80/80 (100%)" -m "" -m "Deliverables:" -m "- ANALYZED_FILES_REPORT.json (48 files)" -m "- WAVE1_REMAINING_18_FILES.json (18 files)" -m "- CRITICAL_FILES_LIST.md (16 protected files)" -m "- METHODOLOGY_GUIDE_COMPACT.md" -m "- OPERATION_TEMPLATES.md" -m "- CONTINUATION_PLAN.md" -m "- WAVE1_COMPLETION_STATUS.md"

Write-Host "`n=== PUSHING ===" -ForegroundColor Yellow
git push

Write-Host "`n=== DONE ===" -ForegroundColor Green
