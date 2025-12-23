"""
Скрипт для исправления типа данных в существующих записях БД.
Обновляет записи с типом 'consumption' на 'realization' для файлов "Реализация".
"""
import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

import database

DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

def fix_data_types():
    """Исправляет тип данных для записей из файлов 'Реализация'."""
    print("=" * 80)
    print("ИСПРАВЛЕНИЕ ТИПА ДАННЫХ ДЛЯ ФАЙЛОВ 'РЕАЛИЗАЦИЯ'")
    print("=" * 80)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Находим записи из файлов "Реализация" с неправильным типом
    # Сначала проверяем все записи из файлов "Реализация"
    cursor = conn.execute(
        """
        SELECT nc.id, nc.batch_id, u.filename, nc.data_type
        FROM node_consumption nc
        JOIN uploads u ON nc.batch_id = u.batch_id
        WHERE (u.filename LIKE '%Реализация%' OR u.filename LIKE '%реализация%')
        """
    )
    
    records = cursor.fetchall()
    
    if not records:
        print("\n⚠️ Записи из файлов 'Реализация' не найдены")
        conn.close()
        return
    
    # Фильтруем только те, которые нужно исправить
    records_to_fix = [r for r in records if r['data_type'] != 'realization']
    
    if not records_to_fix:
        print("\n✅ Все записи уже имеют правильный тип данных 'realization'")
        conn.close()
        return
    
    print(f"\n📋 Найдено {len(records_to_fix)} записей для исправления (из {len(records)} всего):\n")
    
    # Группируем по файлам
    by_file = {}
    for record in records_to_fix:
        filename = record['filename']
        if filename not in by_file:
            by_file[filename] = []
        by_file[filename].append(record['id'])
    
    for filename, record_ids in by_file.items():
        print(f"   - {filename}: {len(record_ids)} записей")
    
    # Обновляем тип данных
    print(f"\n🔄 Обновление типа данных...")
    
    record_ids = [r['id'] for r in records_to_fix]
    placeholders = ','.join('?' * len(record_ids))
    
    updated = conn.execute(
        f"""
        UPDATE node_consumption
        SET data_type = 'realization'
        WHERE id IN ({placeholders})
        """,
        record_ids
    )
    
    conn.commit()
    rows_affected = updated.rowcount
    
    print(f"✅ Обновлено {rows_affected} записей")
    
    # Проверяем результаты
    cursor2 = conn.execute(
        """
        SELECT data_type, COUNT(*) as count
        FROM node_consumption nc
        JOIN uploads u ON nc.batch_id = u.batch_id
        WHERE u.filename LIKE '%Реализация%' OR u.filename LIKE '%реализация%'
        GROUP BY data_type
        """
    )
    
    stats = cursor2.fetchall()
    
    print(f"\n📊 Статистика после исправления:")
    for stat in stats:
        print(f"   - {stat['data_type']}: {stat['count']} записей")
    
    conn.close()
    
    print(f"\n✅ Исправление завершено!")


if __name__ == "__main__":
    fix_data_types()

