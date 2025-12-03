"""
Модуль оптимизации использования памяти при OCR
"""

import logging
import gc
from PIL import Image

logger = logging.getLogger(__name__)


class OCRMemoryOptimizer:
    """
    Класс для оптимизации использования памяти при OCR обработке
    """

    def __init__(self, max_image_size_mb: float = 10.0):
        """
        Инициализация оптимизатора памяти

        Args:
            max_image_size_mb: Максимальный размер изображения в MB перед обработкой
        """
        self.max_image_size_mb = max_image_size_mb

    def optimize_image_for_ocr(
        self, image: Image.Image, target_dpi: int = 300, max_dimension: int = 2000
    ) -> Image.Image:
        """
        Оптимизация изображения для OCR с учетом памяти

        Args:
            image: Исходное изображение
            target_dpi: Целевой DPI (уменьшается если изображение слишком большое)
            max_dimension: Максимальный размер по любой стороне

        Returns:
            Оптимизированное изображение
        """
        # Проверяем размер изображения
        width, height = image.size
        image_size_mb = (width * height * 3) / (1024 * 1024)  # Примерный размер в MB

        logger.debug(f"Размер изображения: {width}x{height} ({image_size_mb:.2f} MB)")

        # Если изображение слишком большое, уменьшаем
        if width > max_dimension or height > max_dimension:
            scale_factor = min(max_dimension / width, max_dimension / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)

            logger.info(
                f"Уменьшаю изображение с {width}x{height} до {new_width}x{new_height} "
                f"для экономии памяти"
            )

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Конвертируем в RGB если нужно (для экономии памяти)
        if image.mode != "RGB":
            image = image.convert("RGB")

        return image

    def process_image_in_chunks(
        self,
        image: Image.Image,
        chunk_height: int = 1000,
        processor_func: callable = None,
    ) -> list:
        """
        Обработка большого изображения по частям (чанкам)

        Args:
            image: Исходное изображение
            chunk_height: Высота одного чанка
            processor_func: Функция обработки чанка

        Returns:
            Список результатов обработки чанков
        """
        if processor_func is None:
            raise ValueError("processor_func обязателен")

        width, height = image.size
        results = []

        # Разбиваем изображение на чанки
        for y in range(0, height, chunk_height):
            chunk_end = min(y + chunk_height, height)
            chunk = image.crop((0, y, width, chunk_end))

            # Обрабатываем чанк
            result = processor_func(chunk)
            results.append(result)

            # Принудительная сборка мусора после каждого чанка
            del chunk
            gc.collect()

        return results

    def cleanup_memory(self):
        """
        Принудительная очистка памяти
        """
        gc.collect()
        logger.debug("Память очищена")

    @staticmethod
    def get_image_memory_usage(image: Image.Image) -> float:
        """
        Получение примерного использования памяти изображением

        Args:
            image: Изображение

        Returns:
            Размер в MB
        """
        width, height = image.size
        channels = len(image.getbands())
        size_bytes = width * height * channels
        size_mb = size_bytes / (1024 * 1024)
        return size_mb


def get_ocr_memory_optimizer() -> OCRMemoryOptimizer:
    """
    Получение экземпляра оптимизатора памяти

    Returns:
        Экземпляр OCRMemoryOptimizer
    """
    import os

    max_size = float(os.getenv("OCR_MAX_IMAGE_SIZE_MB", "10.0"))
    return OCRMemoryOptimizer(max_image_size_mb=max_size)
