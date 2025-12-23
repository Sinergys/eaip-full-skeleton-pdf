"""
Создание полного семантического профиля всех листов энергетического паспорта
С включением полной онтологии и связей между листами
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class EnergyPassportOntology:
    """Онтология энергетического паспорта."""
    
    RESOURCE_TYPES = {
        "electricity": {
            "name": "Электроэнергия",
            "units": ["кВт·ч", "кВтч", "тыс. кВт·ч", "кВАр·ч"],
            "categories": ["active", "reactive", "total"]
        },
        "gas": {
            "name": "Природный газ",
            "units": ["м³", "м3", "тыс. м³"],
            "categories": ["volume", "cost"]
        },
        "water": {
            "name": "Вода",
            "units": ["м³", "м3", "тыс. м³"],
            "categories": ["volume", "cost"]
        },
        "fuel": {
            "name": "Мазут",
            "units": ["т", "тонн", "кг"],
            "categories": ["volume", "cost"]
        },
        "coal": {
            "name": "Уголь",
            "units": ["т", "тонн", "кг"],
            "categories": ["volume", "cost"]
        },
        "heat": {
            "name": "Тепловая энергия",
            "units": ["Гкал", "Мкал"],
            "categories": ["energy", "cost"]
        }
    }
    
    CONSUMPTION_CATEGORIES = {
        "technological": "Технологические нужды",
        "own_needs": "Собственные нужды",
        "production": "Производственные нужды",
        "household": "Хозяйственно-бытовые нужды"
    }
    
    TIME_PERIODS = {
        "year": "Год",
        "quarter": "Квартал",
        "month": "Месяц"
    }
    
    SHEET_PURPOSES = {
        "regulatory_documentation": "Нормативно-правовая документация",
        "metering_nodes": "Узлы учета энергоресурсов",
        "structure": "Структура потребления энергоресурсов",
        "balance": "Баланс энергоресурсов",
        "dynamics": "Динамика потребления",
        "fuel_consumption": "Потребление топлива",
        "consumption_per_unit": "Расход на единицу продукции",
        "measures": "Энергосберегающие мероприятия",
        "summary": "Сводные данные"
    }


def create_full_semantic_profile(analysis_dir: Path, output_path: Path) -> Dict[str, Any]:
    """
    Создание полного семантического профиля на основе анализа листов.
    
    Args:
        analysis_dir: Директория с результатами анализа листов
        output_path: Путь для сохранения профиля
        
    Returns:
        Словарь с полным семантическим профилем
    """
    summary_file = analysis_dir / "all_sheets_analysis_summary.json"
    
    if not summary_file.exists():
        raise FileNotFoundError(f"Файл сводки не найден: {summary_file}")
    
    # Загружаем результаты анализа
    with open(summary_file, "r", encoding="utf-8") as f:
        analysis_data = json.load(f)
    
    ontology = EnergyPassportOntology()
    
    # Строим онтологию
    profile = {
        "metadata": {
            "template_path": analysis_data.get("template_path"),
            "template_name": analysis_data.get("template_name"),
            "total_sheets": analysis_data.get("total_sheets"),
            "analyzed_sheets": analysis_data.get("analyzed_sheets"),
            "ontology_version": "1.0",
            "created_at": Path(__file__).stat().st_mtime
        },
        "ontology": {
            "resource_types": ontology.RESOURCE_TYPES,
            "consumption_categories": ontology.CONSUMPTION_CATEGORIES,
            "time_periods": ontology.TIME_PERIODS,
            "sheet_purposes": ontology.SHEET_PURPOSES
        },
        "sheets": {},
        "relationships": {
            "data_flow": [],
            "dependencies": [],
            "references": []
        },
        "data_mapping": {
            "by_resource_type": {},
            "by_time_period": {},
            "by_consumption_category": {}
        }
    }
    
    # Обрабатываем каждый лист
    sheets_analysis = analysis_data.get("sheets_analysis", {})
    
    for sheet_name, sheet_data in sheets_analysis.items():
        if "error" in sheet_data:
            continue
        
        summary = sheet_data.get("summary", {})
        semantic_analysis = sheet_data.get("table_structure_analysis", {}).get("semantic_analysis", {})
        
        sheet_info = {
            "name": sheet_name,
            "purpose": summary.get("sheet_purpose", "unknown"),
            "purpose_description": ontology.SHEET_PURPOSES.get(
                summary.get("sheet_purpose", "unknown"), 
                "Неизвестно"
            ),
            "resource_types": summary.get("resource_types", []),
            "time_periods": summary.get("time_periods", []),
            "structural_info": {
                "total_tables": summary.get("total_tables", 0),
                "total_rows": summary.get("total_rows", 0),
                "total_columns": summary.get("total_columns", 0)
            },
            "data_categories": semantic_analysis.get("data_categories", []),
            "key_indicators": semantic_analysis.get("key_indicators", [])
        }
        
        profile["sheets"][sheet_name] = sheet_info
        
        # Добавляем в маппинг по типам ресурсов
        for resource_type in sheet_info["resource_types"]:
            if resource_type not in profile["data_mapping"]["by_resource_type"]:
                profile["data_mapping"]["by_resource_type"][resource_type] = []
            profile["data_mapping"]["by_resource_type"][resource_type].append(sheet_name)
        
        # Добавляем в маппинг по временным периодам
        for time_period in sheet_info["time_periods"]:
            if time_period not in profile["data_mapping"]["by_time_period"]:
                profile["data_mapping"]["by_time_period"][time_period] = []
            profile["data_mapping"]["by_time_period"][time_period].append(sheet_name)
        
        # Добавляем в маппинг по категориям потребления
        for category in sheet_info["data_categories"]:
            if category not in profile["data_mapping"]["by_consumption_category"]:
                profile["data_mapping"]["by_consumption_category"][category] = []
            profile["data_mapping"]["by_consumption_category"][category].append(sheet_name)
    
    # Определяем связи между листами
    profile["relationships"] = _determine_relationships(profile["sheets"], ontology)
    
    # Сохраняем профиль
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    return profile


def _determine_relationships(sheets: Dict[str, Any], ontology: EnergyPassportOntology) -> Dict[str, List[Any]]:
    """Определение связей между листами."""
    relationships = {
        "data_flow": [],
        "dependencies": [],
        "references": []
    }
    
    sheet_names = list(sheets.keys())
    
    # Связи потока данных
    # Структура -> Баланс (данные о потреблении передаются в баланс)
    if "Структура пр 2 " in sheets and "Баланс" in sheets:
        relationships["data_flow"].append({
            "from": "Структура пр 2 ",
            "to": "Баланс",
            "type": "consumption_data",
            "description": "Данные о потреблении передаются из структуры в баланс"
        })
    
    # Структура -> Динамика (данные используются для построения динамики)
    if "Структура пр 2 " in sheets and "Динамика ср" in sheets:
        relationships["data_flow"].append({
            "from": "Структура пр 2 ",
            "to": "Динамика ср",
            "type": "time_series_data",
            "description": "Квартальные данные используются для анализа динамики"
        })
    
    # Баланс -> Динамика
    if "Баланс" in sheets and "Динамика ср" in sheets:
        relationships["data_flow"].append({
            "from": "Баланс",
            "to": "Динамика ср",
            "type": "aggregated_data",
            "description": "Сводные данные баланса используются в динамике"
        })
    
    # Структура -> Расход на единицу продукции
    if "Структура пр 2 " in sheets and "Расход  на ед.п" in sheets:
        relationships["data_flow"].append({
            "from": "Структура пр 2 ",
            "to": "Расход  на ед.п",
            "type": "specific_consumption",
            "description": "Данные потребления используются для расчета удельных показателей"
        })
    
    # Зависимости (листы, которые должны быть заполнены перед другими)
    # Узлы учета -> Структура (информация об узлах учета нужна для структуры)
    if "Узел учета " in sheets and "Структура пр 2 " in sheets:
        relationships["dependencies"].append({
            "dependent": "Структура пр 2 ",
            "depends_on": "Узел учета ",
            "reason": "Информация об узлах учета необходима для правильного распределения потребления"
        })
    
    # Структура -> Баланс
    if "Структура пр 2 " in sheets and "Баланс" in sheets:
        relationships["dependencies"].append({
            "dependent": "Баланс",
            "depends_on": "Структура пр 2 ",
            "reason": "Баланс формируется на основе данных структуры потребления"
        })
    
    # Баланс -> Динамика
    if "Баланс" in sheets and "Динамика ср" in sheets:
        relationships["dependencies"].append({
            "dependent": "Динамика ср",
            "depends_on": "Баланс",
            "reason": "Динамика строится на основе данных баланса"
        })
    
    # Ссылки между листами (когда один лист ссылается на другой через формулы)
    # Это будет определено при анализе формул, здесь добавляем базовые
    
    return relationships


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Создание полного семантического профиля")
    parser.add_argument("--analysis-dir", required=True, help="Директория с результатами анализа")
    parser.add_argument("--output", required=True, help="Путь для сохранения профиля")
    
    args = parser.parse_args()
    
    analysis_dir = Path(args.analysis_dir)
    output_path = Path(args.output)
    
    if not analysis_dir.exists():
        raise FileNotFoundError(f"Директория анализа не найдена: {analysis_dir}")
    
    print("=" * 80)
    print("🔬 СОЗДАНИЕ ПОЛНОГО СЕМАНТИЧЕСКОГО ПРОФИЛЯ")
    print("=" * 80)
    print(f"Директория анализа: {analysis_dir}")
    print(f"Выходной файл: {output_path}")
    print()
    
    profile = create_full_semantic_profile(analysis_dir, output_path)
    
    print("✅ Семантический профиль создан")
    print("\n📊 Статистика:")
    print(f"  Листов: {len(profile['sheets'])}")
    print(f"  Типов ресурсов: {len(profile['ontology']['resource_types'])}")
    print(f"  Связей данных: {len(profile['relationships']['data_flow'])}")
    print(f"  Зависимостей: {len(profile['relationships']['dependencies'])}")
    print(f"\n💾 Профиль сохранен в: {output_path}")

