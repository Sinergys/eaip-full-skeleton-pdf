"""Тест исправления парсинга Word файлов с проблемными таблицами"""
import sys
from pathlib import Path

# Добавляем путь к модулям
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

from file_parser import parse_docx_file
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_docx_parsing():
    """Тест парсинга Word файлов"""
    print("=" * 70)
    print("ТЕСТ ИСПРАВЛЕНИЯ ПАРСИНГА WORD ФАЙЛОВ")
    print("=" * 70)
    
    # Ищем Word файлы в inbox
    inbox_dir = INGEST_DIR / "data" / "inbox"
    docx_files = list(inbox_dir.glob("*.docx"))
    
    if not docx_files:
        print("❌ Word файлы не найдены в inbox/")
        print(f"   Искал в: {inbox_dir}")
        return
    
    print(f"\n📂 Найдено Word файлов: {len(docx_files)}")
    
    success_count = 0
    error_count = 0
    
    for docx_file in docx_files[:5]:  # Тестируем первые 5 файлов
        print(f"\n📄 Тестирую: {docx_file.name}")
        try:
            result = parse_docx_file(str(docx_file))
            
            # Проверяем результат
            if result:
                tables_count = result.get("table_count", 0)
                paragraphs_count = len(result.get("paragraphs", []))
                
                print(f"   ✅ Успешно распарсен")
                print(f"      Таблиц: {tables_count}")
                print(f"      Параграфов: {paragraphs_count}")
                
                # Проверяем таблицы
                if tables_count > 0:
                    for table in result.get("tables", []):
                        rows_count = len(table.get("rows", []))
                        print(f"      → Таблица {table.get('index')}: {rows_count} строк")
                
                success_count += 1
            else:
                print(f"   ⚠️ Результат пустой")
                error_count += 1
                
        except Exception as e:
            print(f"   ❌ ОШИБКА: {e}")
            error_count += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Успешно: {success_count}")
    print(f"   ❌ Ошибок: {error_count}")
    print("=" * 70)


if __name__ == "__main__":
    test_docx_parsing()

