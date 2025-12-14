"""
Word Document Validation Endpoint.
Handles file upload and validation orchestration.
"""
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
import aiofiles

from core.config import settings
from core.models import CheckReportResponse
from core.constants import ALLOWED_EXTENSIONS, ProcessingStatus
from utils.exceptions import (
    FileValidationError,
    FileSizeError,
    FileFormatError,
)
from utils.helpers import (
    calculate_file_hash,
    sanitize_filename,
    validate_file_extension,
    format_file_size,
)
from services.orchestrator import OrchestratorService
from db.cache import CacheManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
cache_manager = CacheManager(settings.DATABASE_URL)


@router.post("/check-report/", response_model=CheckReportResponse)
async def check_report(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
) -> CheckReportResponse:
    """
    Endpoint для автоматической проверки отчёта энергоаудита.
    
    Соответствует разделу 4.2 ТЗ.
    
    Args:
        file: DOCX файл для проверки
        background_tasks: Фоновые задачи для cleanup
    
    Returns:
        CheckReportResponse с результатами обработки
    
    Raises:
        HTTPException: При ошибках валидации или обработки
    """
    start_time = None
    temp_file_path: Optional[Path] = None
    
    try:
        import time
        start_time = time.time()
        
        # ============ Шаг 1: Валидация формата (3.1.2) ============
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Имя файла не указано"
            )
        
        if not validate_file_extension(file.filename, ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail="Файл не может быть обработан. Убедитесь, что загружаемый файл в формате DOCX, содержащий редактируемый текст (не отсканированное изображение)."
            )
        
        # ============ Шаг 2: Чтение и валидация размера ============
        file_content = await file.read()
        file_size = len(file_content)
        
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Файл слишком большой ({format_file_size(file_size)}). Максимальный размер: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        logger.info(
            f"Получен файл: {file.filename}, "
            f"размер: {format_file_size(file_size)}"
        )
        
        # ============ Шаг 3: Расчёт хеша для кеширования ============
        # Сохраняем во временный файл для расчёта хеша
        temp_filename = f"{uuid.uuid4()}_{sanitize_filename(file.filename)}"
        temp_file_path = settings.TEMP_DIR / temp_filename
        
        async with aiofiles.open(temp_file_path, 'wb') as buffer:
            await buffer.write(file_content)
        
        file_hash = calculate_file_hash(temp_file_path)
        logger.info(f"Хеш файла: {file_hash[:16]}...")
        
        # ============ Шаг 4: Проверка кеша ============
        cached_result = await cache_manager.get(file_hash)
        
        if cached_result:
            logger.info(f"Результат найден в кеше: {cached_result}")
            
            # Cleanup временного файла в фоне
            if background_tasks:
                background_tasks.add_task(
                    _cleanup_temp_file,
                    temp_file_path
                )
            
            processing_time = time.time() - start_time if start_time else 0
            
            return CheckReportResponse(
                message="Результат получен из кеша",
                file_path=cached_result,
                from_cache=True,
                processing_time_seconds=round(processing_time, 2),
                file_hash=file_hash
            )
        
        # ============ Шаг 5: Запуск обработки ============
        logger.info("Кеш не найден, начинаю обработку...")
        
        orchestrator = OrchestratorService(settings)
        
        result_file_path = await orchestrator.process_report(
            file_path=str(temp_file_path),
            file_hash=file_hash,
            original_filename=file.filename
        )
        
        # ============ Шаг 6: Сохранение в кеш ============
        await cache_manager.set(
            file_hash=file_hash,
            result_path=result_file_path,
            original_filename=file.filename,
            file_size=file_size
        )
        
        # ============ Шаг 7: Cleanup временных файлов ============
        if background_tasks:
            background_tasks.add_task(
                _cleanup_temp_file,
                temp_file_path
            )
        
        processing_time = time.time() - start_time if start_time else 0
        
        logger.info(
            f"Обработка завершена успешно за {processing_time:.2f}с, "
            f"результат: {result_file_path}"
        )
        
        return CheckReportResponse(
            message="Обработка завершена",
            file_path=result_file_path,
            from_cache=False,
            processing_time_seconds=round(processing_time, 2),
            file_hash=file_hash
        )
    
    except FileValidationError as e:
        logger.error(f"Ошибка валидации файла: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except FileSizeError as e:
        logger.error(f"Файл слишком большой: {e}")
        raise HTTPException(status_code=413, detail=str(e))
    
    except FileFormatError as e:
        logger.error(f"Неверный формат файла: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Внутренняя ошибка обработки: {e}", exc_info=True)
        
        # Cleanup при ошибке
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Ошибка cleanup: {cleanup_error}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка обработки: {str(e)}"
        )


async def _cleanup_temp_file(file_path: Path) -> None:
    """
    Фоновая задача для удаления временного файла.
    
    Args:
        file_path: Путь к файлу для удаления
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Удалён временный файл: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка удаления временного файла {file_path}: {e}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint для мониторинга.
    
    Returns:
        Статус сервиса
    """
    return {
        "service": "word-validator",
        "status": "ok",
        "cache_enabled": settings.CACHE_ENABLED,
        "deepseek_configured": bool(settings.DEEPSEEK_API_KEY),
        "ollama_url": settings.OLLAMA_URL
    }
