"""
Классификатор типа предприятия на основе анализа загруженных файлов.
"""
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Словарь ключевых слов для определения отрасли
INDUSTRY_KEYWORDS = {
    "энергетика": [
        "энерг", "электро", "тэс", "гэс", "энерго", "энергоснабж",
        "энергоаудит", "энергобаланс", "энергопотребление"
    ],
    "химия": [
        "хими", "азот", "навоийазот", "химическ", "удобрен",
        "аммиак", "нитрат", "химическ"
    ],
    "металлургия": [
        "металл", "сталь", "железо", "чугун", "прокат",
        "металлург", "сталевар"
    ],
    "нефтепереработка": [
        "нефть", "нефте", "нефтепереработ", "нефтепродукт",
        "бензин", "дизель", "мазут"
    ],
    "машиностроение": [
        "машин", "оборудование", "станок", "механизм",
        "машиностроен"
    ],
    "пищевая": [
        "пищев", "продукт", "молоко", "мясо", "хлеб",
        "консерв", "переработка"
    ],
}

# Словарь типов предприятий по отраслям
ENTERPRISE_TYPES = {
    "энергетика": ["ТЭС", "ГЭС", "АЭС", "ТЭЦ", "Энергокомпания"],
    "химия": ["Химический завод", "Завод удобрений", "Химический комбинат"],
    "металлургия": ["Металлургический завод", "Сталелитейный завод"],
    "нефтепереработка": ["НПЗ", "Нефтеперерабатывающий завод"],
    "машиностроение": ["Машиностроительный завод", "Завод оборудования"],
    "пищевая": ["Пищевой комбинат", "Мясокомбинат", "Молочный завод"],
}

# Словарь типов продукции по отраслям
PRODUCT_TYPES = {
    "энергетика": ["электроэнергия", "теплоэнергия"],
    "химия": ["азотные удобрения", "химическая продукция", "аммиак"],
    "металлургия": ["сталь", "прокат", "металлопродукция"],
    "нефтепереработка": ["бензин", "дизельное топливо", "мазут"],
    "машиностроение": ["оборудование", "машины", "механизмы"],
    "пищевая": ["пищевая продукция", "молочная продукция", "мясная продукция"],
}


def analyze_filenames(filenames: List[str], enterprise_name: str) -> Dict[str, float]:
    """
    Анализирует названия файлов для определения отрасли.
    Учитывает контекст: файлы про само предприятие vs файлы про потребителей.
    
    Args:
        filenames: Список названий файлов
        enterprise_name: Название предприятия
    
    Returns:
        Словарь с количеством упоминаний каждой отрасли (с весами)
    """
    industry_counts = {industry: 0.0 for industry in INDUSTRY_KEYWORDS.keys()}
    enterprise_name_lower = enterprise_name.lower()
    
    # Ключевые слова, указывающие на файлы про ПОТРЕБИТЕЛЕЙ (не про само предприятие)
    consumer_keywords = ["ташкари", "внешн", "потребител", "клиент", "заказчик"]
    
    # Ключевые слова, указывающие на файлы про САМО предприятие
    self_keywords = ["энергопаспорт", "баланс", "отчет", "реализация", "продаж", "выработк"]
    
    for filename in filenames:
        filename_lower = filename.lower()
        
        # Определяем тип файла: про само предприятие или про потребителей
        is_consumer_file = any(kw in filename_lower for kw in consumer_keywords)
        is_self_file = any(kw in filename_lower for kw in self_keywords)
        
        # Вес файла: файлы про само предприятие важнее
        weight = 2.0 if is_self_file else (0.5 if is_consumer_file else 1.0)
        
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    # Дополнительная проверка: если файл про потребителя и отрасль не совпадает с названием предприятия
                    if is_consumer_file and industry != "энергетика":
                        # Уменьшаем вес для отраслей потребителей
                        industry_counts[industry] += weight * 0.3
                    else:
                        industry_counts[industry] += weight
                    break  # Одно упоминание на файл
    
    return industry_counts


def determine_industry(filenames: List[str], enterprise_name: str) -> Optional[str]:
    """
    Определяет отрасль предприятия на основе анализа названий файлов и названия предприятия.
    
    Args:
        filenames: Список названий файлов
        enterprise_name: Название предприятия
    
    Returns:
        Название отрасли или None
    """
    if not filenames:
        return None
    
    enterprise_name_lower = enterprise_name.lower()
    
    # ПРИОРИТЕТ 1: Анализ названия предприятия
    # Если в названии есть явные указания на отрасль - используем их
    if any(kw in enterprise_name_lower for kw in ["тэс", "гэс", "аэс", "тэц", "энерго", "электростанция"]):
        logger.info(f"Определена отрасль 'энергетика' по названию предприятия '{enterprise_name}'")
        return "энергетика"
    
    if any(kw in enterprise_name_lower for kw in ["химическ", "азот", "химзавод"]):
        logger.info(f"Определена отрасль 'химия' по названию предприятия '{enterprise_name}'")
        return "химия"
    
    # ПРИОРИТЕТ 2: Анализ файлов (с учетом контекста)
    industry_counts = analyze_filenames(filenames, enterprise_name)
    
    # Находим отрасль с максимальным количеством упоминаний
    max_count = max(industry_counts.values())
    if max_count == 0:
        return None
    
    # Если есть несколько отраслей с одинаковым количеством, выбираем первую
    for industry, count in industry_counts.items():
        if count == max_count:
            logger.info(
                f"Определена отрасль '{industry}' на основе {count:.1f} взвешенных упоминаний в {len(filenames)} файлах"
            )
            return industry
    
    return None


def determine_enterprise_type(industry: Optional[str], enterprise_name: str) -> Optional[str]:
    """
    Определяет тип предприятия на основе отрасли и названия.
    
    Args:
        industry: Отрасль предприятия
        enterprise_name: Название предприятия
    
    Returns:
        Тип предприятия или None
    """
    if not industry:
        return None
    
    name_lower = enterprise_name.lower()
    
    # Проверяем название предприятия на специфические типы
    if industry == "энергетика":
        if "тэс" in name_lower or "теплоэлектростанция" in name_lower:
            return "ТЭС"
        elif "гэс" in name_lower or "гидроэлектростанция" in name_lower:
            return "ГЭС"
        elif "аэс" in name_lower or "атомная" in name_lower:
            return "АЭС"
        elif "тэц" in name_lower:
            return "ТЭЦ"
        else:
            return ENTERPRISE_TYPES.get(industry, ["Энергокомпания"])[0]
    
    # Для других отраслей используем первый тип из списка
    types = ENTERPRISE_TYPES.get(industry)
    if types:
        return types[0]
    
    return None


def determine_product_type(industry: Optional[str]) -> Optional[str]:
    """
    Определяет тип продукции на основе отрасли.
    
    Args:
        industry: Отрасль предприятия
    
    Returns:
        Тип продукции или None
    """
    if not industry:
        return None
    
    product_types = PRODUCT_TYPES.get(industry)
    if product_types:
        return product_types[0]  # Возвращаем первый тип продукции
    
    return None


def classify_enterprise(
    enterprise_name: str,
    filenames: List[str],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Классифицирует предприятие: определяет отрасль, тип предприятия и тип продукции.
    
    Args:
        enterprise_name: Название предприятия
        filenames: Список названий загруженных файлов
    
    Returns:
        Кортеж (industry, enterprise_type, product_type)
    """
    industry = determine_industry(filenames, enterprise_name)
    enterprise_type = determine_enterprise_type(industry, enterprise_name)
    product_type = determine_product_type(industry)
    
    return industry, enterprise_type, product_type

