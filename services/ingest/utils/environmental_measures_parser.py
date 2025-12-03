"""
Парсер для извлечения плана экологических мероприятий из отчётов (ПДВ, ПДС и др.)
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Ключевые слова для поиска раздела с мероприятиями
MEASURES_KEYWORDS = [
    "план мероприятий",
    "мероприятия",
    "рекомендации",
    "предложения",
    "меры",
    "экологические мероприятия",
    "мероприятия по снижению",
    "план работ",
    "программа мероприятий",
]

# Паттерны для извлечения мероприятий
MEASURE_PATTERNS = [
    re.compile(r"(\d+)[\.\)]\s*(.+?)(?=\d+[\.\)]|$)", re.DOTALL | re.IGNORECASE),
    re.compile(r"[-•]\s*(.+?)(?=[-•]|$)", re.DOTALL | re.IGNORECASE),
    re.compile(r"([А-ЯЁ][^.!?]+[.!?])", re.MULTILINE),
]

# Ключевые слова для определения типа мероприятия
MEASURE_TYPE_KEYWORDS = {
    "emission_reduction": [
        "снижение выбросов",
        "уменьшение выбросов",
        "очистка выбросов",
        "фильтр",
        "пылеулавливание",
        "газоочистка",
    ],
    "discharge_reduction": [
        "снижение сбросов",
        "очистка сточных вод",
        "очистные сооружения",
        "биологическая очистка",
        "механическая очистка",
    ],
    "monitoring": [
        "мониторинг",
        "контроль",
        "измерение",
        "учёт",
        "наблюдение",
    ],
    "equipment": [
        "модернизация",
        "замена оборудования",
        "установка",
        "реконструкция",
    ],
    "management": [
        "организационные",
        "управление",
        "нормирование",
        "документация",
    ],
}


def is_environmental_document(filename: str, raw_json: Optional[Dict[str, Any]] = None) -> bool:
    """
    Проверяет, является ли файл экологическим документом (ПДВ, ПДС и т.д.).

    Args:
        filename: Имя файла
        raw_json: Распарсенные данные файла (опционально)

    Returns:
        True если файл содержит экологические данные
    """
    filename_lower = filename.lower()
    environmental_keywords = [
        "пдв",
        "пдс",
        "экологи",
        "выброс",
        "сброс",
        "environmental",
        "emission",
        "discharge",
    ]
    
    if any(keyword in filename_lower for keyword in environmental_keywords):
        return True
    
    # Проверка содержимого, если доступно
    if raw_json:
        extracted_text = raw_json.get("extracted_text", "")
        if extracted_text:
            text_lower = extracted_text.lower()
            if any(keyword in text_lower for keyword in environmental_keywords):
                return True
    
    return False


def parse_environmental_measures(
    text: str,
    source_file: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Извлекает план экологических мероприятий из текста документа.

    Args:
        text: Текст документа
        source_file: Путь к исходному файлу (опционально)

    Returns:
        Словарь с извлеченными мероприятиями
    """
    measures: List[Dict[str, Any]] = []
    
    # Поиск раздела с мероприятиями
    measures_section = _find_measures_section(text)
    
    if not measures_section:
        logger.warning("Раздел с мероприятиями не найден в документе")
        return {
            "source": source_file or "unknown",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "measures": [],
            "summary": {
                "total_measures": 0,
            },
        }
    
    # Извлечение мероприятий из раздела
    measures = _extract_measures_from_text(measures_section)
    
    # Определение типов мероприятий
    for measure in measures:
        measure["type"] = _classify_measure_type(measure.get("name", ""))
    
    return {
        "source": source_file or "unknown",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "measures": measures,
        "summary": {
            "total_measures": len(measures),
            "by_type": _count_by_type(measures),
        },
    }


def _find_measures_section(text: str) -> Optional[str]:
    """Находит раздел документа с мероприятиями"""
    text_lower = text.lower()
    
    # Поиск заголовка раздела
    for keyword in MEASURES_KEYWORDS:
        # Ищем заголовок (может быть в разных форматах)
        patterns = [
            rf"{keyword}[^\n]*\n",
            rf"{keyword}[^\n]*:",
            rf"{keyword}[^\n]*\.",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Извлекаем текст после заголовка (до следующего заголовка или конца)
                start_pos = match.end()
                # Ищем следующий заголовок (обычно начинается с цифры или заглавной буквы)
                next_section = re.search(
                    r"\n\s*\d+[\.\)]\s*[А-ЯЁ]|\n\s*[А-ЯЁ]{2,}",
                    text[start_pos:],
                    re.MULTILINE,
                )
                
                if next_section:
                    end_pos = start_pos + next_section.start()
                    section = text[start_pos:end_pos].strip()
                else:
                    section = text[start_pos:].strip()
                
                if len(section) > 50:  # Минимальная длина раздела
                    return section
    
    return None


def _extract_measures_from_text(text: str) -> List[Dict[str, Any]]:
    """Извлекает список мероприятий из текста"""
    measures: List[Dict[str, Any]] = []
    
    # Разбиваем текст на предложения/пункты
    # Паттерн 1: Нумерованный список (1. ..., 2. ..., и т.д.)
    numbered_pattern = re.compile(r"(\d+)[\.\)]\s*([^\n]+(?:\n(?!\d+[\.\)])[^\n]+)*)", re.MULTILINE)
    matches = numbered_pattern.findall(text)
    
    if matches:
        for order, content in matches:
            measure = _parse_measure_item(content.strip(), int(order))
            if measure:
                measures.append(measure)
    
    # Если не нашли нумерованный список, пробуем маркированный
    if not measures:
        bullet_pattern = re.compile(r"[-•]\s*([^\n]+(?:\n(?![-•])[^\n]+)*)", re.MULTILINE)
        matches = bullet_pattern.findall(text)
        
        for idx, content in enumerate(matches, 1):
            measure = _parse_measure_item(content.strip(), idx)
            if measure:
                measures.append(measure)
    
    # Если всё ещё нет мероприятий, разбиваем по предложениям
    if not measures:
        sentences = re.split(r"[.!?]\s+", text)
        for idx, sentence in enumerate(sentences, 1):
            sentence = sentence.strip()
            if len(sentence) > 20:  # Минимальная длина
                measure = _parse_measure_item(sentence, idx)
                if measure:
                    measures.append(measure)
    
    return measures


def _parse_measure_item(text: str, order: int) -> Optional[Dict[str, Any]]:
    """Парсит отдельное мероприятие из текста"""
    if not text or len(text) < 10:
        return None
    
    # Очистка текста
    text = re.sub(r"\s+", " ", text).strip()
    
    # Извлечение названия (первое предложение или до определённых маркеров)
    name_match = re.match(r"^([^.:]+?)(?:[.:]|$)", text)
    name = name_match.group(1).strip() if name_match else text[:100]
    
    # Извлечение описания (остальной текст)
    description = text[len(name):].strip()
    if description.startswith(":"):
        description = description[1:].strip()
    
    # Попытка извлечь сроки, стоимость и другие параметры
    deadline = _extract_deadline(text)
    cost = _extract_cost(text)
    responsible = _extract_responsible(text)
    
    return {
        "order": order,
        "name": name,
        "description": description if description else None,
        "deadline": deadline,
        "cost": cost,
        "responsible": responsible,
        "status": "planned",  # По умолчанию "запланировано"
    }


def _extract_deadline(text: str) -> Optional[str]:
    """Извлекает срок выполнения мероприятия"""
    patterns = [
        r"срок[^\n]*?(\d{1,2}[\./]\d{1,2}[\./]\d{2,4})",
        r"до\s+(\d{1,2}[\./]\d{1,2}[\./]\d{2,4})",
        r"(\d{4})\s+год",
        r"квартал\s+(\d)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) if match.lastindex else match.group(0)
    
    return None


def _extract_cost(text: str) -> Optional[float]:
    """Извлекает стоимость мероприятия"""
    patterns = [
        r"стоимость[^\n]*?(\d+(?:\s+\d+)*(?:[.,]\d+)?)\s*(?:тыс\.?|млн\.?)?\s*(?:сум|руб|usd|долл)",
        r"(\d+(?:\s+\d+)*(?:[.,]\d+)?)\s*(?:тыс\.?|млн\.?)?\s*(?:сум|руб|usd|долл)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(" ", "").replace(",", ".")
            try:
                value = float(value_str)
                # Проверяем, есть ли множитель (тыс., млн)
                if "млн" in match.group(0).lower():
                    value *= 1000000
                elif "тыс" in match.group(0).lower():
                    value *= 1000
                return value
            except ValueError:
                continue
    
    return None


def _extract_responsible(text: str) -> Optional[str]:
    """Извлекает ответственного за мероприятие"""
    patterns = [
        r"ответственн[^\n]*?([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)+)",
        r"выполнени[^\n]*?([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def _classify_measure_type(text: str) -> str:
    """Определяет тип мероприятия"""
    text_lower = text.lower()
    
    for measure_type, keywords in MEASURE_TYPE_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return measure_type
    
    return "other"


def _count_by_type(measures: List[Dict[str, Any]]) -> Dict[str, int]:
    """Подсчитывает мероприятия по типам"""
    counts: Dict[str, int] = {}
    for measure in measures:
        measure_type = measure.get("type", "other")
        counts[measure_type] = counts.get(measure_type, 0) + 1
    return counts


def write_environmental_measures_json(
    batch_id: str,
    measures_data: Dict[str, Any],
    destination_dir: Union[str, Path],
) -> Path:
    """
    Сохраняет план экологических мероприятий в JSON файл.

    Args:
        batch_id: ID батча
        measures_data: Данные мероприятий
        destination_dir: Директория для сохранения

    Returns:
        Путь к сохраненному файлу
    """
    destination = Path(destination_dir)
    destination.mkdir(parents=True, exist_ok=True)
    target_file = destination / f"{batch_id}_environmental_measures.json"
    target_file.write_text(
        json.dumps(measures_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return target_file

