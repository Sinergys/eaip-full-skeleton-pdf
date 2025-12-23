#!/usr/bin/env python3
"""
Скрипт для проверки форматирования всех используемых файлов проекта.

Исключает:
- тестовые файлы (test_*.py, *_test.py)
- временные скрипты в корне
- файлы в __pycache__
- файлы в .venv, venv, node_modules
"""
import subprocess
import sys
from pathlib import Path
from typing import List

# Директории с основным кодом проекта
MAIN_DIRECTORIES = [
    "services",
    "eaip_full_skeleton/services",
    "tools",
]

# Исключаемые паттерны
EXCLUDE_PATTERNS = [
    "**/test_*.py",
    "**/*_test.py",
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/node_modules/**",
    "**/.git/**",
    # Временные скрипты в корне (можно добавить исключения)
    "analyze_*.py",
    "check_*.py",
    "test_*.py",
    "verify_*.py",
    "diagnose_*.py",
    "fix_*.py",
    "create_*.py",
    "generate_*.py",
    "run_*.py",
    "simple_*.py",
    "quick_*.py",
    "final_*.py",
]


def find_python_files(directories: List[str]) -> List[Path]:
    """Находит все Python файлы в указанных директориях."""
    files = []
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob("*.py"):
            # Проверяем исключения
            should_exclude = False
            
            # Проверяем паттерны исключений
            for pattern in EXCLUDE_PATTERNS:
                if py_file.match(pattern):
                    should_exclude = True
                    break
            
            # Проверяем, находится ли в тестовой директории
            if "test" in py_file.parts and "tests" in py_file.parts:
                should_exclude = True
            
            if not should_exclude:
                files.append(py_file)
    
    return sorted(files)


def check_formatting(files: List[Path], fix: bool = False) -> tuple[int, int]:
    """
    Проверяет форматирование файлов.
    
    Args:
        files: Список файлов для проверки
        fix: Если True, исправляет форматирование
    
    Returns:
        (количество файлов с ошибками, общее количество файлов)
    """
    if not files:
        print("Файлы не найдены")
        return 0, 0
    
    print(f"\nНайдено {len(files)} файлов для проверки\n")
    
    if fix:
        cmd = ["ruff", "format"] + [str(f) for f in files]
        print("Исправление форматирования...")
    else:
        cmd = ["ruff", "format", "--check"] + [str(f) for f in files]
        print("Проверка форматирования...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = result.stdout + result.stderr
        
        if fix:
            if "reformatted" in output:
                print(output)
                return 0, len(files)
            else:
                print("Все файлы уже отформатированы")
                return 0, len(files)
        else:
            # Подсчитываем файлы, которые нужно отформатировать
            lines = output.split("\n")
            files_to_format = [l for l in lines if "Would reformat:" in l]
            count = len(files_to_format)
            
            if count > 0:
                print(f"\nНайдено {count} файлов, требующих форматирования:")
                for line in files_to_format[:10]:  # Показываем первые 10
                    print(f"  {line.replace('Would reformat: ', '')}")
                if count > 10:
                    print(f"  ... и еще {count - 10} файлов")
            else:
                print("Все файлы отформатированы правильно!")
            
            return count, len(files)
            
    except Exception as e:
        print(f"Ошибка при проверке: {e}")
        return len(files), len(files)


def main():
    """Главная функция."""
    fix = "--fix" in sys.argv or "-f" in sys.argv
    
    print("Поиск используемых Python файлов в проекте...")
    files = find_python_files(MAIN_DIRECTORIES)
    
    if not files:
        print("Файлы не найдены")
        return
    
    print(f"\nНайдено {len(files)} файлов для проверки")
    
    # Показываем примеры найденных файлов
    print("\nПримеры найденных файлов:")
    for f in files[:5]:
        print(f"  {f}")
    if len(files) > 5:
        print(f"  ... и еще {len(files) - 5} файлов")
    
    # Проверяем форматирование
    count, total = check_formatting(files, fix=fix)
    
    if not fix and count > 0:
        print(f"\nДля автоматического исправления запустите:")
        print(f"  python {sys.argv[0]} --fix")
    
    sys.exit(1 if count > 0 else 0)


if __name__ == "__main__":
    main()

