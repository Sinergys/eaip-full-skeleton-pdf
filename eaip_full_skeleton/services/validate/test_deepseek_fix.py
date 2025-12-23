#!/usr/bin/env python3
"""
Тест для проверки исправления DeepSeek парсинга с fallback стратегиями.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_processor import AIProcessor
from core.constants import START_CORRECTED_TEXT, END_CORRECTED_TEXT
import logging

# Настройка логирования для теста
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fallback_parsing():
    """Тест различных сценариев ответов DeepSeek."""
    
    # Создаем экземпляр AIProcessor (без реальных API вызовов)
    processor = AIProcessor(
        ollama_url="http://localhost:11434",
        deepseek_api_key="test-key",
        deepseek_url="https://api.deepseek.com/v1/chat/completions"
    )
    
    test_cases = [
        {
            "name": "Case 1: Отсутствуют маркеры (должен сработать Strategy 4)",
            "response": """
            Это исправленный текст документа.
            
            Рекомендации:
            1. Добавить недостающую информацию
            2. Исправить формулировки
            """
        },
        {
            "name": "Case 2: Частичные маркеры (должен сработать Strategy 3)",
            "response": """
            [START_OF_CORRECTED_TEXT]
            Это исправленный текст без конечного маркера.
            
            RECOMMENDATIONS
            1. Первая рекомендация
            2. Вторая рекомендация
            """
        },
        {
            "name": "Case 3: Полные маркеры (должен сработать Strategy 1)",
            "response": """
            [START_OF_CORRECTED_TEXT]
            Это текст с полными маркерами.
            [END_OF_CORRECTED_TEXT]
            
            [CHUNK_RECOMMENDATIONS]
            1. Рекомендация один
            2. Рекомендация два
            [END_OF_RECOMMENDATIONS]
            """
        },
        {
            "name": "Case 4: Маркеры без скобок (должен сработать Strategy 2)",
            "response": """
            START_OF_CORRECTED_TEXT
            Это текст с маркерами без скобок.
            END_OF_CORRECTED_TEXT
            
            ---
            RECOMMENDATIONS
            1. Тестовая рекомендация
            """
        }
    ]
    
    print("🧪 ТЕСТИРОВАНИЕ DEEPSEEK FALLBACK PARSING")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 {test_case['name']}")
        print("-" * 40)
        
        try:
            # Тестируем парсинг
            corrected_text, recommendations = processor._parse_deepseek_response(test_case['response'])
            
            print(f"✅ УСПЕХ:")
            print(f"   Текст: {len(corrected_text)} символов")
            print(f"   Рекомендации: {len(recommendations)} шт.")
            if recommendations:
                print(f"   Первая рекомендация: {recommendations[0][:50]}...")
            
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 ТЕСТ ЗАВЕРШЕН")

if __name__ == "__main__":
    test_fallback_parsing()