"""
Тест для демонстрации low_confidence (ШАГ 2)
Создаёт пример JSON с низким confidence для проверки логирования
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import _check_confidence

# Создаём тестовый результат с низким confidence
test_result = {
    "text": "Тестовый текст с низким confidence",
    "tables": [
        {
            "rows": [["1", "2"]],
            "headers": ["A", "B"],
            "confidence": 0.50  # Ниже порога 0.70 для таблиц
        }
    ],
    "confidence": 0.20  # Ниже порога 0.30 для текста
}

print("Тест low_confidence:")
print(f"Исходный confidence: {test_result['confidence']}")
print(f"Confidence таблицы: {test_result['tables'][0]['confidence']}")
print()

# Проверяем confidence
checked = _check_confidence(test_result, "test_example.pdf", page_num=1)

print("Результат проверки:")
print(f"validation_flag: {checked.get('validation_flag', 'none')}")
print()

# Проверяем лог
log_path = Path(__file__).parent.parent / "reports" / "ocr" / "low_confidence.log"
if log_path.exists():
    print("Последние записи в low_confidence.log:")
    lines = log_path.read_text(encoding='utf-8').strip().split('\n')
    for line in lines[-5:]:  # Последние 5 строк
        if line.strip():
            print(f"  {line}")
else:
    print("⚠️  Файл low_confidence.log не найден")

print()
print("Пример JSON с low_confidence:")
print(json.dumps(checked, ensure_ascii=False, indent=2))

