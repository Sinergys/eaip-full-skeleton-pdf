"""Миграция таблицы aggregated_data к новой структуре"""
import sqlite3
import sys
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
DB_PATH = INGEST_DIR / "ingest_data.db"

def migrate_aggregated_table():
    """Мигрирует таблицу aggregated_data к новой структуре"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем текущую структуру
        cursor.execute("PRAGMA table_info(aggregated_data)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print("Текущая структура таблицы:")
        for col_name, col_type in columns.items():
            print(f"  {col_name}: {col_type}")
        
        # Если таблица имеет старую структуру, создаём новую
        if "data_period" in columns or "period_value" in columns:
            print("\n⚠️ Обнаружена старая структура таблицы")
            print("Создаём резервную копию и новую таблицу...")
            
            # Создаём резервную копию
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aggregated_data_backup AS
                SELECT * FROM aggregated_data
            """)
            print("✅ Резервная копия создана: aggregated_data_backup")
            
            # Удаляем старую таблицу
            cursor.execute("DROP TABLE IF EXISTS aggregated_data")
            print("✅ Старая таблица удалена")
            
            # Создаём новую таблицу
            cursor.execute("""
                CREATE TABLE aggregated_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enterprise_id INTEGER NOT NULL,
                    batch_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    period TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (enterprise_id) REFERENCES enterprises(id),
                    UNIQUE(enterprise_id, resource_type, period)
                )
            """)
            print("✅ Новая таблица создана")
            
            conn.commit()
            print("\n✅ Миграция завершена успешно")
        else:
            print("\n✅ Таблица уже имеет правильную структуру")
        
        # Проверяем финальную структуру
        cursor.execute("PRAGMA table_info(aggregated_data)")
        print("\nФинальная структура таблицы:")
        for row in cursor.fetchall():
            print(f"  {row[1]}: {row[2]}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Ошибка миграции: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 70)
    print("МИГРАЦИЯ ТАБЛИЦЫ aggregated_data")
    print("=" * 70)
    migrate_aggregated_table()
    print("=" * 70)

