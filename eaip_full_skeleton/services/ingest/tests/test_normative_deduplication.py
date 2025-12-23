"""
Тесты для дедупликации нормативных документов
"""
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Добавляем путь к модулям
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_deduplication_by_hash():
    """Тест дедупликации по хешу файла"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Дедупликация нормативных документов")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        import database
        
        # Инициализируем БД
        database.init_db()
        
        importer = NormativeImporter()
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            test_content = "Тестовый нормативный документ для проверки дедупликации"
            f.write(test_content)
            temp_path = f.name
        
        try:
            # Первый импорт (мокаем AI и парсинг)
            with patch.object(importer, '_parse_document') as mock_parse, \
                 patch.object(importer, '_extract_rules_with_ai') as mock_ai:
                
                mock_parse.return_value = {
                    "parsing": {
                        "data": {
                            "text": test_content
                        }
                    }
                }
                mock_ai.return_value = [
                    {
                        "rule_type": "normative",
                        "description": "Тестовый норматив",
                        "numeric_value": 0.15,
                        "unit": "кВт·ч/м²",
                        "confidence": 0.9,
                        "references": []
                    }
                ]
                
                # Первый импорт
                result1 = importer.import_normative_document(
                    temp_path,
                    title="Тестовый документ 1",
                    document_type="PKM690"
                )
                
                if result1.get("status") == "processed":
                    doc_id_1 = result1["document_id"]
                    print(f"✅ Первый импорт успешен: ID={doc_id_1}")
                else:
                    print(f"❌ Первый импорт не удался: {result1}")
                    return False
                
                # Второй импорт того же файла (должен быть дубликат)
                result2 = importer.import_normative_document(
                    temp_path,
                    title="Тестовый документ 2",  # Другое название, но тот же файл
                    document_type="PKM690"
                )
                
                if result2.get("status") == "duplicate":
                    if result2["document_id"] == doc_id_1:
                        print(f"✅ Дедупликация работает: обнаружен дубликат ID={doc_id_1}")
                        print(f"   Сообщение: {result2.get('message')}")
                        return True
                    else:
                        print(f"❌ Неверный ID дубликата: {result2['document_id']} != {doc_id_1}")
                        return False
                else:
                    print(f"❌ Дедупликация не сработала: статус={result2.get('status')}")
                    print(f"   Результат: {result2}")
                    return False
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_text_saving():
    """Тест сохранения полного текста в БД"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Сохранение полного текста документа")
    print("=" * 70)
    
    try:
        from domain.normative_importer import NormativeImporter
        import database
        
        # Инициализируем БД
        database.init_db()
        
        importer = NormativeImporter()
        
        # Создаем временный файл с известным содержимым
        test_text = "Это полный текст нормативного документа. Формула: Q = A * B. Норматив: 0.15 кВт·ч/м²"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_text)
            temp_path = f.name
        
        try:
            # Импорт с моками
            with patch.object(importer, '_parse_document') as mock_parse, \
                 patch.object(importer, '_extract_rules_with_ai') as mock_ai:
                
                mock_parse.return_value = {
                    "parsing": {
                        "data": {
                            "text": test_text
                        }
                    }
                }
                mock_ai.return_value = []
                
                result = importer.import_normative_document(
                    temp_path,
                    title="Тест сохранения текста",
                    document_type="PKM690"
                )
                
                if result.get("status") == "processed":
                    doc_id = result["document_id"]
                    
                    # Проверяем, что текст сохранен
                    doc = database.get_normative_document(doc_id)
                    
                    if doc and doc.get("full_text"):
                        saved_text = doc["full_text"]
                        if test_text in saved_text or saved_text == test_text:
                            print(f"✅ Полный текст сохранен в БД (ID={doc_id})")
                            print(f"   Длина текста: {len(saved_text)} символов")
                            
                            # Проверяем parsed_data_json
                            if doc.get("parsed_data_json"):
                                print("✅ Результат парсинга также сохранен")
                                return True
                            else:
                                print("⚠️ Результат парсинга не сохранен")
                                return True  # Не критично
                        else:
                            print(f"❌ Текст не совпадает: сохранено '{saved_text[:50]}...', ожидалось '{test_text[:50]}...'")
                            return False
                    else:
                        print(f"❌ Полный текст не сохранен в БД")
                        return False
                else:
                    print(f"❌ Импорт не удался: {result}")
                    return False
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_document_text():
    """Тест получения текста документа из БД"""
    print("\n" + "=" * 70)
    print("ТЕСТ: Получение текста документа из БД")
    print("=" * 70)
    
    try:
        import database
        
        # Инициализируем БД
        database.init_db()
        
        # Создаем тестовый документ напрямую в БД
        test_text = "Тестовый текст для проверки получения из БД"
        doc = database.create_normative_document(
            title="Тест получения текста",
            document_type="PKM690",
            file_path="/test/path.pdf",
            file_hash="test_hash_123",
            file_size=1000,
            full_text=test_text,
            parsed_data_json='{"test": "data"}'
        )
        
        doc_id = doc["id"]
        
        # Получаем документ
        retrieved_doc = database.get_normative_document(doc_id)
        
        if retrieved_doc:
            if retrieved_doc.get("full_text") == test_text:
                print(f"✅ Текст успешно получен из БД (ID={doc_id})")
                return True
            else:
                print(f"❌ Текст не совпадает")
                return False
        else:
            print(f"❌ Документ не найден")
            return False
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать модуль: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Запустить все тесты дедупликации"""
    print("\n" + "=" * 70)
    print("ЗАПУСК ТЕСТОВ ДЕДУПЛИКАЦИИ И СОХРАНЕНИЯ ТЕКСТА")
    print("=" * 70)
    
    tests = [
        ("Дедупликация по хешу", test_deduplication_by_hash),
        ("Сохранение полного текста", test_full_text_saving),
        ("Получение текста из БД", test_get_document_text),
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

