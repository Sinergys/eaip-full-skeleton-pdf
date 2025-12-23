"""
Модуль извлечения таблиц из PDF документов
Решает проблему потери табличных данных в PDF
Эффект: восстановление 90% табличной информации
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Импорты с проверкой доступности
try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    logger.warning("pdfplumber не установлен. Базовое извлечение таблиц недоступно.")

try:
    import camelot
    import camelot.io

    HAS_CAMELOT = True
except ImportError:
    HAS_CAMELOT = False
    logger.warning(
        "camelot-py не установлен. Расширенное извлечение таблиц недоступно."
    )

try:
    import tabula

    HAS_TABULA = True
except ImportError:
    HAS_TABULA = False
    logger.warning(
        "tabula-py не установлен. Альтернативное извлечение таблиц недоступно."
    )


# Проверка наличия Java для Tabula
def check_java_available() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Проверяет наличие Java Runtime Environment и возвращает детальную информацию
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (доступна ли Java, версия Java, путь к Java если найден)
    """
    import subprocess
    import shutil

    java_version = None
    java_path = None

    try:
        # Проверяем наличие java в PATH
        java_path = shutil.which("java")
        
        if java_path:
            # Пытаемся получить версию
            result = subprocess.run(
                ["java", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                # Java выводит версию в stderr, а не stdout
                output = result.stderr or result.stdout or ""
                for line in output.split("\n"):
                    if "version" in line.lower():
                        # Извлекаем версию (например, "1.8.0_291" или "17.0.1")
                        import re
                        version_match = re.search(r'version\s+"?([0-9._]+)', line, re.IGNORECASE)
                        if version_match:
                            java_version = version_match.group(1)
                        break
                return True, java_version, java_path
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.debug(f"Java не найдена: {e}")
    
    return False, None, None


def get_java_info() -> dict:
    """
    Возвращает детальную информацию о Java для диагностики
    
    Returns:
        dict: Информация о Java (доступность, версия, путь, инструкции)
    """
    java_available, java_version, java_path = check_java_available()
    
    info = {
        "available": java_available,
        "version": java_version,
        "path": java_path,
        "tabula_installed": HAS_TABULA,
        "tabula_usable": java_available and HAS_TABULA,
    }
    
    if not java_available:
        info["installation_instructions"] = {
            "windows": "Установите Java с https://www.java.com/download/ или используйте Chocolatey: choco install openjdk",
            "linux": "sudo apt-get install default-jre  # или sudo yum install java-11-openjdk",
            "macos": "brew install openjdk  # или скачайте с https://www.java.com/download/",
        }
    
    return info


JAVA_AVAILABLE, JAVA_VERSION, JAVA_PATH = check_java_available() if HAS_TABULA else (False, None, None)

# Автоматически устанавливаем JAVA_HOME для jpype, если Java найдена, но JAVA_HOME не установлена
if HAS_TABULA and JAVA_AVAILABLE and JAVA_PATH:
    import os
    if not os.environ.get("JAVA_HOME"):
        java_exe_path = Path(JAVA_PATH)
        if java_exe_path.name in ("java.exe", "java"):
            java_home = java_exe_path.parent.parent  # bin -> jdk
            jvm_dll = java_home / "bin" / "server" / "jvm.dll"
            if not jvm_dll.exists():
                jvm_dll = java_home / "bin" / "client" / "jvm.dll"
            if jvm_dll.exists() or (java_home / "bin" / "java.exe").exists():
                os.environ["JAVA_HOME"] = str(java_home)
                logger.debug(f"Автоматически установлен JAVA_HOME={java_home} для jpype")

if HAS_TABULA:
    if JAVA_AVAILABLE:
        logger.info(
            f"✅ Tabula доступен: Java {JAVA_VERSION or 'найдена'} установлена "
            f"({JAVA_PATH or 'в PATH'})"
        )
    else:
        logger.warning(
            "⚠️ Tabula установлен, но Java Runtime Environment не найдена. "
            "Tabula будет недоступен для извлечения таблиц из PDF.\n"
            "📋 Инструкции по установке Java:\n"
            "   Windows: https://www.java.com/download/ или 'choco install openjdk'\n"
            "   Linux: 'sudo apt-get install default-jre'\n"
            "   macOS: 'brew install openjdk'\n"
            "💡 Система будет использовать альтернативные методы (pdfplumber, camelot)."
        )


def extract_tables_with_pdfplumber(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Извлечение таблиц из PDF с помощью pdfplumber (базовый метод)

    Args:
        pdf_path: Путь к PDF файлу

    Returns:
        Список таблиц с данными
    """
    if not HAS_PDFPLUMBER:
        logger.warning("pdfplumber не установлен")
        return []

    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()

                for table_idx, table in enumerate(page_tables):
                    if not table or len(table) == 0:
                        continue

                    # Очистка данных таблицы
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [cell.strip() if cell else "" for cell in row]
                        if any(cleaned_row):  # Пропускаем пустые строки
                            cleaned_table.append(cleaned_row)

                    if cleaned_table:
                        tables.append(
                            {
                                "page": page_num,
                                "table_index": table_idx,
                                "method": "pdfplumber",
                                "rows": cleaned_table,
                                "row_count": len(cleaned_table),
                                "col_count": len(cleaned_table[0])
                                if cleaned_table
                                else 0,
                            }
                        )

        logger.info(f"pdfplumber извлек {len(tables)} таблиц из {pdf_path}")
        return tables

    except Exception as e:
        logger.error(f"Ошибка извлечения таблиц через pdfplumber: {e}")
        return []


def extract_tables_with_camelot(
    pdf_path: str, flavor: str = "lattice"
) -> List[Dict[str, Any]]:
    """
    Извлечение таблиц из PDF с помощью Camelot (лучше для структурированных таблиц)

    Args:
        pdf_path: Путь к PDF файлу
        flavor: Метод извлечения ("lattice" для таблиц с границами, "stream" для без границ)

    Returns:
        Список таблиц с данными
    """
    if not HAS_CAMELOT:
        logger.warning("camelot-py не установлен")
        return []

    tables = []
    try:
        # Пробуем оба метода
        for method in [flavor, "stream" if flavor == "lattice" else "lattice"]:
            try:
                camelot_tables = camelot.read_pdf(
                    pdf_path,
                    flavor=method,
                    pages="all",
                    line_scale=40,
                    copy_text=["v", "h"],
                )

                for table_idx, table in enumerate(camelot_tables):
                    if table.df.empty:
                        continue

                    # Конвертируем DataFrame в список списков
                    rows = table.df.values.tolist()
                    headers = table.df.columns.tolist()

                    # Добавляем заголовки как первую строку
                    all_rows = [headers] + rows

                    # Очистка данных
                    cleaned_table = []
                    for row in all_rows:
                        cleaned_row = [
                            str(cell).strip() if cell else "" for cell in row
                        ]
                        if any(cleaned_row):
                            cleaned_table.append(cleaned_row)

                    if cleaned_table:
                        tables.append(
                            {
                                "page": table.page,
                                "table_index": table_idx,
                                "method": f"camelot_{method}",
                                "rows": cleaned_table,
                                "row_count": len(cleaned_table),
                                "col_count": len(cleaned_table[0])
                                if cleaned_table
                                else 0,
                                "accuracy": table.accuracy,
                                "whitespace": table.whitespace,
                            }
                        )

                if tables:
                    logger.info(
                        f"Camelot ({method}) извлек {len(tables)} таблиц из {pdf_path}"
                    )
                    break  # Если нашли таблицы, прекращаем попытки

            except Exception as e:
                logger.debug(f"Camelot метод {method} не сработал: {e}")
                continue

        return tables

    except Exception as e:
        logger.error(f"Ошибка извлечения таблиц через Camelot: {e}")
        return []


def extract_tables_with_tabula(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Извлечение таблиц из PDF с помощью Tabula (альтернативный метод)

    Args:
        pdf_path: Путь к PDF файлу

    Returns:
        Список таблиц с данными
    """
    if not HAS_TABULA:
        logger.warning("tabula-py не установлен")
        return []

    if not JAVA_AVAILABLE:
        logger.warning(
            "⚠️ Java не найдена. Tabula требует Java Runtime Environment (JRE).\n"
            "📋 Для установки Java:\n"
            "   Windows: https://www.java.com/download/ или 'choco install openjdk'\n"
            "   Linux: 'sudo apt-get install default-jre'\n"
            "   macOS: 'brew install openjdk'\n"
            "💡 Используются альтернативные методы извлечения таблиц."
        )
        return []

    # Устанавливаем JAVA_HOME для jpype, если не установлена
    import os
    if not os.environ.get("JAVA_HOME") and JAVA_PATH:
        # Пытаемся определить JAVA_HOME из пути к java.exe
        java_exe_path = Path(JAVA_PATH)
        if java_exe_path.name == "java.exe" or java_exe_path.name == "java":
            java_home = java_exe_path.parent.parent  # bin -> jdk
            if (java_home / "bin" / "java.exe").exists() or (java_home / "bin" / "java").exists():
                os.environ["JAVA_HOME"] = str(java_home)
                logger.debug(f"Установлен JAVA_HOME={java_home} для jpype")

    tables = []
    try:
        # Извлекаем все таблицы со всех страниц
        dfs = tabula.read_pdf(
            pdf_path, pages="all", multiple_tables=True, pandas_options={"header": None}
        )

        for table_idx, df in enumerate(dfs):
            if df.empty:
                continue

            # Конвертируем DataFrame в список списков
            rows = df.values.tolist()

            # Очистка данных
            cleaned_table = []
            for row in rows:
                cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                if any(cleaned_row):
                    cleaned_table.append(cleaned_row)

            if cleaned_table:
                tables.append(
                    {
                        "page": None,  # Tabula не всегда возвращает номер страницы
                        "table_index": table_idx,
                        "method": "tabula",
                        "rows": cleaned_table,
                        "row_count": len(cleaned_table),
                        "col_count": len(cleaned_table[0]) if cleaned_table else 0,
                    }
                )

        logger.info(f"Tabula извлек {len(tables)} таблиц из {pdf_path}")
        return tables

    except Exception as e:
        logger.error(f"Ошибка извлечения таблиц через Tabula: {e}")
        return []


def merge_duplicate_tables(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Объединяет дублирующиеся таблицы (когда один метод находит таблицу несколько раз)

    Args:
        tables: Список таблиц

    Returns:
        Список уникальных таблиц
    """
    if not tables:
        return []

    # Группируем по странице и количеству строк/столбцов
    seen = {}
    unique_tables = []

    for table in tables:
        key = (table.get("page"), table.get("row_count", 0), table.get("col_count", 0))

        if key not in seen:
            seen[key] = True
            unique_tables.append(table)
        else:
            # Если таблица похожа, выбираем ту, у которой выше accuracy (если есть)
            existing = next(
                (
                    t
                    for t in unique_tables
                    if (
                        t.get("page") == table.get("page")
                        and t.get("row_count") == table.get("row_count")
                        and t.get("col_count") == table.get("col_count")
                    )
                ),
                None,
            )

            if existing:
                existing_accuracy = existing.get("accuracy", 0)
                new_accuracy = table.get("accuracy", 0)
                if new_accuracy > existing_accuracy:
                    unique_tables.remove(existing)
                    unique_tables.append(table)

    return unique_tables


def extract_tables_from_pdf(
    pdf_path: str, methods: Optional[List[str]] = None, prefer_camelot: bool = True
) -> List[Dict[str, Any]]:
    """
    Извлечение таблиц из PDF документов с использованием нескольких методов

    Стратегия:
    1. Пробуем Camelot (лучше для структурированных таблиц)
    2. Fallback на pdfplumber (универсальный метод)
    3. Дополнительно пробуем Tabula (если доступен)
    4. Объединяем результаты, убирая дубликаты

    Args:
        pdf_path: Путь к PDF файлу
        methods: Список методов для использования (None = автоматический выбор)
        prefer_camelot: Предпочитать ли Camelot другим методам

    Returns:
        Список таблиц с данными
    """
    if not Path(pdf_path).exists():
        logger.error(f"PDF файл не найден: {pdf_path}")
        return []

    all_tables = []

    # Определяем порядок методов
    if methods is None:
        if prefer_camelot and HAS_CAMELOT:
            methods = ["camelot", "pdfplumber", "tabula"]
        elif HAS_PDFPLUMBER:
            methods = ["pdfplumber", "camelot", "tabula"]
        else:
            methods = ["pdfplumber"]

    # Извлекаем таблицы каждым методом
    for method in methods:
        try:
            if method == "tabula" and (not HAS_TABULA or not JAVA_AVAILABLE):
                logger.debug("Пропускаем Tabula: не установлен или Java недоступна")
                continue
            if method == "camelot" and HAS_CAMELOT:
                logger.info("Пробую извлечь таблицы через Camelot...")
                tables = extract_tables_with_camelot(pdf_path)
                if tables:
                    all_tables.extend(tables)
                    logger.info(f"Camelot нашел {len(tables)} таблиц")

            elif method == "pdfplumber" and HAS_PDFPLUMBER:
                logger.info("Пробую извлечь таблицы через pdfplumber...")
                tables = extract_tables_with_pdfplumber(pdf_path)
                if tables:
                    all_tables.extend(tables)
                    logger.info(f"pdfplumber нашел {len(tables)} таблиц")

            elif method == "tabula" and HAS_TABULA:
                logger.info("Пробую извлечь таблицы через Tabula...")
                tables = extract_tables_with_tabula(pdf_path)
                if tables:
                    all_tables.extend(tables)
                    logger.info(f"Tabula нашел {len(tables)} таблиц")

        except Exception as e:
            logger.warning(f"Ошибка при использовании метода {method}: {e}")
            continue

    # Объединяем результаты, убирая дубликаты
    if len(all_tables) > 1:
        all_tables = merge_duplicate_tables(all_tables)

    logger.info(f"Всего извлечено {len(all_tables)} уникальных таблиц из {pdf_path}")
    return all_tables


def format_table_as_markdown(table: Dict[str, Any]) -> str:
    """
    Форматирует таблицу в Markdown формат для удобного просмотра

    Args:
        table: Словарь с данными таблицы

    Returns:
        Таблица в формате Markdown
    """
    rows = table.get("rows", [])
    if not rows:
        return ""

    markdown_lines = []

    # Заголовок (первая строка)
    if rows:
        header = rows[0]
        markdown_lines.append("| " + " | ".join(str(cell) for cell in header) + " |")
        markdown_lines.append("| " + " | ".join("---" for _ in header) + " |")

    # Данные
    for row in rows[1:]:
        markdown_lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

    return "\n".join(markdown_lines)


def format_table_as_csv(table: Dict[str, Any]) -> str:
    """
    Форматирует таблицу в CSV формат

    Args:
        table: Словарь с данными таблицы

    Returns:
        Таблица в формате CSV
    """
    import csv
    import io

    rows = table.get("rows", [])
    if not rows:
        return ""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)

    return output.getvalue()


# Проверка доступности функций
def detect_pdf_type(pdf_path: str) -> str:
    """
    Определяет тип PDF файла: текстовый, скан/изображение или гибридный

    Args:
        pdf_path: Путь к PDF файлу

    Returns:
        'text' - текстовый PDF (есть извлекаемый текст)
        'image' - скан/изображение (только картинки, нет текста)
        'hybrid' - гибридный (текст + изображения)
    """
    if not HAS_PDFPLUMBER:
        logger.warning("pdfplumber не установлен, невозможно определить тип PDF")
        return "unknown"

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            if total_pages == 0:
                return "unknown"

            text_pages = 0
            image_pages = 0
            total_text_length = 0
            total_images = 0

            # Анализируем первые 5 страниц для быстрой проверки
            pages_to_check = min(5, total_pages)

            for page_num in range(pages_to_check):
                page = pdf.pages[page_num]

                # Проверяем наличие текста
                page_text = page.extract_text()
                if page_text and len(page_text.strip()) > 50:  # Минимум 50 символов
                    text_pages += 1
                    total_text_length += len(page_text)

                # Проверяем наличие изображений
                images = page.images
                if images and len(images) > 0:
                    image_pages += 1
                    total_images += len(images)

            # Определяем тип на основе анализа
            text_ratio = text_pages / pages_to_check if pages_to_check > 0 else 0
            image_ratio = image_pages / pages_to_check if pages_to_check > 0 else 0

            # Если есть значительный текст (>80% страниц)
            if text_ratio > 0.8 and total_text_length > 500:
                if image_ratio > 0.3:
                    return "hybrid"  # Текст + изображения
                else:
                    return "text"  # Преимущественно текст

            # Если есть изображения, но мало текста
            elif image_ratio > 0.5 and text_ratio < 0.2:
                return "image"  # Скан/изображение

            # Если есть и текст, и изображения
            elif text_ratio > 0.3 and image_ratio > 0.3:
                return "hybrid"

            # Если мало всего - вероятно скан
            elif total_text_length < 100:
                return "image"

            # По умолчанию считаем текстовым, если есть хоть какой-то текст
            elif text_ratio > 0.2:
                return "text"
            else:
                return "image"

    except Exception as e:
        logger.error(f"Ошибка определения типа PDF {pdf_path}: {e}")
        return "unknown"


def extract_tables_with_ocr(pdf_path: str, timeout: int = 300) -> List[Dict[str, Any]]:
    """
    Извлечение таблиц из сканированного PDF через OCR

    Args:
        pdf_path: Путь к PDF файлу
        timeout: Максимальное время выполнения в секундах (по умолчанию 5 минут)

    Returns:
        Список таблиц с данными
    """
    try:
        import sys
        from pathlib import Path

        # Импортируем OCR функцию из file_parser
        ingest_path = Path(__file__).resolve().parent.parent
        if str(ingest_path) not in sys.path:
            sys.path.insert(0, str(ingest_path))

        from file_parser import apply_ocr_to_pdf

        logger.info(f"Применяю OCR к сканированному PDF (таймаут: {timeout}с)...")

        # Для Windows используем threading.Timer вместо signal
        import threading

        ocr_result = [None]
        ocr_error = [None]

        def run_ocr():
            try:
                ocr_result[0] = apply_ocr_to_pdf(pdf_path)
            except Exception as e:
                ocr_error[0] = e

        ocr_thread = threading.Thread(target=run_ocr, daemon=True)
        ocr_thread.start()
        ocr_thread.join(timeout=timeout)

        if ocr_thread.is_alive():
            logger.warning(f"OCR превысил таймаут {timeout}с, прерываю...")
            return []

        if ocr_error[0]:
            logger.error(f"Ошибка OCR: {ocr_error[0]}")
            return []

        ocr_text = ocr_result[0]

        if not ocr_text or len(ocr_text.strip()) < 100:
            logger.warning("OCR не извлек достаточно текста для поиска таблиц")
            return []

        # Парсим OCR текст для поиска табличных структур
        # Простой подход: ищем строки с разделителями (табуляция, множественные пробелы)
        lines = ocr_text.split("\n")
        tables = []
        current_table = []

        for line in lines:
            line = line.strip()
            if not line:
                if current_table and len(current_table) > 1:
                    # Сохраняем найденную таблицу
                    tables.append(
                        {
                            "page": None,
                            "table_index": len(tables),
                            "method": "ocr_extraction",
                            "rows": current_table,
                            "row_count": len(current_table),
                            "col_count": max(len(row) for row in current_table)
                            if current_table
                            else 0,
                        }
                    )
                current_table = []
                continue

            # Пробуем разделить строку на колонки
            # Разделители: табуляция, множественные пробелы (>=3)
            import re

            cells = re.split(r"\t+|\s{3,}", line)
            cells = [cell.strip() for cell in cells if cell.strip()]

            if len(cells) >= 2:  # Минимум 2 колонки для таблицы
                current_table.append(cells)

        # Сохраняем последнюю таблицу если есть
        if current_table and len(current_table) > 1:
            tables.append(
                {
                    "page": None,
                    "table_index": len(tables),
                    "method": "ocr_extraction",
                    "rows": current_table,
                    "row_count": len(current_table),
                    "col_count": max(len(row) for row in current_table)
                    if current_table
                    else 0,
                }
            )

        logger.info(f"OCR извлек {len(tables)} таблиц из сканированного PDF")
        return tables

    except ImportError:
        logger.warning("OCR функции недоступны")
        return []
    except Exception as e:
        logger.error(f"Ошибка извлечения таблиц через OCR: {e}")
        return []


def hybrid_table_extraction(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Гибридный парсер таблиц с автоматическим выбором стратегии

    Стратегия:
    1. Определяет тип PDF (text/image/hybrid)
    2. Для ТЕКСТОВЫХ PDF: Camelot + pdfplumber
    3. Для СКАНОВ: OCR → поиск таблиц
    4. Для ГИБРИДНЫХ: комбинация обоих подходов

    Args:
        pdf_path: Путь к PDF файлу

    Returns:
        Список таблиц с данными
    """
    if not Path(pdf_path).exists():
        logger.error(f"PDF файл не найден: {pdf_path}")
        return []

    # Шаг 1: Определяем тип PDF
    pdf_type = detect_pdf_type(pdf_path)
    logger.info(f"Определен тип PDF: {pdf_type}")

    all_tables = []

    # Шаг 2: Выбираем стратегию на основе типа
    if pdf_type == "text":
        # ТЕКСТОВЫЙ PDF: используем стандартные методы
        logger.info("Обработка текстового PDF: Camelot + pdfplumber")

        if HAS_CAMELOT:
            try:
                camelot_tables = extract_tables_with_camelot(pdf_path)
                if camelot_tables:
                    all_tables.extend(camelot_tables)
                    logger.info(f"Camelot нашел {len(camelot_tables)} таблиц")
            except Exception as e:
                logger.warning(f"Ошибка Camelot: {e}")

        if HAS_PDFPLUMBER:
            try:
                pdfplumber_tables = extract_tables_with_pdfplumber(pdf_path)
                if pdfplumber_tables:
                    all_tables.extend(pdfplumber_tables)
                    logger.info(f"pdfplumber нашел {len(pdfplumber_tables)} таблиц")
            except Exception as e:
                logger.warning(f"Ошибка pdfplumber: {e}")

    elif pdf_type == "image":
        # СКАН: используем OCR (с таймаутом)
        logger.info("Обработка сканированного PDF: OCR → извлечение таблиц")
        logger.warning("⚠️ OCR может занять много времени для больших файлов...")

        ocr_tables = extract_tables_with_ocr(pdf_path, timeout=180)  # 3 минуты таймаут
        if ocr_tables:
            all_tables.extend(ocr_tables)
            logger.info(f"OCR извлек {len(ocr_tables)} таблиц")
        else:
            logger.warning(
                "OCR не извлек таблицы (возможно, превышен таймаут или poppler не установлен)"
            )

        # Также пробуем pdfplumber на случай если есть какие-то структуры
        if HAS_PDFPLUMBER:
            try:
                pdfplumber_tables = extract_tables_with_pdfplumber(pdf_path)
                if pdfplumber_tables:
                    all_tables.extend(pdfplumber_tables)
                    logger.info(
                        f"pdfplumber нашел {len(pdfplumber_tables)} дополнительных таблиц"
                    )
            except Exception as e:
                logger.debug(f"pdfplumber не нашел таблицы в скане: {e}")

    elif pdf_type == "hybrid":
        # ГИБРИДНЫЙ: комбинация обоих подходов
        logger.info("Обработка гибридного PDF: комбинация методов")

        # Сначала стандартные методы для текстовой части
        if HAS_CAMELOT:
            try:
                camelot_tables = extract_tables_with_camelot(pdf_path)
                if camelot_tables:
                    all_tables.extend(camelot_tables)
            except Exception as e:
                logger.debug(f"Camelot: {e}")

        if HAS_PDFPLUMBER:
            try:
                pdfplumber_tables = extract_tables_with_pdfplumber(pdf_path)
                if pdfplumber_tables:
                    all_tables.extend(pdfplumber_tables)
            except Exception as e:
                logger.debug(f"pdfplumber: {e}")

        # Затем OCR для сканированных частей (с таймаутом)
        logger.warning("⚠️ OCR для гибридного PDF может занять много времени...")
        ocr_tables = extract_tables_with_ocr(pdf_path, timeout=180)  # 3 минуты таймаут
        if ocr_tables:
            all_tables.extend(ocr_tables)
            logger.info(f"OCR извлек {len(ocr_tables)} таблиц из сканированных страниц")

    else:
        # UNKNOWN: пробуем все методы
        logger.warning("Неизвестный тип PDF, пробую все методы")
        all_tables = extract_tables_from_pdf(pdf_path)

    # Убираем дубликаты
    if len(all_tables) > 1:
        all_tables = merge_duplicate_tables(all_tables)

    logger.info(
        f"Гибридный парсер извлек {len(all_tables)} уникальных таблиц из {pdf_path}"
    )
    return all_tables


def check_dependencies() -> dict:
    """
    Проверяет доступность зависимостей для извлечения таблиц

    Returns:
        Словарь с информацией о доступных методах и Java
    """
    java_info = get_java_info()
    
    available_methods = []
    if HAS_PDFPLUMBER:
        available_methods.append("pdfplumber")
    if HAS_CAMELOT:
        available_methods.append("camelot")
    if HAS_TABULA and JAVA_AVAILABLE:
        available_methods.append("tabula")
    
    result = {
        "pdfplumber": HAS_PDFPLUMBER,
        "camelot": HAS_CAMELOT,
        "tabula": HAS_TABULA,
        "tabula_usable": HAS_TABULA and JAVA_AVAILABLE,
        "java": java_info,
        "available_methods": available_methods,
    }
    
    if HAS_TABULA and not JAVA_AVAILABLE:
        result["tabula_warning"] = (
            "Tabula установлен, но Java не найдена. "
            "Установите Java для использования Tabula."
        )
    
    return result


if __name__ == "__main__":
    # Тестирование зависимостей
    deps = check_dependencies()
    print("Доступность зависимостей для извлечения таблиц:")
    for key, value in deps.items():
        print(f"  {key}: {value}")
