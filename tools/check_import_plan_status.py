"""Проверка статуса плана импорта после сбоя"""
from pathlib import Path
import json
from datetime import datetime

project_root = Path(__file__).parent.parent
plans_dir = project_root / "reports" / "ocr" / "import_plan"

print("=" * 80)
print("ПРОВЕРКА СТАТУСА ПЛАНА ИМПОРТА ДАННЫХ В БД")
print("=" * 80)
print()

# Проверка файлов
files_to_check = [
    ("IMPORT_PLAN.md", "План импорта"),
    ("blocks_status.json", "Статус блоков"),
    ("user_commands_log.jsonl", "Лог команд пользователя"),
    ("execution_log.jsonl", "Лог выполнения"),
    ("tdlv_reports/", "Директория TDLV отчётов"),
]

print("📁 ПРОВЕРКА ФАЙЛОВ:")
print("-" * 80)
all_ok = True
for filename, description in files_to_check:
    file_path = plans_dir / filename
    exists = file_path.exists()
    if exists:
        if file_path.is_file():
            size = file_path.stat().st_size
            print(f"✅ {description}: {filename} ({size} байт)")
        else:
            print(f"✅ {description}: {filename} (директория)")
    else:
        print(f"❌ {description}: {filename} - НЕ НАЙДЕН")
        all_ok = False
print()

# Проверка статуса блоков
print("📊 СТАТУС БЛОКОВ:")
print("-" * 80)
status_file = plans_dir / "blocks_status.json"
if status_file.exists():
    with open(status_file, 'r', encoding='utf-8') as f:
        status = json.load(f)
    
    print(f"План создан: {status.get('plan_created', 'неизвестно')}")
    print()
    
    blocks = status.get('blocks', {})
    pending = sum(1 for b in blocks.values() if b.get('status') == 'pending')
    in_progress = sum(1 for b in blocks.values() if b.get('status') == 'in_progress')
    completed = sum(1 for b in blocks.values() if b.get('status') == 'completed')
    failed = sum(1 for b in blocks.values() if b.get('status') == 'failed')
    
    print(f"Всего блоков: {len(blocks)}")
    print(f"  ⏳ Ожидают выполнения: {pending}")
    print(f"  🔄 В процессе: {in_progress}")
    print(f"  ✅ Завершены: {completed}")
    print(f"  ❌ Ошибки: {failed}")
    print()
    
    # Проверка вопросов
    questions = status.get('questions', [])
    answered = sum(1 for q in questions if q.get('status') == 'answered')
    pending_q = sum(1 for q in questions if q.get('status') == 'pending')
    
    print(f"❓ ВОПРОСЫ К ПОЛЬЗОВАТЕЛЮ:")
    print(f"  ✅ Отвечено: {answered}")
    print(f"  ⏳ Ожидают ответа: {pending_q}")
    print()
    
    if pending_q > 0:
        print("Вопросы, требующие ответа:")
        for q in questions:
            if q.get('status') == 'pending':
                print(f"  {q.get('id')}. {q.get('question')}")
        print()
else:
    print("❌ Файл статуса не найден!")
    all_ok = False

# Проверка логов
print("📝 ПРОВЕРКА ЛОГОВ:")
print("-" * 80)
for log_file, description in [("user_commands_log.jsonl", "Команды пользователя"), 
                               ("execution_log.jsonl", "Выполнение блоков")]:
    log_path = plans_dir / log_file
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"✅ {description}: {len(lines)} записей")
        if lines:
            print(f"   Последняя запись: {lines[-1][:100]}...")
    else:
        print(f"⚠️  {description}: файл пуст или не создан")
print()

# Итоговый статус
print("=" * 80)
print("ИТОГОВЫЙ СТАТУС:")
print("=" * 80)
if all_ok and pending == len(blocks) and pending_q == len(questions):
    print("✅ План создан успешно, все блоки в статусе 'pending'")
    print("⚠️  ТРЕБУЕТСЯ ОТВЕТ НА ВОПРОСЫ перед началом выполнения")
    print()
    print("Следующий шаг: Ответить на вопросы в плане импорта")
elif in_progress > 0:
    print("⚠️  Обнаружены блоки в процессе выполнения")
    print("   Возможен сбой или незавершённое выполнение")
    print()
    print("Рекомендация: Проверить логи выполнения")
elif failed > 0:
    print("❌ Обнаружены блоки с ошибками")
    print()
    print("Рекомендация: Проверить ошибки в blocks_status.json")
else:
    print("✅ Все файлы на месте, план готов к использованию")
print()

