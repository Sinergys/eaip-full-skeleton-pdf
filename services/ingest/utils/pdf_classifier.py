"""
Модуль предварительной классификации типа PDF
Определяет тип PDF (текстовый/изображение) ДО начала парсинга
Решает проблему неэффективной обработки сканированных документов
"""

import logging
import os
import subprocess
from typing import Dict, Any, Literal

logger = logging.getLogger(__name__)

# Импорты с проверкой доступности
try:
    import PyPDF2

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    logger.warning("PyPDF2 не установлен. Классификация PDF будет ограничена.")

try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    logger.warning("pdfplumber не установлен. Классификация PDF будет ограничена.")


def check_java_available() -> bool:
    """
    Проверяет наличие Java Runtime Environment в системе

    Returns:
        True если Java доступна, False иначе
    """
    try:
        result = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def classify_pdf_type(file_path: str) -> Dict[str, Any]:
    """
    Предварительная классификация типа PDF (текстовый/изображение)
    Выполняется ДО начала парсинга для оптимизации процесса

    Args:
        file_path: Путь к PDF файлу

    Returns:
        Словарь с информацией о типе PDF:
        {
            "type": "text_based" | "image_based" | "hybrid" | "unknown",
            "confidence": "high" | "medium" | "low",
            "text_ratio": float,  # Доля текстового контента (0-1)
            "estimated_pages": int,
            "metadata": dict
        }
    """
    result = {
        "type": "unknown",
        "confidence": "low",
        "text_ratio": 0.0,
        "estimated_pages": 0,
        "metadata": {},
    }

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return result

    # Метод 1: Быстрая проверка через PyPDF2 (самый быстрый)
    if HAS_PYPDF2:
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                result["estimated_pages"] = num_pages
                result["metadata"] = pdf_reader.metadata or {}

                if num_pages == 0:
                    result["type"] = "unknown"
                    result["confidence"] = "high"
                    return result

                # Быстрая проверка первых 3 страниц
                sample_pages = min(3, num_pages)
                total_text_chars = 0
                pages_with_text = 0

                for i in range(sample_pages):
                    try:
                        page = pdf_reader.pages[i]
                        page_text = page.extract_text() or ""
                        text_length = len(page_text.strip())
                        total_text_chars += text_length
                        if text_length > 10:  # Порог для "есть текст"
                            pages_with_text += 1
                    except Exception as e:
                        logger.debug(f"Ошибка при чтении страницы {i + 1}: {e}")
                        continue

                # Расчет метрик
                avg_chars_per_page = (
                    total_text_chars / sample_pages if sample_pages > 0 else 0
                )
                text_ratio = pages_with_text / sample_pages if sample_pages > 0 else 0
                result["text_ratio"] = text_ratio

                # Классификация на основе метрик
                if avg_chars_per_page > 100 and text_ratio > 0.7:
                    result["type"] = "text_based"
                    result["confidence"] = "high"
                elif avg_chars_per_page < 20 and text_ratio < 0.3:
                    result["type"] = "image_based"
                    result["confidence"] = "high"
                elif avg_chars_per_page > 50 and text_ratio > 0.5:
                    result["type"] = "text_based"
                    result["confidence"] = "medium"
                elif avg_chars_per_page < 50 and text_ratio < 0.5:
                    result["type"] = "image_based"
                    result["confidence"] = "medium"
                else:
                    result["type"] = "hybrid"
                    result["confidence"] = "medium"

                logger.info(
                    f"Классификация PDF (PyPDF2): type={result['type']}, "
                    f"confidence={result['confidence']}, "
                    f"avg_chars={avg_chars_per_page:.1f}, "
                    f"text_ratio={text_ratio:.2f}"
                )

                # Если уверенность высокая, возвращаем результат
                if result["confidence"] == "high":
                    return result

        except Exception as e:
            logger.warning(f"Ошибка при классификации через PyPDF2: {e}")

    # Метод 2: Более точная проверка через pdfplumber (если PyPDF2 не дал высокой уверенности)
    if HAS_PDFPLUMBER and result["confidence"] != "high":
        try:
            with pdfplumber.open(file_path) as pdf:
                num_pages = len(pdf.pages)
                if num_pages == 0:
                    return result

                result["estimated_pages"] = num_pages

                # Проверяем больше страниц для точности
                sample_pages = min(5, num_pages)
                total_text_chars = 0
                pages_with_text = 0
                total_objects = 0
                image_objects = 0

                for i in range(sample_pages):
                    try:
                        page = pdf.pages[i]
                        page_text = page.extract_text() or ""
                        text_length = len(page_text.strip())
                        total_text_chars += text_length

                        if text_length > 10:
                            pages_with_text += 1

                        # Проверяем объекты на странице
                        try:
                            # pdfplumber может дать доступ к объектам страницы
                            if hasattr(page, "chars") and page.chars:
                                total_objects += len(page.chars)
                            if hasattr(page, "images") and page.images:
                                image_objects += len(page.images)
                        except (AttributeError, TypeError):
                            # Игнорируем ошибки доступа к атрибутам страницы
                            pass

                    except Exception as e:
                        logger.debug(
                            f"Ошибка при чтении страницы {i + 1} через pdfplumber: {e}"
                        )
                        continue

                avg_chars_per_page = (
                    total_text_chars / sample_pages if sample_pages > 0 else 0
                )
                text_ratio = pages_with_text / sample_pages if sample_pages > 0 else 0
                result["text_ratio"] = text_ratio

                # Улучшенная классификация с учетом объектов
                if avg_chars_per_page > 100 and text_ratio > 0.8:
                    result["type"] = "text_based"
                    result["confidence"] = "high"
                elif avg_chars_per_page < 15 and text_ratio < 0.2:
                    result["type"] = "image_based"
                    result["confidence"] = "high"
                elif image_objects > total_objects * 0.5 and avg_chars_per_page < 30:
                    result["type"] = "image_based"
                    result["confidence"] = "medium"
                elif avg_chars_per_page > 50:
                    result["type"] = "text_based"
                    result["confidence"] = "medium"
                else:
                    result["type"] = "hybrid"
                    result["confidence"] = "medium"

                logger.info(
                    f"Классификация PDF (pdfplumber): type={result['type']}, "
                    f"confidence={result['confidence']}, "
                    f"avg_chars={avg_chars_per_page:.1f}, "
                    f"text_ratio={text_ratio:.2f}, "
                    f"images={image_objects}/{total_objects}"
                )

        except Exception as e:
            logger.warning(f"Ошибка при классификации через pdfplumber: {e}")

    return result


def get_pdf_processing_strategy(
    pdf_classification: Dict[str, Any],
) -> Literal["text_first", "ocr_first", "hybrid"]:
    """
    Определяет стратегию обработки PDF на основе классификации

    Args:
        pdf_classification: Результат classify_pdf_type()

    Returns:
        "text_first" - сначала текстовые парсеры, потом OCR
        "ocr_first" - сразу OCR для сканированных документов
        "hybrid" - комбинированный подход
    """
    pdf_type = pdf_classification.get("type", "unknown")
    confidence = pdf_classification.get("confidence", "low")

    if pdf_type == "image_based" and confidence in ["high", "medium"]:
        return "ocr_first"
    elif pdf_type == "text_based" and confidence in ["high", "medium"]:
        return "text_first"
    else:
        return "hybrid"
