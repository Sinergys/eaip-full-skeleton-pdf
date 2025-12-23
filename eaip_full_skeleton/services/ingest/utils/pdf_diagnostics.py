"""
Диагностический инструмент для анализа PDF файлов
Помогает определить тип PDF (текстовый/сканированный) и диагностировать проблемы OCR
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Импорты с проверкой доступности
try:
    import PyPDF2

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from pdf2image import convert_from_path

    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    import pytesseract

    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


def analyze_pdf_structure(pdf_path: str) -> Dict[str, Any]:
    """
    Комплексный анализ структуры PDF файла

    Returns:
        Словарь с детальной информацией о PDF
    """
    result = {
        "file_path": pdf_path,
        "file_size": os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0,
        "has_pypdf2": HAS_PYPDF2,
        "has_pdfplumber": HAS_PDFPLUMBER,
        "has_pdf2image": HAS_PDF2IMAGE,
        "has_tesseract": HAS_TESSERACT,
        "metadata": {},
        "text_analysis": {},
        "image_analysis": {},
        "scanned_detection": {},
        "recommendations": [],
    }

    if not os.path.exists(pdf_path):
        result["error"] = "Файл не найден"
        return result

    # 1. Анализ через pdfplumber (если доступен)
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result["metadata"]["num_pages"] = len(pdf.pages)
                result["metadata"]["info"] = pdf.metadata or {}

                # Анализ текста
                full_text = []
                text_by_page = []

                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text() or ""
                    full_text.append(page_text)
                    text_by_page.append(
                        {
                            "page": page_num,
                            "char_count": len(page_text),
                            "word_count": len(page_text.split()),
                            "has_text": len(page_text.strip()) > 0,
                            "sample": page_text[:100] if page_text else "",
                        }
                    )

                result["text_analysis"] = {
                    "total_characters": sum(len(t) for t in full_text),
                    "total_words": sum(len(t.split()) for t in full_text),
                    "pages_with_text": sum(1 for p in text_by_page if p["has_text"]),
                    "pages_without_text": sum(
                        1 for p in text_by_page if not p["has_text"]
                    ),
                    "avg_chars_per_page": sum(len(t) for t in full_text)
                    / len(pdf.pages)
                    if pdf.pages
                    else 0,
                    "by_page": text_by_page,
                }

                # Анализ изображений на страницах
                images_by_page = []
                for page_num, page in enumerate(pdf.pages, 1):
                    images = page.images if hasattr(page, "images") else []
                    images_by_page.append(
                        {
                            "page": page_num,
                            "image_count": len(images),
                            "has_images": len(images) > 0,
                        }
                    )

                result["image_analysis"] = {
                    "total_images": sum(p["image_count"] for p in images_by_page),
                    "pages_with_images": sum(
                        1 for p in images_by_page if p["has_images"]
                    ),
                    "by_page": images_by_page,
                }

        except Exception as e:
            result["error"] = f"Ошибка анализа через pdfplumber: {e}"
            logger.error(result["error"])

    # 2. Анализ через PyPDF2 (fallback)
    if not result.get("text_analysis") and HAS_PYPDF2:
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                result["metadata"]["num_pages"] = len(pdf_reader.pages)
                result["metadata"]["info"] = pdf_reader.metadata or {}

                full_text = []
                for page in pdf_reader.pages:
                    page_text = page.extract_text() or ""
                    full_text.append(page_text)

                result["text_analysis"] = {
                    "total_characters": sum(len(t) for t in full_text),
                    "total_words": sum(len(t.split()) for t in full_text),
                    "avg_chars_per_page": sum(len(t) for t in full_text)
                    / len(pdf_reader.pages)
                    if pdf_reader.pages
                    else 0,
                }
        except Exception as e:
            result["error"] = f"Ошибка анализа через PyPDF2: {e}"
            logger.error(result["error"])

    # 3. Определение типа PDF (сканированный или текстовый)
    text_analysis = result.get("text_analysis", {})
    avg_chars = text_analysis.get("avg_chars_per_page", 0)
    pages_with_text = text_analysis.get("pages_with_text", 0)
    total_pages = result["metadata"].get("num_pages", 0)

    result["scanned_detection"] = {
        "avg_chars_per_page": avg_chars,
        "threshold": 50,  # Порог для определения сканированного PDF
        "is_likely_scanned": avg_chars < 50,
        "is_definitely_scanned": avg_chars < 10,
        "text_coverage": (pages_with_text / total_pages * 100)
        if total_pages > 0
        else 0,
        "confidence": "high"
        if avg_chars < 10
        else ("medium" if avg_chars < 50 else "low"),
    }

    # 4. Попытка извлечь изображения (если pdf2image доступен)
    if HAS_PDF2IMAGE:
        try:
            images = convert_from_path(
                pdf_path, dpi=150, first_page=1, last_page=min(3, total_pages)
            )
            result["image_analysis"]["can_extract_images"] = True
            result["image_analysis"]["sample_pages_extracted"] = len(images)
            result["image_analysis"]["sample_dpi"] = 150

            # Анализ первого изображения
            if images:
                img = images[0]
                result["image_analysis"]["sample_image"] = {
                    "size": img.size,
                    "mode": img.mode,
                    "format": img.format,
                }
        except Exception as e:
            error_msg = str(e).lower()
            if "poppler" in error_msg or "page count" in error_msg:
                result["image_analysis"]["can_extract_images"] = False
                result["image_analysis"]["error"] = "poppler_not_installed"
            else:
                result["image_analysis"]["can_extract_images"] = False
                result["image_analysis"]["error"] = str(e)

    # 5. Рекомендации
    recommendations = []

    if not HAS_PDFPLUMBER:
        recommendations.append(
            "Установите pdfplumber для лучшего анализа: pip install pdfplumber"
        )

    if result["scanned_detection"]["is_likely_scanned"]:
        if not HAS_PDF2IMAGE:
            recommendations.append(
                "PDF похож на сканированный. Установите pdf2image: pip install pdf2image"
            )
        elif not result["image_analysis"].get("can_extract_images"):
            recommendations.append(
                "PDF похож на сканированный, но poppler не установлен. См. INSTALL_POPPLER.md"
            )
        if not HAS_TESSERACT:
            recommendations.append(
                "PDF похож на сканированный. Установите pytesseract: pip install pytesseract"
            )

    if avg_chars > 50:
        recommendations.append("PDF содержит достаточно текста, OCR не требуется")

    result["recommendations"] = recommendations

    return result


def test_ocr_pipeline(pdf_path: str, languages: str = "rus+eng") -> Dict[str, Any]:
    """
    Тестирование OCR конвейера для PDF

    Returns:
        Результаты тестирования OCR
    """
    result = {
        "pdf_path": pdf_path,
        "languages": languages,
        "can_convert": False,
        "can_ocr": False,
        "pages_processed": 0,
        "total_chars_extracted": 0,
        "errors": [],
    }

    if not HAS_PDF2IMAGE:
        result["errors"].append("pdf2image не установлен")
        return result

    if not HAS_TESSERACT:
        result["errors"].append("pytesseract не установлен")
        return result

    try:
        # Попытка конвертации
        images = convert_from_path(
            pdf_path, dpi=300, first_page=1, last_page=1
        )  # Только первая страница для теста
        result["can_convert"] = True
        result["pages_processed"] = len(images)

        if images:
            # Тест OCR на первой странице
            try:
                text = pytesseract.image_to_string(images[0], lang=languages)
                result["can_ocr"] = True
                result["total_chars_extracted"] = len(text)
                result["sample_text"] = text[:200]  # Первые 200 символов
            except Exception as e:
                result["errors"].append(f"Ошибка OCR: {e}")

    except Exception as e:
        error_msg = str(e).lower()
        if "poppler" in error_msg or "page count" in error_msg:
            result["errors"].append("poppler не установлен или не найден в PATH")
        else:
            result["errors"].append(f"Ошибка конвертации: {e}")

    return result


def diagnose_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Комплексная диагностика PDF файла

    Returns:
        Полный отчет о диагностике
    """
    logger.info(f"Начинаю диагностику PDF: {pdf_path}")

    # 1. Анализ структуры
    structure = analyze_pdf_structure(pdf_path)

    # 2. Тест OCR (если PDF похож на сканированный)
    ocr_test = {}
    if structure.get("scanned_detection", {}).get("is_likely_scanned"):
        logger.info("PDF похож на сканированный, тестирую OCR...")
        ocr_test = test_ocr_pipeline(pdf_path)

    # 3. Формируем итоговый отчет
    report = {
        "file": {
            "path": pdf_path,
            "size_mb": structure.get("file_size", 0) / (1024 * 1024),
            "exists": os.path.exists(pdf_path),
        },
        "structure_analysis": structure,
        "ocr_test": ocr_test,
        "summary": {
            "pdf_type": "scanned"
            if structure.get("scanned_detection", {}).get("is_likely_scanned")
            else "text",
            "can_process_with_ocr": ocr_test.get("can_ocr", False)
            if ocr_test
            else False,
            "needs_ocr": structure.get("scanned_detection", {}).get(
                "is_likely_scanned", False
            ),
            "ready_for_processing": True,
        },
    }

    # Определяем готовность к обработке
    if structure.get("scanned_detection", {}).get("is_likely_scanned"):
        if not ocr_test.get("can_ocr", False):
            report["summary"]["ready_for_processing"] = False
            report["summary"]["blocking_issue"] = (
                "OCR недоступен для сканированного PDF"
            )

    return report


def print_diagnostic_report(report: Dict[str, Any]):
    """
    Выводит диагностический отчет в читаемом формате
    """
    print("=" * 80)
    print("PDF ДИАГНОСТИЧЕСКИЙ ОТЧЕТ")
    print("=" * 80)
    print(f"\nФайл: {report['file']['path']}")
    print(f"Размер: {report['file']['size_mb']:.2f} МБ")
    print(f"Существует: {'Да' if report['file']['exists'] else 'Нет'}")

    structure = report.get("structure_analysis", {})
    scanned = structure.get("scanned_detection", {})
    text_analysis = structure.get("text_analysis", {})

    print("\n" + "-" * 80)
    print("АНАЛИЗ СТРУКТУРЫ PDF")
    print("-" * 80)
    print(f"Страниц: {structure.get('metadata', {}).get('num_pages', 'N/A')}")
    print(f"Среднее символов на страницу: {scanned.get('avg_chars_per_page', 0):.1f}")
    print(f"Всего символов: {text_analysis.get('total_characters', 0)}")
    print(f"Всего слов: {text_analysis.get('total_words', 0)}")
    print(f"Страниц с текстом: {text_analysis.get('pages_with_text', 0)}")

    print("\n" + "-" * 80)
    print("ОПРЕДЕЛЕНИЕ ТИПА PDF")
    print("-" * 80)
    pdf_type = "СКАНИРОВАННЫЙ" if scanned.get("is_likely_scanned") else "ТЕКСТОВЫЙ"
    print(f"Тип: {pdf_type}")
    print(f"Уверенность: {scanned.get('confidence', 'unknown')}")
    print(f"Порог: {scanned.get('threshold', 50)} символов/страницу")

    if report.get("ocr_test"):
        ocr_test = report["ocr_test"]
        print("\n" + "-" * 80)
        print("ТЕСТ OCR")
        print("-" * 80)
        print(f"Может конвертировать: {'Да' if ocr_test.get('can_convert') else 'Нет'}")
        print(f"Может выполнить OCR: {'Да' if ocr_test.get('can_ocr') else 'Нет'}")
        print(f"Символов извлечено: {ocr_test.get('total_chars_extracted', 0)}")
        if ocr_test.get("errors"):
            print(f"Ошибки: {', '.join(ocr_test['errors'])}")

    print("\n" + "-" * 80)
    print("РЕКОМЕНДАЦИИ")
    print("-" * 80)
    recommendations = structure.get("recommendations", [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("Рекомендаций нет. PDF готов к обработке.")

    print("\n" + "-" * 80)
    print("ИТОГОВЫЙ СТАТУС")
    print("-" * 80)
    summary = report.get("summary", {})
    print(f"Тип PDF: {summary.get('pdf_type', 'unknown')}")
    print(f"Требуется OCR: {'Да' if summary.get('needs_ocr') else 'Нет'}")
    print(f"OCR доступен: {'Да' if summary.get('can_process_with_ocr') else 'Нет'}")
    print(
        f"Готов к обработке: {'Да' if summary.get('ready_for_processing') else 'Нет'}"
    )
    if not summary.get("ready_for_processing"):
        print(f"Проблема: {summary.get('blocking_issue', 'Неизвестная')}")

    print("=" * 80)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python pdf_diagnostics.py <путь_к_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    report = diagnose_pdf(pdf_path)
    print_diagnostic_report(report)
