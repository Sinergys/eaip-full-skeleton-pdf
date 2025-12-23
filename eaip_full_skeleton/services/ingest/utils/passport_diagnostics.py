"""
Диагностика и расширенное логирование для генерации энергопаспорта
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

# Флаг verbose debug режима
DEBUG_MODE = os.getenv("ENERGY_PASSPORT_DEBUG", "false").lower() == "true"


@dataclass
class FieldDiagnostic:
    """Диагностическая информация о поле"""

    field_name: str
    sheet_name: str
    cell_reference: Optional[str] = None
    source: Optional[str] = None
    value: Any = None
    calculated: bool = False
    skipped: bool = False
    skip_reason: Optional[str] = None
    formula_used: Optional[str] = None
    normative_ref: Optional[str] = None


@dataclass
class SheetDiagnostic:
    """Диагностическая информация о листе"""

    sheet_name: str
    fields_filled: int = 0
    fields_skipped: int = 0
    fields_calculated: int = 0
    fields: List[FieldDiagnostic] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class PassportGenerationDiagnostic:
    """Полная диагностическая информация о генерации паспорта"""

    batch_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    sheets: List[SheetDiagnostic] = field(default_factory=list)
    total_fields_filled: int = 0
    total_fields_skipped: int = 0
    total_fields_calculated: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def duration_seconds(self) -> Optional[float]:
        """Продолжительность генерации в секундах"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class PassportDiagnostics:
    """
    Класс для сбора диагностической информации при генерации энергопаспорта
    """

    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.diagnostic = PassportGenerationDiagnostic(
            batch_id=batch_id, start_time=datetime.now()
        )
        self.current_sheet: Optional[SheetDiagnostic] = None

    def start_sheet(self, sheet_name: str) -> None:
        """Начать обработку листа"""
        if self.current_sheet:
            self.diagnostic.sheets.append(self.current_sheet)

        self.current_sheet = SheetDiagnostic(sheet_name=sheet_name)

        if DEBUG_MODE:
            logger.debug(f"[DIAG] Начало заполнения листа: {sheet_name}")

    def end_sheet(self) -> None:
        """Завершить обработку листа"""
        if self.current_sheet:
            self.diagnostic.sheets.append(self.current_sheet)

            if DEBUG_MODE:
                logger.debug(
                    f"[DIAG] Лист '{self.current_sheet.sheet_name}' завершен: "
                    f"заполнено={self.current_sheet.fields_filled}, "
                    f"пропущено={self.current_sheet.fields_skipped}, "
                    f"рассчитано={self.current_sheet.fields_calculated}"
                )

            self.current_sheet = None

    def log_field_filled(
        self,
        field_name: str,
        value: Any,
        cell_reference: Optional[str] = None,
        source: Optional[str] = None,
    ) -> None:
        """Логировать заполнение поля"""
        if not self.current_sheet:
            return

        field_diag = FieldDiagnostic(
            field_name=field_name,
            sheet_name=self.current_sheet.sheet_name,
            cell_reference=cell_reference,
            source=source,
            value=value,
            calculated=False,
        )

        self.current_sheet.fields.append(field_diag)
        self.current_sheet.fields_filled += 1
        self.diagnostic.total_fields_filled += 1

        if DEBUG_MODE:
            logger.debug(
                f"[DIAG] Заполнено поле '{field_name}' в {cell_reference or 'неизвестной ячейке'}: "
                f"значение={value}, источник={source}"
            )

    def log_field_calculated(
        self,
        field_name: str,
        value: Any,
        formula: str,
        cell_reference: Optional[str] = None,
        normative_ref: Optional[str] = None,
    ) -> None:
        """Логировать расчетное поле"""
        if not self.current_sheet:
            return

        field_diag = FieldDiagnostic(
            field_name=field_name,
            sheet_name=self.current_sheet.sheet_name,
            cell_reference=cell_reference,
            value=value,
            calculated=True,
            formula_used=formula,
            normative_ref=normative_ref,
        )

        self.current_sheet.fields.append(field_diag)
        self.current_sheet.fields_calculated += 1
        self.diagnostic.total_fields_calculated += 1

        if DEBUG_MODE:
            logger.debug(
                f"[DIAG] Рассчитано поле '{field_name}' в {cell_reference or 'неизвестной ячейке'}: "
                f"значение={value}, формула={formula}"
            )

    def log_field_skipped(
        self, field_name: str, reason: str, cell_reference: Optional[str] = None
    ) -> None:
        """Логировать пропущенное поле"""
        if not self.current_sheet:
            return

        field_diag = FieldDiagnostic(
            field_name=field_name,
            sheet_name=self.current_sheet.sheet_name,
            cell_reference=cell_reference,
            skipped=True,
            skip_reason=reason,
        )

        self.current_sheet.fields.append(field_diag)
        self.current_sheet.fields_skipped += 1
        self.diagnostic.total_fields_skipped += 1

        if DEBUG_MODE:
            logger.warning(
                f"[DIAG] Пропущено поле '{field_name}' в {cell_reference or 'неизвестной ячейке'}: "
                f"причина={reason}"
            )

    def log_error(self, message: str, sheet_name: Optional[str] = None) -> None:
        """Логировать ошибку"""
        self.diagnostic.errors.append(message)

        if (
            sheet_name
            and self.current_sheet
            and self.current_sheet.sheet_name == sheet_name
        ):
            self.current_sheet.errors.append(message)

        logger.error(f"[DIAG] Ошибка: {message}")

    def log_warning(self, message: str, sheet_name: Optional[str] = None) -> None:
        """Логировать предупреждение"""
        self.diagnostic.warnings.append(message)

        if (
            sheet_name
            and self.current_sheet
            and self.current_sheet.sheet_name == sheet_name
        ):
            self.current_sheet.warnings.append(message)

        logger.warning(f"[DIAG] Предупреждение: {message}")

    def finish(self) -> Dict[str, Any]:
        """Завершить сбор диагностики и вернуть отчет"""
        if self.current_sheet:
            self.diagnostic.sheets.append(self.current_sheet)
            self.current_sheet = None

        self.diagnostic.end_time = datetime.now()

        # Формируем отчет
        report = {
            "batch_id": self.batch_id,
            "duration_seconds": self.diagnostic.duration_seconds(),
            "summary": {
                "total_fields_filled": self.diagnostic.total_fields_filled,
                "total_fields_skipped": self.diagnostic.total_fields_skipped,
                "total_fields_calculated": self.diagnostic.total_fields_calculated,
                "total_errors": len(self.diagnostic.errors),
                "total_warnings": len(self.diagnostic.warnings),
            },
            "sheets": [
                {
                    "sheet_name": sheet.sheet_name,
                    "fields_filled": sheet.fields_filled,
                    "fields_skipped": sheet.fields_skipped,
                    "fields_calculated": sheet.fields_calculated,
                    "errors": sheet.errors,
                    "warnings": sheet.warnings,
                }
                for sheet in self.diagnostic.sheets
            ],
            "errors": self.diagnostic.errors,
            "warnings": self.diagnostic.warnings,
        }

        # Логируем итоговую сводку
        logger.info(
            f"[DIAG] Генерация завершена для batch_id={self.batch_id}: "
            f"заполнено={self.diagnostic.total_fields_filled}, "
            f"пропущено={self.diagnostic.total_fields_skipped}, "
            f"рассчитано={self.diagnostic.total_fields_calculated}, "
            f"ошибок={len(self.diagnostic.errors)}, "
            f"предупреждений={len(self.diagnostic.warnings)}"
        )

        return report


def create_diagnostics(batch_id: str) -> PassportDiagnostics:
    """Создать экземпляр диагностики"""
    return PassportDiagnostics(batch_id)
