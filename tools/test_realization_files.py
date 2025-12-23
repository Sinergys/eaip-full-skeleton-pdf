"""
Скрипт для тестирования обработки файлов "Реализация".

Проверяет:
1. Определение файлов как актов балансов
2. Извлечение данных из обоих листов (детальные и общие)
3. Сохранение данных в БД с правильным типом (realization)
4. Наличие данных в агрегаторе
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List

# Путь к БД
DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"


def check_uploaded_files() -> None:
    """Проверяет загруженные файлы 'Реализация'."""
    print("=" * 80)
    print("ПРОВЕРКА ЗАГРУЖЕННЫХ ФАЙЛОВ 'РЕАЛИЗАЦИЯ'")
    print("=" * 80)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Ищем файлы "Реализация"
    cursor = conn.execute(
        """
        SELECT batch_id, filename, status, created_at, parsing_summary
        FROM uploads
        WHERE filename LIKE '%Реализация%' OR filename LIKE '%реализация%'
        ORDER BY created_at DESC
        LIMIT 10
        """
    )
    
    files = cursor.fetchall()
    
    if not files:
        print("❌ Файлы 'Реализация' не найдены в БД")
        return
    
    print(f"\n✅ Найдено {len(files)} файлов 'Реализация':\n")
    
    for file in files:
        print(f"📄 {file['filename']}")
        print(f"   batch_id: {file['batch_id'][:16]}...")
        print(f"   status: {file['status']}")
        print(f"   created_at: {file['created_at']}")
        
        # Проверяем parsing_summary
        if file['parsing_summary']:
            try:
                summary = json.loads(file['parsing_summary'])
                if 'sheets' in summary:
                    print(f"   Листов: {summary.get('sheets', 0)}")
                if 'total_rows' in summary:
                    print(f"   Строк: {summary.get('total_rows', 0)}")
            except:
                pass
        
        print()


def check_node_consumption_data() -> None:
    """Проверяет данные по узлам учёта из файлов 'Реализация'."""
    print("=" * 80)
    print("ПРОВЕРКА ДАННЫХ ПО УЗЛАМ УЧЁТА (РЕАЛИЗАЦИЯ)")
    print("=" * 80)
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Ищем данные с типом 'realization'
    cursor = conn.execute(
        """
        SELECT 
            nc.id,
            nc.node_name,
            nc.period,
            nc.active_energy_kwh,
            nc.reactive_energy_kvarh,
            nc.cost_sum,
            nc.data_type,
            nc.batch_id,
            u.filename
        FROM node_consumption nc
        JOIN uploads u ON nc.batch_id = u.batch_id
        WHERE nc.data_type = 'realization'
        ORDER BY nc.created_at DESC
        LIMIT 50
        """
    )
    
    records = cursor.fetchall()
    
    if not records:
        print("❌ Данные по узлам учёта с типом 'realization' не найдены")
        return
    
    print(f"\n✅ Найдено {len(records)} записей по узлам учёта (realization):\n")
    
    # Группируем по файлам
    by_file: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        filename = record['filename']
        if filename not in by_file:
            by_file[filename] = []
        by_file[filename].append(dict(record))
    
    for filename, nodes in by_file.items():
        print(f"📄 {filename}")
        print(f"   Узлов: {len(nodes)}")
        
        # Показываем первые 5 узлов
        for node in nodes[:5]:
            print(f"   - {node['node_name']}: {node['active_energy_kwh']} кВт·ч, период: {node['period']}")
        
        if len(nodes) > 5:
            print(f"   ... и еще {len(nodes) - 5} узлов")
        print()
    
    # Статистика по типам листов
    print("\n📊 Статистика по типам листов:")
    cursor = conn.execute(
        """
        SELECT 
            json_extract(nc.data_json, '$.sheet_type') as sheet_type,
            COUNT(*) as count
        FROM node_consumption nc
        WHERE nc.data_type = 'realization'
        GROUP BY sheet_type
        """
    )
    
    stats = cursor.fetchall()
    for stat in stats:
        sheet_type = stat['sheet_type'] or 'unknown'
        count = stat['count']
        print(f"   {sheet_type}: {count} записей")


def check_aggregation() -> None:
    """Проверяет, попали ли данные в агрегацию."""
    print("=" * 80)
    print("ПРОВЕРКА АГРЕГАЦИИ ДАННЫХ")
    print("=" * 80)
    
    # Ищем агрегированные файлы
    aggregated_dir = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "data" / "inbox" / "aggregated"
    
    if not aggregated_dir.exists():
        print("❌ Директория с агрегированными данными не найдена")
        return
    
    # Ищем файлы, связанные с "Реализация"
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute(
        """
        SELECT batch_id, filename
        FROM uploads
        WHERE filename LIKE '%Реализация%' OR filename LIKE '%реализация%'
        ORDER BY created_at DESC
        LIMIT 5
        """
    )
    
    files = cursor.fetchall()
    
    print(f"\n🔍 Проверка агрегированных файлов для {len(files)} файлов 'Реализация':\n")
    
    for file in files:
        batch_id = file['batch_id']
        filename = file['filename']
        aggregated_file = aggregated_dir / f"{batch_id}_aggregated.json"
        
        if aggregated_file.exists():
            print(f"✅ {filename}")
            print(f"   Агрегированный файл найден: {aggregated_file.name}")
            
            try:
                with open(aggregated_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Проверяем наличие данных по электроэнергии
                if 'electricity' in data:
                    electricity = data['electricity']
                    quarters = list(electricity.keys())
                    print(f"   Кварталов electricity: {len(quarters)}")
                    if quarters:
                        print(f"   Первый квартал: {quarters[0]}")
                else:
                    print(f"   ⚠️ Нет данных electricity в агрегации")
            except Exception as e:
                print(f"   ❌ Ошибка чтения файла: {e}")
        else:
            print(f"❌ {filename}")
            print(f"   Агрегированный файл не найден")
        print()


def main():
    """Основная функция тестирования."""
    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ ОБРАБОТКИ ФАЙЛОВ 'РЕАЛИЗАЦИЯ'")
    print("=" * 80 + "\n")
    
    if not DB_PATH.exists():
        print(f"❌ База данных не найдена: {DB_PATH}")
        return
    
    try:
        check_uploaded_files()
        print("\n")
        check_node_consumption_data()
        print("\n")
        check_aggregation()
        
        print("\n" + "=" * 80)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Ошибка при проверке: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

