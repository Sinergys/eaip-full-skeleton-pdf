"""Обновление плана импорта для работы напрямую с БД"""
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
plans_dir = project_root / "reports" / "ocr" / "import_plan"

# Загружаем текущий статус
status_file = plans_dir / "blocks_status.json"
with open(status_file, 'r', encoding='utf-8') as f:
    status = json.load(f)

# Фиксируем решение пользователя
command_log = plans_dir / "user_commands_log.jsonl"
with open(command_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "command": "Продолжить с работой напрямую из БД",
        "decision": "Вариант 2: импорт напрямую из БД с агрегацией на лету",
        "requirements": [
            "Обязательная проверка целостности",
            "Обязательная проверка безошибочности",
            "Опция отладки (сохранение файлов при необходимости)"
        ],
        "status": "confirmed"
    }, ensure_ascii=False) + "\n")

# Обновляем план
plan_update = {
    "updated_at": datetime.now().isoformat(),
    "decision": "Вариант 2: импорт напрямую из БД",
    "modifications": {
        "block_3": {
            "original": "Импорт агрегированных данных - Электроэнергия (из файлов)",
            "modified": "Импорт агрегированных данных - Электроэнергия (напрямую из БД)",
            "changes": [
                "Чтение данных из parsed_data.raw_json для загрузок Навои",
                "Агрегация на лету через aggregate_from_db_json()",
                "Проверка целостности перед импортом",
                "Проверка безошибочности данных",
                "Опция сохранения файлов для отладки"
            ]
        },
        "block_4": {
            "original": "Импорт агрегированных данных - Газ (из файлов)",
            "modified": "Импорт агрегированных данных - Газ (напрямую из БД)",
            "changes": [
                "Чтение данных из parsed_data.raw_json для загрузок Навои",
                "Агрегация на лету через aggregate_from_db_json()",
                "Проверка целостности перед импортом",
                "Проверка безошибочности данных",
                "Опция сохранения файлов для отладки"
            ]
        },
        "block_5": {
            "original": "Импорт агрегированных данных - Вода (из файлов)",
            "modified": "Импорт агрегированных данных - Вода (напрямую из БД)",
            "changes": [
                "Чтение данных из parsed_data.raw_json для загрузок Навои",
                "Агрегация на лету через aggregate_from_db_json()",
                "Проверка целостности перед импортом",
                "Проверка безошибочности данных",
                "Опция сохранения файлов для отладки"
            ]
        },
        "block_6": {
            "original": "Импорт агрегированных данных - Тепло (из файлов)",
            "modified": "Импорт агрегированных данных - Тепло (напрямую из БД)",
            "changes": [
                "Чтение данных из parsed_data.raw_json для загрузок Навои",
                "Агрегация на лету через aggregate_from_db_json()",
                "Проверка целостности перед импортом",
                "Проверка безошибочности данных",
                "Опция сохранения файлов для отладки"
            ]
        }
    },
    "validation_requirements": {
        "integrity_checks": [
            "Проверка наличия обязательных полей",
            "Проверка ссылок на существующие предприятия",
            "Проверка корректности batch_id",
            "Проверка соответствия типов данных",
            "Проверка бизнес-логики (суммы, балансы)"
        ],
        "error_checks": [
            "Проверка структуры JSON",
            "Проверка типов данных",
            "Проверка диапазонов значений",
            "Проверка на отрицательные значения (где недопустимо)",
            "Проверка на пустые обязательные поля",
            "Проверка единиц измерения"
        ],
        "debug_option": {
            "enabled": True,
            "save_on_error": True,
            "save_on_request": True,
            "location": "reports/ocr/import_plan/debug_files/"
        }
    }
}

# Сохраняем обновление плана
plan_update_file = plans_dir / "plan_update_direct_db.json"
with open(plan_update_file, 'w', encoding='utf-8') as f:
    json.dump(plan_update, f, ensure_ascii=False, indent=2)

# Обновляем статус
status["plan_modification"] = plan_update
status["current_approach"] = "direct_db_import"

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

print("=" * 80)
print("ПЛАН ОБНОВЛЁН: ИМПОРТ НАПРЯМУЮ ИЗ БД")
print("=" * 80)
print()
print("✅ Решение пользователя зафиксировано")
print("✅ План модифицирован для работы напрямую с БД")
print("✅ Добавлены проверки целостности и безошибочности")
print("✅ Добавлена опция отладки")
print()
print("МОДИФИКАЦИИ:")
print("  - БЛОК 3-6: Импорт напрямую из parsed_data с агрегацией на лету")
print("  - Проверки: целостность + безошибочность на каждом этапе")
print("  - Отладка: сохранение файлов при ошибках или по запросу")
print()
print("✅ Готово к продолжению выполнения БЛОКА 2")

