from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PassportSectionMapping:
    """
    Declarative mapping for a passport section.
    Example: which canonical resources feed 'Структура пр 2' or 'Баланс'.
    """

    section_name: str
    required_resources: List[str] = field(
        default_factory=list
    )  # e.g., ["electricity", "gas", "water", "heat"]
    optional_resources: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class PassportFieldMap:
    """
    Top-level field map describing how CanonicalSourceData populates the ПКМ 690 template.
    This is design-first and will be expanded in subsequent iterations.
    """

    sections: Dict[str, PassportSectionMapping] = field(default_factory=dict)


def get_default_passport_field_map() -> PassportFieldMap:
    """
    Default mapping sketch for ПКМ 690 sections.
    """
    return PassportFieldMap(
        sections={
            "Структура пр 2": PassportSectionMapping(
                section_name="Структура пр 2",
                required_resources=["electricity", "gas", "water", "heat"],
                notes="Structure by resource shares (quarterly/annual).",
            ),
            "Баланс": PassportSectionMapping(
                section_name="Баланс",
                required_resources=[
                    "electricity",
                    "gas",
                    "water",
                    "heat",
                    "fuel",
                    "coal",
                ],
                notes="Balance of resources and uses.",
            ),
            "Динамика ср": PassportSectionMapping(
                section_name="Динамика ср",
                required_resources=["electricity", "gas", "water", "heat"],
                notes="Time series dynamics per resource.",
            ),
            "мазут,уголь 5": PassportSectionMapping(
                section_name="мазут,уголь 5",
                required_resources=["fuel", "coal"],
            ),
            "Расход на ед.п": PassportSectionMapping(
                section_name="Расход на ед.п",
                required_resources=["electricity", "gas", "water", "heat"],
            ),
            "Узел учета": PassportSectionMapping(
                section_name="Узел учета",
                required_resources=[],
                notes="Feeds from canonical nodes list.",
            ),
            "Equipment": PassportSectionMapping(
                section_name="Equipment",
                required_resources=[],
                notes="Feeds from canonical equipment list.",
            ),
        }
    )


@dataclass(frozen=True)
class UsageCategory:
    """
    Usage category for electricity breakdown expected by Balance sheet.
    """

    id: str
    description: str
    template_key: str  # key name expected by fill_balans_sheet by_usage mapping


# Minimal set aligned with fill_balans_sheet expectations
DEFAULT_ELECTRICITY_USAGE_CATEGORIES: List[UsageCategory] = [
    UsageCategory(
        id="technological",
        description="Technological consumption",
        template_key="technological",
    ),
    UsageCategory(
        id="own_needs", description="Own needs (aux)", template_key="own_needs"
    ),
    UsageCategory(
        id="production", description="Production/general", template_key="production"
    ),
    UsageCategory(id="household", description="Household", template_key="household"),
]

# Constants for usage category IDs (single source of truth)
ELECTRICITY_USAGE_TECH = "technological"
ELECTRICITY_USAGE_OWN = "own_needs"
ELECTRICITY_USAGE_PROD = "production"
ELECTRICITY_USAGE_HOUSEHOLD = "household"

# Configuration: keywords mapping for usage classification
# This is the single source of truth for keyword-based classification
ELECTRICITY_USAGE_KEYWORDS: Dict[str, List[str]] = {
    ELECTRICITY_USAGE_TECH: [
        # RU keywords
        "технолог",
        "технологический",
        "технология",
        "агрегат",
        "аппарат",
        "насос технологический",
        "технологический насос",
        "компрессор технологический",
        "технологический компрессор",
        "печь",
        "печной",
        "печная",
        "реактор",
        "сушилка",
        "экструдер",
        "станок технологический",
        "технологический станок",
        "линия технологическая",
        "технологическая линия",
        # UZ keywords (if needed)
        "texnologik",
        "texnologiya",
    ],
    ELECTRICITY_USAGE_OWN: [
        # RU keywords
        "собственные нужды",
        "с.н.",
        "собств. нужды",
        "собственные нужды",
        "котельная",
        "котел",
        "котёл",
        "котельная собственных нужд",
        "подстанция",
        "тп",
        "тп-",
        "трансформатор",
        "насос котельной",
        "котельная насос",
        "вентиляция общеобменная",
        "освещение производственное",
        # UZ keywords
        "kotelxona",
        "podstansiya",
    ],
    ELECTRICITY_USAGE_PROD: [
        # RU keywords
        "производств",
        "производственный",
        "цех",
        "цех №",
        "цех-",
        "участок",
        "участок №",
        "линия производственная",
        "производственная линия",
        "конвейер",
        "станок",
        "станок производственный",
        "механизм",
        # UZ keywords
        "sex",
        "uchastok",
        "konveyer",
    ],
    ELECTRICITY_USAGE_HOUSEHOLD: [
        # RU keywords
        "хоз-быт",
        "хозбыт",
        "хозяйственно-бытовые",
        "бытовые",
        "быт",
        "офис",
        "офисный",
        "административный",
        "админ",
        "администрация",
        "административный корпус",
        "склад",
        "склад готовой продукции",
        "раздевалка",
        "душ",
        "санузел",
        "освещение бытовое",
        "освещение офисное",
        "кондиционер офисный",
        "офисный кондиционер",
        # UZ keywords
        "ofis",
        "ombor",
        "idora",
    ],
}

# Possible column names in RU/UZ that might contain usage category
ELECTRICITY_USAGE_COLUMN_MAP: List[str] = [
    "назначение",
    "purpose",
    "maqsad",
    "категория",
    "category",
    "kategoriya",
    "usage_category",
    "usage",
    "использование",
    "примечание",
    "notes",
    "eslatma",
]

# Priority order for classification when multiple categories match
# Higher priority = checked first
USAGE_CLASSIFICATION_PRIORITY: List[str] = [
    ELECTRICITY_USAGE_TECH,  # Highest priority
    ELECTRICITY_USAGE_OWN,
    ELECTRICITY_USAGE_PROD,
    ELECTRICITY_USAGE_HOUSEHOLD,  # Lowest priority
]
