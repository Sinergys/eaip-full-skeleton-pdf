# 🔄 Инструкция по переобработке файлов с улучшенным Intelligent Router

## Проблема

Файл "т-3а.jpg" был загружен **до** улучшений Intelligent Router, поэтому показывает старые результаты:
- `document_type`: "unknown"
- `resource_type`: "unknown"
- `confidence`: 0.48

## Решение

### Вариант 1: Переобработка конкретного файла

```powershell
cd C:\eaip
python tools/reprocess_with_intelligent_router.py 64dfa04c-daea-4407-bb1b-2b61e3ba4403
```

Где `64dfa04c-daea-4407-bb1b-2b61e3ba4403` - это batch_id файла.

### Вариант 2: Переобработка всех файлов проекта "Navoiy IES"

```powershell
cd C:\eaip
python tools/reprocess_with_intelligent_router.py --enterprise "Navoiy IES"
```

### Вариант 3: Переобработка всех файлов

```powershell
cd C:\eaip
python tools/reprocess_with_intelligent_router.py --all
```

## Что делает скрипт

1. ✅ Находит файл на диске по batch_id
2. ✅ Парсит файл (если нужно)
3. ✅ Анализирует с улучшенным Intelligent Router
4. ✅ Определяет тип документа, ресурса, данных
5. ✅ Обновляет routing_map в БД

## Ожидаемые результаты после переобработки

### Для файла "т-3а.jpg"

**До:**
```json
{
  "document_type": "unknown",
  "resource_type": "unknown",
  "data_type": "meter_readings",
  "confidence": 0.48
}
```

**После:**
```json
{
  "document_type": "meter_readings",
  "resource_type": "electricity",  // если в OCR-тексте есть "квтч"
  "data_type": "meter_readings",
  "confidence": 0.7+  // выше благодаря определению типа
}
```

## Проверка результатов

После переобработки проверьте результаты:

```powershell
python tools/check_navoi_project.py
```

Или проверьте конкретный файл:

```powershell
python tools/test_intelligent_router.py 64dfa04c-daea-4407-bb1b-2b61e3ba4403
```

## Важные замечания

1. **Файл должен существовать на диске** - скрипт ищет файл в `INBOX_DIR`
2. **OCR должен быть применен** - для изображений нужен OCR-текст для анализа
3. **Новые загрузки** - автоматически используют улучшенный Router

## Если файл не найден на диске

Если файл был удален, но есть в БД:
- Скрипт попытается использовать данные из БД (`raw_json`)
- Но анализ будет менее точным без полного парсинга

## Следующие шаги

После переобработки файлов:
1. ✅ Проверьте результаты через `check_navoi_project.py`
2. ✅ Убедитесь, что routing_map обновлен в БД
3. ✅ Загрузите необходимые Excel файлы для генерации паспорта

