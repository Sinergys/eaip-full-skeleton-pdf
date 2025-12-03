"""Утилита для batch-импорта агрегированных данных в БД"""
import sys
from pathlib import Path

# Добавляем путь к модулям
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import database
from database import batch_import_aggregated_files

if __name__ == "__main__":
    print("=" * 70)
    print("BATCH-ИМПОРТ АГРЕГИРОВАННЫХ ДАННЫХ В БД")
    print("=" * 70)
    
    # Сначала проверяем файлы (dry_run)
    print("\n1. Проверка файлов (dry_run)...")
    check_result = batch_import_aggregated_files(dry_run=True)
    
    print(f"\nВсего файлов: {check_result['total_files']}")
    print(f"Обработано: {check_result['processed']}")
    
    if check_result['details']:
        print("\nДетали проверки:")
        for detail in check_result['details'][:5]:  # Показываем первые 5
            status_icon = "✅" if detail['status'] == 'validated' else "⚠️" if detail['status'] == 'validation_failed' else "❌"
            print(f"  {status_icon} {detail['filename']}: {detail['status']}")
            if detail.get('resources_found'):
                print(f"     Ресурсы: {', '.join(detail['resources_found'])}")
            if detail.get('errors'):
                print(f"     Ошибки: {', '.join(detail['errors'])}")
    
    # Спрашиваем подтверждение для реального импорта
    print("\n" + "=" * 70)
    print("2. Импорт данных в БД...")
    
    import_result = batch_import_aggregated_files(dry_run=False)
    
    print(f"\n✅ Импорт завершён:")
    print(f"   Всего файлов: {import_result['total_files']}")
    print(f"   Обработано: {import_result['processed']}")
    print(f"   Импортировано: {import_result['imported']}")
    print(f"   Пропущено: {import_result['skipped']}")
    print(f"   Ошибок: {import_result['errors']}")
    
    if import_result['details']:
        print("\nДетали импорта:")
        for detail in import_result['details']:
            status_icon = "✅" if detail['status'] == 'imported' else "⚠️" if detail['status'] == 'skipped' else "❌"
            print(f"  {status_icon} {detail['filename']}: {detail['status']}")
            if detail.get('resources_imported'):
                resources_str = ", ".join([f"{k}: {v}" for k, v in detail['resources_imported'].items()])
                print(f"     Импортировано: {resources_str}")
            if detail.get('errors'):
                print(f"     Ошибки: {', '.join(detail['errors'])}")
    
    print("\n" + "=" * 70)

