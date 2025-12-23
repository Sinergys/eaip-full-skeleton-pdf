"""
Валидация данных перед генерацией энергопаспорта
Проверяет обязательные поля, балансы и целостность данных
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Импорт модулей
try:
    from .passport_field_mapping import get_field_mapping
    from .energy_passport_calculations import (
        validate_balance,
        sum_categories,
    )

    HAS_DEPENDENCIES = True
except ImportError as e:
    logger.warning(f"Не удалось импортировать зависимости для валидации: {e}")
    HAS_DEPENDENCIES = False


@dataclass
class ValidationError:
    """Ошибка валидации"""

    field_name: str
    sheet_name: str
    message: str
    severity: str = "error"  # error, warning


@dataclass
class ValidationResult:
    """Результат валидации"""

    is_valid: bool
    errors: List[ValidationError] = None
    warnings: List[ValidationError] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class PassportValidator:
    """
    Класс для валидации данных перед генерацией энергопаспорта
    """

    def __init__(self):
        self.field_mapping = None
        if HAS_DEPENDENCIES:
            try:
                self.field_mapping = get_field_mapping()
            except Exception as e:
                logger.warning(f"Не удалось загрузить маппинг полей: {e}")

    def validate_aggregated_data(
        self, agg_data: Dict[str, Any], required_quarters: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Валидировать агрегированные данные перед генерацией паспорта

        Args:
            agg_data: Агрегированные данные из energy_aggregator
            required_quarters: Список обязательных кварталов (опционально)

        Returns:
            ValidationResult с результатами валидации
        """
        result = ValidationResult(is_valid=True)

        if not agg_data:
            result.errors.append(
                ValidationError(
                    field_name="agg_data",
                    sheet_name="all",
                    message="Агрегированные данные отсутствуют",
                    severity="error",
                )
            )
            result.is_valid = False
            return result

        resources = agg_data.get("resources", {})
        if not resources:
            result.errors.append(
                ValidationError(
                    field_name="resources",
                    sheet_name="all",
                    message="Данные по ресурсам отсутствуют",
                    severity="error",
                )
            )
            result.is_valid = False
            return result

        # Проверка электроэнергии (обязательно)
        electricity = resources.get("electricity", {})
        if not electricity:
            result.errors.append(
                ValidationError(
                    field_name="electricity",
                    sheet_name="Структура пр 2",
                    message="Данные по электроэнергии отсутствуют (обязательное поле)",
                    severity="error",
                )
            )
            result.is_valid = False

        # Проверка кварталов
        if electricity:
            quarters = list(electricity.keys())
            if not quarters:
                result.errors.append(
                    ValidationError(
                        field_name="quarters",
                        sheet_name="Структура пр 2",
                        message="Нет данных ни за один квартал",
                        severity="error",
                    )
                )
                result.is_valid = False

            # Проверка обязательных кварталов
            if required_quarters:
                missing_quarters = [q for q in required_quarters if q not in quarters]
                if missing_quarters:
                    result.warnings.append(
                        ValidationError(
                            field_name="quarters",
                            sheet_name="Структура пр 2",
                            message=f"Отсутствуют данные за кварталы: {', '.join(missing_quarters)}",
                            severity="warning",
                        )
                    )

        # Валидация квартальных данных
        if electricity:
            for quarter, quarter_data in electricity.items():
                quarter_totals = quarter_data.get("quarter_totals", {})
                active_kwh = quarter_totals.get("active_kwh", 0)

                # Проверка отрицательных значений
                if active_kwh < 0:
                    result.errors.append(
                        ValidationError(
                            field_name=f"active_kwh_{quarter}",
                            sheet_name="Структура пр 2",
                            message=f"Отрицательное потребление электроэнергии за {quarter}: {active_kwh} кВт·ч",
                            severity="error",
                        )
                    )
                    result.is_valid = False

                # Проверка баланса категорий
                by_usage = quarter_data.get("by_usage", {})
                if by_usage:
                    category_sum = sum_categories(
                        technological=by_usage.get("technological", 0),
                        own_needs=by_usage.get("own_needs", 0),
                        production=by_usage.get("production", 0),
                        household=by_usage.get("household", 0),
                    )

                    if not validate_balance(active_kwh, category_sum, tolerance=0.01):
                        result.warnings.append(
                            ValidationError(
                                field_name=f"balance_{quarter}",
                                sheet_name="Баланс",
                                message=f"Баланс не сходится за {quarter}: общее = {active_kwh}, сумма категорий = {category_sum}",
                                severity="warning",
                            )
                        )

        # Проверка производства (для расчета удельных показателей)
        production = resources.get("production", {})
        if production:
            for quarter, quarter_data in production.items():
                prod_totals = quarter_data.get("quarter_totals", {})
                if prod_totals:
                    total_production = sum(
                        v
                        for v in prod_totals.values()
                        if isinstance(v, (int, float)) and v > 0
                    )

                    if total_production == 0:
                        # Проверяем, есть ли потребление электроэнергии
                        elec_quarter = electricity.get(quarter, {})
                        if (
                            elec_quarter
                            and elec_quarter.get("quarter_totals", {}).get(
                                "active_kwh", 0
                            )
                            > 0
                        ):
                            result.warnings.append(
                                ValidationError(
                                    field_name=f"production_{quarter}",
                                    sheet_name="Расход на ед.п",
                                    message=f"Производство отсутствует за {quarter}, но есть потребление электроэнергии. Удельный расход будет равен 0.",
                                    severity="warning",
                                )
                            )

        return result

    def validate_field_values(
        self, field_values: Dict[str, Any], sheet_name: str
    ) -> ValidationResult:
        """
        Валидировать значения полей для конкретного листа

        Args:
            field_values: Словарь значений полей
            sheet_name: Имя листа

        Returns:
            ValidationResult с результатами валидации
        """
        result = ValidationResult(is_valid=True)

        if not self.field_mapping:
            return result

        # Получаем поля для листа
        fields = self.field_mapping.get_fields_for_sheet(sheet_name)

        for field in fields:
            if field.is_required:
                field_value = field_values.get(field.field_name)

                if field_value is None or field_value == 0:
                    result.errors.append(
                        ValidationError(
                            field_name=field.field_name,
                            sheet_name=sheet_name,
                            message=f"Обязательное поле '{field.field_name}' отсутствует или равно 0",
                            severity="error",
                        )
                    )
                    result.is_valid = False

            # Проверка на отрицательные значения
            field_value = field_values.get(field.field_name)
            if isinstance(field_value, (int, float)) and field_value < 0:
                if (
                    ">= 0" in field.validation_rules
                    or "не может быть отрицательным" in field.validation_rules
                ):
                    result.errors.append(
                        ValidationError(
                            field_name=field.field_name,
                            sheet_name=sheet_name,
                            message=f"Поле '{field.field_name}' не может быть отрицательным: {field_value}",
                            severity="error",
                        )
                    )
                    result.is_valid = False

        return result

    def validate_balance_sheet(
        self, agg_data: Dict[str, Any], quarter: str
    ) -> ValidationResult:
        """
        Валидировать баланс для конкретного квартала

        Args:
            agg_data: Агрегированные данные
            quarter: Идентификатор квартала

        Returns:
            ValidationResult с результатами валидации баланса
        """
        result = ValidationResult(is_valid=True)

        resources = agg_data.get("resources", {})
        electricity = resources.get("electricity", {})

        quarter_data = electricity.get(quarter, {})
        if not quarter_data:
            result.errors.append(
                ValidationError(
                    field_name=f"quarter_data_{quarter}",
                    sheet_name="Баланс",
                    message=f"Данные за квартал {quarter} отсутствуют",
                    severity="error",
                )
            )
            result.is_valid = False
            return result

        quarter_totals = quarter_data.get("quarter_totals", {})
        total_consumption = quarter_totals.get("active_kwh", 0)

        by_usage = quarter_data.get("by_usage", {})
        if by_usage:
            category_sum = sum_categories(
                technological=by_usage.get("technological", 0),
                own_needs=by_usage.get("own_needs", 0),
                production=by_usage.get("production", 0),
                household=by_usage.get("household", 0),
            )

            if not validate_balance(total_consumption, category_sum, tolerance=0.01):
                result.errors.append(
                    ValidationError(
                        field_name=f"balance_{quarter}",
                        sheet_name="Баланс",
                        message=f"Баланс не сходится за {quarter}: общее потребление = {total_consumption}, сумма категорий = {category_sum}",
                        severity="error",
                    )
                )
                result.is_valid = False
        else:
            result.warnings.append(
                ValidationError(
                    field_name=f"by_usage_{quarter}",
                    sheet_name="Баланс",
                    message=f"Категории потребления отсутствуют за {quarter}, баланс не может быть проверен",
                    severity="warning",
                )
            )

        return result


def get_passport_validator() -> PassportValidator:
    """Получить экземпляр валидатора"""
    return PassportValidator()
