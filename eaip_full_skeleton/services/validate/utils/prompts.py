"""
AI prompts for Word Document Validator.
Contains system prompts and prompt templates for Ollama and DeepSeek.
"""
from typing import Dict, Any


# ============ DeepSeek System Prompt ============

DEEPSEEK_SYSTEM_PROMPT = """Вы - главный энергоаудитор с экспертизой в ПКМ №690 Республики Узбекистан.

Ваша задача:
1. Проверить текст на соответствие требованиям ПКМ 690
2. Исправить семантические, логические, стилистические и орфографические ошибки
3. Сформировать конкретные рекомендации по доработке

КРИТИЧЕСКИ ВАЖНО:
- Сохраняйте ВСЕ маркеры вида [[OBJ_001]], [[SECTION_INTERRUPTED_AT_CHAPTER_X]]
- Строго следуйте формату ответа
- Рекомендации должны быть конкретными и actionable"""


# ============ DeepSeek Prompt Template ============

def create_deepseek_prompt(
    chunk_text: str,
    pkm_requirements: str,
    ollama_report: Dict[str, Any],
) -> str:
    """
    Формирование промпта для DeepSeek API (блок B, раздел 3.1.5 ТЗ).
    
    Args:
        chunk_text: Текст текущего чанка с маркерами
        pkm_requirements: Точные текстовые требования ПКМ 690
        ollama_report: JSON отчёт от Ollama {"issues": [...], "fixes": [...]}
    
    Returns:
        Полный промпт для отправки в DeepSeek
    """
    
    prompt = f"""
{DEEPSEEK_SYSTEM_PROMPT}

## ТРЕБОВАНИЯ ПКМ №690:

{pkm_requirements}

---

## ПРЕДВАРИТЕЛЬНЫЙ АНАЛИЗ (Ollama):

**Обнаруженные проблемы:**
{_format_ollama_issues(ollama_report.get('issues', []))}

**Предложенные исправления:**
{_format_ollama_fixes(ollama_report.get('fixes', []))}

---

## ТЕКСТ ДЛЯ ПРОВЕРКИ:

{chunk_text}

---

## ТРЕБОВАНИЯ К ФОРМАТУ ОТВЕТА:

Ваш ответ ДОЛЖЕН строго следовать этому формату:

[START_OF_CORRECTED_TEXT]
<Исправленный текст чанка. Все маркеры [[OBJ_...]], [[SECTION_...]] ОБЯЗАТЕЛЬНО сохранены>
[END_OF_CORRECTED_TEXT]

---
[CHUNK_RECOMMENDATIONS]
1. <Конкретная рекомендация 1>
2. <Конкретная рекомендация 2>
...
[END_OF_RECOMMENDATIONS]

ВНИМАНИЕ: Если в рекомендациях используете примеры с вымышленными данными, обязательно пометьте: [ВНИМАНИЕ: ПРИМЕР С ВЫМЫШЛЕННЫМИ ДАННЫМИ]
"""
    
    return prompt.strip()


def _format_ollama_issues(issues: list) -> str:
    """Форматирование списка проблем от Ollama."""
    if not issues:
        return "Критических проблем не обнаружено."
    
    return "\n".join([f"• {issue}" for issue in issues])


def _format_ollama_fixes(fixes: list) -> str:
    """Форматирование списка исправлений от Ollama."""
    if not fixes:
        return "Автоматических исправлений не предложено."
    
    return "\n".join([f"• {fix}" for fix in fixes])


# ============ Ollama System Prompt ============

OLLAMA_SYSTEM_PROMPT = """Вы - помощник энергоаудитора, специализирующийся на предварительной проверке текстов.

Ваша задача:
1. Выявить орфографические ошибки
2. Обнаружить стилистические проблемы
3. Найти внутренние логические противоречия
4. Предложить конкретные исправления

Отвечайте СТРОГО в формате JSON:
{
  "issues": ["проблема 1", "проблема 2", ...],
  "fixes": ["исправление 1", "исправление 2", ...]
}

НЕ добавляйте никаких комментариев вне JSON структуры."""


def create_ollama_prompt(chunk_text: str) -> str:
    """
    Формирование промпта для Ollama (локальная AI).
    
    Args:
        chunk_text: Текст чанка для анализа
    
    Returns:
        Промпт для Ollama
    """
    return f"""{OLLAMA_SYSTEM_PROMPT}

Проанализируйте следующий текст:

{chunk_text}

Верните результат в формате JSON."""
