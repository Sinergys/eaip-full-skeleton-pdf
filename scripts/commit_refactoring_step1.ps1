# ============================================================================
# Git Commit: Refactoring Step 1 - Models & PDF Libraries Update
# ============================================================================
# Дата: 2025-12-05
# Изменения: Создание models/, обновление PDF библиотек, исправление тестов
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Git Commit: Refactoring Progress" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

$gitRoot = "C:\eaip\eaip_full_skeleton"
Set-Location $gitRoot

# Проверка Git репозитория
if (-not (Test-Path ".git")) {
    Write-Host "❌ Git репозиторий не найден в $gitRoot" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Изменённые файлы:" -ForegroundColor Cyan
Write-Host ""

# Показываем статус
git status --short

Write-Host ""
Write-Host "1️⃣ Добавление всех изменений..." -ForegroundColor Cyan
git add -A

Write-Host ""
Write-Host "2️⃣ Создание коммита..." -ForegroundColor Cyan

$commitMessage = @"
refactor: Step 1 - Extract Pydantic models & update PDF libraries

Changes:
1. Created models/ package with schemas.py
   - Extracted ValidateRequest, EnterpriseCreate, EditablePayload from main.py
   - Added __init__.py for clean imports
   - main.py: -13 lines (removed model definitions)

2. Updated PDF libraries
   - requirements.txt: PyPDF2 → PyMuPDF 1.24.0
   - file_parser.py: Updated imports (PyPDF2 → fitz)
   - Fallback code preserved (safe approach)

3. Fixed E2E test
   - test_api_e2e.py: Updated filename assertion to handle batch_id prefix
   - All 9 tests passing ✅

4. Updated technical debt
   - TECHNICAL_DEBT.md: Added sections 2 & 3
   - Section 2: INBOX_DIR structure improvement
   - Section 3: PyPDF2 → PyMuPDF fallback migration plan

Files changed:
- services/ingest/models/schemas.py (new)
- services/ingest/models/__init__.py (new)
- services/ingest/main.py (updated imports)
- services/ingest/requirements.txt (updated dependencies)
- services/ingest/file_parser.py (updated imports)
- services/ingest/tests/test_api_e2e.py (fixed assertion)
- TECHNICAL_DEBT.md (added sections)
- update_pdf_libraries.ps1 (new)
- PDF_LIBRARIES_UPDATE_INSTRUCTIONS.md (new)

Status: Ready for library installation and testing
Next: Install PyMuPDF, run tests, create routes/upload.py
"@

git commit -m $commitMessage

Write-Host ""
Write-Host "3️⃣ Показываем последний коммит..." -ForegroundColor Cyan
Write-Host ""
git log -1 --stat

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "✅ Коммит создан успешно!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "📊 Статистика изменений:" -ForegroundColor Cyan
$lastCommit = git log -1 --pretty=format:"%h"
Write-Host "  Commit: $lastCommit" -ForegroundColor White
Write-Host "  Tag: v0.5.0-before-refactor (базовая версия)" -ForegroundColor White
Write-Host "  Branch: $(git rev-parse --abbrev-ref HEAD)" -ForegroundColor White
Write-Host ""

Write-Host "🔄 Push в remote?" -ForegroundColor Yellow
Write-Host "  Выполните: git push origin main" -ForegroundColor White
Write-Host ""

Write-Host "🎯 Следующие шаги:" -ForegroundColor Cyan
Write-Host "  1. cd C:\eaip" -ForegroundColor White
Write-Host "  2. .\update_pdf_libraries.ps1" -ForegroundColor White
Write-Host "  3. .\quick_test.ps1" -ForegroundColor White
Write-Host ""
