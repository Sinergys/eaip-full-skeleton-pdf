"""Быстрый тест парсинга Word"""
import sys
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

from file_parser import parse_docx_file

test_file = r"C:\eaip\data\source_files\audit_sinergys\otchet.docx"

print("Тестирую парсинг Word файла...")
print(f"Файл: {test_file}")

try:
    result = parse_docx_file(test_file)
    print("✅ Парсинг выполнен успешно!")
    print(f"Таблиц: {result.get('table_count', 0)}")
    print(f"Параграфов: {len(result.get('paragraphs', []))}")
    
    if result.get('tables'):
        for i, table in enumerate(result['tables']):
            print(f"  Таблица {i}: {len(table.get('rows', []))} строк")
    
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

