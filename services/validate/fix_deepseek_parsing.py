"""
Патч для ai_processor.py - более гибкий парсинг DeepSeek.
"""

def _parse_deepseek_response_flexible(response_text: str) -> tuple[str, list[str]]:
    """
    ГИБКИЙ парсинг ответа DeepSeek.
    Пробует несколько стратегий извлечения текста.
    """
    import re
    import logging
    from utils.exceptions import DeepSeekFormatError
    from core.constants import (
        START_CORRECTED_TEXT,
        END_CORRECTED_TEXT,
        START_RECOMMENDATIONS,
        END_RECOMMENDATIONS
    )
    
    logger = logging.getLogger(__name__)
    
    # Логируем сырой ответ для дебага
    logger.debug(f"DeepSeek raw response (first 500 chars): {response_text[:500]}")
    
    corrected_text = None
    recommendations = []
    
    # === СТРАТЕГИЯ 1: Точные маркеры ===
    try:
        if START_CORRECTED_TEXT in response_text and END_CORRECTED_TEXT in response_text:
            start_idx = response_text.index(START_CORRECTED_TEXT) + len(START_CORRECTED_TEXT)
            end_idx = response_text.index(END_CORRECTED_TEXT)
            corrected_text = response_text[start_idx:end_idx].strip()
            logger.info("✅ Strategy 1: Found exact markers")
    except Exception as e:
        logger.warning(f"Strategy 1 failed: {e}")
    
    # === СТРАТЕГИЯ 2: Регулярки для маркеров (без точных скобок) ===
    if not corrected_text:
        try:
            # Ищем варианты: [START, START_OF, CORRECTED_TEXT и т.д.
            pattern = r'\[?START[_\s]OF[_\s]CORRECTED[_\s]TEXT\]?(.*?)\[?END[_\s]OF[_\s]CORRECTED[_\s]TEXT\]?'
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                corrected_text = match.group(1).strip()
                logger.info("✅ Strategy 2: Found with regex")
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}")
    
    # === СТРАТЕГИЯ 3: Берём всё до секции рекомендаций ===
    if not corrected_text:
        try:
            # Ищем секцию рекомендаций
            rec_markers = [
                'RECOMMENDATIONS',
                'РЕКОМЕНДАЦИИ',
                'CHUNK_RECOMMENDATIONS',
                '---'
            ]
            
            split_idx = len(response_text)
            for marker in rec_markers:
                idx = response_text.find(marker)
                if idx > 0 and idx < split_idx:
                    split_idx = idx
            
            corrected_text = response_text[:split_idx].strip()
            
            # Убираем возможные начальные маркеры
            for marker in ['[START', 'START_OF', 'CORRECTED']:
                if corrected_text.startswith(marker):
                    corrected_text = corrected_text[len(marker):].strip()
            
            logger.info("✅ Strategy 3: Took text before recommendations")
        except Exception as e:
            logger.warning(f"Strategy 3 failed: {e}")
    
    # === СТРАТЕГИЯ 4: Весь текст (last resort) ===
    if not corrected_text:
        corrected_text = response_text.strip()
        logger.warning("⚠️ Strategy 4: Using entire response as corrected text")
    
    # === Извлечение рекомендаций (гибко) ===
    try:
        # Попытка 1: точные маркеры
        if START_RECOMMENDATIONS in response_text and END_RECOMMENDATIONS in response_text:
            rec_start = response_text.index(START_RECOMMENDATIONS) + len(START_RECOMMENDATIONS)
            rec_end = response_text.index(END_RECOMMENDATIONS)
            rec_text = response_text[rec_start:rec_end].strip()
        else:
            # Попытка 2: ищем после "---" или "RECOMMENDATIONS"
            for marker in ['---', 'RECOMMENDATIONS', 'РЕКОМЕНДАЦИИ']:
                if marker in response_text:
                    idx = response_text.index(marker) + len(marker)
                    rec_text = response_text[idx:].strip()
                    break
            else:
                rec_text = ""
        
        # Парсинг списка
        if rec_text:
            lines = rec_text.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    # Убираем нумерацию
                    cleaned = re.sub(r'^[\d\.\-\•\*\[\]]+\s*', '', line)
                    # Убираем END маркеры
                    cleaned = re.sub(r'\[?END.*?\]?', '', cleaned).strip()
                    if cleaned and len(cleaned) > 10:  # Минимум 10 символов
                        recommendations.append(cleaned)
    
    except Exception as e:
        logger.warning(f"Failed to extract recommendations: {e}")
    
    # === Валидация ===
    if not corrected_text or len(corrected_text) < 10:
        raise DeepSeekFormatError(
            f"Failed to extract corrected text. Response length: {len(response_text)}"
        )
    
    logger.info(
        f"✅ Parsed: {len(corrected_text)} chars text, "
        f"{len(recommendations)} recommendations"
    )
    
    return corrected_text, recommendations


# Инструкция по применению:
# 1. Открой services/ai_processor.py
# 2. Найди функцию _parse_deepseek_response (строка ~370)
# 3. Замени её на _parse_deepseek_response_flexible выше
# 4. Перезапусти сервис
