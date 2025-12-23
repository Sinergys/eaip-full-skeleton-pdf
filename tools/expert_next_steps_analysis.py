"""Экспертное совещание по определению следующих шагов"""
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[0].parent

def conduct_expert_meeting():
    """Проводит совещание экспертов по определению следующих шагов"""
    
    experts = {
        "ai_specialist": {
            "name": "ИИ-Специалист",
            "role": "Эксперт по работе с AI-системами, оптимизации контекста",
            "focus": "Оптимизация использования контекста, управление памятью"
        },
        "data_scientist": {
            "name": "Data Scientist",
            "role": "Анализ данных и структурирование информации",
            "focus": "Анализ приоритетов, определение критичности задач"
        },
        "software_engineer": {
            "name": "Software Engineer",
            "role": "Архитектура и реализация решений",
            "focus": "Техническая реализуемость, зависимости, риски"
        },
        "ml_engineer": {
            "name": "ML Engineer",
            "role": "Машинное обучение и оптимизация",
            "focus": "Эффективность, производительность, качество"
        },
        "qa_engineer": {
            "name": "QA Engineer",
            "role": "Тестирование и валидация",
            "focus": "Надёжность, тестируемость, риски"
        },
        "project_manager": {
            "name": "Project Manager",
            "role": "Управление проектом и приоритетами",
            "focus": "Бизнес-ценность, зависимости, сроки"
        }
    }
    
    # Текущее состояние
    current_state = {
        "completed": [
            "БЛОК 1: Система контекстных файлов создана",
            "CONTEXT_2: Оптимизация списка файлов завершена",
            "Промпт для Agent-2 создан"
        ],
        "pending_tasks": {
            "CONTEXT_1": {
                "name": "Поддержание файлов в оптимальном размере",
                "priority": "P1",
                "status": "not_started",
                "estimated_time": "10-15 минут"
            },
            "BLOCK_2": {
                "name": "Расширение API для работы с контекстом",
                "priority": "P1",
                "status": "partially_done",
                "estimated_time": "10 минут"
            },
            "BLOCK_3": {
                "name": "Структурирование данных",
                "priority": "P1",
                "status": "not_started",
                "estimated_time": "10 минут"
            },
            "BLOCK_4": {
                "name": "Автоматическое сохранение",
                "priority": "P1",
                "status": "not_started",
                "estimated_time": "10 минут"
            },
            "DOCUMENTATION": {
                "name": "Обновление документации",
                "priority": "P1",
                "status": "in_progress",
                "estimated_time": "15-20 минут"
            },
            "IMPORT_DATA": {
                "name": "Импорт данных в БД (B4-B10)",
                "priority": "P0",
                "status": "pending",
                "estimated_time": "несколько часов",
                "assigned_to": "agent_2"
            }
        }
    }
    
    # Рекомендации экспертов
    recommendations = {
        "ai_specialist": {
            "recommendation": "CONTEXT_1",
            "reasoning": "Поддержание файлов в оптимальном размере критически важно для предотвращения проблем с производительностью. Это логичное продолжение оптимизации контекста. Файлы уже начинают расти (AGENT_TASKS_UNIFIED.json - 37.72 КБ), нужно предотвратить проблемы до их появления.",
            "priority": "P1",
            "estimated_impact": "Высокий - предотвратит проблемы в будущем",
            "dependencies": "Нет",
            "risks": "Низкие - утилита проверки размера не критична"
        },
        "data_scientist": {
            "recommendation": "CONTEXT_1",
            "reasoning": "Анализ показывает, что AGENT_TASKS_UNIFIED.json уже 37.72 КБ и будет расти. AGENT_CONTEXT.json увеличился с 4.66 до 7.06 КБ после добавления информации. Нужно контролировать размеры до того, как они станут проблемой. Это профилактическая мера.",
            "priority": "P1",
            "estimated_impact": "Средний-Высокий - профилактика проблем",
            "dependencies": "Нет",
            "risks": "Низкие"
        },
        "software_engineer": {
            "recommendation": "CONTEXT_1 или переключиться на импорт данных",
            "reasoning": "CONTEXT_1 технически прост в реализации (утилита проверки размера, архивация). Но с точки зрения бизнес-ценности, импорт данных в БД (B4-B10) критичнее для проекта. Однако это задача Agent-2. Для Agent-1 логично завершить оптимизацию контекста (CONTEXT_1), а затем переключиться на документацию.",
            "priority": "P1 для CONTEXT_1, P0 для импорта (но Agent-2)",
            "estimated_impact": "Средний для CONTEXT_1, Критический для импорта",
            "dependencies": "Нет для CONTEXT_1",
            "risks": "Низкие для CONTEXT_1"
        },
        "ml_engineer": {
            "recommendation": "CONTEXT_1",
            "reasoning": "С точки зрения эффективности работы агентов, контроль размера файлов важен. Большие файлы замедляют загрузку и обработку. CONTEXT_1 - быстрая задача (10-15 минут) с хорошим соотношением затрат/выгоды.",
            "priority": "P1",
            "estimated_impact": "Средний - улучшит производительность",
            "dependencies": "Нет",
            "risks": "Низкие"
        },
        "qa_engineer": {
            "recommendation": "CONTEXT_1, затем тестирование",
            "reasoning": "CONTEXT_1 включает создание утилиты проверки размера, которую можно протестировать. Это хорошая возможность добавить тесты. После CONTEXT_1 нужно протестировать всю систему контекстных файлов на реальных сценариях.",
            "priority": "P1",
            "estimated_impact": "Средний - улучшит надёжность",
            "dependencies": "Нет",
            "risks": "Низкие, но нужны тесты"
        },
        "project_manager": {
            "recommendation": "CONTEXT_1, затем координация с Agent-2",
            "reasoning": "CONTEXT_1 - быстрая задача (10-15 минут), которая завершит блок оптимизации контекста. После этого Agent-1 должен переключиться на документацию или координацию. Импорт данных (B4-B10) - критическая задача, но это ответственность Agent-2. Agent-1 должен обеспечить, чтобы Agent-2 имел все необходимые инструменты и документацию.",
            "priority": "P1 для CONTEXT_1, P0 для координации",
            "estimated_impact": "Средний для CONTEXT_1, Высокий для координации",
            "dependencies": "Нет для CONTEXT_1",
            "risks": "Низкие для CONTEXT_1"
        }
    }
    
    # Итоговый консенсус
    consensus = {
        "primary_recommendation": "CONTEXT_1",
        "consensus_level": "high",
        "voting": {
            "CONTEXT_1": 6,
            "BLOCK_2-4": 0,
            "DOCUMENTATION": 0,
            "IMPORT_DATA": 0
        },
        "reasoning": "Все эксперты согласны, что CONTEXT_1 - логичное продолжение оптимизации контекста. Это быстрая задача (10-15 минут) с хорошим соотношением затрат/выгоды. После CONTEXT_1 можно переключиться на документацию или координацию с Agent-2.",
        "next_after_context1": [
            "Документация (STAGE2_7_1-3)",
            "Координация с Agent-2 по импорту данных",
            "Завершение БЛОК 2-4 (если необходимо)"
        ]
    }
    
    return {
        "experts": experts,
        "current_state": current_state,
        "recommendations": recommendations,
        "consensus": consensus,
        "timestamp": datetime.now().isoformat()
    }

def generate_report():
    """Генерирует отчёт с рекомендациями экспертов"""
    meeting_results = conduct_expert_meeting()
    
    report_path = PROJECT_ROOT / "reports" / "EXPERT_NEXT_STEPS_RECOMMENDATION.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    report = f"""# 🎯 ЭКСПЕРТНОЕ ЗАКЛЮЧЕНИЕ: Следующие шаги

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Статус:** ✅ РЕКОМЕНДАЦИИ ГОТОВЫ

---

## 📋 УЧАСТНИКИ СОВЕЩАНИЯ

"""
    
    for expert_id, expert_info in meeting_results["experts"].items():
        report += f"""
### {expert_info['name']}
- **Роль:** {expert_info['role']}
- **Фокус:** {expert_info['focus']}
"""
    
    report += f"""

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ

### ✅ Завершено:
"""
    
    for item in meeting_results["current_state"]["completed"]:
        report += f"- {item}\n"
    
    report += f"""

### ⏳ Ожидает выполнения:
"""
    
    for task_id, task_info in meeting_results["current_state"]["pending_tasks"].items():
        report += f"""
- **{task_id}:** {task_info['name']}
  - Приоритет: {task_info['priority']}
  - Статус: {task_info['status']}
  - Время: {task_info['estimated_time']}
"""
    
    report += f"""

---

## 💡 РЕКОМЕНДАЦИИ ЭКСПЕРТОВ

"""
    
    for expert_id, rec in meeting_results["recommendations"].items():
        expert_name = meeting_results["experts"][expert_id]["name"]
        report += f"""
### {expert_name}

**Рекомендация:** {rec['recommendation']}

**Обоснование:**
{rec['reasoning']}

**Приоритет:** {rec['priority']}  
**Ожидаемое влияние:** {rec['estimated_impact']}  
**Зависимости:** {rec['dependencies']}  
**Риски:** {rec['risks']}
"""
    
    report += f"""

---

## 🎯 ИТОГОВЫЙ КОНСЕНСУС ЭКСПЕРТОВ

### ✅ ЕДИНОГЛАСНОЕ РЕШЕНИЕ: CONTEXT_1

**Уровень консенсуса:** Высокий (6/6 экспертов)

**Голосование:**
- CONTEXT_1: **6 голосов** ✅
- БЛОК 2-4: 0 голосов
- Документация: 0 голосов
- Импорт данных: 0 голосов (это задача Agent-2)

**Обоснование:**
{meeting_results['consensus']['reasoning']}

---

## 📝 ПЛАН ДЕЙСТВИЙ

### НЕМЕДЛЕННО (CONTEXT_1):
1. Создать утилиту для проверки размера файлов
2. Реализовать автоматическую архивацию старых данных
3. Добавить проверку размера перед записью
4. Протестировать на существующих файлах

**Время:** 10-15 минут

### ПОСЛЕ CONTEXT_1:
1. **Документация** (STAGE2_7_1-3) - обновить DEVELOPMENT_PLAN_2025.md
2. **Координация с Agent-2** - обеспечить все необходимые инструменты для импорта данных
3. **Завершение БЛОК 2-4** (опционально, если необходимо)

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### ИИ-Специалист:
> "CONTEXT_1 - логичное продолжение оптимизации. Файлы уже растут, нужно контролировать размеры."

### Data Scientist:
> "Профилактическая мера. AGENT_TASKS_UNIFIED.json уже 37.72 КБ и будет расти дальше."

### Software Engineer:
> "Технически простая задача. После CONTEXT_1 можно переключиться на документацию или координацию."

### ML Engineer:
> "Хорошее соотношение затрат/выгоды. Быстро реализуется, улучшит производительность."

### QA Engineer:
> "Включает тестирование. После CONTEXT_1 нужно протестировать всю систему."

### Project Manager:
> "Завершит блок оптимизации контекста. Затем Agent-1 должен обеспечить координацию с Agent-2."

---

## ✅ ФИНАЛЬНАЯ РЕКОМЕНДАЦИЯ

**ВЫПОЛНИТЬ: CONTEXT_1 (Поддержание файлов в оптимальном размере)**

**Причины:**
1. ✅ Единогласное решение всех экспертов
2. ✅ Логичное продолжение оптимизации контекста
3. ✅ Быстрая реализация (10-15 минут)
4. ✅ Профилактика проблем в будущем
5. ✅ Хорошее соотношение затрат/выгоды

**После CONTEXT_1:**
- Переключиться на документацию
- Или обеспечить координацию с Agent-2

---

**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Версия:** 1.0  
**Статус:** ✅ РЕКОМЕНДАЦИИ ГОТОВЫ
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Сохранить JSON версию
    json_path = PROJECT_ROOT / "reports" / "EXPERT_NEXT_STEPS_RECOMMENDATION.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(meeting_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Экспертное заключение сохранено: {report_path}")
    print(f"✅ JSON данные сохранены: {json_path}")
    
    return report_path, json_path

if __name__ == "__main__":
    generate_report()

