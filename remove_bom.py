#!/usr/bin/env python3
"""Удаление BOM из файла"""

from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")

print("=== УДАЛЕНИЕ BOM ИЗ ФАЙЛА ===\n")

# Читаем файл в бинарном режиме для проверки BOM
with open(file_path, 'rb') as f:
    content_bytes = f.read()

# Проверяем наличие BOM (EF BB BF)
if content_bytes.startswith(b'\xef\xbb\xbf'):
    print("✓ Найден BOM, удаляем...")
    # Удаляем BOM
    content_bytes = content_bytes[3:]
    
    # Сохраняем без BOM
    with open(file_path, 'wb') as f:
        f.write(content_bytes)
    
    print("✓ BOM удален")
else:
    print("✓ BOM не обнаружен")

# Проверяем синтаксис
print("\n=== ПРОВЕРКА СИНТАКСИСА ===")
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    compile(content, file_path.name, 'exec')
    print("✓ Синтаксис корректен")
except SyntaxError as e:
    print(f"✗ Ошибка синтаксиса: {e}")
    print(f"   Строка {e.lineno}, позиция {e.offset}")
    
    # Показываем проблемную строку
    lines = content.split('\n')
    if e.lineno <= len(lines):
        print(f"   Проблемная строка: {lines[e.lineno-1]}")
except UnicodeDecodeError as e:
    print(f"✗ Ошибка кодировки: {e}")

print("\n=== ЗАПУСТИТЕ ТЕСТ СНОВА ===")
print("python -m pytest services/ingest/tests/test_passport_e2e_audit_sinergys.py::test_passport_generation_with_metin_template -v")