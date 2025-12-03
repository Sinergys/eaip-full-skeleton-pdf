"""
Модуль батчевой обработки документов для оптимизации производительности
"""

import logging
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Класс для батчевой обработки документов
    """

    def __init__(self, max_workers: int = 4, batch_size: int = 10):
        """
        Инициализация батч-процессора

        Args:
            max_workers: Максимальное количество параллельных воркеров
            batch_size: Размер батча для обработки
        """
        self.max_workers = max_workers
        self.batch_size = batch_size

    def process_batch(
        self,
        items: List[Any],
        processor_func: Callable[[Any], Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Обработка батча элементов

        Args:
            items: Список элементов для обработки
            processor_func: Функция обработки одного элемента
            progress_callback: Callback для отслеживания прогресса (current, total)

        Returns:
            Список результатов обработки
        """
        results = []
        total_items = len(items)

        logger.info(f"Начинаю батчевую обработку {total_items} элементов")

        start_time = time.time()

        # Разбиваем на батчи
        batches = [
            items[i : i + self.batch_size]
            for i in range(0, total_items, self.batch_size)
        ]

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Отправляем батчи на обработку
            future_to_item = {}

            for batch_idx, batch in enumerate(batches):
                for item in batch:
                    future = executor.submit(processor_func, item)
                    future_to_item[future] = item

            # Собираем результаты
            completed = 0
            for future in as_completed(future_to_item):
                completed += 1
                try:
                    result = future.result()
                    results.append(result)

                    if progress_callback:
                        progress_callback(completed, total_items)
                except Exception as e:
                    item = future_to_item[future]
                    logger.error(f"Ошибка при обработке элемента: {e}")
                    results.append({"item": item, "error": str(e), "success": False})

        elapsed_time = time.time() - start_time
        logger.info(
            f"Батчевая обработка завершена: "
            f"{total_items} элементов за {elapsed_time:.2f}с "
            f"({total_items / elapsed_time:.2f} элементов/с)"
        )

        return results

    def process_files_batch(
        self, file_paths: List[str], parse_func: Callable[[str], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Батчевая обработка файлов

        Args:
            file_paths: Список путей к файлам
            parse_func: Функция парсинга файла

        Returns:
            Список результатов парсинга
        """

        def process_file(file_path: str) -> Dict[str, Any]:
            try:
                result = parse_func(file_path)
                return {"file_path": file_path, "result": result, "success": True}
            except Exception as e:
                logger.error(f"Ошибка при обработке файла {file_path}: {e}")
                return {"file_path": file_path, "error": str(e), "success": False}

        return self.process_batch(file_paths, process_file)

    def process_ai_requests_batch(
        self, prompts: List[str], ai_func: Callable[[str], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Батчевая обработка AI-запросов

        Args:
            prompts: Список промптов
            ai_func: Функция AI-обработки

        Returns:
            Список результатов AI-обработки
        """

        def process_prompt(prompt: str) -> Dict[str, Any]:
            try:
                result = ai_func(prompt)
                return {
                    "prompt": prompt[:100],  # Обрезаем для логов
                    "result": result,
                    "success": True,
                }
            except Exception as e:
                logger.error(f"Ошибка при AI-обработке промпта: {e}")
                return {"prompt": prompt[:100], "error": str(e), "success": False}

        return self.process_batch(prompts, process_prompt)


def get_batch_processor(
    max_workers: Optional[int] = None, batch_size: Optional[int] = None
) -> BatchProcessor:
    """
    Получение экземпляра батч-процессора

    Args:
        max_workers: Максимальное количество воркеров (опционально)
        batch_size: Размер батча (опционально)

    Returns:
        Экземпляр BatchProcessor
    """
    import os

    if max_workers is None:
        max_workers = int(os.getenv("BATCH_MAX_WORKERS", "4"))

    if batch_size is None:
        batch_size = int(os.getenv("BATCH_SIZE", "10"))

    return BatchProcessor(max_workers=max_workers, batch_size=batch_size)
