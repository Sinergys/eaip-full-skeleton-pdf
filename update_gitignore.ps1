# PowerShell - Update .gitignore
Set-Location C:\eaip\eaip_full_skeleton

Write-Host "=== UPDATING .gitignore ===" -ForegroundColor Yellow

$newRules = @"

# ========================================
# AUDIT & ANALYSIS (Added 2025-12-12)
# ========================================

# Temporary analysis files
*_analysis_temp.md
*_scratch.md
wave*_draft*.json
audit_temp/

# Intermediate group analysis (keep final reports)
group_*_analysis.md
intermediate_*.json

# Scripts for one-time operations
cleanup_*.sh
analyze_*.sh
temp_*.py

# Personal notes (not project documentation)
NOTES_*.md
TODO_personal.md
scratch/
"@

Add-Content -Path ".gitignore" -Value $newRules

Write-Host "Rules added to .gitignore" -ForegroundColor Green

Write-Host "`n=== COMMITTING ===" -ForegroundColor Yellow
git add .gitignore
git commit -m "chore: Update .gitignore for audit workflow" -m "" -m "Added rules for:" -m "- Temporary analysis files" -m "- Intermediate group analysis" -m "- One-time operation scripts" -m "- Personal notes"

Write-Host "`n=== PUSHING ===" -ForegroundColor Yellow
git push

Write-Host "`n=== DONE ===" -ForegroundColor Green
