# 📄 Проверка Word документов через AI

## Endpoint: /api/validate-word-document

### Использование

```powershell
curl -X POST http://localhost:8001/api/validate-word-document `
  -F "file=@document.docx"
```

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
```powershell
pip install python-docx
```

## AI настройка
Endpoint использует существующую конфигурацию AI.
Проверить: `curl http://localhost:8001/api/normative/ai-status`
