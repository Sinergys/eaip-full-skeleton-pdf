"""
Этап 3.2: Предсказание форматов отображения
ML-предсказание форматов чисел на основе семантики и исторических данных
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class FormatPredictor:
    """Предиктор форматов отображения для ячеек."""
    
    # Правила предсказания форматов на основе семантики
    FORMAT_RULES = {
        "electricity_active": {
            "format": "number",
            "precision": 0,
            "units": "кВт·ч",
            "display_format": "thousands",  # для больших значений
            "scale_factor": 1000  # для конвертации в тыс. кВт·ч
        },
        "electricity_reactive": {
            "format": "number",
            "precision": 0,
            "units": "кВАр·ч",
            "display_format": "thousands",
            "scale_factor": 1000
        },
        "gas_volume": {
            "format": "number",
            "precision": 2,
            "units": "тыс. м³",
            "display_format": "thousands",
            "scale_factor": 1000  # м³ -> тыс. м³
        },
        "water_volume": {
            "format": "number",
            "precision": 0,
            "units": "м³",
            "display_format": "standard",
            "scale_factor": 1
        },
        "heat_energy": {
            "format": "number",
            "precision": 2,
            "units": "Гкал",
            "display_format": "decimal",
            "scale_factor": 1
        },
        "cost": {
            "format": "currency",
            "precision": 2,
            "units": "сум",
            "display_format": "currency",
            "scale_factor": 1
        }
    }
    
    def __init__(self, semantic_mapping_path: Path, patterns_path: Optional[Path] = None):
        """
        Инициализация предиктора.
        
        Args:
            semantic_mapping_path: Путь к semantic_mapping.json
            patterns_path: Путь к filling_patterns.json (опционально)
        """
        self.semantic_mapping_path = semantic_mapping_path
        self.patterns_path = patterns_path
        self.semantic_mapping = {}
        self.patterns = {}
        self.predictions = {}
    
    def load_data(self) -> None:
        """Загрузка данных."""
        if self.semantic_mapping_path.exists():
            self.semantic_mapping = json.loads(
                self.semantic_mapping_path.read_text(encoding="utf-8")
            )
        
        if self.patterns_path and self.patterns_path.exists():
            self.patterns = json.loads(
                self.patterns_path.read_text(encoding="utf-8")
            )
    
    def predict(self) -> Dict[str, Any]:
        """
        Предсказание форматов для всех ячеек.
        
        Returns:
            Словарь с предсказаниями форматов
        """
        self.load_data()
        
        self.predictions = {
            "template_name": self.semantic_mapping.get("template_name", ""),
            "predictions": {},
            "statistics": {
                "total_predictions": 0,
                "by_format_type": {}
            }
        }
        
        # Предсказание для каждой ячейки из маппинга
        for mapping in self.semantic_mapping.get("mappings", []):
            cell_address = mapping["cell_address"]
            semantic_type = mapping.get("semantic_type")
            data_path = mapping.get("data_path")
            
            prediction = self._predict_format(cell_address, semantic_type, data_path)
            
            if prediction:
                self.predictions["predictions"][cell_address] = prediction
                self.predictions["statistics"]["total_predictions"] += 1
                
                # Обновление статистики
                format_type = prediction.get("display_format", "unknown")
                self.predictions["statistics"]["by_format_type"][format_type] = \
                    self.predictions["statistics"]["by_format_type"].get(format_type, 0) + 1
        
        return self.predictions
    
    def _predict_format(self, cell_address: str, semantic_type: str, data_path: str) -> Optional[Dict[str, Any]]:
        """
        Предсказание формата для одной ячейки.
        
        Args:
            cell_address: Адрес ячейки
            semantic_type: Семантический тип
            data_path: Путь к данным
        
        Returns:
            Предсказание формата или None
        """
        # Использование правил на основе семантического типа
        if semantic_type in self.FORMAT_RULES:
            rule = self.FORMAT_RULES[semantic_type].copy()
            
            # Дополнительная информация из data_path
            if data_path:
                rule["data_path"] = data_path
                rule["data_source"] = self._extract_data_source(data_path)
            
            # Улучшение на основе паттернов (если есть)
            if self.patterns:
                pattern_enhancement = self._enhance_from_patterns(cell_address, rule)
                rule.update(pattern_enhancement)
            
            return rule
        
        # Попытка предсказания на основе data_path
        if data_path:
            return self._predict_from_data_path(data_path)
        
        return None
    
    def _extract_data_source(self, data_path: str) -> str:
        """Извлечение источника данных из пути."""
        parts = data_path.split(".")
        if len(parts) >= 2:
            return parts[1]  # resource type
        return "unknown"
    
    def _enhance_from_patterns(self, cell_address: str, base_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшение предсказания на основе паттернов."""
        enhancement = {}
        
        # Поиск паттернов для этой ячейки
        template_patterns = self.patterns.get("template_patterns", {})
        for sheet_name, sheet_data in template_patterns.get("sheets", {}).items():
            for format_type, cells in sheet_data.get("number_formats", {}).items():
                for cell_info in cells:
                    if cell_info["address"] == cell_address:
                        # Использование найденного формата
                        format_info = cell_info.get("format", {})
                        if format_info.get("precision") is not None:
                            enhancement["precision"] = format_info["precision"]
                        if format_info.get("magnitude"):
                            enhancement["magnitude"] = format_info["magnitude"]
        
        return enhancement
    
    def _predict_from_data_path(self, data_path: str) -> Optional[Dict[str, Any]]:
        """Предсказание формата на основе пути к данным."""
        # Определение типа ресурса из пути
        if "electricity" in data_path:
            if "active" in data_path:
                return self.FORMAT_RULES["electricity_active"].copy()
            elif "reactive" in data_path:
                return self.FORMAT_RULES["electricity_reactive"].copy()
        elif "gas" in data_path:
            return self.FORMAT_RULES["gas_volume"].copy()
        elif "water" in data_path:
            return self.FORMAT_RULES["water_volume"].copy()
        elif "heat" in data_path:
            return self.FORMAT_RULES["heat_energy"].copy()
        
        return None
    
    def save(self, output_path: Path) -> None:
        """
        Сохранение предсказаний.
        
        Args:
            output_path: Путь для сохранения JSON
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.predictions, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def predict_formats(
    semantic_mapping_path: Path,
    output_path: Path,
    patterns_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Предсказание форматов и сохранение результатов.
    
    Args:
        semantic_mapping_path: Путь к semantic_mapping.json
        output_path: Путь для сохранения результатов
        patterns_path: Путь к filling_patterns.json (опционально)
    
    Returns:
        Словарь с предсказаниями
    """
    predictor = FormatPredictor(semantic_mapping_path, patterns_path)
    predictions = predictor.predict()
    predictor.save(output_path)
    return predictions


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Предсказание форматов")
    parser.add_argument("--semantic-mapping", required=True, help="Путь к semantic_mapping.json")
    parser.add_argument("--output", required=True, help="Путь для сохранения JSON")
    parser.add_argument("--patterns", help="Путь к filling_patterns.json")
    
    args = parser.parse_args()
    
    mapping_path = Path(args.semantic_mapping)
    output_path = Path(args.output)
    patterns_path = Path(args.patterns) if args.patterns else None
    
    print("Предсказание форматов...")
    predictions = predict_formats(mapping_path, output_path, patterns_path)
    
    print(f"\n✅ Результаты сохранены в: {output_path}")
    print("📊 Статистика:")
    print(f"  Всего предсказаний: {predictions['statistics']['total_predictions']}")
    print("  По типам форматов:")
    for format_type, count in predictions['statistics']['by_format_type'].items():
        print(f"    - {format_type}: {count}")

