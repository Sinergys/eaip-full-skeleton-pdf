"""
Модуль интеграции OCR в процесс импорта данных
ЭТАП 3: Интеграция в процесс импорта
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from pdf2image import convert_from_path
from PIL import Image

from .gemini_vision_ocr import extract_with_gemini_vision
from .ocr_data_adapter import (
    find_energy_tables_in_ocr,
    identify_resource_type,
    identify_period_type,
    extract_dates_from_table,
    extract_values_from_table,
    convert_to_aggregator_format,
    validate_aggregator_data
)

logger = logging.getLogger(__name__)


def process_pdf_with_ocr(
    pdf_path: str,
    batch_id: str,
    debug_dir: Optional[Path] = None,
    save_debug: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Обрабатывает PDF файл через OCR и преобразует в формат агрегатора.
    
    БЛОК 3.1: Обработка PDF через OCR
    
    Args:
        pdf_path: Путь к PDF файлу
        batch_id: ID загрузки
        debug_dir: Директория для сохранения отладочных файлов
        save_debug: Сохранять ли отладочные данные
    
    Returns:
        Словарь в формате агрегатора или None при ошибке
    """
    if not Path(pdf_path).exists():
        logger.error(f"PDF файл не найден: {pdf_path}")
        return None
    
    try:
        logger.info(f"🔍 Обработка PDF через OCR: {Path(pdf_path).name}")
        
        # Конвертируем PDF в изображения (только первая страница для начала)
        images = convert_from_path(str(pdf_path), dpi=200, first_page=1, last_page=1)
        if not images:
            logger.error(f"Не удалось конвертировать PDF в изображение: {pdf_path}")
            return None
        
        # Сохраняем изображение во временный файл
        temp_image_path = Path(pdf_path).parent / f"temp_ocr_{batch_id}.png"
        images[0].save(temp_image_path, 'PNG')
        
        # Применяем OCR
        ocr_result = extract_with_gemini_vision(str(temp_image_path), page_num=1, skip_adaptive_retry=False)
        
        # Удаляем временный файл (с обработкой ошибок блокировки)
        try:
            if temp_image_path.exists():
                # Пробуем закрыть файл, если он открыт
                import time
                time.sleep(0.1)  # Небольшая задержка для освобождения файла
                temp_image_path.unlink()
        except (PermissionError, OSError) as e:
            # Если файл занят, пробуем удалить позже или просто пропускаем
            logger.warning(f"Не удалось удалить временный файл {temp_image_path}: {e}. Файл будет удалён позже.")
            # Можно добавить в очередь на удаление или просто оставить
        
        if not ocr_result or ocr_result.get("error"):
            logger.error(f"Ошибка OCR: {ocr_result.get('error', 'unknown')}")
            return None
        
        # Находим таблицы с данными энергоресурсов
        found_tables = find_energy_tables_in_ocr(ocr_result)
        
        if not found_tables:
            logger.warning(f"Таблицы с данными энергоресурсов не найдены в {Path(pdf_path).name}")
            return None
        
        # Обрабатываем каждую найденную таблицу
        aggregated_resources = {}
        
        for table_info in found_tables:
            table = table_info["table"]
            resource_type = identify_resource_type(table, table_info.get("resource_type"))
            period_type = identify_period_type(table)
            
            # Извлекаем даты и значения
            dates_data = extract_dates_from_table(table, period_type)
            values_data = extract_values_from_table(table, resource_type)
            
            # Преобразуем в формат агрегатора
            aggregator_data = convert_to_aggregator_format(
                dates_data, values_data, resource_type, period_type
            )
            
            # Валидируем данные
            validation_result = validate_aggregator_data(aggregator_data)
            
            if not validation_result.get("is_valid"):
                logger.warning(
                    f"Данные не прошли валидацию для {resource_type}: "
                    f"{len(validation_result.get('errors', []))} ошибок"
                )
            
            # Объединяем данные по типам ресурсов
            for res_type, res_data in aggregator_data.items():
                if res_type not in aggregated_resources:
                    aggregated_resources[res_type] = {}
                aggregated_resources[res_type].update(res_data)
        
        # Формируем результат в формате агрегатора
        result = {
            "resources": aggregated_resources,
            "generated_at": datetime.now().isoformat(),
            "source": {
                "type": "ocr",
                "file_path": str(pdf_path),  # Преобразуем Path в строку
                "batch_id": batch_id,
                "confidence": ocr_result.get("confidence", 0.0),
                "tables_count": ocr_result.get("tables_count", 0)
            }
        }
        
        # Сохраняем отладочные данные
        if save_debug and debug_dir:
            debug_dir.mkdir(parents=True, exist_ok=True)
            
            # Сохраняем результаты OCR
            ocr_debug_file = debug_dir / f"{batch_id}_ocr_result.json"
            with open(ocr_debug_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "batch_id": batch_id,
                    "pdf_path": pdf_path,
                    "ocr_result": ocr_result,
                    "found_tables": [
                        {
                            "resource_type": t.get("resource_type"),
                            "confidence_score": t.get("confidence_score"),
                            "table_index": t.get("table_index")
                        }
                        for t in found_tables
                    ],
                    "aggregated": result,
                    "timestamp": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Отладочные данные сохранены: {ocr_debug_file}")
        
        logger.info(f"✅ PDF обработан успешно: {len(aggregated_resources)} типов ресурсов")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка обработки PDF через OCR: {e}")
        return None


def save_debug_data(
    data: Dict[str, Any],
    batch_id: str,
    resource_type: str,
    debug_dir: Path,
    operation: str = "unknown"
) -> Optional[Path]:
    """
    Сохраняет отладочные данные.
    
    БЛОК 3.2: Сохранение отладочных данных
    
    Args:
        data: Данные для сохранения
        batch_id: ID загрузки
        resource_type: Тип ресурса
        debug_dir: Директория для сохранения
        operation: Название операции
    
    Returns:
        Путь к сохранённому файлу или None
    """
    try:
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        debug_file = debug_dir / f"{batch_id}_{resource_type}_{operation}_debug.json"
        
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump({
                "batch_id": batch_id,
                "resource_type": resource_type,
                "operation": operation,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Отладочные данные сохранены: {debug_file}")
        return debug_file
        
    except Exception as e:
        logger.warning(f"Не удалось сохранить отладочные данные: {e}")
        return None


def log_execution_step(
    batch_id: str,
    step: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
    log_file: Optional[Path] = None
):
    """
    Логирует шаг выполнения в execution_log.jsonl.
    
    БЛОК 3.2: Логирование процесса
    
    Args:
        batch_id: ID загрузки
        step: Название шага
        status: Статус (success, error, warning)
        details: Дополнительные детали
        log_file: Путь к файлу лога
    """
    try:
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "batch_id": batch_id,
                "step": step,
                "status": status,
                "details": details or {}
            }
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
            logger.debug(f"Лог записан: {step} ({status})")
        
    except Exception as e:
        logger.warning(f"Не удалось записать лог: {e}")

