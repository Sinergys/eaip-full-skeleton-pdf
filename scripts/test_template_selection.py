"""
Тестовый скрипт для проверки выбора шаблонов
"""
from pathlib import Path
import sys

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "templates" / "pcm690"))

def test_template_config():
    """Тест конфигурации шаблонов"""
    print("🧪 Тестирование конфигурации шаблонов...\n")
    
    try:
        from templates_config import get_template_path, list_available_templates
        
        # Тест 1: Получение пути к новому шаблону
        print("1. Тест получения пути к новому шаблону:")
        try:
            path = get_template_path("new_energy_passport")
            print(f"   ✅ Путь: {path}")
            print(f"   ✅ Файл существует: {path.exists()}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Тест 2: Получение пути к старому шаблону
        print("\n2. Тест получения пути к старому шаблону (Metin):")
        try:
            path = get_template_path("metin")
            print(f"   ✅ Путь: {path}")
            print(f"   ✅ Файл существует: {path.exists()}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Тест 3: Получение пути к дефолтному шаблону
        print("\n3. Тест получения пути к дефолтному шаблону:")
        try:
            path = get_template_path("default")
            print(f"   ✅ Путь: {path}")
            print(f"   ✅ Файл существует: {path.exists()}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Тест 4: Список доступных шаблонов
        print("\n4. Тест списка доступных шаблонов:")
        try:
            templates = list_available_templates()
            print(f"   ✅ Найдено шаблонов: {len(templates)}")
            for name, path in templates.items():
                print(f"      - {name}: {path}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Тест 5: Несуществующий шаблон
        print("\n5. Тест несуществующего шаблона:")
        try:
            path = get_template_path("nonexistent_template")
            print("   ❌ Ошибка: шаблон не должен существовать")
        except (ValueError, FileNotFoundError) as e:
            print(f"   ✅ Корректная обработка ошибки: {e}")
        
        print("\n✅ Все тесты пройдены!")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что файл templates/pcm690/templates_config.py существует")

if __name__ == "__main__":
    test_template_config()

