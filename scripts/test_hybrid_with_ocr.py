"""Тестирование гибридного парсера с работающим OCR"""

import sys
import time
from pathlib import Path

# Добавляем путь к сервисам
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

from utils.table_detector import hybrid_table_extraction, detect_pdf_type

def main():
    pdf_file = Path(r"C:\eaip\eaip_full_skeleton\infra\data\inbox\2458dc3a-91e8-4e5b-863b-2fbde7693267__TTZ 133AA faktura.pdf")
    
    if not pdf_file.exists():
        print(f"❌ Файл не найден: {pdf_file}")
        return
    
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ГИБРИДНОГО ПАРСЕРА С OCR")
    print("=" * 80)
    
    # Определяем тип
    print("\n🔍 Определение типа PDF...")
    start_time = time.time()
    pdf_type = detect_pdf_type(str(pdf_file))
    elapsed = time.time() - start_time
    print(f"📄 Файл: {pdf_file.name}")
    print(f"🔍 Тип PDF: {pdf_type} (заняло {elapsed:.1f}с)")
    
    # Извлекаем таблицы
    print("\n🚀 Запуск гибридного парсера...")
    if pdf_type == "image":
        print("⚠️  ВНИМАНИЕ: PDF определен как сканированный, OCR может занять 3-5 минут!")
        print("   Если зависнет, нажмите Ctrl+C для прерывания")
    
    start_time = time.time()
    try:
        tables = hybrid_table_extraction(str(pdf_file))
        elapsed = time.time() - start_time
        print(f"⏱️  Время выполнения: {elapsed:.1f}с")
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем (Ctrl+C)")
        return
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return
    
    print("\n✅ Результаты:")
    print(f"   Найдено таблиц: {len(tables)}")
    
    if tables:
        for i, table in enumerate(tables[:5], 1):
            print(f"\n   Таблица {i}:")
            print(f"      Метод: {table.get('method', 'unknown')}")
            print(f"      Строк: {table.get('row_count', 0)}")
            print(f"      Колонок: {table.get('col_count', 0)}")
            if table.get('rows'):
                print("      Первые строки:")
                for row in table['rows'][:3]:
                    print(f"         {row[:5]}")  # Первые 5 ячеек
    else:
        print("   ⚠ Таблицы не найдены")

if __name__ == "__main__":
    main()

