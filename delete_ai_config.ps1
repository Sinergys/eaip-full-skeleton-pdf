# PowerShell - Delete ai_config.py
Set-Location C:\eaip\eaip_full_skeleton

Write-Host "=== DELETING OBSOLETE FILE ===" -ForegroundColor Yellow
$file = "services/ingest/ai_config.py"

if (Test-Path $file) {
    Write-Host "Found: $file" -ForegroundColor Green
    
    git rm $file
    Write-Host "Removed from git" -ForegroundColor Green
    
    git commit -m "refactor: Remove obsolete ai_config.py" -m "" -m "Conflict resolved: ai_config.py vs ai_settings.py" -m "- ai_settings.py is newer (Dec 1) and larger (10KB vs 4KB)" -m "- ai_config.py not used in codebase" -m "- Keeping ai_settings.py as the canonical config"
    
    git push
    
    Write-Host "`n=== DONE ===" -ForegroundColor Green
    Write-Host "Deleted: ai_config.py" -ForegroundColor Green
} else {
    Write-Host "File not found: $file" -ForegroundColor Red
}
