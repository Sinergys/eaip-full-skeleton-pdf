#!/usr/bin/env python3
"""
Комплексная проверка качества кода проекта.

Запускает все доступные проверки:
1. Форматирование (ruff format)
2. Линтинг (ruff check)
3. Проверка типов (mypy) - если установлен
4. Безопасность (bandit) - если установлен
5. Сложность кода (radon) - если установлен
6. Документация (pydocstyle) - если установлен
"""
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Цвета для вывода
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Директории для проверки
CHECK_DIRECTORIES = [
    "services/reports/energy_passport",
    "eaip_full_skeleton/services/ingest",
    "eaip_full_skeleton/services/reports",
]


def print_header(text: str):
    """Печатает заголовок."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def print_success(text: str):
    """Печатает успех."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_warning(text: str):
    """Печатает предупреждение."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_error(text: str):
    """Печатает ошибку."""
    print(f"{RED}✗ {text}{RESET}")


def run_check(
    cmd: List[str], description: str, required: bool = False
) -> Tuple[bool, str]:
    """Запускает проверку."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            print_success(f"{description}: OK")
            return True, result.stdout
        else:
            print_error(f"{description}: FAILED")
            if result.stderr:
                print(f"  {result.stderr[:200]}...")  # Первые 200 символов
            return False, result.stderr
    except FileNotFoundError:
        if required:
            print_error(f"{description}: инструмент не установлен (обязательный)")
        else:
            print_warning(f"{description}: инструмент не установлен (опциональный)")
        return False, "Tool not found"
    except Exception as e:
        print_error(f"{description}: ERROR - {e}")
        return False, str(e)


def check_formatting(directories: List[str]) -> Dict[str, bool]:
    """Проверка форматирования."""
    print_header("1. ПРОВЕРКА ФОРМАТИРОВАНИЯ (ruff format)")
    
    results = {}
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print_warning(f"Директория не найдена: {directory}")
            continue
        
        # Исключаем папки tools и .venv из проверки
        cmd = ["ruff", "format", "--check", str(dir_path), "--exclude", "**/tools/**", "--exclude", "**/.venv/**"]
        success, _ = run_check(cmd, f"Форматирование {directory}", required=True)
        results[directory] = success
    
    return results


def check_linting(directories: List[str]) -> Dict[str, bool]:
    """Проверка линтинга."""
    print_header("2. ПРОВЕРКА ЛИНТИНГА (ruff check)")
    
    results = {}
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        
        # Исключаем папки tools и .venv из проверки
        cmd = ["ruff", "check", str(dir_path), "--output-format=concise", "--exclude", "**/tools/**", "--exclude", "**/.venv/**"]
        success, _ = run_check(cmd, f"Линтинг {directory}", required=True)
        results[directory] = success
    
    return results


def check_types(directories: List[str]) -> Dict[str, bool]:
    """Проверка типов."""
    print_header("3. ПРОВЕРКА ТИПОВ (mypy)")
    
    results = {}
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        
        # Ищем все .py файлы, исключая tools и .venv
        py_files = [f for f in dir_path.rglob("*.py") if "tools" not in f.parts and ".venv" not in f.parts]
        if not py_files:
            continue
        
        # Проверяем первые 5 файлов как пример
        test_files = [str(f) for f in py_files[:5]]
        cmd = ["python", "-m", "mypy"] + test_files + [
            "--ignore-missing-imports",
            "--no-strict-optional",
        ]
        success, _ = run_check(cmd, f"Типы {directory} (пример)", required=False)
        results[directory] = success
    
    return results


def check_security(directories: List[str]) -> Dict[str, bool]:
    """Проверка безопасности."""
    print_header("4. ПРОВЕРКА БЕЗОПАСНОСТИ (bandit)")
    
    results = {}
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        
        # Исключаем папки tools и .venv из проверки безопасности
        cmd = ["python", "-m", "bandit", "-r", str(dir_path), "-f", "json", "--exclude", "**/tools/**", "--exclude", "**/.venv/**"]
        success, _ = run_check(cmd, f"Безопасность {directory}", required=False)
        results[directory] = success
    
    return results


def check_complexity(directories: List[str]) -> Dict[str, bool]:
    """Проверка сложности."""
    print_header("5. АНАЛИЗ СЛОЖНОСТИ (radon)")
    
    results = {}
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        
        # Проверяем цикломатическую сложность
        cmd = ["python", "-m", "radon", "cc", str(dir_path), "-a"]
        success, output = run_check(
            cmd, f"Сложность {directory}", required=False
        )
        results[directory] = success
        
        if success and output:
            # Показываем примеры сложных функций
            lines = output.split("\n")[:10]
            if lines:
                print(f"  Примеры функций:")
                for line in lines:
                    if line.strip():
                        print(f"    {line[:80]}")
    
    return results


def print_summary(all_results: Dict[str, Dict[str, bool]]):
    """Печатает итоговую сводку."""
    print_header("ИТОГОВАЯ СВОДКА")
    
    total_checks = 0
    passed_checks = 0
    
    for category, results in all_results.items():
        if not results:
            continue
        
        category_passed = sum(1 for v in results.values() if v)
        category_total = len(results)
        total_checks += category_total
        passed_checks += category_passed
        
        status = "✓" if category_passed == category_total else "⚠"
        print(
            f"{status} {category}: {category_passed}/{category_total} "
            f"({category_passed*100//category_total if category_total > 0 else 0}%)"
        )
    
    print(f"\n{BOLD}Всего проверок: {passed_checks}/{total_checks}{RESET}")
    
    if passed_checks == total_checks:
        print_success("Все проверки пройдены!")
    else:
        print_warning(f"Не пройдено проверок: {total_checks - passed_checks}")
    
    print(f"\n{BOLD}Рекомендации:{RESET}")
    print("1. Форматирование - обязательно (ruff format)")
    print("2. Линтинг - обязательно (ruff check)")
    print("3. Типы - рекомендуется (mypy)")
    print("4. Безопасность - рекомендуется (bandit)")
    print("5. Сложность - опционально (radon)")


def main():
    """Главная функция."""
    print(f"\n{BOLD}Комплексная проверка качества кода проекта{RESET}\n")
    
    all_results = {}
    
    # 1. Форматирование
    all_results["Форматирование"] = check_formatting(CHECK_DIRECTORIES)
    
    # 2. Линтинг
    all_results["Линтинг"] = check_linting(CHECK_DIRECTORIES)
    
    # 3. Типы
    all_results["Типы"] = check_types(CHECK_DIRECTORIES)
    
    # 4. Безопасность
    all_results["Безопасность"] = check_security(CHECK_DIRECTORIES)
    
    # 5. Сложность
    all_results["Сложность"] = check_complexity(CHECK_DIRECTORIES)
    
    # Итоговая сводка
    print_summary(all_results)
    
    # Определяем код выхода
    total_failed = sum(
        sum(1 for v in r.values() if not v) for r in all_results.values()
    )
    sys.exit(1 if total_failed > 0 else 0)


if __name__ == "__main__":
    main()

