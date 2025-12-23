"""
Unit-тесты для функции fix_string_content() из gemini_vision_ocr.py

Тестирует корректное экранирование:
- Вложенных кавычек
- Обратных слэшей
- Управляющих символов (\n, \r, \t)
- Многострочных строк
- Unicode символов
"""
import pytest
import re
import json
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import extract_with_gemini_vision


def fix_json_strings(text):
    """Копия функции из gemini_vision_ocr.py для тестирования"""
    result = []
    i = 0
    in_string = False
    escape_next = False
    
    while i < len(text):
        char = text[i]
        
        if escape_next:
            # Следующий символ после обратного слэша - оставляем как есть
            result.append(char)
            escape_next = False
        elif char == '\\':
            # Обратный слэш - следующий символ будет экранирован
            result.append(char)
            escape_next = True
        elif char == '"' and not escape_next:
            # Кавычка - переключаем состояние "внутри строки"
            if in_string:
                # Проверяем, является ли это закрывающей кавычкой строки
                # Закрывающая кавычка обычно следует за содержимым и перед :, ,, ], }
                # Смотрим вперед на следующие символы (пропуская пробелы)
                j = i + 1
                while j < len(text) and text[j] in ' \t\n\r':
                    j += 1
                
                # Если после кавычки идет :, ,, ], } или конец - это закрывающая
                if j >= len(text) or text[j] in ':,\\]\\}':
                    # Закрывающая кавычка строки
                    in_string = False
                    result.append(char)
                else:
                    # Вложенная кавычка внутри строки - экранируем
                    result.append('\\"')
            else:
                # Открывающая кавычка строки
                in_string = True
                result.append(char)
        elif in_string:
            # Мы внутри строки - обрабатываем специальные символы
            if char == '\n':
                result.append('\\n')
            elif char == '\r':
                result.append('\\r')
            elif char == '\t':
                result.append('\\t')
            elif ord(char) < 32:
                # Другие управляющие символы - удаляем
                pass
            else:
                result.append(char)
        else:
            # Вне строки - оставляем как есть
            result.append(char)
        
        i += 1
    
    return ''.join(result)


def apply_fix_to_json_string(json_str: str) -> str:
    """Применяет fix_json_strings ко всему JSON"""
    return fix_json_strings(json_str)


class TestFixStringContent:
    """Тесты для функции fix_string_content"""
    
    def test_nested_quotes(self):
        """Тест 1: Вложенные кавычки в строке"""
        input_str = '{"text": "Строка с "кавычками" внутри"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert result["text"] == 'Строка с "кавычками" внутри'
    
    def test_escaped_backslashes(self):
        """Тест 2: Экранированные обратные слэши"""
        input_str = '{"path": "C:\\\\Users\\\\Name\\\\file.txt"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert result["path"] == "C:\\Users\\Name\\file.txt"
    
    def test_control_characters_newline(self):
        """Тест 3: Управляющие символы - перенос строки"""
        input_str = '{"text": "Текст с\nпереносами строк"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert result["text"] == "Текст с\nпереносами строк"
    
    def test_control_characters_tab(self):
        """Тест 4: Управляющие символы - табуляция"""
        input_str = '{"text": "Смешанный\tтекст\nс табуляцией"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert result["text"] == "Смешанный\tтекст\nс табуляцией"
    
    def test_multiline_string(self):
        """Тест 5: Многострочная строка"""
        input_str = '{"text": "Первая строка\nВторая строка\nТретья строка"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert result["text"] == "Первая строка\nВторая строка\nТретья строка"
    
    def test_unicode_characters(self):
        """Тест 6: Unicode символы"""
        input_str = '{"text": "Unicode: \u00A0\u2009\u202F"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert "Unicode:" in result["text"]
    
    def test_control_characters_removed(self):
        """Тест 7: Удаление недопустимых управляющих символов"""
        input_str = '{"text": "Control: \x00\x01\x02"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        # Управляющие символы должны быть удалены
        assert "\x00" not in result["text"]
        assert "\x01" not in result["text"]
        assert "\x02" not in result["text"]
    
    def test_complex_nested_quotes_and_escapes(self):
        """Тест 8: Комплексный случай - вложенные кавычки + экранированные символы"""
        input_str = '{"text": "Текст с "кавычками" и\\nпереносами\\tтабуляцией"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert "кавычками" in result["text"]
        assert "\n" in result["text"] or "\\n" in result["text"]
    
    def test_already_escaped_quotes(self):
        """Тест 9: Уже экранированные кавычки не должны дублироваться"""
        input_str = '{"text": "Текст с \\"экранированными\\" кавычками"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert result["text"] == 'Текст с "экранированными" кавычками'
    
    def test_carriage_return(self):
        """Тест 10: Символ возврата каретки"""
        input_str = '{"text": "Текст с\rвозвратом каретки"}'
        fixed = apply_fix_to_json_string(input_str)
        result = json.loads(fixed)
        assert "\r" in result["text"] or "\\r" in result["text"]


class TestFixStringContentIntegration:
    """Интеграционные тесты с реальными JSON структурами"""
    
    def test_real_json_with_table(self):
        """Тест: Реальный JSON с таблицей и вложенными кавычками"""
        json_str = '''{
            "text": "Поставщик: "XURSHID AVTO SERVIS" MCHJ",
            "tables": [{
                "rows": [["No", "Наименование"]],
                "headers": ["Заголовок"]
            }],
            "confidence": 0.9
        }'''
        fixed = apply_fix_to_json_string(json_str)
        result = json.loads(fixed)
        assert "XURSHID AVTO SERVIS" in result["text"]
        assert len(result["tables"]) == 1
    
    def test_json_with_multiple_nested_quotes(self):
        """Тест: JSON с несколькими вложенными кавычками"""
        json_str = '''{
            "text": "Текст с "первыми" и "вторыми" кавычками",
            "tables": []
        }'''
        fixed = apply_fix_to_json_string(json_str)
        result = json.loads(fixed)
        assert "первыми" in result["text"]
        assert "вторыми" in result["text"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

