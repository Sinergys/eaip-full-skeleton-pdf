"""
Модуль валидации агрегированных данных перед заполнением шаблона паспорта.

Проверяет:
- Корректность структуры данных
- Наличие обязательных полей
- Валидность значений (типы, диапазоны, отсутствие отрицательных значений)
- Целостность данных (соответствие кварталов, сумм)
"""

import logging
from typing import Dict, List, Any, Tuple, Set

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Исключение для ошибок валидации данных"""

    pass


class DataValidator:
    """Валидатор агрегированных данных для паспорта"""

    # Допустимые годы
    VALID_YEARS = [2022, 2023, 2024, 2025]

    # Допустимые кварталы
    VALID_QUARTERS = [1, 2, 3, 4]

    # Обязательные поля для каждого ресурса по типам
    REQUIRED_FIELDS = {
        "electricity": {
            "quarter_totals": ["active_kwh", "reactive_kvarh"],
        },
        "gas": {
            "quarter_totals": ["volume_m3", "cost_sum"],
        },
        "water": {
            "quarter_totals": ["volume_m3", "cost_sum"],
        },
        "production": {
            "quarter_totals": [],  # Может быть любой продукт
        },
        "fuel": {
            "quarter_totals": ["volume_ton"],
        },
        "coal": {
            "quarter_totals": ["volume_ton"],
        },
        "heat": {
            "quarter_totals": ["volume_gcal"],
        },
    }

    def __init__(self, aggregated_data: Dict[str, Any]):
        """
        Инициализация валидатора.

        Args:
            aggregated_data: Агрегированные данные в формате:
                {
                    "resources": {
                        "electricity": {
                            "2022-Q1": {
                                "year": 2022,
                                "quarter": 1,
                                "months": [...],
                                "quarter_totals": {...}
                            }
                        },
                        ...
                    }
                }
        """
        self.aggregated_data = aggregated_data
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.resources_data = aggregated_data.get("resources", {}) or aggregated_data

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Выполняет полную валидацию данных.

        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # 1. Проверка структуры данных
        self._validate_structure()

        # 2. Проверка каждого ресурса
        for resource_name, resource_data in self.resources_data.items():
            if not isinstance(resource_data, dict):
                continue
            self._validate_resource(resource_name, resource_data)

        # 3. Проверка целостности данных
        self._validate_data_integrity()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_structure(self) -> None:
        """Проверяет базовую структуру данных"""
        if not self.resources_data:
            self.errors.append("Отсутствуют данные о ресурсах (resources)")
            return

        if not isinstance(self.resources_data, dict):
            self.errors.append("Данные о ресурсах должны быть словарем")
            return

        # Проверяем наличие хотя бы одного ресурса с данными
        has_data = any(
            resource_data and isinstance(resource_data, dict) and len(resource_data) > 0
            for resource_data in self.resources_data.values()
        )

        if not has_data:
            self.warnings.append("Нет данных ни по одному ресурсу")

    def _validate_resource(
        self, resource_name: str, resource_data: Dict[str, Any]
    ) -> None:
        """Проверяет данные конкретного ресурса"""
        if not isinstance(resource_data, dict):
            return

        # Проверяем каждый квартал
        for quarter_key, quarter_data in resource_data.items():
            if not isinstance(quarter_data, dict):
                continue

            # Валидация формата ключа квартала
            if not self._validate_quarter_key(quarter_key):
                self.errors.append(
                    f"Неверный формат ключа квартала '{quarter_key}' для ресурса '{resource_name}'"
                )
                continue

            # Валидация структуры квартала
            self._validate_quarter_structure(resource_name, quarter_key, quarter_data)

            # Валидация значений квартала
            self._validate_quarter_values(resource_name, quarter_key, quarter_data)

    def _validate_quarter_key(self, quarter_key: str) -> bool:
        """Проверяет формат ключа квартала (например, '2022-Q1')"""
        if not isinstance(quarter_key, str):
            return False

        if "-Q" not in quarter_key:
            return False

        try:
            year_str, quarter_str = quarter_key.split("-Q")
            year = int(year_str)
            quarter = int(quarter_str)

            if year not in self.VALID_YEARS:
                return False
            if quarter not in self.VALID_QUARTERS:
                return False

            return True
        except (ValueError, AttributeError):
            return False

    def _validate_quarter_structure(
        self, resource_name: str, quarter_key: str, quarter_data: Dict[str, Any]
    ) -> None:
        """Проверяет структуру данных квартала"""
        # Проверяем обязательные поля
        year = quarter_data.get("year")
        quarter = quarter_data.get("quarter")

        if year is None or not isinstance(year, int):
            self.errors.append(
                f"Отсутствует или неверный 'year' для {resource_name}/{quarter_key}"
            )

        if quarter is None or not isinstance(quarter, int):
            self.errors.append(
                f"Отсутствует или неверный 'quarter' для {resource_name}/{quarter_key}"
            )

        # Проверяем соответствие ключа квартала и данных
        if year and quarter:
            expected_key = f"{year}-Q{quarter}"
            if quarter_key != expected_key:
                self.warnings.append(
                    f"Несоответствие ключа квартала '{quarter_key}' и данных (year={year}, quarter={quarter}) "
                    f"для ресурса '{resource_name}'"
                )

        # Проверяем наличие quarter_totals
        quarter_totals = quarter_data.get("quarter_totals")
        if not isinstance(quarter_totals, dict):
            self.errors.append(
                f"Отсутствует 'quarter_totals' для {resource_name}/{quarter_key}"
            )
        else:
            # Проверяем обязательные поля для ресурса
            resource_fields = self.REQUIRED_FIELDS.get(resource_name, {})
            if isinstance(resource_fields, dict):
                required_fields = resource_fields.get("quarter_totals", [])
            else:
                required_fields = []
            for field in required_fields:
                if field not in quarter_totals or quarter_totals[field] is None:
                    self.warnings.append(
                        f"Отсутствует обязательное поле '{field}' в quarter_totals для {resource_name}/{quarter_key}"
                    )

    def _validate_quarter_values(
        self, resource_name: str, quarter_key: str, quarter_data: Dict[str, Any]
    ) -> None:
        """Проверяет валидность значений квартала"""
        quarter_totals = quarter_data.get("quarter_totals", {})

        if not isinstance(quarter_totals, dict):
            return

        # Проверяем все числовые значения
        for field_name, value in quarter_totals.items():
            if value is None:
                continue

            # Проверяем тип значения
            if not isinstance(value, (int, float)):
                self.warnings.append(
                    f"Поле '{field_name}' для {resource_name}/{quarter_key} имеет нечисловой тип: {type(value).__name__}"
                )
                continue

            # Проверяем на отрицательные значения (кроме cost, который может быть отрицательным)
            if (
                value < 0
                and "cost" not in field_name.lower()
                and "loss" not in field_name.lower()
            ):
                self.errors.append(
                    f"Отрицательное значение поля '{field_name}' ({value}) для {resource_name}/{quarter_key}"
                )

            # Проверяем на нереалистично большие значения
            if abs(value) > 1e12:  # 1 триллион
                self.warnings.append(
                    f"Подозрительно большое значение поля '{field_name}' ({value}) для {resource_name}/{quarter_key}"
                )

        # Проверяем месяцы, если они есть
        months = quarter_data.get("months", [])
        if months:
            if not isinstance(months, list):
                self.warnings.append(
                    f"Поле 'months' для {resource_name}/{quarter_key} должно быть списком"
                )
            else:
                # Проверяем количество месяцев в квартале
                if len(months) > 3:
                    self.warnings.append(
                        f"Квартал {quarter_key} содержит {len(months)} месяцев (ожидается 3)"
                    )

    def _validate_data_integrity(self) -> None:
        """Проверяет целостность данных между ресурсами"""
        # Собираем все кварталы из всех ресурсов
        all_quarters: Set[str] = set()
        for resource_data in self.resources_data.values():
            if isinstance(resource_data, dict):
                all_quarters.update(resource_data.keys())

        if not all_quarters:
            return

        # Проверяем консистентность кварталов (все ресурсы должны иметь одинаковые кварталы)
        # Это предупреждение, а не ошибка, т.к. некоторые ресурсы могут быть неполными
        quarter_counts: Dict[str, List[str]] = {}
        for resource_name, resource_data in self.resources_data.items():
            if isinstance(resource_data, dict):
                quarters = set(resource_data.keys())
                for quarter in quarters:
                    quarter_counts.setdefault(quarter, []).append(resource_name)

        # Проверяем, есть ли ресурсы с сильно отличающимся набором кварталов
        if len(quarter_counts) > 0:
            max_count = max(len(resources) for resources in quarter_counts.values())
            min_count = min(len(resources) for resources in quarter_counts.values())

            if max_count - min_count > 2:  # Разница больше 2 ресурсов
                self.warnings.append(
                    f"Несоответствие количества кварталов между ресурсами: "
                    f"минимум {min_count}, максимум {max_count} ресурсов на квартал"
                )


def validate_aggregated_data(
    aggregated_data: Dict[str, Any],
) -> Tuple[bool, List[str], List[str]]:
    """
    Удобная функция для валидации агрегированных данных.

    Args:
        aggregated_data: Агрегированные данные для валидации

    Returns:
        Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)

    Example:
        >>> data = {"resources": {"electricity": {"2022-Q1": {...}}}}
        >>> is_valid, errors, warnings = validate_aggregated_data(data)
        >>> if not is_valid:
        ...     print("Ошибки:", errors)
    """
    validator = DataValidator(aggregated_data)
    return validator.validate()


def validate_data_for_template(
    aggregated_data: Dict[str, Any], raise_on_error: bool = False
) -> Tuple[bool, List[str], List[str]]:
    """
    Валидирует данные перед заполнением шаблона.
    Если raise_on_error=True, выбрасывает исключение при наличии ошибок.

    Args:
        aggregated_data: Агрегированные данные
        raise_on_error: Выбрасывать исключение при ошибках

    Returns:
        Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)

    Raises:
        DataValidationError: Если raise_on_error=True и есть ошибки
    """
    is_valid, errors, warnings = validate_aggregated_data(aggregated_data)

    if not is_valid and raise_on_error:
        error_message = "Ошибки валидации данных:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        if warnings:
            error_message += "\n\nПредупреждения:\n" + "\n".join(
                f"  - {w}" for w in warnings
            )
        raise DataValidationError(error_message)

    return is_valid, errors, warnings
