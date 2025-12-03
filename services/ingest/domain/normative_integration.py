"""
Модуль интеграции проверки нормативов в процесс заполнения энергопаспорта
"""
import logging
from typing import Dict, Any, Optional, List
from openpyxl import Workbook
from openpyxl.comments import Comment

logger = logging.getLogger(__name__)

# Импорт функции проверки нормативов
try:
    from domain.normative_validator import validate_against_normative

    HAS_VALIDATOR = True
except ImportError:
    HAS_VALIDATOR = False
    logger.warning("normative_validator модуль не найден. Проверка нормативов недоступна.")


# Импорт database для логирования нарушений
try:
    import database

    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logger.warning("database модуль не найден. Логирование нарушений недоступно.")


class NormativeValidationResult:
    """Результат проверки соответствия нормативу"""

    def __init__(
        self,
        field_name: str,
        sheet_name: str,
        actual_value: float,
        status: str,
        normative_value: Optional[float] = None,
        deviation_percent: float = 0.0,
        message: str = "",
        rule: Optional[Dict[str, Any]] = None,
    ):
        self.field_name = field_name
        self.sheet_name = sheet_name
        self.actual_value = actual_value
        self.status = status  # "compliant", "violation", "below_norm", "unknown"
        self.normative_value = normative_value
        self.deviation_percent = deviation_percent
        self.message = message
        self.rule = rule

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "field_name": self.field_name,
            "sheet_name": self.sheet_name,
            "actual_value": self.actual_value,
            "status": self.status,
            "normative_value": self.normative_value,
            "deviation_percent": self.deviation_percent,
            "message": self.message,
            "rule": self.rule,
        }

    def is_violation(self) -> bool:
        """Проверить, является ли это нарушением"""
        return self.status == "violation"

    def get_comment_text(self) -> str:
        """Получить текст для комментария в Excel"""
        if self.status == "violation":
            return (
                f"⚠️ ПРЕВЫШЕНИЕ НОРМАТИВА\n"
                f"Факт: {self.actual_value}\n"
                f"Норматив: {self.normative_value}\n"
                f"Отклонение: {self.deviation_percent:.1f}%\n"
                f"{self.message}"
            )
        elif self.status == "compliant":
            return (
                f"✅ Соответствует нормативу\n"
                f"Факт: {self.actual_value}\n"
                f"Норматив: {self.normative_value}\n"
                f"Отклонение: {self.deviation_percent:.1f}%"
            )
        elif self.status == "below_norm":
            return (
                f"✅ Значение ниже норматива\n"
                f"Факт: {self.actual_value}\n"
                f"Норматив: {self.normative_value}\n"
                f"Отклонение: {self.deviation_percent:.1f}%"
            )
        else:
            return f"ℹ️ Норматив не найден для поля '{self.field_name}'"


def validate_field_value(
    field_name: str,
    actual_value: float,
    sheet_name: str,
    tolerance_percent: float = 10.0,
) -> NormativeValidationResult:
    """
    Проверить значение поля на соответствие нормативу

    Args:
        field_name: Название поля
        actual_value: Фактическое значение
        sheet_name: Имя листа
        tolerance_percent: Допустимое отклонение в процентах

    Returns:
        NormativeValidationResult с результатами проверки
    """
    if not HAS_VALIDATOR:
        return NormativeValidationResult(
            field_name=field_name,
            sheet_name=sheet_name,
            actual_value=actual_value,
            status="unknown",
            message="Модуль проверки нормативов недоступен",
        )

    try:
        validation = validate_against_normative(
            actual_value=actual_value,
            field_name=field_name,
            sheet_name=sheet_name,
            tolerance_percent=tolerance_percent,
        )

        return NormativeValidationResult(
            field_name=field_name,
            sheet_name=sheet_name,
            actual_value=actual_value,
            status=validation.get("status", "unknown"),
            normative_value=validation.get("normative"),
            deviation_percent=validation.get("deviation_percent", 0.0),
            message=validation.get("message", ""),
            rule=validation.get("rule"),
        )
    except Exception as e:
        logger.error(f"Ошибка проверки норматива для поля {field_name}: {e}")
        return NormativeValidationResult(
            field_name=field_name,
            sheet_name=sheet_name,
            actual_value=actual_value,
            status="unknown",
            message=f"Ошибка проверки: {e}",
        )


def add_validation_comment_to_cell(cell, validation_result: NormativeValidationResult):
    """
    Добавить комментарий с результатом проверки в ячейку Excel

    Args:
        cell: Ячейка openpyxl
        validation_result: Результат проверки
    """
    try:
        comment_text = validation_result.get_comment_text()
        if comment_text:
            cell.comment = Comment(comment_text, "Система проверки нормативов")
    except Exception as e:
        logger.warning(f"Не удалось добавить комментарий в ячейку {cell.coordinate}: {e}")


def log_normative_violation(
    enterprise_id: int,
    batch_id: Optional[str],
    validation_result: NormativeValidationResult,
):
    """
    Логировать нарушение норматива в БД

    Args:
        enterprise_id: ID предприятия
        batch_id: ID загрузки
        validation_result: Результат проверки
    """
    if not HAS_DATABASE:
        logger.warning("База данных недоступна, нарушение не сохранено")
        return

    if not validation_result.is_violation():
        return  # Логируем только нарушения

    try:
        # Логируем в консоль
        logger.warning(
            f"⚠️ НАРУШЕНИЕ НОРМАТИВА: {validation_result.field_name} = "
            f"{validation_result.actual_value} (норматив: {validation_result.normative_value}, "
            f"отклонение: {validation_result.deviation_percent:.1f}%)"
        )

        # Сохраняем в таблицу normative_violations
        rule_id = None
        if validation_result.rule:
            rule_id = validation_result.rule.get("id")

        database.create_normative_violation(
            enterprise_id=enterprise_id,
            batch_id=batch_id,
            field_name=validation_result.field_name,
            sheet_name=validation_result.sheet_name,
            actual_value=validation_result.actual_value,
            normative_value=validation_result.normative_value,
            deviation_percent=validation_result.deviation_percent,
            status=validation_result.status,
            message=validation_result.message,
            rule_id=rule_id,
        )

    except Exception as e:
        logger.error(f"Ошибка логирования нарушения норматива: {e}")


def validate_and_log_critical_field(
    field_name: str,
    actual_value: float,
    sheet_name: str,
    cell,
    enterprise_id: Optional[int] = None,
    batch_id: Optional[str] = None,
    tolerance_percent: float = 10.0,
    add_comment: bool = True,
) -> NormativeValidationResult:
    """
    Проверить критическое поле на соответствие нормативу и залогировать результат

    Args:
        field_name: Название поля
        actual_value: Фактическое значение
        sheet_name: Имя листа
        cell: Ячейка Excel (для добавления комментария)
        enterprise_id: ID предприятия (для логирования)
        batch_id: ID загрузки (для логирования)
        tolerance_percent: Допустимое отклонение
        add_comment: Добавить комментарий в ячейку

    Returns:
        NormativeValidationResult с результатами проверки
    """
    # Проверяем значение
    validation_result = validate_field_value(
        field_name=field_name,
        actual_value=actual_value,
        sheet_name=sheet_name,
        tolerance_percent=tolerance_percent,
    )

    # Добавляем комментарий в ячейку
    if add_comment and cell:
        add_validation_comment_to_cell(cell, validation_result)

    # Логируем нарушение
    if enterprise_id:
        log_normative_violation(enterprise_id, batch_id, validation_result)

    return validation_result


# Список критических полей для автоматической проверки
CRITICAL_FIELDS = [
    {
        "field_name": "Удельный расход",
        "sheet_name": "Динамика ср",
        "tolerance_percent": 10.0,
    },
    {
        "field_name": "Удельный расход по кварталам",
        "sheet_name": "Расход на ед.п",
        "tolerance_percent": 10.0,
    },
    # Можно добавить больше полей
]


def is_critical_field(field_name: str, sheet_name: str) -> bool:
    """Проверить, является ли поле критическим"""
    for field in CRITICAL_FIELDS:
        if field["field_name"] == field_name and field["sheet_name"] == sheet_name:
            return True
    return False

