"""
Тест извлечения таблиц из PDF с помощью Tabula
Сравнивает результаты Tabula с другими методами (pdfplumber, camelot)
"""

import sys
from pathlib import Path
import logging

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.table_detector import (
    extract_tables_with_tabula,
    extract_tables_with_pdfplumber,
    extract_tables_with_camelot,
    extract_tables_from_pdf,
    check_java_available,
    get_java_info,
    format_table_as_markdown,
    HAS_TABULA,
    HAS_PDFPLUMBER,
    HAS_CAMELOT,
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_test_pdfs() -> list:
    """Находит тестовые PDF файлы в проекте"""
    pdf_files = []
    
    # Проверяем inbox директорию
    inbox_dir = Path(__file__).parent.parent.parent.parent / "infra" / "data" / "inbox"
    if inbox_dir.exists():
        pdf_files.extend(list(inbox_dir.glob("*.pdf")))
    
    # Проверяем infra директорию
    infra_dir = Path(__file__).parent.parent.parent.parent / "infra"
    if infra_dir.exists():
        pdf_files.extend(list(infra_dir.glob("*.pdf")))
    
    # Убираем дубликаты
    unique_pdfs = list(set(pdf_files))
    
    return unique_pdfs[:3]  # Берем первые 3 файла для теста


def test_tabula_single_pdf(pdf_path: Path) -> dict:
    """Тестирует извлечение таблиц из одного PDF файла"""
    print("\n" + "=" * 70)
    print(f"📄 ТЕСТИРОВАНИЕ: {pdf_path.name}")
    print("=" * 70)
    
    results = {
        "file": str(pdf_path),
        "file_size_mb": pdf_path.stat().st_size / (1024 * 1024),
        "tabula": None,
        "pdfplumber": None,
        "camelot": None,
        "combined": None,
    }
    
    # Тест Tabula
    print("\n1️⃣ Тест Tabula...")
    try:
        tabula_tables = extract_tables_with_tabula(str(pdf_path))
        results["tabula"] = {
            "success": True,
            "table_count": len(tabula_tables),
            "tables": tabula_tables[:2],  # Первые 2 таблицы для примера
        }
        print(f"   ✅ Tabula извлек {len(tabula_tables)} таблиц")
        if tabula_tables:
            for i, table in enumerate(tabula_tables[:2], 1):
                print(f"      Таблица {i}: {table['row_count']} строк × {table['col_count']} столбцов")
    except Exception as e:
        results["tabula"] = {"success": False, "error": str(e)}
        print(f"   ❌ Ошибка Tabula: {e}")
    
    # Тест pdfplumber
    if HAS_PDFPLUMBER:
        print("\n2️⃣ Тест pdfplumber...")
        try:
            pdfplumber_tables = extract_tables_with_pdfplumber(str(pdf_path))
            results["pdfplumber"] = {
                "success": True,
                "table_count": len(pdfplumber_tables),
                "tables": pdfplumber_tables[:2],
            }
            print(f"   ✅ pdfplumber извлек {len(pdfplumber_tables)} таблиц")
            if pdfplumber_tables:
                for i, table in enumerate(pdfplumber_tables[:2], 1):
                    print(f"      Таблица {i}: {table['row_count']} строк × {table['col_count']} столбцов")
        except Exception as e:
            results["pdfplumber"] = {"success": False, "error": str(e)}
            print(f"   ❌ Ошибка pdfplumber: {e}")
    
    # Тест Camelot
    if HAS_CAMELOT:
        print("\n3️⃣ Тест Camelot...")
        try:
            camelot_tables = extract_tables_with_camelot(str(pdf_path))
            results["camelot"] = {
                "success": True,
                "table_count": len(camelot_tables),
                "tables": camelot_tables[:2],
            }
            print(f"   ✅ Camelot извлек {len(camelot_tables)} таблиц")
            if camelot_tables:
                for i, table in enumerate(camelot_tables[:2], 1):
                    print(f"      Таблица {i}: {table['row_count']} строк × {table['col_count']} столбцов")
        except Exception as e:
            results["camelot"] = {"success": False, "error": str(e)}
            print(f"   ❌ Ошибка Camelot: {e}")
    
    # Комбинированный метод
    print("\n4️⃣ Комбинированный метод (все методы)...")
    try:
        combined_tables = extract_tables_from_pdf(str(pdf_path), methods=["tabula", "pdfplumber", "camelot"])
        results["combined"] = {
            "success": True,
            "table_count": len(combined_tables),
        }
        print(f"   ✅ Комбинированный метод извлек {len(combined_tables)} уникальных таблиц")
    except Exception as e:
        results["combined"] = {"success": False, "error": str(e)}
        print(f"   ❌ Ошибка комбинированного метода: {e}")
    
    return results


def show_table_example(table: dict, method: str):
    """Показывает пример извлеченной таблицы"""
    print(f"\n📊 Пример таблицы (метод: {method}):")
    print("-" * 70)
    
    rows = table.get("rows", [])
    if not rows:
        print("   (Таблица пуста)")
        return
    
    # Показываем первые 5 строк
    for i, row in enumerate(rows[:5], 1):
        row_str = " | ".join(str(cell)[:30] for cell in row[:5])  # Первые 5 столбцов, до 30 символов
        print(f"   {i:2d}. {row_str}")
    
    if len(rows) > 5:
        print(f"   ... и еще {len(rows) - 5} строк")
    
    print(f"   Размер: {table.get('row_count', 0)} строк × {table.get('col_count', 0)} столбцов")


def main():
    """Основная функция тестирования"""
    print("=" * 70)
    print("🔍 ТЕСТ ИЗВЛЕЧЕНИЯ ТАБЛИЦ ИЗ PDF С TABULA")
    print("=" * 70)
    
    # Проверка Java и Tabula
    print("\n📋 ПРОВЕРКА СИСТЕМЫ:")
    java_available, java_version, java_path = check_java_available()
    java_info = get_java_info()
    
    print(f"   Java доступна: {'✅' if java_available else '❌'}")
    if java_available:
        print(f"   Версия Java: {java_version}")
        print(f"   Путь: {java_path}")
    
    print(f"   Tabula установлен: {'✅' if HAS_TABULA else '❌'}")
    print(f"   Tabula доступен: {'✅' if java_info['tabula_usable'] else '❌'}")
    print(f"   pdfplumber установлен: {'✅' if HAS_PDFPLUMBER else '❌'}")
    print(f"   Camelot установлен: {'✅' if HAS_CAMELOT else '❌'}")
    
    if not java_info['tabula_usable']:
        print("\n⚠️ ВНИМАНИЕ: Tabula недоступен. Установите Java для использования Tabula.")
        return
    
    # Поиск тестовых PDF
    print("\n🔍 Поиск тестовых PDF файлов...")
    test_pdfs = find_test_pdfs()
    
    if not test_pdfs:
        print("   ❌ Тестовые PDF файлы не найдены")
        print("   💡 Поместите PDF файлы в:")
        print("      - eaip_full_skeleton/infra/data/inbox/")
        print("      - eaip_full_skeleton/infra/")
        return
    
    print(f"   ✅ Найдено {len(test_pdfs)} PDF файлов для тестирования")
    for pdf in test_pdfs:
        print(f"      - {pdf.name} ({pdf.stat().st_size / (1024 * 1024):.2f} MB)")
    
    # Тестирование каждого PDF
    all_results = []
    for pdf_path in test_pdfs:
        if not pdf_path.exists():
            print(f"\n⚠️ Файл не найден: {pdf_path}")
            continue
        
        results = test_tabula_single_pdf(pdf_path)
        all_results.append(results)
        
        # Показываем примеры таблиц
        if results["tabula"] and results["tabula"].get("success") and results["tabula"].get("tables"):
            show_table_example(results["tabula"]["tables"][0], "Tabula")
    
    # Итоговая статистика
    print("\n" + "=" * 70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    
    for result in all_results:
        print(f"\n📄 {Path(result['file']).name} ({result['file_size_mb']:.2f} MB):")
        
        if result["tabula"]:
            if result["tabula"].get("success"):
                print(f"   Tabula: {result['tabula']['table_count']} таблиц")
            else:
                print(f"   Tabula: ❌ {result['tabula'].get('error', 'Ошибка')}")
        
        if result["pdfplumber"]:
            if result["pdfplumber"].get("success"):
                print(f"   pdfplumber: {result['pdfplumber']['table_count']} таблиц")
            else:
                print(f"   pdfplumber: ❌ {result['pdfplumber'].get('error', 'Ошибка')}")
        
        if result["camelot"]:
            if result["camelot"].get("success"):
                print(f"   Camelot: {result['camelot']['table_count']} таблиц")
            else:
                print(f"   Camelot: ❌ {result['camelot'].get('error', 'Ошибка')}")
        
        if result["combined"]:
            if result["combined"].get("success"):
                print(f"   Комбинированный: {result['combined']['table_count']} уникальных таблиц")
    
    print("\n" + "=" * 70)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)


if __name__ == "__main__":
    main()


