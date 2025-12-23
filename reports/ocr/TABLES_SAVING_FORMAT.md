# ФОРМАТ СОХРАНЕНИЯ ТАБЛИЦ И ТЕКСТА

**Дата:** 2025-11-29  
**Статус:** ✅ Реализовано

---

## СТРУКТУРА СОХРАНЕНИЯ

### Формат JSON (машиночитаемый, без лишнего)

Таблицы и текст сохраняются в структурированном JSON формате в файлах результатов:

**Путь:** `reports/ocr/step4_batch_results.json` (финальные результаты)  
**Путь:** `reports/ocr/step4_batch_intermediate_{N}.json` (промежуточные результаты)

### Структура данных для каждой страницы:

```json
{
  "page_number": 1,
  "characters": 1951,
  "tables_count": 1,
  "tables": [
    {
      "rows": [
        ["Ячейка 1", "Ячейка 2", "Ячейка 3"],
        ["Значение 1", "Значение 2", "Значение 3"]
      ],
      "headers": ["Заголовок 1", "Заголовок 2", "Заголовок 3"],
      "location": "страница 1, верхняя часть"
    }
  ],
  "text": "Полный распознанный текст со страницы...",
  "processing_time_sec": 13.43,
  "error": null,
  "low_confidence": false,
  "confidence": 0.95
}
```

### Структура данных для файла:

```json
{
  "file_path": "C:\\AUDIT\\OBJECTS\\Navoiy IES\\INBOX\\счёт фактура.PDF",
  "file_name": "счёт фактура.PDF",
  "file_size_kb": 91.57,
  "pages": [
    {
      "page_number": 1,
      "characters": 1951,
      "tables_count": 1,
      "tables": [...],
      "text": "...",
      "processing_time_sec": 13.43,
      "error": null,
      "low_confidence": false,
      "confidence": 0.95
    }
  ],
  "total_characters": 1951,
  "total_tables": 1,
  "total_time_sec": 14.00,
  "avg_time_per_page_sec": 14.00,
  "errors": [],
  "low_confidence_count": 0,
  "gemini_retries_count": 0,
  "success": true
}
```

---

## ОСОБЕННОСТИ ФОРМАТА

### 1. Таблицы (`tables`)

- **Тип:** Массив объектов
- **Структура каждого объекта:**
  - `rows`: Массив массивов строк (двумерная таблица)
  - `headers`: Массив строк (заголовки столбцов)
  - `location`: Строка (описание местоположения таблицы)

**Пример:**
```json
"tables": [
  {
    "rows": [
      ["№", "Наименование", "Количество", "Цена"],
      ["1", "Товар 1", "10", "1000"],
      ["2", "Товар 2", "5", "2000"]
    ],
    "headers": ["№", "Наименование", "Количество", "Цена"],
    "location": "страница 1, нижняя часть"
  }
]
```

### 2. Текст (`text`)

- **Тип:** Строка
- **Содержимое:** Полный распознанный текст со страницы
- **Экранирование:** Спецсимволы экранированы (`\n`, `\t`, `\"`)

**Пример:**
```json
"text": "СЧЕТ-ФАКТУРА №123\nот 29.11.2025\n\nПоставщик: ООО \"Компания\"\n..."
```

### 3. Метаданные

- `tables_count`: Количество таблиц (число)
- `characters`: Количество символов в тексте (число)
- `confidence`: Уровень уверенности OCR (0.0-1.0)
- `low_confidence`: Флаг низкой уверенности (boolean)
- `processing_time_sec`: Время обработки в секундах (float)

---

## ПРЕИМУЩЕСТВА ФОРМАТА

### ✅ Машиночитаемый JSON
- Легко парсится любым языком программирования
- Стандартный формат для обмена данными
- Поддержка встроенными библиотеками

### ✅ Структурированные данные
- Таблицы в виде массивов (готовы для pandas, Excel)
- Заголовки отдельно от данных
- Метаданные для каждой таблицы

### ✅ Без лишнего
- Только необходимые данные
- Нет markdown оберток
- Нет комментариев в JSON

### ✅ Полнота данных
- Сохранен и текст, и таблицы
- Метаданные для анализа качества
- Информация об ошибках

---

## ИСПОЛЬЗОВАНИЕ

### Загрузка результатов

```python
import json

# Загрузка финальных результатов
with open('reports/ocr/step4_batch_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Извлечение таблиц из первой страницы первого файла
first_file = results['files'][0]
first_page = first_file['pages'][0]
tables = first_page['tables']

# Работа с таблицами
for i, table in enumerate(tables):
    print(f"Таблица {i+1}:")
    print(f"  Заголовки: {table['headers']}")
    print(f"  Строк: {len(table['rows'])}")
    for row in table['rows']:
        print(f"    {row}")
```

### Конвертация в pandas DataFrame

```python
import pandas as pd
import json

# Загрузка результатов
with open('reports/ocr/step4_batch_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Извлечение первой таблицы
first_table = results['files'][0]['pages'][0]['tables'][0]

# Создание DataFrame
df = pd.DataFrame(
    first_table['rows'],
    columns=first_table['headers']
)

print(df)
```

### Экспорт в Excel

```python
import pandas as pd
import json

# Загрузка результатов
with open('reports/ocr/step4_batch_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Экспорт всех таблиц в Excel
with pd.ExcelWriter('tables_export.xlsx') as writer:
    for file_idx, file_data in enumerate(results['files']):
        for page_idx, page_data in enumerate(file_data['pages']):
            for table_idx, table in enumerate(page_data['tables']):
                sheet_name = f"File{file_idx+1}_Page{page_idx+1}_Table{table_idx+1}"
                df = pd.DataFrame(
                    table['rows'],
                    columns=table['headers']
                )
                df.to_excel(writer, sheet_name=sheet_name, index=False)
```

---

## РАСПОЛОЖЕНИЕ ФАЙЛОВ

### Результаты батч-теста
- **Финальные:** `reports/ocr/step4_batch_results.json`
- **Промежуточные:** `reports/ocr/step4_batch_intermediate_{N}.json`

### Изображения страниц
- **Путь:** `tests/ocr_test_files/file_{N}_pages/page_{N}_{timestamp}.png`
- **Формат:** PNG
- **Назначение:** Визуальная проверка и отладка

---

## ПРИМЕРЫ РЕАЛЬНЫХ ДАННЫХ

### Пример 1: Счет-фактура

```json
{
  "page_number": 1,
  "tables_count": 1,
  "tables": [
    {
      "rows": [
        ["№", "Наименование", "Кол-во", "Ед.", "Цена", "Сумма"],
        ["1", "Услуга 1", "10", "шт", "1000", "10000"],
        ["2", "Услуга 2", "5", "шт", "2000", "10000"]
      ],
      "headers": ["№", "Наименование", "Кол-во", "Ед.", "Цена", "Сумма"],
      "location": "страница 1, центральная часть"
    }
  ],
  "text": "СЧЕТ-ФАКТУРА №123\nот 29.11.2025\n\nПоставщик: ООО \"Компания\"\nПокупатель: ООО \"Клиент\"\n...",
  "confidence": 0.95
}
```

### Пример 2: Акт выполненных работ

```json
{
  "page_number": 1,
  "tables_count": 1,
  "tables": [
    {
      "rows": [
        ["№ п/п", "Наименование работ", "Ед. изм.", "Количество", "Цена", "Сумма"],
        ["1", "Работа 1", "м²", "100", "500", "50000"],
        ["2", "Работа 2", "м²", "50", "600", "30000"]
      ],
      "headers": ["№ п/п", "Наименование работ", "Ед. изм.", "Количество", "Цена", "Сумма"],
      "location": "страница 1, нижняя часть"
    }
  ],
  "text": "АКТ\nвыполненных работ\n\n№123 от 29.11.2025\n\nИсполнитель: ООО \"Исполнитель\"\n...",
  "confidence": 0.90
}
```

---

**Формат:** ✅ Машиночитаемый JSON без лишнего  
**Структура:** ✅ Полная (таблицы + текст + метаданные)  
**Готовность:** ✅ Готово к использованию

