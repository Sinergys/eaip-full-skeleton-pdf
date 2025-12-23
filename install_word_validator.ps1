# 🚀 Установка Word Validator в проект EAIP
# Добавляет новый endpoint /api/validate-word-document

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🚀 Установка Word Validator" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$projectMain = "C:\eaip\eaip_full_skeleton\services\ingest\main.py"

# Проверка файла
if (-not (Test-Path $projectMain)) {
    Write-Host "❌ Файл не найден: $projectMain" -ForegroundColor Red
    exit 1
}

Write-Host "📄 Файл найден: main.py" -ForegroundColor Green
Write-Host ""

# 1. Бэкап
$backupPath = "$projectMain.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "💾 Создаю бэкап..." -ForegroundColor Yellow
Copy-Item $projectMain $backupPath -Force
Write-Host "✅ Бэкап: $(Split-Path $backupPath -Leaf)" -ForegroundColor Green
Write-Host ""

# 2. Добавление endpoint
Write-Host "➕ Добавляю endpoint /api/validate-word-document..." -ForegroundColor Yellow

$newEndpoint = @'


@app.post("/api/validate-word-document")
async def validate_word_document(
    file: UploadFile = File(...),
    check_structure: bool = True,
    check_calculations: bool = True,
    check_compliance: bool = True
):
    """Проверить Word документ энергоаудита через AI"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Только .docx файлы")
    
    try:
        temp_path = DATA_DIR / f"temp_{uuid4().hex}.docx"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        from docx import Document
        doc = Document(temp_path)
        text_content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        
        tables_data = []
        for table in doc.tables:
            table_text = [" | ".join([cell.text.strip() for cell in row.cells]) for row in table.rows]
            tables_data.append("\n".join(table_text))
        
        prompt = f"""Проверь документ энергоаудита на ошибки.

ТЕКСТ ({len(text_content)} символов):
{text_content[:15000]}

ТАБЛИЦЫ ({len(tables_data)} шт):
{chr(10).join(tables_data[:5])}

ЗАДАЧИ:
{'✓ Структура ПКМ-690' if check_structure else ''}
{'✓ Расчеты' if check_calculations else ''}
{'✓ Нормативы' if check_compliance else ''}
✓ Орфография

JSON:
{{"overall_status": "OK|WARNINGS|ERRORS", "summary": "резюме", 
  "errors": [{{"type": "...", "severity": "...", "location": "...", "description": "...", "suggestion": "..."}}],
  "statistics": {{"critical_errors": 0, "warnings": 0}},
  "structure_check": {{"missing_sections": []}},
  "calculations_check": {{"inconsistencies": []}},
  "compliance_check": {{"pkm690_compliant": true}}
}}"""

        from ai_parser import AIParser
        ai_parser = AIParser()
        
        if not ai_parser.enabled:
            raise HTTPException(status_code=503, detail="AI не настроен")
        
        logger.info(f"🤖 Проверка через {ai_parser.provider}")
        ai_response = await ai_parser.parse_text(prompt)
        
        try:
            result = json.loads(ai_response)
        except:
            result = {"overall_status": "UNKNOWN", "summary": ai_response[:500]}
        
        temp_path.unlink()
        
        return {
            "status": "checked",
            "filename": file.filename,
            "validation_result": result,
            "ai_provider": ai_parser.provider
        }
        
    except Exception as e:
        logger.exception(f"Ошибка проверки: {e}")
        if 'temp_path' in locals() and temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))
'@

Add-Content -Path $projectMain -Value $newEndpoint -Encoding UTF8
Write-Host "✅ Endpoint добавлен!" -ForegroundColor Green
Write-Host ""

# 3. Копирование документации
Write-Host "📚 Копирую документацию..." -ForegroundColor Yellow

$docsContent = @"
# 📄 Проверка Word документов через AI

## Endpoint: /api/validate-word-document

### Использование

``````powershell
curl -X POST http://localhost:8001/api/validate-word-document ``
  -F "file=@document.docx"
``````

### Параметры
- check_structure (bool) - Проверить структуру ПКМ-690
- check_calculations (bool) - Проверить расчеты  
- check_compliance (bool) - Проверить соответствие нормативам

### Возвращает
JSON с результатами проверки:
- overall_status: OK | WARNINGS | ERRORS
- errors: Список найденных ошибок
- statistics: Статистика по типам ошибок
- structure_check: Проверка структуры
- calculations_check: Проверка расчетов
- compliance_check: Проверка соответствия ПКМ-690

## Требования
``````powershell
pip install python-docx
``````

## AI настройка
Endpoint использует существующую конфигурацию AI.
Проверить: ``curl http://localhost:8001/api/normative/ai-status``
"@

$docsPath = "C:\eaip\docs\WORD_VALIDATION_API.md"
Set-Content -Path $docsPath -Value $docsContent -Encoding UTF8
Write-Host "✅ Документация: docs\WORD_VALIDATION_API.md" -ForegroundColor Green
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ Установка завершена!" -ForegroundColor Green  
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Следующие шаги:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Установить зависимость:" -ForegroundColor Cyan
Write-Host "    pip install python-docx"
Write-Host ""
Write-Host "2️⃣  Перезапустить сервис:" -ForegroundColor Cyan  
Write-Host "    cd C:\eaip\eaip_full_skeleton\services\ingest"
Write-Host "    uvicorn main:app --reload --port 8001"
Write-Host ""
Write-Host "3️⃣  Проверить endpoint:" -ForegroundColor Cyan
Write-Host "    curl -X POST http://localhost:8001/api/validate-word-document ``"
Write-Host "      -F 'file=@C:\path\to\document.docx'"
Write-Host ""

Write-Host "📚 Документация: C:\eaip\docs\WORD_VALIDATION_API.md" -ForegroundColor Yellow
Write-Host ""
