"""
Маппинг источников данных на поля энергопаспорта
Определяет, откуда берется каждое поле паспорта и как оно заполняется
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum


class FieldType(Enum):
    """Тип поля энергопаспорта"""

    INPUT = "input"  # Входное поле (из парсеров/агрегатора)
    CALCULATED = "calculated"  # Расчетное поле (формула)
    SUMMARY = "summary"  # Итоговое поле (сумма)
    REFERENCE = "reference"  # Ссылочное поле (ссылка на другой лист)


class DataSource(Enum):
    """Источник данных"""

    AGGREGATOR = "aggregator"  # Данные из energy_aggregator
    NODES_PARSER = "nodes_parser"  # Данные из парсера узлов учета
    EQUIPMENT_PARSER = "equipment_parser"  # Данные из парсера оборудования
    ENVELOPE_PARSER = "envelope_parser"  # Данные из парсера ограждающих конструкций
    MANUAL_INPUT = "manual_input"  # Ручной ввод
    NORMATIVE_DB = "normative_db"  # Данные из БД нормативных документов
    CALCULATION = "calculation"  # Расчетное поле


@dataclass
class PassportField:
    """Описание поля энергопаспорта"""

    field_name: str  # Название поля
    sheet_name: str  # Имя листа
    cell_reference: Optional[str] = None  # Адрес ячейки (например, "C9")
    row: Optional[int] = None  # Номер строки
    column: Optional[int] = None  # Номер столбца
    field_type: FieldType = FieldType.INPUT  # Тип поля
    data_source: DataSource = DataSource.AGGREGATOR  # Источник данных
    data_path: Optional[str] = (
        None  # Путь к данным в JSON (например, "resources.electricity.2022-Q1.quarter_totals.active_kwh")
    )
    unit: Optional[str] = None  # Единица измерения
    formula: Optional[str] = None  # Формула Excel (если расчетное)
    calculation_function: Optional[str] = None  # Имя функции расчета (если есть)
    is_required: bool = False  # Обязательное поле
    default_value: Any = None  # Значение по умолчанию
    validation_rules: List[str] = field(default_factory=list)  # Правила валидации
    description: Optional[str] = None  # Описание поля
    normative_refs: List[str] = field(
        default_factory=list
    )  # Ссылки на нормативные документы


class PassportFieldMapping:
    """
    Класс для маппинга источников данных на поля энергопаспорта
    """

    def __init__(self):
        self._mappings: Dict[str, List[PassportField]] = {}
        self._init_mappings()

    def _init_mappings(self):
        """Инициализация маппингов для всех листов"""

        # === ЛИСТ "Структура пр 2" ===
        struktura_fields = [
            # Установленная мощность
            PassportField(
                field_name="Установленная электрическая мощность",
                sheet_name="Структура пр 2",
                row=7,
                column=2,
                cell_reference="B7",
                field_type=FieldType.INPUT,
                data_source=DataSource.MANUAL_INPUT,
                data_path="enterprise.installed_power_kw",
                unit="кВт",
                is_required=False,
                description="Установленная электрическая мощность предприятия",
            ),
            # Общее потребление по предприятию (квартально)
            PassportField(
                field_name="Общее потребление по предприятию - электроэнергия",
                sheet_name="Структура пр 2",
                row=9,
                field_type=FieldType.SUMMARY,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.quarter_totals.active_kwh",
                unit="кВт·ч",
                is_required=True,
                description="Общее потребление электроэнергии активной за квартал",
                validation_rules=[">= 0", "должно равняться итогу листа Баланс"],
            ),
            # Потребление по категориям (технологические нужды)
            PassportField(
                field_name="Потребление для технологических нужд",
                sheet_name="Структура пр 2",
                row=10,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.by_usage.technological",
                unit="кВт·ч",
                is_required=False,
                description="Потребление электроэнергии на технологические нужды",
            ),
            # Потребление по категориям (собственные нужды)
            PassportField(
                field_name="Потребление для собственных нужд",
                sheet_name="Структура пр 2",
                row=11,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.by_usage.own_needs",
                unit="кВт·ч",
                is_required=False,
            ),
            # Потребление по категориям (производственные нужды)
            PassportField(
                field_name="Потребление для производственных нужд",
                sheet_name="Структура пр 2",
                row=12,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.by_usage.production",
                unit="кВт·ч",
                is_required=False,
            ),
            # Потребление по категориям (хоз-бытовые нужды)
            PassportField(
                field_name="Потребление для хозяйственно-бытовых нужд",
                sheet_name="Структура пр 2",
                row=13,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.by_usage.household",
                unit="кВт·ч",
                is_required=False,
            ),
            # Газ (квартально)
            PassportField(
                field_name="Общее потребление газа",
                sheet_name="Структура пр 2",
                row=9,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.gas.{quarter}.quarter_totals.volume_m3",
                unit="м³",
                description="Потребление газа за квартал (конвертируется в тыс. м³)",
            ),
            # Вода (квартально)
            PassportField(
                field_name="Общее потребление воды",
                sheet_name="Структура пр 2",
                row=9,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.water.{quarter}.quarter_totals.volume_m3",
                unit="м³",
            ),
        ]
        self._mappings["Структура пр 2"] = struktura_fields

        # === ЛИСТ "Баланс" ===
        balans_fields = [
            PassportField(
                field_name="Технологические",
                sheet_name="Баланс",
                column=2,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.by_usage.technological",
                unit="кВт·ч",
                is_required=False,
            ),
            PassportField(
                field_name="Собственные нужды",
                sheet_name="Баланс",
                column=3,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.by_usage.own_needs",
                unit="кВт·ч",
                is_required=False,
            ),
            PassportField(
                field_name="Производственные",
                sheet_name="Баланс",
                column=4,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.by_usage.production",
                unit="кВт·ч",
                is_required=False,
            ),
            PassportField(
                field_name="Хоз-бытовые",
                sheet_name="Баланс",
                column=5,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.by_usage.household",
                unit="кВт·ч",
                is_required=False,
            ),
            PassportField(
                field_name="Итого",
                sheet_name="Баланс",
                column=6,
                field_type=FieldType.SUMMARY,
                data_source=DataSource.CALCULATION,
                formula="=SUM(B{row}:E{row})",
                calculation_function="sum_categories",
                unit="кВт·ч",
                is_required=True,
                validation_rules=[
                    "должно равняться общему потреблению из Структура пр 2"
                ],
            ),
        ]
        self._mappings["Баланс"] = balans_fields

        # === ЛИСТ "Динамика ср" ===
        dinamika_fields = [
            PassportField(
                field_name="Электроэнергия",
                sheet_name="Динамика ср",
                column=3,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.electricity.{quarter}.quarter_totals.active_kwh",
                unit="кВт·ч",
            ),
            PassportField(
                field_name="Газ",
                sheet_name="Динамика ср",
                column=4,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.gas.{quarter}.quarter_totals.volume_m3",
                unit="м³",
            ),
            PassportField(
                field_name="Вода",
                sheet_name="Динамика ср",
                column=5,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.water.{quarter}.quarter_totals.volume_m3",
                unit="м³",
            ),
            PassportField(
                field_name="Производство",
                sheet_name="Динамика ср",
                column=6,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.production.{quarter}.quarter_totals",
                unit="кг",
                description="Сумма всех значений производства за квартал",
            ),
            PassportField(
                field_name="Удельный расход",
                sheet_name="Динамика ср",
                column=7,
                field_type=FieldType.CALCULATED,
                data_source=DataSource.CALCULATION,
                formula="=IF(G{row}>0,C{row}/G{row},0)",
                calculation_function="specific_consumption_kwh_per_kg",
                unit="кВт·ч/кг",
                validation_rules=[">= 0", "если производство = 0, то расход = 0"],
                description="Удельный расход электроэнергии на единицу продукции",
            ),
        ]
        self._mappings["Динамика ср"] = dinamika_fields

        # === ЛИСТ "Расход на ед.п" ===
        specific_fields = [
            PassportField(
                field_name="Удельный расход по кварталам",
                sheet_name="Расход на ед.п",
                field_type=FieldType.CALCULATED,
                data_source=DataSource.CALCULATION,
                calculation_function="specific_consumption_kwh_per_kg",
                unit="кВт·ч/кг",
                description="Удельный расход электроэнергии на единицу продукции по кварталам",
            ),
        ]
        self._mappings["Расход на ед.п"] = specific_fields

        # === ЛИСТ "Узел учета" ===
        nodes_fields = [
            PassportField(
                field_name="Пункты учёта",
                sheet_name="Узел учета",
                column=1,
                field_type=FieldType.INPUT,
                data_source=DataSource.NODES_PARSER,
                data_path="nodes.{index}.name",
                description="Название узла учета",
            ),
            PassportField(
                field_name="Вид учёта мощности P",
                sheet_name="Узел учета",
                column=2,
                field_type=FieldType.INPUT,
                data_source=DataSource.NODES_PARSER,
                data_path="nodes.{index}.power_type",
            ),
            PassportField(
                field_name="Место установки",
                sheet_name="Узел учета",
                column=4,
                field_type=FieldType.INPUT,
                data_source=DataSource.NODES_PARSER,
                data_path="nodes.{index}.location",
            ),
            PassportField(
                field_name="Коэффициент учёта",
                sheet_name="Узел учета",
                column=5,
                field_type=FieldType.INPUT,
                data_source=DataSource.NODES_PARSER,
                data_path="nodes.{index}.coefficient",
                unit="-",
            ),
        ]
        self._mappings["Узел учета"] = nodes_fields

        # === ЛИСТ "Мериаприятия 1" ===
        measures_fields = [
            PassportField(
                field_name="Мероприятие",
                sheet_name="Мериаприятия 1",
                column=1,
                field_type=FieldType.INPUT,
                data_source=DataSource.MANUAL_INPUT,
                data_path="measures.{index}.name",
            ),
            PassportField(
                field_name="Экономия",
                sheet_name="Мериаприятия 1",
                column=2,
                field_type=FieldType.INPUT,
                data_source=DataSource.MANUAL_INPUT,
                data_path="measures.{index}.savings",
                unit="зависит от единицы измерения",
            ),
            PassportField(
                field_name="Ед. изм.",
                sheet_name="Мериаприятия 1",
                column=3,
                field_type=FieldType.INPUT,
                data_source=DataSource.MANUAL_INPUT,
                data_path="measures.{index}.unit",
            ),
            PassportField(
                field_name="Стоимость",
                sheet_name="Мериаприятия 1",
                column=4,
                field_type=FieldType.INPUT,
                data_source=DataSource.MANUAL_INPUT,
                data_path="measures.{index}.cost_usd",
                unit="USD",
            ),
            PassportField(
                field_name="Срок окупаемости",
                sheet_name="Мериаприятия 1",
                column=5,
                field_type=FieldType.CALCULATED,
                data_source=DataSource.CALCULATION,
                calculation_function="payback_period_years",
                unit="лет",
                description="Срок окупаемости мероприятия",
            ),
        ]
        self._mappings["Мериаприятия 1"] = measures_fields

        # === ЛИСТ "мазут,уголь 5" ===
        fuel_fields = [
            PassportField(
                field_name="Мазут",
                sheet_name="мазут,уголь 5",
                column=3,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.fuel.{quarter}.quarter_totals.volume_ton",
                unit="тонна",
            ),
            PassportField(
                field_name="Уголь",
                sheet_name="мазут,уголь 5",
                column=8,
                field_type=FieldType.INPUT,
                data_source=DataSource.AGGREGATOR,
                data_path="resources.coal.{quarter}.quarter_totals.volume_ton",
                unit="тонна",
            ),
        ]
        self._mappings["мазут,уголь 5"] = fuel_fields

    def get_fields_for_sheet(self, sheet_name: str) -> List[PassportField]:
        """Получить все поля для указанного листа"""
        return self._mappings.get(sheet_name, [])

    def get_field_by_name(
        self, field_name: str, sheet_name: Optional[str] = None
    ) -> Optional[PassportField]:
        """Найти поле по имени"""
        if sheet_name:
            fields = self.get_fields_for_sheet(sheet_name)
            for field_item in fields:
                if field_item.field_name == field_name:
                    return field_item
        else:
            # Поиск по всем листам
            for sheet_fields in self._mappings.values():
                for sheet_field in sheet_fields:
                    if sheet_field.field_name == field_name:
                        return sheet_field
        return None

    def get_calculated_fields(self) -> List[PassportField]:
        """Получить все расчетные поля"""
        calculated = []
        for sheet_fields in self._mappings.values():
            for sheet_field in sheet_fields:
                if sheet_field.field_type == FieldType.CALCULATED:
                    calculated.append(sheet_field)
        return calculated

    def get_required_fields(self) -> List[PassportField]:
        """Получить все обязательные поля"""
        required = []
        for sheet_fields in self._mappings.values():
            for sheet_field in sheet_fields:
                if sheet_field.is_required:
                    required.append(sheet_field)
        return required

    def get_fields_by_data_source(self, data_source: DataSource) -> List[PassportField]:
        """Получить поля по источнику данных"""
        result = []
        for sheet_fields in self._mappings.values():
            for sheet_field in sheet_fields:
                if sheet_field.data_source == data_source:
                    result.append(sheet_field)
        return result

    def build_quarter_mapping(
        self, year: str
    ) -> Dict[str, Tuple[int, int, int, int, int]]:
        """
        Построить маппинг кварталов на столбцы для листа "Структура пр 2"

        Args:
            year: Год (например, "2022")

        Returns:
            Словарь: {quarter: (start_row, elec_active_col, elec_reactive_col, gas_col, water_col)}
        """
        # Базовая структура: каждый квартал занимает блок из ~16 столбцов
        # Q1: колонки 3-16, Q2: 19-32, Q3: 35-48, Q4: 51-64

        base_col = 3  # Первый столбец данных (C)
        quarter_width = 16  # Ширина блока для квартала

        mapping = {}
        for q_num in range(1, 5):
            quarter = f"{year}-Q{q_num}"
            start_col = base_col + (q_num - 1) * quarter_width
            mapping[quarter] = (
                9,  # start_row (строка "Общее потребление")
                start_col,  # elec_active_col (активная электроэнергия)
                start_col + 1,  # elec_reactive_col (реактивная)
                start_col + 3,  # gas_col (газ, пропуская тепловую)
                start_col + 11,  # water_col (вода)
            )

        return mapping


# Глобальный экземпляр маппинга
_field_mapping = None


def get_field_mapping() -> PassportFieldMapping:
    """Получить экземпляр маппинга полей"""
    global _field_mapping
    if _field_mapping is None:
        _field_mapping = PassportFieldMapping()
    return _field_mapping
