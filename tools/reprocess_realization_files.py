"""
Скрипт для повторной обработки уже загруженных файлов "Реализация" из БД.

Извлекает данные по узлам учёта из файлов, которые были загружены ранее,
но не были обработаны как акты балансов.
"""
import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

try:
    import database
    from utils.balance_sheet_node_extractor import extract_node_consumption_from_balance_sheet
    from extract_from_raw_json import extract_nodes_from_raw_json
    
    # Инициализируем БД (создаст таблицы, если их нет)
    database.init_db()
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    sys.exit(1)

DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"
INBOX_DIR = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "data" / "inbox"


def find_file_on_disk(filename: str) -> Optional[Path]:
    """Ищет файл на диске в различных возможных местах."""
    # Возможные места поиска
    search_paths = [
        INBOX_DIR,
        INBOX_DIR.parent,
        Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "web",
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Ищем файл рекурсивно
        for file_path in search_path.rglob(filename):
            if file_path.is_file():
                return file_path
    
    return None


def reprocess_file_from_db(batch_id: str, filename: str) -> None:
    """Повторно обрабатывает файл из БД."""
    print(f"\n{'='*80}")
    print(f"ОБРАБОТКА: {filename}")
    print(f"batch_id: {batch_id}")
    print(f"{'='*80}")
    
    # Получаем данные из БД
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Получаем upload
    cursor = conn.execute(
        "SELECT id, enterprise_id, filename, file_type FROM uploads WHERE batch_id = ?",
        (batch_id,)
    )
    upload = cursor.fetchone()
    
    if not upload:
        print(f"❌ Upload не найден в БД")
        conn.close()
        return
    
    upload_id = upload['id']
    enterprise_id = upload['enterprise_id']
    
    # Получаем raw_json
    cursor = conn.execute(
        "SELECT raw_json FROM parsed_data WHERE upload_id = ?",
        (upload_id,)
    )
    parsed_row = cursor.fetchone()
    
    if not parsed_row or not parsed_row['raw_json']:
        print(f"❌ Данные парсинга не найдены в БД")
        conn.close()
        return
    
    try:
        raw_json = json.loads(parsed_row['raw_json'])
    except:
        print(f"❌ Ошибка парсинга raw_json")
        conn.close()
        return
    
    conn.close()
    
    # Ищем файл на диске
    file_path = find_file_on_disk(filename)
    
    if not file_path:
        print(f"⚠️ Файл не найден на диске: {filename}")
        print(f"   Попытка обработки только на основе данных из БД...")
        
        # Пытаемся обработать на основе raw_json из БД
        # Проверяем различные возможные структуры raw_json
        sheets_data = None
        if 'parsing' in raw_json and 'data' in raw_json['parsing']:
            # Структура: raw_json['parsing']['data']['sheets']
            if 'sheets' in raw_json['parsing']['data']:
                sheets_data = raw_json['parsing']['data']['sheets']
        elif 'data' in raw_json and 'sheets' in raw_json['data']:
            # Структура: raw_json['data']['sheets']
            sheets_data = raw_json['data']['sheets']
        
        if sheets_data:
            print(f"   ✅ Найдены данные листов в raw_json: {len(sheets_data)} листов")
            for sheet in sheets_data[:3]:
                print(f"      - {sheet.get('name', 'Без имени')}: {len(sheet.get('rows', []))} строк")
            
            # Формируем правильную структуру для extract_node_consumption_from_balance_sheet
            # Функция ожидает структуру с 'data' -> 'sheets' или 'sheets' на верхнем уровне
            normalized_raw_json = {
                'data': {
                    'sheets': sheets_data
                }
            }
            
            # Извлекаем данные по узлам из raw_json
            try:
                # Используем специальную функцию для работы с raw_json без файла
                # Передаем filename для извлечения периода
                node_data = extract_nodes_from_raw_json(
                    raw_json=raw_json,
                    batch_id=batch_id,
                    enterprise_id=enterprise_id,
                    filename=filename  # Передаем filename
                )
                
                if node_data:
                    print(f"   ✅ Извлечено {len(node_data)} записей по узлам из raw_json")
                    
                    # Сохраняем в БД
                    imported = database.import_node_consumption_to_db(
                        enterprise_id=enterprise_id,
                        batch_id=batch_id,
                        node_consumption_data=node_data
                    )
                    print(f"   ✅ Сохранено {len(imported)} записей в БД")
                    
                    # Показываем примеры
                    print(f"\n   📋 Примеры данных:")
                    for i, record in enumerate(node_data[:5], 1):
                        print(f"      {i}. {record['node_name']}: {record.get('active_energy_kwh', 'N/A')} кВт·ч, "
                              f"период: {record.get('period', 'unknown')}, "
                              f"тип: {record.get('data_type', 'unknown')}")
                else:
                    print(f"   ⚠️ Данные по узлам не извлечены из raw_json")
            except Exception as e:
                print(f"   ❌ Ошибка обработки: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ❌ Нет данных листов в raw_json")
        return
    
    print(f"✅ Файл найден: {file_path}")
    
    # Обрабатываем файл
    try:
        node_data = extract_node_consumption_from_balance_sheet(
            file_path=str(file_path),
            batch_id=batch_id,
            enterprise_id=enterprise_id,
            raw_json=raw_json
        )
        
        if node_data:
            print(f"✅ Извлечено {len(node_data)} записей по узлам")
            
            # Группируем по типам листов
            by_sheet_type = {}
            for record in node_data:
                sheet_type = record.get('data_json', {}).get('sheet_type', 'unknown')
                if sheet_type not in by_sheet_type:
                    by_sheet_type[sheet_type] = []
                by_sheet_type[sheet_type].append(record)
            
            print(f"📊 По типам листов:")
            for sheet_type, records in by_sheet_type.items():
                print(f"   - {sheet_type}: {len(records)} записей")
            
            # Сохраняем в БД
            imported = database.import_node_consumption_to_db(
                enterprise_id=enterprise_id,
                batch_id=batch_id,
                node_consumption_data=node_data
            )
            print(f"✅ Сохранено {len(imported)} записей в БД")
            
            # Показываем примеры
            print(f"\n📋 Примеры данных (первые 5):")
            for i, record in enumerate(node_data[:5], 1):
                print(f"   {i}. {record['node_name']}: {record.get('active_energy_kwh', 'N/A')} кВт·ч, "
                      f"период: {record.get('period', 'unknown')}, "
                      f"тип: {record.get('data_type', 'unknown')}")
        else:
            print(f"⚠️ Данные по узлам не извлечены")
    except Exception as e:
        print(f"❌ Ошибка обработки: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Основная функция."""
    print("\n" + "="*80)
    print("ПОВТОРНАЯ ОБРАБОТКА ФАЙЛОВ 'РЕАЛИЗАЦИЯ' ИЗ БД")
    print("="*80)
    
    if not DB_PATH.exists():
        print(f"❌ База данных не найдена: {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Ищем файлы "Реализация" без данных по узлам
    cursor = conn.execute(
        """
        SELECT u.batch_id, u.filename, u.enterprise_id
        FROM uploads u
        WHERE (u.filename LIKE '%Реализация%' OR u.filename LIKE '%реализация%')
        AND u.status = 'success'
        AND NOT EXISTS (
            SELECT 1 FROM node_consumption nc 
            WHERE nc.batch_id = u.batch_id AND nc.data_type = 'realization'
        )
        ORDER BY u.created_at DESC
        """
    )
    
    files = cursor.fetchall()
    conn.close()
    
    if not files:
        print("\n✅ Все файлы 'Реализация' уже обработаны или не найдены")
        return
    
    print(f"\n📋 Найдено {len(files)} файлов для обработки:\n")
    for file in files:
        print(f"   - {file['filename']} (batch_id: {file['batch_id'][:16]}...)")
    
    print(f"\n🚀 Начинаю обработку...\n")
    
    for file in files:
        try:
            reprocess_file_from_db(
                batch_id=file['batch_id'],
                filename=file['filename']
            )
        except Exception as e:
            print(f"❌ Ошибка при обработке {file['filename']}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("✅ ОБРАБОТКА ЗАВЕРШЕНА")
    print("="*80)
    
    # Проверяем результаты
    print(f"\n📊 Проверка результатов...")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute(
        """
        SELECT COUNT(*) as count, COUNT(DISTINCT batch_id) as files_count
        FROM node_consumption
        WHERE data_type = 'realization'
        """
    )
    
    stats = cursor.fetchone()
    conn.close()
    
    print(f"   ✅ Всего записей по узлам (realization): {stats['count']}")
    print(f"   ✅ Обработано файлов: {stats['files_count']}")


if __name__ == "__main__":
    main()

