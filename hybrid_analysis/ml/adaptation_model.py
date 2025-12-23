"""
Этап 3.3: Обучение на существующих данных
Создание модели адаптации к новым данным
"""

import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from collections import defaultdict


class AdaptationModel:
    """Модель адаптации к новым данным и шаблонам."""
    
    def __init__(self):
        """Инициализация модели."""
        self.model = {
            "rules": {},
            "patterns": {},
            "mappings": {},
            "statistics": {}
        }
    
    def train(
        self,
        semantic_mapping_path: Path,
        format_predictions_path: Path,
        patterns_path: Optional[Path] = None
    ) -> None:
        """
        Обучение модели на существующих данных.
        
        Args:
            semantic_mapping_path: Путь к semantic_mapping.json
            format_predictions_path: Путь к format_predictions.json
            patterns_path: Путь к filling_patterns.json (опционально)
        """
        # Загрузка данных
        semantic_mapping = {}
        format_predictions = {}
        patterns = {}
        
        if semantic_mapping_path.exists():
            semantic_mapping = json.loads(
                semantic_mapping_path.read_text(encoding="utf-8")
            )
        
        if format_predictions_path.exists():
            format_predictions = json.loads(
                format_predictions_path.read_text(encoding="utf-8")
            )
        
        if patterns_path and patterns_path.exists():
            patterns = json.loads(
                patterns_path.read_text(encoding="utf-8")
            )
        
        # Извлечение правил из семантического маппинга
        self._extract_rules(semantic_mapping)
        
        # Извлечение паттернов
        self._extract_patterns(format_predictions, patterns)
        
        # Построение статистики
        self._build_statistics(semantic_mapping, format_predictions)
    
    def _extract_rules(self, semantic_mapping: Dict[str, Any]) -> None:
        """Извлечение правил из семантического маппинга."""
        rules = defaultdict(list)
        
        for mapping in semantic_mapping.get("mappings", []):
            semantic_type = mapping.get("semantic_type")
            data_path = mapping.get("data_path")
            
            if semantic_type and data_path:
                rule = {
                    "semantic_type": semantic_type,
                    "data_path": data_path,
                    "confidence": mapping.get("confidence", 0.0)
                }
                rules[semantic_type].append(rule)
        
        self.model["rules"] = dict(rules)
    
    def _extract_patterns(self, format_predictions: Dict[str, Any], patterns: Dict[str, Any]) -> None:
        """Извлечение паттернов из предсказаний и данных."""
        extracted_patterns = {
            "format_patterns": {},
            "filling_patterns": {}
        }
        
        # Паттерны форматов
        for cell_address, prediction in format_predictions.get("predictions", {}).items():
            format_type = prediction.get("display_format", "unknown")
            if format_type not in extracted_patterns["format_patterns"]:
                extracted_patterns["format_patterns"][format_type] = []
            
            extracted_patterns["format_patterns"][format_type].append({
                "cell": cell_address,
                "format": prediction
            })
        
        # Паттерны заполнения
        if patterns:
            template_patterns = patterns.get("template_patterns", {})
            for sheet_name, sheet_data in template_patterns.get("sheets", {}).items():
                for format_type, cells in sheet_data.get("number_formats", {}).items():
                    if format_type not in extracted_patterns["filling_patterns"]:
                        extracted_patterns["filling_patterns"][format_type] = []
                    
                    extracted_patterns["filling_patterns"][format_type].extend(cells)
        
        self.model["patterns"] = extracted_patterns
    
    def _build_statistics(self, semantic_mapping: Dict[str, Any], format_predictions: Dict[str, Any]) -> None:
        """Построение статистики модели."""
        stats = {
            "total_rules": len(self.model["rules"]),
            "total_patterns": len(self.model["patterns"].get("format_patterns", {})),
            "mapping_coverage": 0.0,
            "format_coverage": 0.0
        }
        
        # Покрытие маппингом
        total_cells = semantic_mapping.get("statistics", {}).get("total_cells", 0)
        mapped_cells = semantic_mapping.get("statistics", {}).get("mapped_cells", 0)
        if total_cells > 0:
            stats["mapping_coverage"] = (mapped_cells / total_cells) * 100
        
        # Покрытие форматами
        total_predictions = format_predictions.get("statistics", {}).get("total_predictions", 0)
        if mapped_cells > 0:
            stats["format_coverage"] = (total_predictions / mapped_cells) * 100
        
        self.model["statistics"] = stats
    
    def predict(self, cell_semantic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Предсказание для новой ячейки на основе обученной модели.
        
        Args:
            cell_semantic: Семантический профиль ячейки
        
        Returns:
            Предсказание или None
        """
        semantic_type = cell_semantic.get("semantic_type")
        
        if semantic_type in self.model["rules"]:
            # Использование правила
            rules = self.model["rules"][semantic_type]
            if rules:
                best_rule = max(rules, key=lambda x: x.get("confidence", 0.0))
                return {
                    "data_path": best_rule["data_path"],
                    "confidence": best_rule["confidence"],
                    "source": "rule_based"
                }
        
        return None
    
    def save(self, output_path: Path) -> None:
        """
        Сохранение модели.
        
        Args:
            output_path: Путь для сохранения .pkl файла
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            pickle.dump(self.model, f)
    
    @classmethod
    def load(cls, model_path: Path) -> 'AdaptationModel':
        """
        Загрузка модели.
        
        Args:
            model_path: Путь к .pkl файлу
        
        Returns:
            Загруженная модель
        """
        model = cls()
        with open(model_path, 'rb') as f:
            model.model = pickle.load(f)
        return model


def train_adaptation_model(
    semantic_mapping_path: Path,
    format_predictions_path: Path,
    output_path: Path,
    patterns_path: Optional[Path] = None
) -> AdaptationModel:
    """
    Обучение модели адаптации и сохранение результатов.
    
    Args:
        semantic_mapping_path: Путь к semantic_mapping.json
        format_predictions_path: Путь к format_predictions.json
        output_path: Путь для сохранения .pkl файла
        patterns_path: Путь к filling_patterns.json (опционально)
    
    Returns:
        Обученная модель
    """
    model = AdaptationModel()
    model.train(semantic_mapping_path, format_predictions_path, patterns_path)
    model.save(output_path)
    return model


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Обучение модели адаптации")
    parser.add_argument("--semantic-mapping", required=True, help="Путь к semantic_mapping.json")
    parser.add_argument("--format-predictions", required=True, help="Путь к format_predictions.json")
    parser.add_argument("--output", required=True, help="Путь для сохранения .pkl")
    parser.add_argument("--patterns", help="Путь к filling_patterns.json")
    
    args = parser.parse_args()
    
    mapping_path = Path(args.semantic_mapping)
    predictions_path = Path(args.format_predictions)
    output_path = Path(args.output)
    patterns_path = Path(args.patterns) if args.patterns else None
    
    print("Обучение модели адаптации...")
    model = train_adaptation_model(mapping_path, predictions_path, output_path, patterns_path)
    
    print(f"\n✅ Модель сохранена в: {output_path}")
    print("📊 Статистика модели:")
    stats = model.model["statistics"]
    print(f"  Правил: {stats['total_rules']}")
    print(f"  Паттернов: {stats['total_patterns']}")
    print(f"  Покрытие маппингом: {stats['mapping_coverage']:.2f}%")
    print(f"  Покрытие форматами: {stats['format_coverage']:.2f}%")

