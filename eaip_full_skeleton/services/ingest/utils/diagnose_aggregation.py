"""
Диагностический скрипт для проверки агрегации данных.
Используется для отладки проблем с расчетом квартальных данных.
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """Получить путь к базе данных"""
    # Ищем базу данных в разных местах
    possible_paths = [
        Path("ingest_data.db"),
        Path("eaip_full_skeleton/ingest_data.db"),
        Path("services/ingest/ingest_data.db"),
    ]
    for path in possible_paths:
        if path.exists():
            return path
    raise FileNotFoundError("База данных не найдена")


def get_electricity_uploads() -> List[Dict[str, Any]]:
    """Получить список загрузок с типом electricity"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute(
            """
            SELECT batch_id, filename, resource_type, created_at, status
            FROM uploads 
            WHERE resource_type = 'electricity'
            ORDER BY created_at DESC
            LIMIT 10
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_parsed_data(batch_id: str) -> Optional[Dict[str, Any]]:
    """Получить распарсенные данные для batch_id"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute(
            "SELECT raw_json FROM parsed_data WHERE batch_id = ?", (batch_id,)
        )
        row = cursor.fetchone()
        if row and row["raw_json"]:
            return json.loads(row["raw_json"])
        return None
    finally:
        conn.close()


def get_aggregated_data(batch_id: str) -> Optional[Dict[str, Any]]:
    """Получить агрегированные данные для batch_id"""
    # Ищем файл агрегированных данных
    possible_dirs = [
        Path("data/inbox/aggregated"),
        Path("eaip_full_skeleton/data/inbox/aggregated"),
        Path("services/ingest/data/inbox/aggregated"),
    ]

    for dir_path in possible_dirs:
        if dir_path.exists():
            # Ищем файлы с batch_id
            for file_path in dir_path.glob(f"*{batch_id}*.json"):
                try:
                    return json.loads(file_path.read_text(encoding="utf-8"))
                except Exception as e:
                    logger.warning(f"Ошибка чтения {file_path}: {e}")

    return None


def diagnose_electricity_aggregation(batch_id: Optional[str] = None):
    """Диагностика агрегации данных по электроэнергии"""
    print("=" * 80)
    print("🔍 ДИАГНОСТИКА АГРЕГАЦИИ ДАННЫХ ПО ЭЛЕКТРОЭНЕРГИИ")
    print("=" * 80)

    # Получаем список загрузок
    uploads = get_electricity_uploads()

    if not uploads:
        print("❌ Не найдено загрузок с типом 'electricity'")
        return

    print(f"\n📋 Найдено {len(uploads)} загрузок с типом 'electricity':")
    for idx, upload in enumerate(uploads, 1):
        print(f"  {idx}. {upload['filename']} (batch_id: {upload['batch_id'][:8]}...)")

    # Используем указанный batch_id или первый из списка
    if not batch_id:
        batch_id = uploads[0]["batch_id"]
        print(f"\n🔍 Используем первый batch_id: {batch_id[:8]}...")
    else:
        print(f"\n🔍 Используем указанный batch_id: {batch_id[:8]}...")

    # Проверяем распарсенные данные
    print("\n" + "=" * 80)
    print("1️⃣ РАСПАРСЕННЫЕ ДАННЫЕ (raw_json)")
    print("=" * 80)

    parsed_data = get_parsed_data(batch_id)
    if not parsed_data:
        print("❌ Распарсенные данные не найдены")
        return

    print("✅ Распарсенные данные найдены")
    print(f"   Ключи верхнего уровня: {list(parsed_data.keys())}")

    # Ищем данные об электроэнергии
    if "parsing" in parsed_data:
        parsing = parsed_data["parsing"]
        if "data" in parsing:
            data = parsing["data"]
            if "sheets" in data:
                sheets = data["sheets"]
                print(f"   Найдено листов: {len(sheets)}")
                for sheet in sheets:
                    sheet_name = sheet.get("name", "Unknown")
                    rows_count = len(sheet.get("rows", []))
                    print(f"     - {sheet_name}: {rows_count} строк")

                    # Ищем лист с электроэнергией
                    if any(
                        keyword in sheet_name.upper()
                        for keyword in ["ЭЛЕКТР", "ELECTRICITY", "ТП"]
                    ):
                        print("       ⚡ Найден лист с электроэнергией!")
                        if rows_count > 0:
                            print("       Первые 3 строки:")
                            for i, row in enumerate(sheet.get("rows", [])[:3], 1):
                                print(f"         {i}. {row}")

    # Проверяем агрегированные данные
    print("\n" + "=" * 80)
    print("2️⃣ АГРЕГИРОВАННЫЕ ДАННЫЕ")
    print("=" * 80)

    aggregated_data = get_aggregated_data(batch_id)
    if not aggregated_data:
        print("❌ Агрегированные данные не найдены")
        print("   Проверьте путь к файлам агрегированных данных")
        return

    print("✅ Агрегированные данные найдены")
    print(f"   Ключи верхнего уровня: {list(aggregated_data.keys())}")

    if "resources" in aggregated_data:
        resources = aggregated_data["resources"]
        print(f"   Ресурсы: {list(resources.keys())}")

        if "electricity" in resources:
            electricity = resources["electricity"]
            print("\n   ⚡ Данные по электроэнергии:")
            print(f"      Кварталов: {len(electricity)}")

            for quarter_key, quarter_data in electricity.items():
                months = quarter_data.get("months", [])
                quarter_totals = quarter_data.get("quarter_totals", {})

                print(f"\n      📊 Квартал {quarter_key}:")
                print(f"         - Месяцев: {len(months)}")
                print(
                    f"         - quarter_totals: {list(quarter_totals.keys()) if quarter_totals else 'отсутствует'}"
                )

                if months:
                    print(f"         - Пример месяца: {months[0].get('month')}")
                    if months[0].get("values"):
                        print(
                            f"         - Поля в месячных данных: {list(months[0]['values'].keys())}"
                        )
                        print(
                            f"         - Значения: {[(k, v) for k, v in months[0]['values'].items() if v is not None]}"
                        )

                if quarter_totals:
                    print(
                        f"         - Значения quarter_totals: {[(k, v) for k, v in quarter_totals.items()]}"
                    )
                else:
                    print("         ⚠️  quarter_totals отсутствует или пуст!")

    print("\n" + "=" * 80)
    print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 80)


if __name__ == "__main__":
    import sys

    batch_id = sys.argv[1] if len(sys.argv) > 1 else None
    diagnose_electricity_aggregation(batch_id)
