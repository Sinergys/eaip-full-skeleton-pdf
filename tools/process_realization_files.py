"""
Скрипт для обработки файлов "Реализация" напрямую и проверки результатов.

Использование:
    python tools/process_realization_files.py [путь_к_файлу]
    
Если путь не указан, скрипт проверит БД на наличие уже загруженных файлов.
"""
import sys
import sqlite3
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

# Импорты модулей
try:
    import database
    from utils.balance_sheet_detector import is_balance_sheet_file
    from utils.balance_sheet_node_extractor import extract_node_consumption_from_balance_sheet
    from file_parser import parse_excel_file
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    print("Убедитесь, что вы запускаете скрипт из корня проекта")
    sys.exit(1)

# Путь к БД
DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"


def check_existing_files() -> None:
    """Проверяет уже загруженные файлы 'Реализация' в БД."""
    print("=" * 80)
    print("ПРОВЕРКА УЖЕ ЗАГРУЖЕННЫХ ФАЙЛОВ 'РЕАЛИЗАЦИЯ'")
    print("=" * 80)
    
    if not DB_PATH.exists():
        print(f"❌ База данных не найдена: {DB_PATH}")
        return
    
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
        print("\n💡 Подсказка: Загрузите файлы через веб-интерфейс или укажите путь к файлу при запуске скрипта")
        return
    
    print(f"\n✅ Найдено {len(files)} файлов 'Реализация' в БД:\n")
    
    for file in files:
        print(f"📄 {file['filename']}")
        print(f"   batch_id: {file['batch_id']}")
        print(f"   status: {file['status']}")
        print(f"   created_at: {file['created_at']}")
        
        # Проверяем данные по узлам
        cursor2 = conn.execute(
            """
            SELECT COUNT(*) as count, 
                   COUNT(DISTINCT node_name) as unique_nodes,
                   MIN(period) as min_period,
                   MAX(period) as max_period
            FROM node_consumption
            WHERE batch_id = ? AND data_type = 'realization'
            """,
            (file['batch_id'],)
        )
        
        node_stats = cursor2.fetchone()
        if node_stats and node_stats['count'] > 0:
            print(f"   ✅ Данные по узлам: {node_stats['count']} записей, {node_stats['unique_nodes']} узлов")
            print(f"      Периоды: {node_stats['min_period']} - {node_stats['max_period']}")
        else:
            print(f"   ⚠️ Данные по узлам не найдены")
        
        print()
    
    conn.close()


def process_file_directly(file_path: str) -> None:
    """Обрабатывает файл напрямую без веб-интерфейса."""
    print("=" * 80)
    print(f"ОБРАБОТКА ФАЙЛА: {Path(file_path).name}")
    print("=" * 80)
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f"❌ Файл не найден: {file_path}")
        return
    
    # Проверяем, является ли файл актом баланса
    filename = file_path_obj.name
    print(f"\n1️⃣ Проверка типа файла...")
    
    is_balance = is_balance_sheet_file(filename)
    print(f"   {'✅' if is_balance else '❌'} Файл определен как акт баланса: {is_balance}")
    
    if not is_balance:
        print("   ⚠️ Файл не определен как акт баланса, но продолжим обработку...")
    
    # Получаем или создаем предприятие
    print(f"\n2️⃣ Получение предприятия...")
    enterprise = database.get_or_create_enterprise("Navoiy IES")
    enterprise_id = enterprise["id"]
    print(f"   ✅ Предприятие: {enterprise['name']} (ID: {enterprise_id})")
    
    # Создаем batch_id
    batch_id = str(uuid.uuid4())
    print(f"   ✅ batch_id: {batch_id}")
    
    # Парсим файл
    print(f"\n3️⃣ Парсинг файла...")
    try:
        raw_json = parse_excel_file(file_path, batch_id)
        print(f"   ✅ Файл распарсен успешно")
        
        if 'sheets' in raw_json.get('data', {}):
            sheets = raw_json['data']['sheets']
            print(f"   📊 Найдено листов: {len(sheets)}")
            for sheet in sheets:
                sheet_name = sheet.get('name', 'Без имени')
                rows_count = len(sheet.get('rows', []))
                print(f"      - {sheet_name}: {rows_count} строк")
    except Exception as e:
        print(f"   ❌ Ошибка парсинга: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Извлекаем данные по узлам
    print(f"\n4️⃣ Извлечение данных по узлам учёта...")
    try:
        node_data = extract_node_consumption_from_balance_sheet(
            file_path=file_path,
            batch_id=batch_id,
            enterprise_id=enterprise_id,
            raw_json=raw_json
        )
        
        if node_data:
            print(f"   ✅ Извлечено {len(node_data)} записей по узлам")
            
            # Группируем по типам листов
            by_sheet_type = {}
            for record in node_data:
                sheet_type = record.get('data_json', {}).get('sheet_type', 'unknown')
                if sheet_type not in by_sheet_type:
                    by_sheet_type[sheet_type] = []
                by_sheet_type[sheet_type].append(record)
            
            print(f"   📊 По типам листов:")
            for sheet_type, records in by_sheet_type.items():
                print(f"      - {sheet_type}: {len(records)} записей")
            
            # Показываем примеры
            print(f"\n   📋 Примеры данных (первые 5 записей):")
            for i, record in enumerate(node_data[:5], 1):
                print(f"      {i}. {record['node_name']}: {record.get('active_energy_kwh', 'N/A')} кВт·ч, "
                      f"период: {record.get('period', 'unknown')}, "
                      f"тип: {record.get('data_type', 'unknown')}")
        else:
            print(f"   ⚠️ Данные по узлам не извлечены")
    except Exception as e:
        print(f"   ❌ Ошибка извлечения данных: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Сохраняем в БД (если есть данные)
    if node_data:
        print(f"\n5️⃣ Сохранение данных в БД...")
        try:
            imported = database.import_node_consumption_to_db(
                enterprise_id=enterprise_id,
                batch_id=batch_id,
                node_consumption_data=node_data
            )
            print(f"   ✅ Сохранено {len(imported)} записей в БД")
        except Exception as e:
            print(f"   ❌ Ошибка сохранения в БД: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Обработка завершена!")


def main():
    """Основная функция."""
    print("\n" + "=" * 80)
    print("ОБРАБОТКА И ПРОВЕРКА ФАЙЛОВ 'РЕАЛИЗАЦИЯ'")
    print("=" * 80 + "\n")
    
    # Если указан путь к файлу, обрабатываем его
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        process_file_directly(file_path)
    else:
        # Иначе проверяем БД
        check_existing_files()
        
        print("\n" + "=" * 80)
        print("💡 Для обработки конкретного файла используйте:")
        print("   python tools/process_realization_files.py <путь_к_файлу>")
        print("=" * 80)


if __name__ == "__main__":
    main()

