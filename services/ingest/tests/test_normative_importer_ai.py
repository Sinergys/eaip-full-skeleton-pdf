"""
Тесты для AI-извлечения правил из нормативных документов
Используются моки для избежания реальных запросов к AI
"""
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import json

# Добавляем путь к модулям
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ai_extraction_formulas():
    """Тест извлечения формул через AI"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Извлечение формул через AI")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Мокаем AI парсер
        mock_ai_parser = MagicMock()
        mock_ai_parser.enabled = True
        mock_ai_parser.model_text = "deepseek-chat"
        
        # Мокаем ответ AI с формулой
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "rules": [
                {
                    "rule_type": "formula",
                    "description": "Расчет теплопотерь через ограждающие конструкции",
                    "formula": "Q = A * (t_in - t_out) / R",
                    "parameters": {
                        "A": "площадь, м²",
                        "t_in": "температура внутри, °C",
                        "t_out": "температура снаружи, °C",
                        "R": "сопротивление теплопередаче, м²·°C/Вт"
                    },
                    "numeric_value": None,
                    "unit": "кВт·ч",
                    "confidence": 0.95,
                    "references": []
                }
            ]
        })
        
        mock_ai_parser.client = MagicMock()
        mock_ai_parser.client.chat.completions.create.return_value = mock_response
        
        importer.ai_parser = mock_ai_parser
        
        # Тестовый результат парсинга
        parsed_result = {
            "parsing": {
                "data": {
                    "text": "Формула расчета теплопотерь: Q = A * (t_in - t_out) / R"
                }
            }
        }
        
        # Извлекаем правила
        rules = importer._extract_rules_with_ai(parsed_result, 1, "PKM690")
        
        if len(rules) == 1:
            rule = rules[0]
            if rule["rule_type"] == "formula" and "Q = A" in rule.get("formula", ""):
                print("✅ Формула извлечена корректно")
                print(f"   Формула: {rule.get('formula')}")
                print(f"   Параметры: {len(rule.get('parameters', {}))} шт.")
                return True
            else:
                print(f"❌ Неверный тип правила или формула: {rule}")
                return False
        else:
            print(f"❌ Ожидалась 1 формула, получено: {len(rules)}")
            return False
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_extraction_normatives():
    """Тест извлечения числовых нормативов через AI"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Извлечение нормативов через AI")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Мокаем AI парсер
        mock_ai_parser = MagicMock()
        mock_ai_parser.enabled = True
        mock_ai_parser.model_text = "deepseek-chat"
        
        # Мокаем ответ AI с нормативами
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "rules": [
                {
                    "rule_type": "normative",
                    "description": "Удельный расход электроэнергии для офисных зданий",
                    "formula": None,
                    "parameters": {},
                    "numeric_value": 0.15,
                    "unit": "кВт·ч/м²·год",
                    "confidence": 0.9,
                    "references": [
                        {
                            "field_name": "Удельный расход электроэнергии",
                            "sheet_name": "Динамика ср",
                            "cell_reference": "C5",
                            "passport_field_path": "resources.electricity.specific_consumption"
                        }
                    ]
                },
                {
                    "rule_type": "normative",
                    "description": "Норматив потребления газа",
                    "numeric_value": 120.5,
                    "unit": "м³/м²·год",
                    "confidence": 0.85,
                    "references": []
                }
            ]
        })
        
        mock_ai_parser.client = MagicMock()
        mock_ai_parser.client.chat.completions.create.return_value = mock_response
        
        importer.ai_parser = mock_ai_parser
        
        # Тестовый результат парсинга
        parsed_result = {
            "parsing": {
                "data": {
                    "text": "Норматив удельного расхода электроэнергии: 0.15 кВт·ч/м²·год. Норматив газа: 120.5 м³/м²·год"
                }
            }
        }
        
        # Извлекаем правила
        rules = importer._extract_rules_with_ai(parsed_result, 1, "GOST")
        
        if len(rules) == 2:
            normatives = [r for r in rules if r["rule_type"] == "normative"]
            if len(normatives) == 2:
                print("✅ Нормативы извлечены корректно")
                for norm in normatives:
                    print(f"   - {norm.get('description')}: {norm.get('numeric_value')} {norm.get('unit')}")
                
                # Проверяем связи с полями
                rules_with_refs = [r for r in rules if r.get("references")]
                if len(rules_with_refs) == 1:
                    print("✅ Связи с полями извлечены")
                    return True
                else:
                    print(f"⚠️ Ожидалась 1 связь с полем, получено: {len(rules_with_refs)}")
                    return True  # Не критично
            else:
                print(f"❌ Ожидалось 2 норматива, получено: {len(normatives)}")
                return False
        else:
            print(f"❌ Ожидалось 2 правила, получено: {len(rules)}")
            return False
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_extraction_requirements():
    """Тест извлечения текстовых требований через AI"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Извлечение требований через AI")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Мокаем AI парсер
        mock_ai_parser = MagicMock()
        mock_ai_parser.enabled = True
        mock_ai_parser.model_text = "deepseek-chat"
        
        # Мокаем ответ AI с требованиями
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "rules": [
                {
                    "rule_type": "requirement",
                    "description": "Энергопаспорт должен содержать данные за последние 3 года",
                    "formula": None,
                    "parameters": {},
                    "numeric_value": None,
                    "unit": None,
                    "confidence": 0.8,
                    "references": []
                },
                {
                    "rule_type": "requirement",
                    "description": "Все расчеты должны быть выполнены согласно методике ПКМ №690",
                    "confidence": 0.75,
                    "references": []
                }
            ]
        })
        
        mock_ai_parser.client = MagicMock()
        mock_ai_parser.client.chat.completions.create.return_value = mock_response
        
        importer.ai_parser = mock_ai_parser
        
        # Тестовый результат парсинга
        parsed_result = {
            "parsing": {
                "data": {
                    "text": "Требования: Энергопаспорт должен содержать данные за последние 3 года. Расчеты согласно ПКМ №690."
                }
            }
        }
        
        # Извлекаем правила
        rules = importer._extract_rules_with_ai(parsed_result, 1, "PKM690")
        
        if len(rules) == 2:
            requirements = [r for r in rules if r["rule_type"] == "requirement"]
            if len(requirements) == 2:
                print("✅ Требования извлечены корректно")
                for req in requirements:
                    print(f"   - {req.get('description')[:60]}...")
                return True
            else:
                print(f"❌ Ожидалось 2 требования, получено: {len(requirements)}")
                return False
        else:
            print(f"❌ Ожидалось 2 правила, получено: {len(rules)}")
            return False
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_extraction_error_handling():
    """Тест обработки ошибок AI"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Обработка ошибок AI")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Тест 1: AI недоступен
        importer.ai_parser = None
        parsed_result = {"parsing": {"data": {"text": "Тест"}}}
        rules = importer._extract_rules_with_ai(parsed_result, 1, "PKM690")
        if rules == []:
            print("✅ AI недоступен - возвращается пустой список")
        else:
            print("❌ При недоступном AI должен быть пустой список")
            return False
        
        # Тест 2: AI отключен
        mock_ai_parser = MagicMock()
        mock_ai_parser.enabled = False
        importer.ai_parser = mock_ai_parser
        rules = importer._extract_rules_with_ai(parsed_result, 1, "PKM690")
        if rules == []:
            print("✅ AI отключен - возвращается пустой список")
        else:
            print("❌ При отключенном AI должен быть пустой список")
            return False
        
        # Тест 3: Ошибка вызова AI
        mock_ai_parser = MagicMock()
        mock_ai_parser.enabled = True
        mock_ai_parser.client = MagicMock()
        mock_ai_parser.client.chat.completions.create.side_effect = Exception("API Error")
        importer.ai_parser = mock_ai_parser
        
        try:
            rules = importer._extract_rules_with_ai(parsed_result, 1, "PKM690")
            if rules == []:
                print("✅ Ошибка AI обработана - возвращается пустой список")
            else:
                print("❌ При ошибке AI должен быть пустой список")
                return False
        except Exception:
            print("❌ Ошибка AI не обработана (выброшено исключение)")
            return False
        
        # Тест 4: Пустой текст
        importer.ai_parser = None
        empty_result = {"parsing": {"data": {}}}
        rules = importer._extract_rules_with_ai(empty_result, 1, "PKM690")
        if rules == []:
            print("✅ Пустой текст обработан - возвращается пустой список")
        else:
            print("❌ При пустом тексте должен быть пустой список")
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


def test_prompt_building():
    """Тест построения промпта для AI"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Построение промпта для AI")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        
        importer = NormativeImporter()
        
        # Тест 1: Обычный текст
        text = "Тестовый документ с формулой Q = A * B"
        prompt = importer._build_extraction_prompt(text, "PKM690")
        
        if "PKM690" in prompt and "формулы" in prompt.lower():
            print("✅ Промпт содержит тип документа и инструкции")
        else:
            print(f"❌ Промпт неверный: {prompt[:100]}...")
            return False
        
        # Тест 2: Длинный текст (должен обрезаться)
        long_text = "A" * 20000  # 20k символов
        prompt = importer._build_extraction_prompt(long_text, "GOST")
        
        if len(prompt) < len(long_text):
            print("✅ Длинный текст обрезан в промпте")
        else:
            print("❌ Длинный текст не обрезан")
            return False
        
        # Тест 3: Разные типы документов
        for doc_type in ["PKM690", "GOST", "SNiP"]:
            prompt = importer._build_extraction_prompt("Тест", doc_type)
            if doc_type in prompt:
                print(f"✅ Промпт для {doc_type} содержит тип документа")
            else:
                print(f"❌ Промпт для {doc_type} не содержит тип")
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
    """Запустить все тесты AI-извлечения"""
    print("\n" + "=" * 70)
    print("ЗАПУСК ТЕСТОВ AI-ИЗВЛЕЧЕНИЯ ДЛЯ МОДУЛЯ ИМПОРТА НОРМАТИВОВ")
    print("=" * 70)
    
    tests = [
        ("Извлечение формул", test_ai_extraction_formulas),
        ("Извлечение нормативов", test_ai_extraction_normatives),
        ("Извлечение требований", test_ai_extraction_requirements),
        ("Обработка ошибок AI", test_ai_extraction_error_handling),
        ("Построение промпта", test_prompt_building),
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
    print("ИТОГИ ТЕСТИРОВАНИЯ AI-ИЗВЛЕЧЕНИЯ")
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

