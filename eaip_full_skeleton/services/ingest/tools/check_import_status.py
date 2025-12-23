"""Проверка статуса импорта агрегированных данных"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "ingest_data.db"
AGGREGATED_DIR = Path(__file__).resolve().parent.parent / "data" / "inbox" / "aggregated"

def check_database():
    """Проверка состояния БД"""
    print("=" * 70)
    print("ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Статистика таблиц
    cursor.execute("SELECT COUNT(*) FROM enterprises")
    enterprises = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM uploads")
    uploads = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM parsed_data")
    parsed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM aggregated_data")
    aggregated = cursor.fetchone()[0]
    
    print(f"\n📊 Статистика БД:")
    print(f"   Предприятий: {enterprises}")
    print(f"   Загрузок: {uploads}")
    print(f"   Распарсенных данных: {parsed}")
    print(f"   Агрегированных данных: {aggregated}")
    
    # Проверка структуры aggregated_data
    cursor.execute("PRAGMA table_info(aggregated_data)")
    columns = cursor.fetchall()
    print(f"\n📋 Структура таблицы aggregated_data:")
    for col in columns:
        print(f"   {col[1]:20} | {col[2]:15} | NOT NULL: {bool(col[3])}")
    
    # Последние загрузки
    cursor.execute("""
        SELECT batch_id, filename, status, created_at 
        FROM uploads 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    print(f"\n📁 Последние 5 загрузок:")
    for row in cursor.fetchall():
        print(f"   {row[0][:8]}... | {row[1][:40]:40} | {row[2]:10}")
    
    conn.close()
    return {
        "enterprises": enterprises,
        "uploads": uploads,
        "parsed": parsed,
        "aggregated": aggregated
    }

def check_aggregated_files():
    """Проверка файлов в aggregated/"""
    print("\n" + "=" * 70)
    print("ПРОВЕРКА ФАЙЛОВ В aggregated/")
    print("=" * 70)
    
    if not AGGREGATED_DIR.exists():
        print(f"❌ Директория не найдена: {AGGREGATED_DIR}")
        return {}
    
    files = list(AGGREGATED_DIR.glob("*_aggregated.json"))
    print(f"\n📂 Всего файлов: {len(files)}")
    
    files_with_data = []
    files_empty = []
    files_with_errors = []
    
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            resources = data.get("resources", {})
            has_data = False
            
            for resource_type, resource_data in resources.items():
                if isinstance(resource_data, dict) and resource_data:
                    # Проверяем, есть ли периоды с данными
                    for period, period_data in resource_data.items():
                        if isinstance(period_data, dict):
                            # Проверяем, есть ли числовые значения
                            for key, value in period_data.items():
                                if isinstance(value, (int, float)) and value != 0:
                                    has_data = True
                                    break
                            if has_data:
                                break
                    if has_data:
                        break
            
            if has_data:
                files_with_data.append(f.name)
            else:
                files_empty.append(f.name)
        except Exception as e:
            files_with_errors.append((f.name, str(e)))
    
    print(f"\n✅ Файлы с данными: {len(files_with_data)}")
    if files_with_data:
        print("   Примеры:")
        for fname in files_with_data[:3]:
            print(f"     - {fname}")
    
    print(f"\n⚠️ Пустые файлы: {len(files_empty)}")
    if files_empty:
        print("   Примеры:")
        for fname in files_empty[:3]:
            print(f"     - {fname}")
    
    if files_with_errors:
        print(f"\n❌ Файлы с ошибками: {len(files_with_errors)}")
        for fname, error in files_with_errors[:3]:
            print(f"     - {fname}: {error}")
    
    return {
        "total": len(files),
        "with_data": len(files_with_data),
        "empty": len(files_empty),
        "errors": len(files_with_errors)
    }

def check_import_code():
    """Проверка кода импорта"""
    print("\n" + "=" * 70)
    print("ПРОВЕРКА КОДА ИМПОРТА")
    print("=" * 70)
    
    main_py = Path(__file__).resolve().parent.parent / "main.py"
    
    if not main_py.exists():
        print("❌ Файл main.py не найден")
        return
    
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_import = "import_resource_to_db" in content
    has_try_except = "try:" in content and "import_exc" in content
    
    print(f"\n✅ Импорт в коде:")
    print(f"   Вызов import_resource_to_db: {'✅ Да' if has_import else '❌ Нет'}")
    print(f"   Обработка ошибок: {'✅ Да' if has_try_except else '❌ Нет'}")
    
    # Ищем строки с импортом
    lines = content.split('\n')
    import_lines = []
    for i, line in enumerate(lines, 1):
        if "import_resource_to_db" in line:
            import_lines.append((i, line.strip()[:80]))
    
    if import_lines:
        print(f"\n   Найдено вызовов: {len(import_lines)}")
        for line_num, line_content in import_lines[:3]:
            print(f"     Строка {line_num}: {line_content}...")

def check_logs():
    """Проверка логов"""
    print("\n" + "=" * 70)
    print("ПРОВЕРКА ЛОГОВ")
    print("=" * 70)
    
    log_file = Path(__file__).resolve().parent.parent / "logs" / "aggregation_events.jsonl"
    
    if not log_file.exists():
        print("⚠️ Файл логов не найден")
        return
    
    events = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except:
                    pass
    
    print(f"\n📝 Событий в логе: {len(events)}")
    
    if events:
        success = sum(1 for e in events if e.get("status") == "success")
        failed = sum(1 for e in events if e.get("status") == "error")
        
        print(f"   ✅ Успешных: {success}")
        print(f"   ❌ Ошибок: {failed}")
        
        print(f"\n   Последние 3 события:")
        for event in events[-3:]:
            print(f"     {event.get('timestamp', '')[:19]} | {event.get('status', '')} | {event.get('batch_id', '')[:8]}...")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ПОЛНАЯ ПРОВЕРКА СТАТУСА ИМПОРТА АГРЕГИРОВАННЫХ ДАННЫХ")
    print("=" * 70)
    
    db_stats = check_database()
    file_stats = check_aggregated_files()
    check_import_code()
    check_logs()
    
    print("\n" + "=" * 70)
    print("ИТОГОВАЯ СВОДКА")
    print("=" * 70)
    print(f"\n📊 БД:")
    print(f"   Агрегированных данных: {db_stats['aggregated']}")
    print(f"   Загрузок: {db_stats['uploads']}")
    
    print(f"\n📂 Файлы:")
    print(f"   Всего: {file_stats.get('total', 0)}")
    print(f"   С данными: {file_stats.get('with_data', 0)}")
    print(f"   Пустые: {file_stats.get('empty', 0)}")
    
    print(f"\n🔍 ВЫВОД:")
    if db_stats['aggregated'] == 0:
        print("   ⚠️ В БД нет агрегированных данных!")
        if file_stats.get('with_data', 0) > 0:
            print("   ✅ Но есть файлы с данными - нужен batch-импорт")
        else:
            print("   ⚠️ И все файлы пустые - возможно, импорт не работает")
    else:
        print("   ✅ Импорт работает, данные есть в БД")
    
    print("=" * 70)

