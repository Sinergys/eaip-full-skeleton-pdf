"""
Этап 4.2: Семантическое сопоставление шаблонов
Выявление общих и уникальных концептов
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict


class SemanticComparator:
    """Класс для сравнения семантики двух шаблонов."""
    
    def __init__(self, semantic1_path: Optional[Path] = None, semantic2_path: Optional[Path] = None):
        """
        Инициализация компаратора.
        
        Args:
            semantic1_path: Путь к семантическому анализу первого шаблона
            semantic2_path: Путь к семантическому анализу второго шаблона
        """
        self.semantic1_path = semantic1_path
        self.semantic2_path = semantic2_path
        self.semantic1_data = {}
        self.semantic2_data = {}
        self.comparison = {}
    
    def load_semantics(self) -> None:
        """Загрузка семантических данных."""
        if self.semantic1_path and self.semantic1_path.exists():
            self.semantic1_data = json.loads(
                self.semantic1_path.read_text(encoding="utf-8")
            )
        
        if self.semantic2_path and self.semantic2_path.exists():
            self.semantic2_data = json.loads(
                self.semantic2_path.read_text(encoding="utf-8")
            )
    
    def compare(self) -> Dict[str, Any]:
        """
        Сравнение семантики шаблонов.
        
        Returns:
            Словарь с результатами сравнения
        """
        self.comparison = {
            "template1": {
                "name": self.semantic1_data.get("template_name", "unknown"),
                "semantic_types": self._extract_semantic_types(self.semantic1_data),
                "total_concepts": 0
            },
            "template2": {
                "name": self.semantic2_data.get("template_name", "unknown"),
                "semantic_types": self._extract_semantic_types(self.semantic2_data),
                "total_concepts": 0
            },
            "common_concepts": [],
            "unique_to_template1": [],
            "unique_to_template2": [],
            "semantic_mapping": {},
            "conversion_rules": []
        }
        
        # Извлечение концептов
        concepts1 = self._extract_concepts(self.semantic1_data)
        concepts2 = self._extract_concepts(self.semantic2_data)
        
        # Сравнение концептов
        common_concepts = concepts1.intersection(concepts2)
        unique_to_1 = concepts1 - concepts2
        unique_to_2 = concepts2 - concepts1
        
        self.comparison["common_concepts"] = list(common_concepts)
        self.comparison["unique_to_template1"] = list(unique_to_1)
        self.comparison["unique_to_template2"] = list(unique_to_2)
        
        # Обновление статистики
        self.comparison["template1"]["total_concepts"] = len(concepts1)
        self.comparison["template2"]["total_concepts"] = len(concepts2)
        
        # Создание семантического маппинга
        self.comparison["semantic_mapping"] = self._create_semantic_mapping()
        
        # Генерация правил конвертации
        self.comparison["conversion_rules"] = self._generate_conversion_rules()
        
        return self.comparison
    
    def _extract_semantic_types(self, semantic_data: Dict[str, Any]) -> Dict[str, int]:
        """Извлечение типов семантики и их частоты."""
        semantic_types = defaultdict(int)
        
        # Из mappings
        for mapping in semantic_data.get("mappings", []):
            semantic_type = mapping.get("semantic_type")
            if semantic_type:
                semantic_types[semantic_type] += 1
        
        # Из cells (если есть)
        for cell_address, cell_data in semantic_data.get("cells", {}).items():
            semantic_type = cell_data.get("semantic_type")
            if semantic_type:
                semantic_types[semantic_type] += 1
        
        return dict(semantic_types)
    
    def _extract_concepts(self, semantic_data: Dict[str, Any]) -> Set[str]:
        """Извлечение концептов из семантических данных."""
        concepts = set()
        
        # Из mappings
        for mapping in semantic_data.get("mappings", []):
            semantic_type = mapping.get("semantic_type")
            if semantic_type:
                concepts.add(semantic_type)
        
        # Из cells
        for cell_address, cell_data in semantic_data.get("cells", {}).items():
            semantic_type = cell_data.get("semantic_type")
            if semantic_type:
                concepts.add(semantic_type)
            
            resource_type = cell_data.get("resource_type")
            if resource_type:
                concepts.add(resource_type)
            
            category = cell_data.get("category")
            if category:
                concepts.add(category)
        
        return concepts
    
    def _create_semantic_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Создание маппинга между семантическими типами."""
        mapping = {}
        
        types1 = set(self.comparison["template1"]["semantic_types"].keys())
        types2 = set(self.comparison["template2"]["semantic_types"].keys())
        
        common_types = types1.intersection(types2)
        
        for semantic_type in common_types:
            mapping[semantic_type] = {
                "status": "direct_mapping",
                "template1_count": self.comparison["template1"]["semantic_types"].get(semantic_type, 0),
                "template2_count": self.comparison["template2"]["semantic_types"].get(semantic_type, 0),
                "confidence": 1.0
            }
        
        # Поиск похожих типов для маппинга
        unique_to_1 = types1 - types2
        unique_to_2 = types2 - types1
        
        for type1 in unique_to_1:
            # Поиск похожих типов
            similar_types = self._find_similar_types(type1, unique_to_2)
            if similar_types:
                mapping[type1] = {
                    "status": "similar_mapping",
                    "target_types": similar_types,
                    "confidence": 0.7
                }
        
        return mapping
    
    def _find_similar_types(self, source_type: str, target_types: Set[str]) -> List[str]:
        """Поиск похожих типов."""
        # Простая эвристика для поиска похожих типов
        similar = []
        
        source_lower = source_type.lower()
        
        # Словарь синонимов
        synonyms = {
            "electricity_active": ["active_electricity", "active_power", "active_energy"],
            "electricity_reactive": ["reactive_electricity", "reactive_power", "reactive_energy"],
            "gas_volume": ["gas", "gas_consumption", "gas_usage"],
            "water_volume": ["water", "water_consumption", "water_usage"],
            "heat_energy": ["heating", "heat", "thermal_energy"],
            "quarter": ["q1", "q2", "q3", "q4", "period"],
            "year": ["annual", "yearly"]
        }
        
        for target_type in target_types:
            target_lower = target_type.lower()
            
            # Прямое совпадение
            if source_lower == target_lower:
                similar.append(target_type)
                continue
            
            # Проверка синонимов
            for key, values in synonyms.items():
                if key in source_lower and any(v in target_lower for v in values):
                    similar.append(target_type)
                    break
                elif any(v in source_lower for v in values) and key in target_lower:
                    similar.append(target_type)
                    break
            
            # Частичное совпадение
            if len(source_lower) > 3 and len(target_lower) > 3:
                if source_lower[:4] in target_lower or target_lower[:4] in source_lower:
                    similar.append(target_type)
        
        return similar[:3]  # Возвращаем максимум 3 похожих типа
    
    def _generate_conversion_rules(self) -> List[Dict[str, Any]]:
        """Генерация правил конвертации."""
        rules = []
        
        # Правила для общих концептов
        for concept in self.comparison["common_concepts"]:
            rules.append({
                "source_concept": concept,
                "target_concept": concept,
                "rule_type": "direct_copy",
                "confidence": 1.0,
                "description": f"Прямое копирование концепта '{concept}'"
            })
        
        # Правила для уникальных концептов Template 1
        for concept in self.comparison["unique_to_template1"]:
            similar_in_2 = self._find_similar_concepts(concept, self.comparison["template2"]["semantic_types"].keys())
            if similar_in_2:
                rules.append({
                    "source_concept": concept,
                    "target_concept": similar_in_2[0],
                    "rule_type": "semantic_mapping",
                    "confidence": 0.7,
                    "description": f"Маппинг '{concept}' -> '{similar_in_2[0]}'"
                })
            else:
                rules.append({
                    "source_concept": concept,
                    "target_concept": None,
                    "rule_type": "skip",
                    "confidence": 0.0,
                    "description": f"Концепт '{concept}' не имеет эквивалента в Template 2"
                })
        
        return rules
    
    def _find_similar_concepts(self, concept: str, target_concepts: List[str]) -> List[str]:
        """Поиск похожих концептов."""
        return self._find_similar_types(concept, set(target_concepts))
    
    def save(self, output_path: Path) -> None:
        """Сохранение результатов сравнения."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.comparison, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def compare_semantics(semantic1_path: Optional[Path], semantic2_path: Optional[Path],
                     output_path: Path) -> Dict[str, Any]:
    """
    Сравнение семантики двух шаблонов.
    
    Args:
        semantic1_path: Путь к семантическому анализу первого шаблона
        semantic2_path: Путь к семантическому анализу второго шаблона
        output_path: Путь для сохранения результатов
    
    Returns:
        Словарь с результатами сравнения
    """
    comparator = SemanticComparator(semantic1_path, semantic2_path)
    comparator.load_semantics()
    comparison = comparator.compare()
    comparator.save(output_path)
    
    return comparison


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Семантическое сравнение шаблонов")
    parser.add_argument("--semantic1", help="Путь к семантическому анализу первого шаблона")
    parser.add_argument("--semantic2", help="Путь к семантическому анализу второго шаблона")
    parser.add_argument("--output", required=True, help="Путь для сохранения JSON")
    
    args = parser.parse_args()
    
    semantic1_path = Path(args.semantic1) if args.semantic1 else None
    semantic2_path = Path(args.semantic2) if args.semantic2 else None
    output_path = Path(args.output)
    
    if semantic1_path and not semantic1_path.exists():
        raise FileNotFoundError(f"Файл не найден: {semantic1_path}")
    if semantic2_path and not semantic2_path.exists():
        raise FileNotFoundError(f"Файл не найден: {semantic2_path}")
    
    print("Сравнение семантики шаблонов")
    if semantic1_path:
        print(f"  Semantic 1: {semantic1_path}")
    if semantic2_path:
        print(f"  Semantic 2: {semantic2_path}")
    
    comparison = compare_semantics(semantic1_path, semantic2_path, output_path)
    
    print(f"\n✅ Результаты сохранены в: {output_path}")
    print("\n📊 Результаты сравнения:")
    print(f"  Общие концепты: {len(comparison['common_concepts'])}")
    print(f"  Уникальные концепты (Template 1): {len(comparison['unique_to_template1'])}")
    print(f"  Уникальные концепты (Template 2): {len(comparison['unique_to_template2'])}")
    print(f"  Правила конвертации: {len(comparison['conversion_rules'])}")

