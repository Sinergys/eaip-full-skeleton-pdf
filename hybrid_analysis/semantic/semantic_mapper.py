"""
Этап 2.3: Сопоставление с данными
Интеллектуальное сопоставление полей шаблона с aggregated_data
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class SemanticMapper:
    """Маппер для сопоставления семантических профилей с данными."""
    
    def __init__(self, cell_semantics_path: Path, aggregated_data_path: Path):
        """
        Инициализация маппера.
        
        Args:
            cell_semantics_path: Путь к cell_semantics.json
            aggregated_data_path: Путь к aggregated_data.json
        """
        self.cell_semantics_path = cell_semantics_path
        self.aggregated_data_path = aggregated_data_path
        self.cell_semantics = {}
        self.aggregated_data = {}
        self.mapping = {}
    
    def load_data(self) -> None:
        """Загрузка данных."""
        if self.cell_semantics_path.exists():
            self.cell_semantics = json.loads(
                self.cell_semantics_path.read_text(encoding="utf-8")
            )
        
        if self.aggregated_data_path.exists():
            self.aggregated_data = json.loads(
                self.aggregated_data_path.read_text(encoding="utf-8")
            )
    
    def map(self) -> Dict[str, Any]:
        """
        Сопоставление семантических профилей с данными.
        
        Returns:
            Словарь с маппингом
        """
        self.load_data()
        
        # Нормализация структуры aggregated_data
        normalized_data = self._normalize_aggregated_data()
        
        self.mapping = {
            "template_name": self.cell_semantics.get("template_name", ""),
            "mappings": [],
            "unmapped_cells": [],
            "statistics": {
                "total_cells": 0,
                "mapped_cells": 0,
                "unmapped_cells": 0
            }
        }
        
        # Сопоставление ячеек с данными
        for cell_address, cell_semantic in self.cell_semantics.get("cells", {}).items():
            self.mapping["statistics"]["total_cells"] += 1
            
            data_path = self._find_data_path(cell_semantic, normalized_data)
            
            if data_path:
                mapping_entry = {
                    "cell_address": cell_address,
                    "sheet": cell_semantic.get("sheet"),
                    "semantic_type": cell_semantic.get("semantic_type"),
                    "data_path": data_path,
                    "confidence": cell_semantic.get("confidence", 0.0)
                }
                self.mapping["mappings"].append(mapping_entry)
                self.mapping["statistics"]["mapped_cells"] += 1
            else:
                self.mapping["unmapped_cells"].append({
                    "cell_address": cell_address,
                    "semantic_type": cell_semantic.get("semantic_type"),
                    "reason": "No matching data found"
                })
                self.mapping["statistics"]["unmapped_cells"] += 1
        
        return self.mapping
    
    def _normalize_aggregated_data(self) -> Dict[str, Any]:
        """Нормализация структуры aggregated_data."""
        normalized = {"resources": {}}
        
        # Если данные в формате file-based, преобразуем в resource-based
        if isinstance(self.aggregated_data, dict):
            for file_data in self.aggregated_data.values():
                if isinstance(file_data, dict) and "resources" in file_data:
                    for resource_type, resource_data in file_data["resources"].items():
                        if resource_type not in normalized["resources"]:
                            normalized["resources"][resource_type] = {}
                        for quarter, quarter_data in resource_data.items():
                            normalized["resources"][resource_type][quarter] = quarter_data
        
        return normalized
    
    def _find_data_path(self, cell_semantic: Dict[str, Any], normalized_data: Dict[str, Any]) -> Optional[str]:
        """
        Поиск пути к данным для ячейки.
        
        Args:
            cell_semantic: Семантический профиль ячейки
            normalized_data: Нормализованные данные
        
        Returns:
            Путь к данным в формате "resources.electricity.2022-Q1.quarter_totals.active_kwh"
        """
        resource_type = cell_semantic.get("resource_type")
        semantic_type = cell_semantic.get("semantic_type")
        category = cell_semantic.get("category")
        
        if not resource_type:
            return None
        
        # Определение пути к данным на основе семантического типа
        if semantic_type == "electricity_active":
            # Первый доступный квартал
            quarters = list(normalized_data.get("resources", {}).get("electricity", {}).keys())
            if quarters:
                quarter = sorted(quarters)[0]
                return f"resources.electricity.{quarter}.quarter_totals.active_kwh"
        
        elif semantic_type == "electricity_reactive":
            quarters = list(normalized_data.get("resources", {}).get("electricity", {}).keys())
            if quarters:
                quarter = sorted(quarters)[0]
                return f"resources.electricity.{quarter}.quarter_totals.reactive_kvarh"
        
        elif semantic_type == "gas_volume":
            quarters = list(normalized_data.get("resources", {}).get("gas", {}).keys())
            if quarters:
                quarter = sorted(quarters)[0]
                return f"resources.gas.{quarter}.quarter_totals.volume_m3"
        
        elif semantic_type == "water_volume":
            quarters = list(normalized_data.get("resources", {}).get("water", {}).keys())
            if quarters:
                quarter = sorted(quarters)[0]
                return f"resources.water.{quarter}.quarter_totals.volume_m3"
        
        elif semantic_type == "technological":
            quarters = list(normalized_data.get("resources", {}).get("electricity", {}).keys())
            if quarters:
                quarter = sorted(quarters)[0]
                return f"resources.electricity.{quarter}.by_usage.technological"
        
        elif semantic_type == "own_needs":
            quarters = list(normalized_data.get("resources", {}).get("electricity", {}).keys())
            if quarters:
                quarter = sorted(quarters)[0]
                return f"resources.electricity.{quarter}.by_usage.own_needs"
        
        elif semantic_type == "production":
            quarters = list(normalized_data.get("resources", {}).get("electricity", {}).keys())
            if quarters:
                quarter = sorted(quarters)[0]
                return f"resources.electricity.{quarter}.by_usage.production"
        
        elif semantic_type == "household":
            quarters = list(normalized_data.get("resources", {}).get("electricity", {}).keys())
            if quarters:
                quarter = sorted(quarters)[0]
                return f"resources.electricity.{quarter}.by_usage.household"
        
        return None
    
    def save(self, output_path: Path) -> None:
        """
        Сохранение маппинга.
        
        Args:
            output_path: Путь для сохранения JSON
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.mapping, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def create_semantic_mapping(
    cell_semantics_path: Path,
    aggregated_data_path: Path,
    output_path: Path
) -> Dict[str, Any]:
    """
    Создание семантического маппинга и сохранение результатов.
    
    Args:
        cell_semantics_path: Путь к cell_semantics.json
        aggregated_data_path: Путь к aggregated_data.json
        output_path: Путь для сохранения результатов
    
    Returns:
        Словарь с маппингом
    """
    mapper = SemanticMapper(cell_semantics_path, aggregated_data_path)
    mapping = mapper.map()
    mapper.save(output_path)
    return mapping


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Семантическое сопоставление")
    parser.add_argument("--cell-semantics", required=True, help="Путь к cell_semantics.json")
    parser.add_argument("--aggregated-data", required=True, help="Путь к aggregated_data.json")
    parser.add_argument("--output", required=True, help="Путь для сохранения JSON")
    
    args = parser.parse_args()
    
    semantics_path = Path(args.cell_semantics)
    aggregated_path = Path(args.aggregated_data)
    output_path = Path(args.output)
    
    print("Создание семантического маппинга...")
    mapping = create_semantic_mapping(semantics_path, aggregated_path, output_path)
    
    print(f"\n✅ Маппинг сохранен в: {output_path}")
    print("📊 Статистика:")
    print(f"  Всего ячеек: {mapping['statistics']['total_cells']}")
    print(f"  Сопоставлено: {mapping['statistics']['mapped_cells']}")
    print(f"  Не сопоставлено: {mapping['statistics']['unmapped_cells']}")

