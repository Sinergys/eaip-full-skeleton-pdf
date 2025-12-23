"""
Быстрая генерация отчета по METIN IRODA с шаблоном metin.

Использование:
    python quick_generate_metin_report.py

Скрипт:
1. Проверяет наличие данных METIN IRODA в БД
2. Если данных нет - загружает минимальный набор
3. Генерирует отчет с шаблоном metin
4. Сохраняет результат в output/
"""

import sys
from pathlib import Path

# Добавляем пути
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database
from starlette.testclient import TestClient
from main import app

ENTERPRISE_NAME = "METIN IRODA"
TEMPLATE_NAME = "metin"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def get_or_create_enterprise():
    """Получает или создает предприятие"""
    enterprise = database.get_or_create_enterprise(ENTERPRISE_NAME)
    print(f"✅ Предприятие: {enterprise['name']} (ID: {enterprise['id']})")
    return enterprise


def get_existing_batches(enterprise_id: int):
    """Получает существующие загрузки для предприятия"""
    uploads = database.list_uploads_for_enterprise(enterprise_id, limit=20)
    completed = [
        upload for upload in uploads 
        if upload.get("status") == "completed"
    ]
    return [u["batch_id"] for u in completed]


def generate_report(client: TestClient, batch_id: str):
    """Генерирует отчет с шаблоном metin"""
    print(f"\n📊 Генерация отчета для batch_id: {batch_id[:16]}...")
    
    response = client.post(
        f"/api/generate-passport/{batch_id}",
        params={"template_name": TEMPLATE_NAME},
    )
    
    if response.status_code != 200:
        print(f"❌ Ошибка генерации: {response.status_code}")
        print(f"   {response.text}")
        return None
    
    # Сохраняем файл
    output_file = OUTPUT_DIR / f"metin_report_{batch_id[:8]}.xlsx"
    with open(output_file, "wb") as f:
        f.write(response.content)
    
    print(f"✅ Отчет сохранен: {output_file}")
    print(f"   Размер: {output_file.stat().st_size} байт")
    return output_file


def main():
    print("=" * 80)
    print("БЫСТРАЯ ГЕНЕРАЦИЯ ОТЧЕТА METIN IRODA")
    print("=" * 80)
    
    # Инициализация БД
    database.init_db()
    
    # Получаем предприятие
    enterprise = get_or_create_enterprise()
    enterprise_id = enterprise["id"]
    
    # Получаем существующие загрузки
    print(f"\n🔍 Поиск существующих загрузок...")
    existing_batches = get_existing_batches(enterprise_id)
    
    if not existing_batches:
        print("❌ Нет загруженных данных для предприятия")
        print("   Запустите тест или загрузите файлы через веб-интерфейс")
        return
    
    print(f"✅ Найдено загрузок: {len(existing_batches)}")
    print(f"   Batch IDs: {[b[:16] + '...' for b in existing_batches[:5]]}")
    
    # Используем последний batch_id
    batch_id = existing_batches[0]
    print(f"\n📋 Используем batch_id: {batch_id[:16]}...")
    
    # Генерируем отчет
    client = TestClient(app)
    report_file = generate_report(client, batch_id)
    
    if report_file:
        print(f"\n{'=' * 80}")
        print("✅ ОТЧЕТ УСПЕШНО СГЕНЕРИРОВАН!")
        print(f"{'=' * 80}")
        print(f"Файл: {report_file}")
        print(f"Шаблон: {TEMPLATE_NAME}")
        print(f"Предприятие: {ENTERPRISE_NAME}")


if __name__ == "__main__":
    main()

