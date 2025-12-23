"""Проверка принадлежности файлов агрегации к Навои ТЭС"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
plans_dir = project_root / "reports" / "ocr" / "import_plan"
db_path = project_root / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"
aggregated_path = Path(r"C:\eaip\eaip_full_skeleton\services\ingest\data\inbox\aggregated")

print("=" * 80)
print("ПРОВЕРКА ПРИНАДЛЕЖНОСТИ ФАЙЛОВ К НАВОИ ТЭС")
print("=" * 80)
print()

# Получаем информацию о предприятии Navoiy IES из БД
print("📊 ШАГ 1: Проверка предприятия Navoiy IES в БД...")
print("-" * 80)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Находим предприятие Navoiy IES
cursor.execute("SELECT id, name FROM enterprises WHERE name LIKE '%Navoiy%' OR name LIKE '%Навои%'")
navoiy_enterprise = cursor.fetchone()

if navoiy_enterprise:
    navoiy_id = navoiy_enterprise['id']
    navoiy_name = navoiy_enterprise['name']
    print(f"✅ Предприятие найдено: {navoiy_name} (ID: {navoiy_id})")
    
    # Получаем все загрузки для Навои
    cursor.execute("""
        SELECT batch_id, filename, file_type, created_at, status
        FROM uploads
        WHERE enterprise_id = ?
        ORDER BY created_at DESC
    """, (navoiy_id,))
    
    navoiy_uploads = cursor.fetchall()
    print(f"✅ Найдено загрузок для Навои: {len(navoiy_uploads)}")
    print()
    
    # Извлекаем batch_id
    navoiy_batch_ids = [row['batch_id'] for row in navoiy_uploads]
    print(f"📋 Batch ID для Навои ({len(navoiy_batch_ids)}):")
    for i, batch_id in enumerate(navoiy_batch_ids[:10], 1):
        print(f"   {i}. {batch_id}")
    if len(navoiy_batch_ids) > 10:
        print(f"   ... и ещё {len(navoiy_batch_ids) - 10} batch_id")
    print()
else:
    print("❌ Предприятие Navoiy IES не найдено в БД")
    navoiy_batch_ids = []
    navoiy_id = None

conn.close()

# Проверяем файлы агрегации
print("📁 ШАГ 2: Проверка файлов агрегации...")
print("-" * 80)

if aggregated_path.exists():
    all_files = list(aggregated_path.glob("*_aggregated.json"))
    print(f"✅ Найдено всего файлов: {len(all_files)}")
    print()
    
    # Проверяем, какие файлы относятся к Навои
    navoiy_files = []
    other_files = []
    unknown_files = []
    
    for file in all_files:
        # Извлекаем batch_id из имени файла
        # Формат: {batch_id}_aggregated.json
        batch_id = file.stem.replace('_aggregated', '')
        
        if batch_id in navoiy_batch_ids:
            navoiy_files.append({
                "filename": file.name,
                "batch_id": batch_id,
                "size_kb": round(file.stat().st_size / 1024, 2),
                "status": "✅ Навои ТЭС"
            })
        elif batch_id:
            # Проверяем, есть ли этот batch_id в БД для других предприятий
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.batch_id, e.name as enterprise_name
                FROM uploads u
                JOIN enterprises e ON u.enterprise_id = e.id
                WHERE u.batch_id = ?
            """, (batch_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                other_files.append({
                    "filename": file.name,
                    "batch_id": batch_id,
                    "enterprise": result['enterprise_name'],
                    "size_kb": round(file.stat().st_size / 1024, 2),
                    "status": f"⚠️ Другое предприятие: {result['enterprise_name']}"
                })
            else:
                unknown_files.append({
                    "filename": file.name,
                    "batch_id": batch_id,
                    "size_kb": round(file.stat().st_size / 1024, 2),
                    "status": "❓ Неизвестный batch_id"
                })
    
    # Выводим результаты
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("=" * 80)
    print()
    
    print(f"✅ ФАЙЛЫ ДЛЯ НАВОИ ТЭС: {len(navoiy_files)}")
    print("-" * 80)
    if navoiy_files:
        for file_info in navoiy_files:
            print(f"   ✅ {file_info['filename']} ({file_info['size_kb']} KB)")
            print(f"      Batch ID: {file_info['batch_id']}")
    else:
        print("   ❌ Файлов для Навои ТЭС не найдено!")
    print()
    
    print(f"⚠️  ФАЙЛЫ ДЛЯ ДРУГИХ ПРЕДПРИЯТИЙ: {len(other_files)}")
    print("-" * 80)
    if other_files:
        enterprises = {}
        for file_info in other_files:
            ent = file_info['enterprise']
            if ent not in enterprises:
                enterprises[ent] = []
            enterprises[ent].append(file_info)
        
        for enterprise, files in enterprises.items():
            print(f"   📌 {enterprise}: {len(files)} файлов")
            for file_info in files[:3]:
                print(f"      - {file_info['filename']} ({file_info['size_kb']} KB)")
            if len(files) > 3:
                print(f"      ... и ещё {len(files) - 3} файлов")
    else:
        print("   Нет файлов для других предприятий")
    print()
    
    print(f"❓ НЕИЗВЕСТНЫЕ ФАЙЛЫ: {len(unknown_files)}")
    print("-" * 80)
    if unknown_files:
        for file_info in unknown_files[:5]:
            print(f"   ❓ {file_info['filename']} (batch_id: {file_info['batch_id']})")
        if len(unknown_files) > 5:
            print(f"   ... и ещё {len(unknown_files) - 5} файлов")
    else:
        print("   Неизвестных файлов нет")
    print()
    
    # Формируем рекомендацию
    print("=" * 80)
    print("РЕКОМЕНДАЦИЯ")
    print("=" * 80)
    print()
    
    if len(navoiy_files) == 0:
        print("❌ КРИТИЧНО: Файлов для Навои ТЭС не найдено!")
        print()
        print("Возможные причины:")
        print("   1. Файлы агрегации ещё не созданы для загрузок Навои")
        print("   2. Файлы находятся в другом месте")
        print("   3. Batch ID в именах файлов не совпадают с БД")
        print()
        print("Действия:")
        print("   - Проверить, были ли созданы файлы агрегации для загрузок Навои")
        print("   - Проверить другие возможные расположения файлов")
        print("   - Создать файлы агрегации для существующих загрузок Навои")
    elif len(navoiy_files) < len(navoiy_batch_ids):
        print(f"⚠️  ВНИМАНИЕ: Найдено только {len(navoiy_files)} файлов из {len(navoiy_batch_ids)} загрузок")
        print()
        print("Это означает, что:")
        print(f"   - Для {len(navoiy_files)} загрузок есть файлы агрегации")
        print(f"   - Для {len(navoiy_batch_ids) - len(navoiy_files)} загрузок файлов нет")
        print()
        print("Рекомендация:")
        print("   - Импортировать найденные файлы")
        print("   - Для остальных загрузок создать файлы агрегации или пропустить")
    else:
        print(f"✅ ВСЁ В ПОРЯДКЕ: Найдено {len(navoiy_files)} файлов для Навои ТЭС")
        print()
        print("Можно продолжать импорт этих файлов")
    
    # Сохраняем результаты
    results = {
        "check_date": datetime.now().isoformat(),
        "navoiy_enterprise": {
            "id": navoiy_id,
            "name": navoiy_name if navoiy_enterprise else None,
            "uploads_count": len(navoiy_uploads) if navoiy_enterprise else 0,
            "batch_ids": navoiy_batch_ids
        },
        "files_analysis": {
            "total_files": len(all_files),
            "navoiy_files": navoiy_files,
            "other_files": other_files,
            "unknown_files": unknown_files
        },
        "recommendation": {
            "status": "ok" if len(navoiy_files) > 0 else "error",
            "navoiy_files_count": len(navoiy_files),
            "expected_count": len(navoiy_batch_ids)
        }
    }
    
    results_file = plans_dir / "navoiy_files_check.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ Результаты проверки сохранены: {results_file}")
    
else:
    print("❌ Директория с файлами агрегации не найдена!")

print()

