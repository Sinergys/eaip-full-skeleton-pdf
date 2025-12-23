"""
Базовые тесты для модуля импорта нормативных документов
"""
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import tempfile
import json

# Добавляем путь к модулям
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_file_not_found():
    """Тест обработки отсутствующего файла"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Файл не найден")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Пытаемся импортировать несуществующий файл
        try:
            result = importer.import_normative_document("/nonexistent/file.pdf")
            print("❌ ОШИБКА: Должно было быть исключение FileNotFoundError")
            return False
        except FileNotFoundError as e:
            print(f"✅ Правильно обработана ошибка: {e}")
            return True
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
            return False
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False


def test_document_type_detection():
    """Тест автоматического определения типа документа"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Определение типа документа")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        test_cases = [
            ("pkm690.pdf", "PKM690"),
            ("690_постановление.doc", "PKM690"),
            ("ГОСТ_31427-2010.pdf", "GOST"),
            ("gost_12345.docx", "GOST"),
            ("СНиП_23-02-2003.pdf", "SNiP"),
            ("snip_heating.docx", "SNiP"),
            ("СанПиН_2.1.4.pdf", "SanPiN"),
            ("ПУЭ_7.pdf", "PUE"),
            ("ПТЭЭП_2024.doc", "PTEEP"),
            ("random_document.pdf", "normative"),
        ]
        
        all_passed = True
        for filename, expected_type in test_cases:
            detected = importer._detect_document_type(filename)
            if detected == expected_type:
                print(f"✅ {filename:30} -> {detected}")
            else:
                print(f"❌ {filename:30} -> {detected} (ожидалось: {expected_type})")
                all_passed = False
        
        return all_passed
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False


def test_file_hash_calculation():
    """Тест вычисления хеша файла"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Вычисление хеша файла")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            test_content = "Тестовое содержимое файла для проверки хеша"
            f.write(test_content)
            temp_path = f.name
        
        try:
            # Вычисляем хеш
            file_hash = importer._calculate_file_hash(temp_path)
            
            # Проверяем, что хеш - это строка из 40 символов (SHA1)
            if isinstance(file_hash, str) and len(file_hash) == 40:
                print(f"✅ Хеш вычислен корректно: {file_hash[:20]}...")
                
                # Проверяем, что хеш одинаковый для одного файла
                hash2 = importer._calculate_file_hash(temp_path)
                if file_hash == hash2:
                    print("✅ Хеш стабилен (одинаковый для одного файла)")
                    return True
                else:
                    print("❌ Хеш нестабилен")
                    return False
            else:
                print(f"❌ Неверный формат хеша: {file_hash}")
                return False
        finally:
            # Удаляем временный файл
            os.unlink(temp_path)
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_text_extraction_from_parsed_result():
    """Тест извлечения текста из результата парсинга"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Извлечение текста из результата парсинга")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Тест 1: PDF с текстом
        pdf_result = {
            "parsing": {
                "data": {
                    "text": "Это текст из PDF документа с формулой Q = A * B"
                }
            }
        }
        
        text = importer._extract_text_content(pdf_result)
        if "формулой Q = A * B" in text:
            print("✅ Текст из PDF извлечен корректно")
        else:
            print(f"❌ Текст из PDF не извлечен: {text[:50]}...")
            return False
        
        # Тест 2: Word с параграфами
        word_result = {
            "parsing": {
                "data": {
                    "paragraphs": [
                        {"text": "Параграф 1"},
                        {"text": "Параграф 2 с нормативом 0.15 кВт·ч/м²"}
                    ]
                }
            }
        }
        
        text = importer._extract_text_content(word_result)
        if "нормативом 0.15" in text:
            print("✅ Текст из Word извлечен корректно")
        else:
            print(f"❌ Текст из Word не извлечен: {text[:50]}...")
            return False
        
        # Тест 3: Excel с листами
        excel_result = {
            "parsing": {
                "data": {
                    "sheets": [
                        {
                            "name": "Лист1",
                            "rows": [
                                ["Колонка1", "Колонка2", "Значение"],
                                ["Энергия", "кВт·ч", "1000"]
                            ]
                        }
                    ]
                }
            }
        }
        
        text = importer._extract_text_content(excel_result)
        if "Энергия" in text and "1000" in text:
            print("✅ Текст из Excel извлечен корректно")
        else:
            print(f"❌ Текст из Excel не извлечен: {text[:50]}...")
            return False
        
        # Тест 4: Пустой результат
        empty_result = {}
        text = importer._extract_text_content(empty_result)
        if text == "":
            print("✅ Пустой результат обработан корректно")
        else:
            print(f"❌ Пустой результат обработан неверно: {text}")
            return False
        
        return True
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_extraction_without_ai():
    """Тест поведения при недоступном AI"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Извлечение правил без AI")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        # Создаем импортер с отключенным AI
        importer = NormativeImporter()
        importer.ai_parser = None
        
        parsed_result = {
            "parsing": {
                "data": {
                    "text": "Тестовый документ"
                }
            }
        }
        
        rules = importer._extract_rules_with_ai(parsed_result, 1, "PKM690")
        
        if rules == []:
            print("✅ Без AI возвращается пустой список правил")
            return True
        else:
            print(f"❌ Без AI должны быть пустые правила, получено: {len(rules)}")
            return False
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parse_ai_extraction_result():
    """Тест парсинга ответа AI"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Парсинг ответа AI")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Тест 1: Корректный JSON ответ
        ai_response = """
        {
            "rules": [
                {
                    "rule_type": "formula",
                    "description": "Расчет теплопотерь",
                    "formula": "Q = A * ΔT / R",
                    "parameters": {"A": "площадь, м²", "ΔT": "разница температур, °C"},
                    "numeric_value": null,
                    "unit": "кВт·ч",
                    "confidence": 0.9,
                    "references": []
                }
            ]
        }
        """
        
        rules = importer._parse_ai_extraction_result(ai_response, "PKM690")
        
        if len(rules) == 1 and rules[0]["rule_type"] == "formula":
            print("✅ Корректный JSON ответ распарсен")
        else:
            print(f"❌ Неверный парсинг: {rules}")
            return False
        
        # Тест 2: JSON в markdown блоке
        ai_response_markdown = """
        Вот результат:
        ```json
        {
            "rules": [
                {
                    "rule_type": "normative",
                    "description": "Норматив",
                    "numeric_value": 0.15,
                    "unit": "кВт·ч/м²",
                    "confidence": 0.8
                }
            ]
        }
        ```
        """
        
        rules = importer._parse_ai_extraction_result(ai_response_markdown, "PKM690")
        
        if len(rules) == 1 and rules[0]["rule_type"] == "normative":
            print("✅ JSON в markdown блоке распарсен")
        else:
            print(f"❌ Неверный парсинг markdown: {rules}")
            return False
        
        # Тест 3: Некорректный JSON
        invalid_json = "Это не JSON {неправильный формат}"
        rules = importer._parse_ai_extraction_result(invalid_json, "PKM690")
        
        if rules == []:
            print("✅ Некорректный JSON обработан (пустой список)")
        else:
            print(f"❌ Некорректный JSON должен вернуть пустой список: {rules}")
            return False
        
        # Тест 4: Правило без rule_type
        ai_response_no_type = """
        {
            "rules": [
                {
                    "description": "Правило без типа"
                }
            ]
        }
        """
        
        rules = importer._parse_ai_extraction_result(ai_response_no_type, "PKM690")
        
        if len(rules) == 1 and rules[0]["rule_type"] == "unknown":
            print("✅ Правило без типа обработано (добавлен 'unknown')")
        else:
            print(f"❌ Правило без типа обработано неверно: {rules}")
            return False
        
        return True
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Запустить все тесты"""
    print("\n" + "=" * 70)
    print("ЗАПУСК БАЗОВЫХ ТЕСТОВ ДЛЯ МОДУЛЯ ИМПОРТА НОРМАТИВОВ")
    print("=" * 70)
    
    tests = [
        ("Файл не найден", test_file_not_found),
        ("Определение типа документа", test_document_type_detection),
        ("Вычисление хеша файла", test_file_hash_calculation),
        ("Извлечение текста", test_text_extraction_from_parsed_result),
        ("Извлечение без AI", test_ai_extraction_without_ai),
        ("Парсинг ответа AI", test_parse_ai_extraction_result),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА в тесте '{test_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Итоги
    print("\n" + "=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{status:15} - {test_name}")
    
    print(f"\nВсего: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n🎉 Все тесты пройдены успешно!")
        return True
    else:
        print(f"\n⚠️ {total - passed} тест(ов) провалено")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

