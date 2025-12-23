"""Быстрое тестирование гибридного парсера (без полного OCR)"""

import sys
import time
from pathlib import Path

# Добавляем путь к сервисам
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

from utils.table_detector import (
    detect_pdf_type,
    hybrid_table_extraction,
    extract_tables_from_pdf
)

def main():
    print("=" * 80)
    print("БЫСТРОЕ ТЕСТИРОВАНИЕ ГИБРИДНОГО ПАРСЕРА")
    print("=" * 80)
    
    # Тестовый файл
    pdf_file = Path(r"C:\eaip\eaip_full_skeleton\infra\data\inbox\2458dc3a-91e8-4e5b-863b-2fbde7693267__TTZ 133AA faktura.pdf")
    
    if not pdf_file.exists():
        print(f"❌ Файл не найден: {pdf_file}")
        return
    
    print(f"\n📄 Файл: {pdf_file.name}")
    print(f"📊 Размер: {pdf_file.stat().st_size / (1024 * 1024):.2f} MB")
    
    # Шаг 1: Определение типа
    print("\n🔍 Определение типа PDF...")
    pdf_type = detect_pdf_type(str(pdf_file))
    print(f"   ✅ Тип: {pdf_type}")
    
    # Шаг 2: Старый подход
    print("\n📊 Старый подход (extract_tables_from_pdf)...")
    start = time.time()
    old_tables = extract_tables_from_pdf(str(pdf_file))
    old_time = time.time() - start
    print(f"   ✅ Найдено таблиц: {len(old_tables)}")
    print(f"   ⏱ Время: {old_time:.2f} сек")
    
    # Шаг 3: Гибридный подход
    print("\n🚀 Гибридный подход (hybrid_table_extraction)...")
    print("   (OCR ограничен 3 страницами, таймаут 60 сек)")
    start = time.time()
    hybrid_tables = hybrid_table_extraction(str(pdf_file))
    hybrid_time = time.time() - start
    print(f"   ✅ Найдено таблиц: {len(hybrid_tables)}")
    print(f"   ⏱ Время: {hybrid_time:.2f} сек")
    
    # Сравнение
    print("\n📈 Сравнение:")
    print(f"   Старый: {len(old_tables)} таблиц за {old_time:.2f} сек")
    print(f"   Гибридный: {len(hybrid_tables)} таблиц за {hybrid_time:.2f} сек")
    
    if len(hybrid_tables) > len(old_tables):
        print(f"   ✅ Улучшение: +{len(hybrid_tables) - len(old_tables)} таблиц")
    elif len(hybrid_tables) < len(old_tables):
        print(f"   ⚠ Ухудшение: {len(hybrid_tables) - len(old_tables)} таблиц")
    else:
        print("   ➡️  Без изменений")
    
    # Детали таблиц
    if hybrid_tables:
        print("\n📋 Детали найденных таблиц:")
        for i, table in enumerate(hybrid_tables[:3], 1):
            print(f"   Таблица {i}:")
            print(f"      Метод: {table.get('method', 'unknown')}")
            print(f"      Строк: {table.get('row_count', 0)}")
            print(f"      Колонок: {table.get('col_count', 0)}")

if __name__ == "__main__":
    main()

