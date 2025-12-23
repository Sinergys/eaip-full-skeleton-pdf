"""Быстрый тест Tabula с JAVA_HOME"""
import os
import sys
from pathlib import Path

# Устанавливаем JAVA_HOME
java_home = r"C:\Program Files\Microsoft\jdk-17.0.17.10-hotspot"
os.environ["JAVA_HOME"] = java_home
print(f"✅ JAVA_HOME установлен: {java_home}")

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.table_detector import extract_tables_with_tabula

# Тестируем на маленьком файле
pdf_path = Path(__file__).parent.parent.parent.parent / "infra" / "passport_demo1_full.pdf"

if not pdf_path.exists():
    print(f"❌ Файл не найден: {pdf_path}")
    sys.exit(1)

print(f"\n📄 Тестирую: {pdf_path.name}")
print("=" * 70)

try:
    tables = extract_tables_with_tabula(str(pdf_path))
    print(f"\n✅ УСПЕХ! Найдено таблиц: {len(tables)}")
    
    for i, table in enumerate(tables[:3], 1):
        print(f"\n📊 Таблица {i}:")
        print(f"   Размер: {table['row_count']} строк × {table['col_count']} столбцов")
        print(f"   Метод: {table['method']}")
        
        # Показываем первые 3 строки
        rows = table.get('rows', [])
        if rows:
            print("   Первые строки:")
            for j, row in enumerate(rows[:3], 1):
                row_preview = " | ".join(str(cell)[:20] for cell in row[:5])
                print(f"      {j}. {row_preview}")
    
    print("\n" + "=" * 70)
    print("✅ Tabula работает с jpype!")
    
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

