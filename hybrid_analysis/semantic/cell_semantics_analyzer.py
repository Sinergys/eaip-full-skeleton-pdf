"""
Этап 2.1: Создание семантического профиля ячеек
Понимание бизнес-смысла каждой ячейки
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import re


class CellSemanticsAnalyzer:
    """Анализатор семантики ячеек на основе правил и контекста."""
    
    # Словарь ключевых слов для определения семантики
    SEMANTIC_PATTERNS = {
        "electricity_active": {
            "keywords": ["электроэнергия", "актив", "квт·ч", "квтч", "электричество", "электр энергияси"],
            "units": ["кВт·ч", "кВтч", "тыс. кВт·ч"],
            "category": "energy_consumption",
            "resource_type": "electricity"
        },
        "electricity_reactive": {
            "keywords": ["реактив", "квар·ч", "кварч", "реактивная"],
            "units": ["кВАр·ч", "квар·ч"],
            "category": "energy_consumption",
            "resource_type": "electricity"
        },
        "gas_volume": {
            "keywords": ["газ", "природный газ", "газ объем", "газ м³"],
            "units": ["м³", "тыс. м³", "м3"],
            "category": "energy_consumption",
            "resource_type": "gas"
        },
        "water_volume": {
            "keywords": ["вода", "воды", "водоснабжение", "вода м³"],
            "units": ["м³", "м3"],
            "category": "energy_consumption",
            "resource_type": "water"
        },
        "heat_energy": {
            "keywords": ["тепловая", "тепло", "отопление", "гкал"],
            "units": ["Гкал", "Мкал"],
            "category": "energy_consumption",
            "resource_type": "heat"
        },
        "cost": {
            "keywords": ["стоимость", "цена", "затраты", "расходы", "сум"],
            "units": ["сум", "руб", "usd", "$"],
            "category": "financial",
            "resource_type": None
        },
        "technological": {
            "keywords": ["технологические", "технологические нужды", "технологическое"],
            "category": "consumption_category",
            "resource_type": None
        },
        "own_needs": {
            "keywords": ["собственные нужды", "собственные", "собственные потребности"],
            "category": "consumption_category",
            "resource_type": None
        },
        "production": {
            "keywords": ["производственные", "производство", "производственные нужды"],
            "category": "consumption_category",
            "resource_type": None
        },
        "household": {
            "keywords": ["хозяйственно-бытовые", "бытовые", "хозяйственные", "хоз-бытовые"],
            "category": "consumption_category",
            "resource_type": None
        },
        "total_consumption": {
            "keywords": ["общее потребление", "итого", "всего", "суммарное"],
            "category": "aggregate",
            "resource_type": None
        },
        "year": {
            "keywords": ["год", "year", "йил"],
            "category": "temporal",
            "resource_type": None
        },
        "quarter": {
            "keywords": ["квартал", "quarter", "i", "ii", "iii", "iv"],
            "category": "temporal",
            "resource_type": None
        },
        "month": {
            "keywords": ["месяц", "month", "январь", "февраль", "март"],
            "category": "temporal",
            "resource_type": None
        }
    }
    
    def __init__(self, cell_coordinates_path: Path, data_types_path: Path):
        """
        Инициализация анализатора.
        
        Args:
            cell_coordinates_path: Путь к cell_coordinates.json
            data_types_path: Путь к data_types.json
        """
        self.cell_coordinates_path = cell_coordinates_path
        self.data_types_path = data_types_path
        self.cell_coordinates = {}
        self.data_types = {}
        self.semantics = {}
    
    def load_data(self) -> None:
        """Загрузка данных из JSON файлов."""
        if self.cell_coordinates_path.exists():
            self.cell_coordinates = json.loads(
                self.cell_coordinates_path.read_text(encoding="utf-8")
            )
        
        if self.data_types_path.exists():
            self.data_types = json.loads(
                self.data_types_path.read_text(encoding="utf-8")
            )
    
    def analyze(self) -> Dict[str, Any]:
        """
        Анализ семантики всех ячеек.
        
        Returns:
            Словарь с семантическими профилями
        """
        self.load_data()
        
        self.semantics = {
            "template_name": self.cell_coordinates.get("template_name", ""),
            "cells": {},
            "summary": {
                "total_cells_analyzed": 0,
                "semantic_categories": {}
            }
        }
        
        # Анализ ячеек из каждого листа
        for sheet_name, sheet_data in self.cell_coordinates.get("sheets", {}).items():
            for row_data in sheet_data.get("cells", []):
                for cell in row_data.get("cells", []):
                    cell_address = cell["address"]
                    semantic_profile = self._analyze_cell(cell, sheet_name)
                    
                    if semantic_profile:
                        self.semantics["cells"][cell_address] = semantic_profile
                        
                        # Обновление сводки
                        category = semantic_profile.get("category")
                        if category:
                            self.semantics["summary"]["semantic_categories"][category] = \
                                self.semantics["summary"]["semantic_categories"].get(category, 0) + 1
        
        self.semantics["summary"]["total_cells_analyzed"] = len(self.semantics["cells"])
        
        return self.semantics
    
    def _analyze_cell(self, cell: Dict[str, Any], sheet_name: str) -> Optional[Dict[str, Any]]:
        """
        Анализ семантики одной ячейки.
        
        Args:
            cell: Данные ячейки
            sheet_name: Имя листа
        
        Returns:
            Семантический профиль ячейки или None
        """
        cell_value = cell.get("value")
        if not cell_value:
            return None
        
        cell_str = str(cell_value).lower()
        
        # Поиск совпадений с паттернами
        matches = []
        for pattern_name, pattern_data in self.SEMANTIC_PATTERNS.items():
            keywords = pattern_data.get("keywords", [])
            if any(keyword.lower() in cell_str for keyword in keywords):
                match_score = sum(1 for keyword in keywords if keyword.lower() in cell_str)
                matches.append({
                    "pattern": pattern_name,
                    "score": match_score,
                    "data": pattern_data
                })
        
        if not matches:
            return None
        
        # Выбор лучшего совпадения
        best_match = max(matches, key=lambda x: x["score"])
        pattern_data = best_match["data"]
        
        # Извлечение единиц измерения
        units = self._extract_units(cell_value)
        
        # Определение типа данных
        data_type = self._determine_data_type(cell_value, pattern_data)
        
        semantic_profile = {
            "address": cell["address"],
            "sheet": sheet_name,
            "row": cell["row"],
            "column": cell["column"],
            "value": cell_value,
            "semantic_type": best_match["pattern"],
            "category": pattern_data.get("category"),
            "resource_type": pattern_data.get("resource_type"),
            "units": units,
            "data_type": data_type,
            "confidence": min(best_match["score"] / len(pattern_data.get("keywords", [])), 1.0)
        }
        
        return semantic_profile
    
    def _extract_units(self, value: str) -> Optional[str]:
        """Извлечение единиц измерения из значения."""
        if not value:
            return None
        
        # Паттерны единиц измерения
        unit_patterns = [
            r'кВт·ч', r'кВтч', r'тыс\. кВт·ч',
            r'кВАр·ч', r'квар·ч',
            r'м³', r'м3', r'тыс\. м³',
            r'Гкал', r'Мкал',
            r'сум', r'руб', r'usd', r'\$',
            r'тонна', r'т', r'кг'
        ]
        
        for pattern in unit_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return re.search(pattern, value, re.IGNORECASE).group()
        
        return None
    
    def _determine_data_type(self, value: str, pattern_data: Dict[str, Any]) -> str:
        """Определение типа данных на основе паттерна."""
        category = pattern_data.get("category")
        
        if category == "energy_consumption":
            return "energy_value"
        elif category == "financial":
            return "monetary_value"
        elif category == "consumption_category":
            return "category_label"
        elif category == "temporal":
            return "temporal_value"
        elif category == "aggregate":
            return "aggregate_value"
        else:
            return "unknown"
    
    def save(self, output_path: Path) -> None:
        """
        Сохранение результатов анализа.
        
        Args:
            output_path: Путь для сохранения JSON
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.semantics, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def analyze_cell_semantics(
    cell_coordinates_path: Path,
    data_types_path: Path,
    output_path: Path
) -> Dict[str, Any]:
    """
    Анализ семантики ячеек и сохранение результатов.
    
    Args:
        cell_coordinates_path: Путь к cell_coordinates.json
        data_types_path: Путь к data_types.json
        output_path: Путь для сохранения результатов
    
    Returns:
        Словарь с семантическими профилями
    """
    analyzer = CellSemanticsAnalyzer(cell_coordinates_path, data_types_path)
    result = analyzer.analyze()
    analyzer.save(output_path)
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Семантический анализ ячеек")
    parser.add_argument("--cell-coordinates", required=True, help="Путь к cell_coordinates.json")
    parser.add_argument("--data-types", required=True, help="Путь к data_types.json")
    parser.add_argument("--output", required=True, help="Путь для сохранения JSON")
    
    args = parser.parse_args()
    
    cell_coords_path = Path(args.cell_coordinates)
    data_types_path = Path(args.data_types)
    output_path = Path(args.output)
    
    print("Семантический анализ ячеек...")
    result = analyze_cell_semantics(cell_coords_path, data_types_path, output_path)
    
    print(f"\n✅ Результаты сохранены в: {output_path}")
    print("📊 Статистика:")
    print(f"  Проанализировано ячеек: {result['summary']['total_cells_analyzed']}")
    print("  Категории:")
    for category, count in result["summary"]["semantic_categories"].items():
        print(f"    - {category}: {count}")

