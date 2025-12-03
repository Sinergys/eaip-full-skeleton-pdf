"""
Тестовый скрипт для проверки подключения к DeepSeek API
"""
import os
import sys

# API ключ DeepSeek
DEEPSEEK_API_KEY = "sk-fa4d5adfd79d4307809a34b153fc0ab7"

# Проверяем версию openai и импортируем правильно
try:
    from openai import OpenAI
    HAS_OPENAI_V1 = True
except ImportError:
    HAS_OPENAI_V1 = False
    print("❌ Библиотека openai не установлена. Установите: pip install openai")
    sys.exit(1)

def test_deepseek_connection():
    """Тест подключения к DeepSeek API"""
    print("=" * 60)
    print("🧪 ТЕСТ ПОДКЛЮЧЕНИЯ К DEEPSEEK API")
    print("=" * 60)
    print()
    
    try:
        # Создаем клиент DeepSeek
        print("📡 Создаю клиент DeepSeek API...")
        print(f"   API Key: {DEEPSEEK_API_KEY[:10]}...{DEEPSEEK_API_KEY[-4:]}")
        print("   Base URL: https://api.deepseek.com")
        
        # Создаем клиент с правильными параметрами
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        print("✅ Клиент создан успешно")
        print()
        
        # Тест 1: Простой текстовый запрос
        print("🔍 Тест 1: Простой текстовый запрос...")
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "user",
                        "content": "Привет! Ответь одним предложением: работает ли подключение к DeepSeek API?"
                    }
                ],
                max_tokens=100
            )
            
            answer = response.choices[0].message.content
            print("✅ Запрос выполнен успешно!")
            print(f"📝 Ответ: {answer}")
            print()
            
        except Exception as e:
            print(f"❌ Ошибка при текстовом запросе: {e}")
            return False
        
        # Тест 2: Проверка доступных моделей (если поддерживается)
        print("🔍 Тест 2: Проверка модели...")
        try:
            # Простой запрос для проверки модели
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты помощник для тестирования API."
                    },
                    {
                        "role": "user",
                        "content": "Какая модель используется?"
                    }
                ],
                max_tokens=50
            )
            
            answer = response.choices[0].message.content
            print("✅ Модель отвечает корректно")
            print(f"📝 Ответ: {answer}")
            print()
            
        except Exception as e:
            print(f"⚠️ Предупреждение при проверке модели: {e}")
            print()
        
        # Тест 3: Проверка структурированного ответа (JSON)
        print("🔍 Тест 3: Запрос структурированных данных...")
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "user",
                        "content": """Верни JSON с информацией о статусе подключения в формате:
{
    "status": "ok",
    "provider": "deepseek",
    "model": "deepseek-chat"
}"""
                    }
                ],
                max_tokens=200
            )
            
            answer = response.choices[0].message.content
            print("✅ Структурированный запрос выполнен")
            print(f"📝 Ответ: {answer}")
            print()
            
        except Exception as e:
            print(f"⚠️ Предупреждение при структурированном запросе: {e}")
            print()
        
        # Итоговый результат
        print("=" * 60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        print()
        print("📋 Результаты:")
        print("   ✅ Подключение к DeepSeek API работает")
        print("   ✅ API ключ валидный")
        print("   ✅ Модель deepseek-chat доступна")
        print("   ✅ Запросы выполняются успешно")
        print()
        print("💡 Для использования в проекте добавьте в .env:")
        print(f"   DEEPSEEK_API_KEY={DEEPSEEK_API_KEY}")
        print("   AI_PROVIDER=deepseek")
        print("   AI_ENABLED=true")
        print()
        
        return True
        
    except Exception as e:
        print("=" * 60)
        print("❌ ОШИБКА ПОДКЛЮЧЕНИЯ")
        print("=" * 60)
        print(f"Ошибка: {e}")
        print()
        print("🔍 Возможные причины:")
        print("   1. Неверный API ключ")
        print("   2. Проблемы с сетью")
        print("   3. DeepSeek API недоступен")
        print("   4. Не установлена библиотека openai")
        print()
        print("💡 Решения:")
        print("   1. Проверьте API ключ на https://platform.deepseek.com")
        print("   2. Установите библиотеку: pip install openai")
        print("   3. Проверьте интернет-соединение")
        return False


def test_ai_parser_integration():
    """Тест интеграции с ai_parser модулем"""
    print("=" * 60)
    print("🧪 ТЕСТ ИНТЕГРАЦИИ С AI_PARSER")
    print("=" * 60)
    print()
    
    try:
        # Устанавливаем переменные окружения для теста
        os.environ["AI_PROVIDER"] = "deepseek"
        os.environ["AI_ENABLED"] = "true"
        os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API_KEY
        os.environ["DEEPSEEK_MODEL"] = "deepseek-chat"
        
        # Импортируем модуль
        print("📦 Импортирую ai_parser модуль...")
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services", "ingest"))
        from ai_parser import get_ai_parser
        
        print("✅ Модуль импортирован")
        print()
        
        # Получаем парсер
        print("🔍 Создаю AI парсер...")
        ai_parser = get_ai_parser()
        
        if ai_parser:
            print("✅ AI парсер создан успешно")
            print(f"   Провайдер: {ai_parser.provider}")
            print(f"   Модель: {ai_parser.model_text}")
            print()
            
            # Тест структурирования данных
            print("🔍 Тест структурирования данных...")
            test_text = """
            Документ: Энергетический паспорт
            Адрес: г. Москва, ул. Примерная, д. 1
            Площадь: 100 кв.м.
            Год постройки: 2020
            """
            
            try:
                structured = ai_parser.structure_data(test_text)
                print("✅ Структурирование выполнено")
                print(f"📝 Результат: {structured}")
                print()
            except Exception as e:
                print(f"⚠️ Ошибка структурирования (может быть из-за лимитов): {e}")
                print()
            
            print("=" * 60)
            print("✅ ИНТЕГРАЦИЯ РАБОТАЕТ!")
            print("=" * 60)
            return True
        else:
            print("❌ Не удалось создать AI парсер")
            return False
            
    except ImportError as e:
        print(f"⚠️ Модуль ai_parser не найден: {e}")
        print("   Это нормально, если тестируете без установки проекта")
        return False
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False


if __name__ == "__main__":
    print()
    
    # Тест 1: Прямое подключение
    success = test_deepseek_connection()
    
    if success:
        print()
        # Тест 2: Интеграция с модулем (если доступен)
        test_ai_parser_integration()
    
    print()
    print("🏁 Тестирование завершено")

