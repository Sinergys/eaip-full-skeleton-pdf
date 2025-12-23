"""
Универсальная система отслеживания прогресса обработки файлов
Поддерживает все типы файлов и все этапы обработки
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class FileType(str, Enum):
    """Типы файлов"""

    PDF = "pdf"
    EXCEL = "excel"
    WORD = "word"
    IMAGE = "image"
    UNKNOWN = "unknown"


class ProcessingStage(str, Enum):
    """Этапы обработки файла"""

    UPLOAD = "upload"
    VALIDATION = "validation"
    PARSING = "parsing"
    OCR = "ocr"
    AI_ANALYSIS = "ai_analysis"
    SPECIALIZED_PARSING = "specialized_parsing"
    AGGREGATION = "aggregation"
    SAVING = "saving"
    COMPLETED = "completed"
    ERROR = "error"


# Веса этапов для расчета общего прогресса (в процентах)
# ВАЖНО: Сумма весов должна быть <= 100 для корректного расчета
STAGE_WEIGHTS: Dict[FileType, Dict[ProcessingStage, int]] = {
    FileType.PDF: {
        ProcessingStage.UPLOAD: 5,
        ProcessingStage.VALIDATION: 2,
        ProcessingStage.PARSING: 15,
        ProcessingStage.OCR: 50,  # OCR может занять много времени для PDF
        ProcessingStage.AI_ANALYSIS: 10,
        ProcessingStage.AGGREGATION: 5,
        ProcessingStage.SAVING: 8,
        ProcessingStage.COMPLETED: 5,
        # Итого: 100%
    },
    FileType.EXCEL: {
        ProcessingStage.UPLOAD: 5,
        ProcessingStage.VALIDATION: 2,
        ProcessingStage.PARSING: 40,
        ProcessingStage.SPECIALIZED_PARSING: 25,  # Оборудование, узлы учета и т.д.
        ProcessingStage.AGGREGATION: 15,
        ProcessingStage.SAVING: 8,
        ProcessingStage.COMPLETED: 5,
        # Итого: 100%
    },
    FileType.WORD: {
        ProcessingStage.UPLOAD: 5,
        ProcessingStage.VALIDATION: 2,
        ProcessingStage.PARSING: 60,
        ProcessingStage.AGGREGATION: 15,
        ProcessingStage.SAVING: 8,
        ProcessingStage.COMPLETED: 10,
        # Итого: 100%
    },
    FileType.IMAGE: {
        ProcessingStage.UPLOAD: 5,
        ProcessingStage.VALIDATION: 2,
        ProcessingStage.PARSING: 10,
        ProcessingStage.OCR: 60,  # OCR - основной этап для изображений
        ProcessingStage.AI_ANALYSIS: 10,
        ProcessingStage.SAVING: 8,
        ProcessingStage.COMPLETED: 5,
        # Итого: 100%
    },
    FileType.UNKNOWN: {
        ProcessingStage.UPLOAD: 10,
        ProcessingStage.VALIDATION: 10,
        ProcessingStage.PARSING: 50,
        ProcessingStage.SAVING: 20,
        ProcessingStage.COMPLETED: 10,
        # Итого: 100%
    },
}


class ProgressTracker:
    """Трекер прогресса обработки файла"""

    def __init__(self, batch_id: str, file_type: FileType):
        self.batch_id = batch_id
        self.file_type = file_type
        self.stages: Dict[ProcessingStage, Dict[str, Any]] = {}
        self.current_stage: Optional[ProcessingStage] = None
        self.overall_progress: int = 0
        self.started_at: datetime = datetime.now(timezone.utc)
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.cancelled: bool = False
        self.cancelled_at: Optional[datetime] = None

    def update_stage(
        self,
        stage: ProcessingStage,
        progress: int = 100,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Обновляет прогресс конкретного этапа

        Args:
            stage: Этап обработки
            progress: Прогресс этапа (0-100)
            message: Сообщение о текущем действии
            metadata: Дополнительные метаданные
        """
        if stage not in self.stages:
            self.stages[stage] = {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "progress": 0,
                "message": "",
                "metadata": {},
            }

        self.stages[stage]["progress"] = max(0, min(100, progress))
        self.stages[stage]["message"] = message
        if metadata:
            self.stages[stage]["metadata"].update(metadata)

        self.current_stage = stage
        self._calculate_overall_progress()

        logger.debug(
            f"Прогресс обновлен: batch_id={self.batch_id}, stage={stage.value}, "
            f"progress={progress}%, overall={self.overall_progress}%, message={message}"
        )

    def _calculate_overall_progress(self) -> None:
        """Рассчитывает общий прогресс на основе весов этапов"""
        total_progress = 0
        weights = STAGE_WEIGHTS.get(self.file_type, STAGE_WEIGHTS[FileType.UNKNOWN])

        # Проверяем, что сумма весов не превышает 100
        total_weight = sum(weights.values())
        if total_weight > 100:
            logger.warning(
                f"Сумма весов этапов для {self.file_type.value} превышает 100%: {total_weight}%"
            )

        for stage, stage_data in self.stages.items():
            if stage in weights:
                stage_weight = weights[stage]
                stage_progress = stage_data["progress"]
                total_progress += (stage_weight * stage_progress) // 100

        self.overall_progress = min(100, total_progress)

    def complete_stage(self, stage: ProcessingStage, message: str = "") -> None:
        """Завершает этап обработки"""
        self.update_stage(
            stage, progress=100, message=message or f"Этап {stage.value} завершен"
        )

    def set_error(self, stage: ProcessingStage, error_message: str) -> None:
        """Устанавливает ошибку на этапе"""
        self.current_stage = stage
        self.error_message = error_message
        self.update_stage(ProcessingStage.ERROR, progress=100, message=error_message)
        logger.error(
            f"Ошибка обработки: batch_id={self.batch_id}, stage={stage.value}, error={error_message}"
        )

    def cancel(self) -> None:
        """Отменяет обработку файла"""
        if not self.cancelled:
            self.cancelled = True
            self.cancelled_at = datetime.now(timezone.utc)
            self.update_stage(
                ProcessingStage.ERROR,
                progress=100,
                message="Обработка отменена пользователем",
            )
            logger.info(f"Обработка отменена: batch_id={self.batch_id}")

    def is_cancelled(self) -> bool:
        """Проверяет, была ли отменена обработка"""
        return self.cancelled

    def complete(self) -> None:
        """Завершает обработку файла"""
        if not self.cancelled:
            self.complete_stage(
                ProcessingStage.COMPLETED, "Обработка завершена успешно"
            )
            self.completed_at = datetime.now(timezone.utc)
            self.overall_progress = 100

    def get_status(self) -> Dict[str, Any]:
        """Возвращает текущий статус прогресса"""
        return {
            "batch_id": self.batch_id,
            "file_type": self.file_type.value,
            "overall_progress": self.overall_progress,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "stages": {
                stage.value: {
                    "progress": data["progress"],
                    "message": data["message"],
                    "started_at": data["started_at"],
                    "metadata": data.get("metadata", {}),
                }
                for stage, data in self.stages.items()
            },
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "cancelled_at": self.cancelled_at.isoformat()
            if self.cancelled_at
            else None,
            "error": self.error_message,
            "is_completed": self.completed_at is not None,
            "has_error": self.error_message is not None,
            "is_cancelled": self.cancelled,
        }


# Глобальное хранилище трекеров прогресса (в продакшене использовать Redis)
_progress_trackers: Dict[str, ProgressTracker] = {}


def get_progress_tracker(batch_id: str) -> Optional[ProgressTracker]:
    """Получает трекер прогресса по batch_id"""
    return _progress_trackers.get(batch_id)


def create_progress_tracker(batch_id: str, file_type: FileType) -> ProgressTracker:
    """Создает новый трекер прогресса"""
    tracker = ProgressTracker(batch_id, file_type)
    _progress_trackers[batch_id] = tracker
    logger.info(
        f"Создан трекер прогресса: batch_id={batch_id}, file_type={file_type.value}"
    )
    return tracker


def remove_progress_tracker(batch_id: str) -> None:
    """Удаляет трекер прогресса (после завершения обработки)"""
    if batch_id in _progress_trackers:
        del _progress_trackers[batch_id]
        logger.debug(f"Удален трекер прогресса: batch_id={batch_id}")


def update_file_processing_progress(
    batch_id: str,
    file_type: FileType,
    stage: ProcessingStage,
    progress: int = 100,
    message: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Универсальная функция для обновления прогресса обработки файла

    Args:
        batch_id: Уникальный идентификатор загрузки
        file_type: Тип файла
        stage: Этап обработки
        progress: Прогресс этапа (0-100)
        message: Сообщение о текущем действии
        metadata: Дополнительные метаданные
    """
    tracker = get_progress_tracker(batch_id)
    if not tracker:
        tracker = create_progress_tracker(batch_id, file_type)

    tracker.update_stage(stage, progress, message, metadata)
