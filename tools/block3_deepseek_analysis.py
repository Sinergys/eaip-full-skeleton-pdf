"""
БЛОК 3: AI анализ качества OCR через DeepSeek

Анализирует результаты OCR и оценивает качество распознавания
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Добавляем путь к сервису ingest
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    print("❌ Библиотека httpx не установлена. Установите: pip install httpx")
    HAS_HTTPX = False
    sys.exit(1)

# Путь к отчету
REPORT_PATH = Path(__file__).parent.parent / "tests" / "ocr_test_20251129_090258" / "results" / "full_report.json"
OUTPUT_DIR = Path(__file__).parent.parent / "tests" / "ocr_test_20251129_090258"
OUTPUT_FILE = OUTPUT_DIR / "deepseek_analysis.json"

# DeepSeek API настройки
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    # Пробуем найти в тестовом файле
    test_file = Path(__file__).parent.parent / "eaip_full_skeleton" / "test_deepseek_simple.py"
    if test_file.exists():
        content = test_file.read_text(encoding='utf-8')
        import re
        match = re.search(r'DEEPSEEK_API_KEY\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            DEEPSEEK_API_KEY = match.group(1)
            print(f"✅ Найден API ключ в тестовом файле")

if not DEEPSEEK_API_KEY:
    print("❌ DEEPSEEK_API_KEY не установлен")
    print("   Установите переменную окружения или добавьте ключ в test_deepseek_simple.py")
    sys.exit(1)

print("=" * 80)
print("БЛОК 3: AI АНАЛИЗ КАЧЕСТВА OCR ЧЕРЕЗ DEEPSEEK")
print("=" * 80)
print()

# ШАГ 1: Загрузка данных
print("ШАГ 1: Загрузка результатов OCR...")
if not REPORT_PATH.exists():
    print(f"❌ Файл не найден: {REPORT_PATH}")
    sys.exit(1)

with open(REPORT_PATH, 'r', encoding='utf-8') as f:
    report_data = json.load(f)

print(f"✅ Отчет загружен: {REPORT_PATH}")
print(f"   Страниц: {report_data.get('statistics', {}).get('total_pages', 0)}")
print(f"   Символов: {report_data.get('statistics', {}).get('total_characters', 0)}")
print(f"   Таблиц: {report_data.get('statistics', {}).get('total_tables', 0)}")
print()

# Извлечение данных для анализа
stats = report_data.get('statistics', {})
pages = report_data.get('pages', [])
tables = report_data.get('tables', [])

# Загружаем полный OCR текст
full_text_path = OUTPUT_DIR / "results" / "full_ocr_text.txt"
if full_text_path.exists():
    with open(full_text_path, 'r', encoding='utf-8') as f:
        full_text = f.read()
else:
    # Собираем текст из страниц
    full_text = "\n\n".join([
        f"--- Страница {p.get('page_number', i+1)} ---\n{p.get('text', '')}"
        for i, p in enumerate(pages)
    ])

# Берем первые 2000 символов для анализа
text_preview = full_text[:2000]

# Формируем структуру таблиц
tables_info = []
for i, table in enumerate(tables[:4], 1):  # Первые 4 таблицы
    tables_info.append({
        'table_number': i,
        'page': table.get('page', '?'),
        'rows': table.get('row_count', 0),
        'columns': table.get('col_count', 0),
        'method': table.get('method', 'unknown'),
        'preview': str(table.get('rows', []))[:500] if table.get('rows') else ''
    })

# ШАГ 2: Подготовка промпта
print("ШАГ 2: Подготовка промпта для DeepSeek...")

prompt = f"""АНАЛИЗ КАЧЕСТВА OCR ЭНЕРГЕТИЧЕСКОГО ДОКУМЕНТА

ДАННЫЕ OCR:

- Страниц: {stats.get('total_pages', 0)}
- Символов: {stats.get('total_characters', 0)}
- Таблиц найдено: {stats.get('total_tables', 0)}
- Средняя уверенность: {stats.get('avg_confidence', 0):.2f}%
- Время обработки: ~105 сек

РАСПОЗНАННЫЙ ТЕКСТ (первые 2000 символов):

{text_preview}

СТРУКТУРА ТАБЛИЦ:

{json.dumps(tables_info, ensure_ascii=False, indent=2)}

ПРОБЛЕМЫ ИЗВЕСТНЫЕ:

- Уверенность низкая (55.17%)
- Страницы 2 и 4 повернуты на 90° (автоповорот применен)
- Возможны ошибки OCR

ЗАДАЧА: Оценить по критериям 0-100%:

1. КАЧЕСТВО ТЕКСТА:
   - Связность и читаемость
   - Типичные ошибки OCR
   - Сохранение структуры

2. КАЧЕСТВО ТАБЛИЦ:
   - Правильность структуры
   - Полнота данных
   - Соответствие энергоданным

3. ОБЩАЯ ОЦЕНКА:
   - Готовность данных для энергоаудита
   - Критические проблемы
   - Рекомендации по улучшению

ОТВЕТ В JSON:

{{
  "overall_score": 0-100,
  "text_quality": 0-100,
  "table_quality": 0-100,
  "energy_data_completeness": 0-100,
  "critical_issues": ["список"],
  "improvement_recommendations": ["список"],
  "confidence_in_data": 0-100,
  "detailed_analysis": {{
    "text_issues": ["список проблем с текстом"],
    "table_issues": ["список проблем с таблицами"],
    "ocr_errors_detected": ["типичные ошибки OCR"],
    "data_completeness": "оценка полноты данных"
  }}
}}
"""

print("✅ Промпт подготовлен")
print()

# ШАГ 3: Отправка в DeepSeek API
print("ШАГ 3: Отправка запроса в DeepSeek API...")

try:
    # Используем httpx напрямую для обхода проблем с версией openai
    print("   Отправляю запрос через httpx...")
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "Ты эксперт по анализу качества OCR распознавания документов. Ты анализируешь результаты OCR и даешь детальную оценку качества в формате JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
    
    ai_response = result["choices"][0]["message"]["content"]
    print("✅ Ответ получен от DeepSeek")
    print()
    
    # Парсим JSON ответ
    try:
        # Пробуем извлечь JSON из ответа (может быть обернут в markdown)
        import re
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            analysis_result = json.loads(json_match.group(0))
        else:
            analysis_result = json.loads(ai_response)
    except json.JSONDecodeError:
        print("⚠️  Не удалось распарсить JSON ответ, сохраняю как текст")
        analysis_result = {
            "raw_response": ai_response,
            "parse_error": True
        }
    
    # Формируем полный результат
    full_result = {
        "analysis_date": datetime.now().isoformat(),
        "source_report": str(REPORT_PATH),
        "ocr_statistics": stats,
        "ai_analysis": analysis_result,
        "raw_ai_response": ai_response,
        "prompt_used": prompt[:500] + "..." if len(prompt) > 500 else prompt
    }
    
    # ШАГ 4: Сохранение результата
    print("ШАГ 4: Сохранение результата...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Результат сохранен: {OUTPUT_FILE}")
    print()
    
    # Выводим краткий отчет
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА DEEPSEEK")
    print("=" * 80)
    
    if not analysis_result.get("parse_error"):
        print(f"\nОБЩАЯ ОЦЕНКА: {analysis_result.get('overall_score', 'N/A')}/100")
        print(f"Качество текста: {analysis_result.get('text_quality', 'N/A')}/100")
        print(f"Качество таблиц: {analysis_result.get('table_quality', 'N/A')}/100")
        print(f"Полнота энергоданных: {analysis_result.get('energy_data_completeness', 'N/A')}/100")
        print(f"Уверенность в данных: {analysis_result.get('confidence_in_data', 'N/A')}/100")
        
        print(f"\nКРИТИЧЕСКИЕ ПРОБЛЕМЫ ({len(analysis_result.get('critical_issues', []))}):")
        for issue in analysis_result.get('critical_issues', [])[:5]:
            print(f"  - {issue}")
        
        print(f"\nРЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ ({len(analysis_result.get('improvement_recommendations', []))}):")
        for rec in analysis_result.get('improvement_recommendations', [])[:5]:
            print(f"  - {rec}")
    else:
        print("\n⚠️  JSON не распарсен, полный ответ сохранен в файл")
        print(f"Первые 500 символов ответа:")
        print(ai_response[:500])
    
    print()
    print("=" * 80)
    print(f"Полный анализ сохранен: {OUTPUT_FILE}")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ Ошибка при работе с DeepSeek API: {e}")
    import traceback
    traceback.print_exc()
    
    # Сохраняем ошибку
    error_result = {
        "analysis_date": datetime.now().isoformat(),
        "source_report": str(REPORT_PATH),
        "error": str(e),
        "error_type": type(e).__name__
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(error_result, f, ensure_ascii=False, indent=2)
    
    sys.exit(1)

