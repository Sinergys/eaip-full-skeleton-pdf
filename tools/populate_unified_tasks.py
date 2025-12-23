"""Заполнение единого файла задач всеми задачами проекта"""
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
TASKS_FILE = PROJECT_ROOT / "docs" / "AGENT_TASKS_UNIFIED.json"

# Все задачи проекта
ALL_TASKS = {
    # Критические задачи (9)
    "CRIT_1": {
        "id": "CRIT_1",
        "name": "Электроэнергия - по узлам учёта",
        "status": "not_started",
        "priority": "P0",
        "category": "critical",
        "area": "Данные",
        "stage": "Блоки импорта"
    },
    "CRIT_2": {
        "id": "CRIT_2",
        "name": "Электроэнергия - активная/реактивная",
        "status": "not_started",
        "priority": "P0",
        "category": "critical",
        "area": "Данные",
        "stage": "Блоки импорта"
    },
    "CRIT_3": {
        "id": "CRIT_3",
        "name": "Газ - поквартальные данные (полные)",
        "status": "partial",
        "priority": "P0",
        "category": "critical",
        "area": "Данные",
        "stage": "Блоки импорта"
    },
    "CRIT_4": {
        "id": "CRIT_4",
        "name": "Импорт агрегированных данных в БД",
        "status": "not_started",
        "priority": "P0",
        "category": "critical",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "CRIT_5": {
        "id": "CRIT_5",
        "name": "Оборудование - импорт в БД",
        "status": "partial",
        "priority": "P0",
        "category": "critical",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "CRIT_6": {
        "id": "CRIT_6",
        "name": "Узлы учёта - импорт в БД",
        "status": "partial",
        "priority": "P0",
        "category": "critical",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "CRIT_7": {
        "id": "CRIT_7",
        "name": "Узлы учёта - данные потребления",
        "status": "not_started",
        "priority": "P0",
        "category": "critical",
        "area": "Данные",
        "stage": "Блоки импорта"
    },
    "CRIT_8": {
        "id": "CRIT_8",
        "name": "Акты балансов - обработка",
        "status": "partial",
        "priority": "P0",
        "category": "critical",
        "area": "Данные",
        "stage": "Блоки импорта"
    },
    "CRIT_9": {
        "id": "CRIT_9",
        "name": "Расчёты балансов",
        "status": "not_started",
        "priority": "P0",
        "category": "critical",
        "area": "Функциональность",
        "stage": "Stage 2"
    },
    # Важные задачи (10)
    "IMPORTANT_1": {
        "id": "IMPORTANT_1",
        "name": "Данные предприятия - полнота",
        "status": "partial",
        "priority": "P1",
        "category": "important",
        "area": "Данные",
        "stage": "Stage 1"
    },
    "IMPORTANT_2": {
        "id": "IMPORTANT_2",
        "name": "Газ - по месяцам",
        "status": "not_started",
        "priority": "P1",
        "category": "important",
        "area": "Данные",
        "stage": "Блоки импорта"
    },
    "IMPORTANT_3": {
        "id": "IMPORTANT_3",
        "name": "Вода - импорт в БД",
        "status": "partial",
        "priority": "P1",
        "category": "important",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "IMPORTANT_4": {
        "id": "IMPORTANT_4",
        "name": "Топливо/ГСМ - обработка",
        "status": "partial",
        "priority": "P1",
        "category": "important",
        "area": "Данные",
        "stage": "Блоки импорта"
    },
    "IMPORTANT_5": {
        "id": "IMPORTANT_5",
        "name": "Оборудование - стоимость",
        "status": "not_started",
        "priority": "P1",
        "category": "important",
        "area": "Данные",
        "stage": "Stage 2"
    },
    "IMPORTANT_6": {
        "id": "IMPORTANT_6",
        "name": "Оболочка зданий - импорт в БД",
        "status": "partial",
        "priority": "P1",
        "category": "important",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "IMPORTANT_7": {
        "id": "IMPORTANT_7",
        "name": "Потери электроэнергии",
        "status": "not_started",
        "priority": "P1",
        "category": "important",
        "area": "Данные",
        "stage": "Stage 2"
    },
    "IMPORTANT_8": {
        "id": "IMPORTANT_8",
        "name": "Экологические данные - обработка",
        "status": "partial",
        "priority": "P1",
        "category": "important",
        "area": "Данные",
        "stage": "Stage 2"
    },
    "IMPORTANT_9": {
        "id": "IMPORTANT_9",
        "name": "OCR модуль - интеграция",
        "status": "partial",
        "priority": "P1",
        "category": "important",
        "area": "Функциональность",
        "stage": "Stage 2"
    },
    "IMPORTANT_10": {
        "id": "IMPORTANT_10",
        "name": "Система ручной идентификации",
        "status": "not_started",
        "priority": "P1",
        "category": "important",
        "area": "Функциональность",
        "stage": "Stage 2"
    },
    # Рекомендуемые задачи (5)
    "RECOMMENDED_1": {
        "id": "RECOMMENDED_1",
        "name": "Категория энергоэффективности",
        "status": "completed",
        "priority": "P2",
        "category": "recommended",
        "area": "Структура данных",
        "stage": "Stage 2",
        "assigned_to": "agent_1"
    },
    "RECOMMENDED_2": {
        "id": "RECOMMENDED_2",
        "name": "Экологические нормативы",
        "status": "completed",
        "priority": "P2",
        "category": "recommended",
        "area": "Структура данных",
        "stage": "Stage 2",
        "assigned_to": "agent_1"
    },
    "RECOMMENDED_3": {
        "id": "RECOMMENDED_3",
        "name": "План экологических мероприятий",
        "status": "completed",
        "priority": "P2",
        "category": "recommended",
        "area": "Парсер",
        "stage": "Stage 2",
        "assigned_to": "agent_1"
    },
    "RECOMMENDED_4": {
        "id": "RECOMMENDED_4",
        "name": "Централизованные формулы",
        "status": "completed",
        "priority": "P2",
        "category": "recommended",
        "area": "Функциональность",
        "stage": "Stage 2",
        "assigned_to": "agent_1"
    },
    "RECOMMENDED_5": {
        "id": "RECOMMENDED_5",
        "name": "Readiness-проверка",
        "status": "completed",
        "priority": "P2",
        "category": "recommended",
        "area": "QA",
        "stage": "Stage 2",
        "assigned_to": "agent_1"
    },
    # Блоки импорта (7)
    "B4": {
        "id": "B4",
        "name": "Импорт электроэнергии",
        "status": "pending",
        "priority": "P0",
        "category": "import_block",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "B5": {
        "id": "B5",
        "name": "Импорт газа",
        "status": "pending",
        "priority": "P0",
        "category": "import_block",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "B6": {
        "id": "B6",
        "name": "Импорт воды",
        "status": "pending",
        "priority": "P1",
        "category": "import_block",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "B7": {
        "id": "B7",
        "name": "Импорт тепла",
        "status": "pending",
        "priority": "P0",
        "category": "import_block",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "B8": {
        "id": "B8",
        "name": "Импорт оборудования",
        "status": "pending",
        "priority": "P0",
        "category": "import_block",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "B9": {
        "id": "B9",
        "name": "Импорт узлов учёта",
        "status": "pending",
        "priority": "P0",
        "category": "import_block",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    "B10": {
        "id": "B10",
        "name": "Импорт ограждающих конструкций",
        "status": "pending",
        "priority": "P1",
        "category": "import_block",
        "area": "Инфраструктура",
        "stage": "Блоки импорта"
    },
    # Stage 1 задачи (6)
    "STAGE1_1": {
        "id": "STAGE1_1",
        "name": "Веб-интерфейс загрузки файлов",
        "status": "completed",
        "priority": "P0",
        "category": "stage1",
        "area": "UI",
        "stage": "Stage 1",
        "assigned_to": "agent_1"
    },
    "STAGE1_2": {
        "id": "STAGE1_2",
        "name": "Парсинг Excel/PDF/Word",
        "status": "completed",
        "priority": "P0",
        "category": "stage1",
        "area": "Функциональность",
        "stage": "Stage 1",
        "assigned_to": "agent_1"
    },
    "STAGE1_3": {
        "id": "STAGE1_3",
        "name": "Редактирование данных",
        "status": "completed",
        "priority": "P0",
        "category": "stage1",
        "area": "UI",
        "stage": "Stage 1",
        "assigned_to": "agent_1"
    },
    "STAGE1_4": {
        "id": "STAGE1_4",
        "name": "Сохранение в SQLite БД",
        "status": "completed",
        "priority": "P0",
        "category": "stage1",
        "area": "Инфраструктура",
        "stage": "Stage 1",
        "assigned_to": "agent_1"
    },
    "STAGE1_5": {
        "id": "STAGE1_5",
        "name": "Привязка к предприятиям",
        "status": "completed",
        "priority": "P0",
        "category": "stage1",
        "area": "Инфраструктура",
        "stage": "Stage 1",
        "assigned_to": "agent_1"
    },
    "STAGE1_6": {
        "id": "STAGE1_6",
        "name": "Дедупликация загрузок",
        "status": "completed",
        "priority": "P0",
        "category": "stage1",
        "area": "Функциональность",
        "stage": "Stage 1",
        "assigned_to": "agent_1"
    },
    # Stage 2 задачи (выборочно, основные)
    "STAGE2_7_1": {
        "id": "STAGE2_7_1",
        "name": "Обновить DEVELOPMENT_PLAN_2025.md",
        "status": "in_progress",
        "priority": "P1",
        "category": "stage2",
        "area": "Документация",
        "stage": "Stage 2"
    },
    "STAGE2_7_2": {
        "id": "STAGE2_7_2",
        "name": "Создать тестовый чеклист",
        "status": "in_progress",
        "priority": "P1",
        "category": "stage2",
        "area": "QA",
        "stage": "Stage 2"
    },
    "STAGE2_7_3": {
        "id": "STAGE2_7_3",
        "name": "Финальное тестирование",
        "status": "in_progress",
        "priority": "P1",
        "category": "stage2",
        "area": "QA",
        "stage": "Stage 2"
    }
}

# Рекомендации экспертов для каждой задачи
EXPERT_RECOMMENDATIONS = {
    "CRIT_1": {
        "data_scientist": "Запросить у предприятия",
        "software_engineer": "Использовать OCR для извлечения из PDF актов",
        "qa_engineer": "Валидировать после получения"
    },
    "CRIT_2": {
        "data_scientist": "Критично для расчётов",
        "software_engineer": "Парсить из коммерческих отчётов",
        "ml_engineer": "Использовать специализированные промпты для разделения"
    },
    "CRIT_3": {
        "data_scientist": "Дополнить недостающие кварталы",
        "software_engineer": "Использовать агрегатор для объединения данных",
        "qa_engineer": "Проверить целостность временных рядов"
    },
    "CRIT_4": {
        "software_engineer": "Реализовать batch-импорт в aggregated_data",
        "data_scientist": "Добавить валидацию перед импортом",
        "qa_engineer": "Тестировать на больших объёмах"
    },
    "CRIT_5": {
        "software_engineer": "Использовать существующий парсер equipment_parser.py",
        "data_scientist": "Проверить полноту данных",
        "qa_engineer": "Валидировать структуру JSON"
    },
    "CRIT_6": {
        "software_engineer": "Импортировать из schetchiki.json",
        "data_scientist": "Связать с данными потребления",
        "qa_engineer": "Проверить соответствие узлов и данных"
    },
    "CRIT_7": {
        "data_scientist": "Критично для энергобаланса",
        "software_engineer": "Использовать OCR для извлечения из актов",
        "ml_engineer": "Специализированные промпты для таблиц учёта"
    },
    "CRIT_8": {
        "software_engineer": "Распаковать и обработать через OCR модуль",
        "ml_engineer": "Использовать Gemini Vision (95% confidence)",
        "qa_engineer": "Тестировать на нескольких файлах сначала"
    },
    "CRIT_9": {
        "data_scientist": "Использовать централизованные формулы",
        "software_engineer": "Интегрировать в fill_energy_passport.py",
        "qa_engineer": "Проверить корректность расчётов на эталонных данных"
    },
    "B4": {
        "software_engineer": "Критично, использовать OCR для PDF",
        "data_scientist": "Валидировать данные",
        "ml_engineer": "Специализированные промпты"
    },
    "B5": {
        "software_engineer": "Использовать агрегатор gaz.xlsx",
        "data_scientist": "Проверить единицы измерения",
        "qa_engineer": "Тестировать на реальных данных"
    },
    "B6": {
        "software_engineer": "Использовать агрегатор voda.xlsx",
        "data_scientist": "Группировать по кварталам",
        "qa_engineer": "Валидировать объёмы"
    },
    "B7": {
        "software_engineer": "Использовать агрегатор otoplenie.xlsx",
        "data_scientist": "Проверить данные по зданиям",
        "qa_engineer": "Валидировать площади"
    },
    "B8": {
        "software_engineer": "Использовать equipment_parser.py",
        "data_scientist": "Проверить полноту данных",
        "qa_engineer": "Валидировать структуру"
    },
    "B9": {
        "software_engineer": "Использовать парсер schetchiki.xlsx",
        "data_scientist": "Связать с данными потребления",
        "qa_engineer": "Проверить соответствие"
    },
    "B10": {
        "software_engineer": "Использовать building_envelope_parser.py",
        "data_scientist": "Проверить нормализацию",
        "qa_engineer": "Валидировать теплопотери"
    }
}


def populate_tasks():
    """Заполняет единый файл задач всеми задачами"""
    # Загружаем существующий файл или создаём новый
    if TASKS_FILE.exists():
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0",
                "total_tasks": 0,
                "description": "Единый файл задач проекта EAIP - источник правды для всех агентов"
            },
            "tasks": {}
        }
    
    # Добавляем/обновляем задачи
    for task_id, task_data in ALL_TASKS.items():
        if task_id not in data["tasks"]:
            # Создаём новую задачу
            full_task = {
                **task_data,
                "assigned_to": task_data.get("assigned_to"),
                "locked_by": None,
                "locked_until": None,
                "solutions": [],
                "execution": [],
                "history": [{
                    "timestamp": datetime.now().isoformat(),
                    "agent": "system",
                    "action": "created",
                    "details": "Задача добавлена в единый файл"
                }],
                "expert_recommendations": EXPERT_RECOMMENDATIONS.get(task_id, {})
            }
            data["tasks"][task_id] = full_task
        else:
            # Обновляем существующую задачу (сохраняем решения и выполнение)
            existing = data["tasks"][task_id]
            existing.update({
                "name": task_data["name"],
                "priority": task_data["priority"],
                "category": task_data["category"],
                "area": task_data["area"],
                "stage": task_data["stage"]
            })
            # Обновляем статус только если он не был изменён агентом
            if existing.get("status") == "not_started" or existing.get("status") == "pending":
                existing["status"] = task_data["status"]
    
    # Обновляем метаданные
    data["metadata"]["total_tasks"] = len(data["tasks"])
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    
    # Сохраняем
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Файл задач обновлён: {len(data['tasks'])} задач")
    return data


if __name__ == "__main__":
    populate_tasks()

