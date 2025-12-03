"""Простой тест Java и Tabula"""
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.table_detector import check_dependencies, get_java_info
import subprocess

print("=" * 70)
print("🔍 ПРОВЕРКА JAVA И TABULA")
print("=" * 70)
print()

# Проверка Java напрямую
print("1️⃣ Проверка Java напрямую...")
try:
    result = subprocess.run(
        ["java", "-version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        version_output = result.stderr or result.stdout
        print(f"   ✅ Java найдена!")
        print(f"   Версия: {version_output.split(chr(10))[0] if version_output else 'unknown'}")
    else:
        print(f"   ❌ Java не работает (код возврата: {result.returncode})")
except FileNotFoundError:
    print("   ❌ Java не найдена в PATH")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
print()

# Проверка через модуль
print("2️⃣ Проверка через table_detector...")
deps = check_dependencies()
java_info = get_java_info()

print(f"   Tabula установлен: {deps['tabula']}")
print(f"   Tabula доступен: {deps['tabula_usable']}")
print(f"   Java доступна: {java_info['available']}")
if java_info.get('version'):
    print(f"   Версия Java: {java_info['version']}")
if java_info.get('path'):
    print(f"   Путь к Java: {java_info['path']}")
print()

# Итог
print("=" * 70)
if deps['tabula_usable']:
    print("✅ ВСЁ ОТЛИЧНО! Tabula готов к работе!")
else:
    print("⚠️ Tabula недоступен")
    if not java_info['available']:
        print("   Причина: Java не найдена")
        print("   Решение: Перезапустите терминал или обновите PATH")
print("=" * 70)

