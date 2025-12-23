"""
Этап 2.2: Генерация бизнес-онтологии
Создание онтологии энергетического паспорта
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class OntologyBuilder:
    """Построитель онтологии энергетического паспорта."""
    
    def __init__(self, cell_semantics_path: Path):
        """
        Инициализация построителя онтологии.
        
        Args:
            cell_semantics_path: Путь к cell_semantics.json
        """
        self.cell_semantics_path = cell_semantics_path
        self.cell_semantics = {}
        self.ontology = {}
    
    def load_semantics(self) -> None:
        """Загрузка семантических данных."""
        if self.cell_semantics_path.exists():
            self.cell_semantics = json.loads(
                self.cell_semantics_path.read_text(encoding="utf-8")
            )
    
    def build(self) -> Dict[str, Any]:
        """
        Построение онтологии.
        
        Returns:
            Словарь с онтологией
        """
        self.load_semantics()
        
        self.ontology = {
            "name": "Energy Passport Ontology",
            "version": "1.0",
            "concepts": {},
            "relationships": [],
            "properties": {},
            "hierarchy": {}
        }
        
        # Извлечение концептов (сущностей)
        concepts = self._extract_concepts()
        self.ontology["concepts"] = concepts
        
        # Построение иерархии
        hierarchy = self._build_hierarchy(concepts)
        self.ontology["hierarchy"] = hierarchy
        
        # Извлечение отношений
        relationships = self._extract_relationships()
        self.ontology["relationships"] = relationships
        
        # Извлечение свойств
        properties = self._extract_properties()
        self.ontology["properties"] = properties
        
        return self.ontology
    
    def _extract_concepts(self) -> Dict[str, Dict[str, Any]]:
        """Извлечение концептов из семантических данных."""
        concepts = {}
        
        # Основные концепты
        resource_types = set()
        categories = set()
        temporal_concepts = set()
        
        for cell_address, cell_data in self.cell_semantics.get("cells", {}).items():
            resource_type = cell_data.get("resource_type")
            category = cell_data.get("category")
            semantic_type = cell_data.get("semantic_type")
            
            if resource_type:
                resource_types.add(resource_type)
            
            if category:
                categories.add(category)
            
            if "temporal" in category or "year" in semantic_type or "quarter" in semantic_type:
                temporal_concepts.add(semantic_type)
        
        # Концепты ресурсов
        for resource in resource_types:
            concepts[f"resource_{resource}"] = {
                "name": resource,
                "type": "resource",
                "description": f"Энергетический ресурс: {resource}",
                "properties": ["volume", "consumption", "cost"]
            }
        
        # Концепты категорий
        for category in categories:
            concepts[f"category_{category}"] = {
                "name": category,
                "type": "category",
                "description": f"Категория: {category}"
            }
        
        # Концепты временных периодов
        for temporal in temporal_concepts:
            concepts[f"temporal_{temporal}"] = {
                "name": temporal,
                "type": "temporal",
                "description": f"Временной период: {temporal}"
            }
        
        # Базовые концепты
        concepts["energy_passport"] = {
            "name": "Energy Passport",
            "type": "document",
            "description": "Энергетический паспорт предприятия"
        }
        
        concepts["enterprise"] = {
            "name": "Enterprise",
            "type": "entity",
            "description": "Предприятие"
        }
        
        concepts["consumption"] = {
            "name": "Consumption",
            "type": "measurement",
            "description": "Потребление энергоресурсов"
        }
        
        return concepts
    
    def _build_hierarchy(self, concepts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Построение иерархии концептов."""
        hierarchy = {
            "root": "energy_passport",
            "levels": {
                "level_1": ["enterprise", "consumption", "temporal"],
                "level_2": {
                    "consumption": ["resource", "category"],
                    "temporal": ["year", "quarter", "month"]
                }
            }
        }
        
        return hierarchy
    
    def _extract_relationships(self) -> List[Dict[str, Any]]:
        """Извлечение отношений между концептами."""
        relationships = [
            {
                "from": "enterprise",
                "to": "consumption",
                "type": "has",
                "description": "Предприятие имеет потребление"
            },
            {
                "from": "consumption",
                "to": "resource",
                "type": "includes",
                "description": "Потребление включает ресурсы"
            },
            {
                "from": "consumption",
                "to": "category",
                "type": "categorized_by",
                "description": "Потребление категоризируется"
            },
            {
                "from": "consumption",
                "to": "temporal",
                "type": "measured_in",
                "description": "Потребление измеряется во времени"
            }
        ]
        
        return relationships
    
    def _extract_properties(self) -> Dict[str, List[str]]:
        """Извлечение свойств концептов."""
        properties = {
            "resource": ["volume", "consumption", "cost", "unit"],
            "category": ["name", "description"],
            "temporal": ["year", "quarter", "month", "period"],
            "consumption": ["value", "unit", "category", "resource_type", "temporal"]
        }
        
        return properties
    
    def save(self, output_path: Path) -> None:
        """
        Сохранение онтологии.
        
        Args:
            output_path: Путь для сохранения JSON
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.ontology, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def build_ontology(cell_semantics_path: Path, output_path: Path) -> Dict[str, Any]:
    """
    Построение онтологии и сохранение результатов.
    
    Args:
        cell_semantics_path: Путь к cell_semantics.json
        output_path: Путь для сохранения результатов
    
    Returns:
        Словарь с онтологией
    """
    builder = OntologyBuilder(cell_semantics_path)
    ontology = builder.build()
    builder.save(output_path)
    return ontology


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Построение онтологии")
    parser.add_argument("--cell-semantics", required=True, help="Путь к cell_semantics.json")
    parser.add_argument("--output", required=True, help="Путь для сохранения JSON")
    
    args = parser.parse_args()
    
    semantics_path = Path(args.cell_semantics)
    output_path = Path(args.output)
    
    print("Построение онтологии...")
    ontology = build_ontology(semantics_path, output_path)
    
    print(f"\n✅ Онтология сохранена в: {output_path}")
    print("📊 Статистика:")
    print(f"  Концептов: {len(ontology['concepts'])}")
    print(f"  Отношений: {len(ontology['relationships'])}")
    print(f"  Свойств: {len(ontology['properties'])}")

