#!/usr/bin/env python3
"""
Скрипт для комплексной проверки качества кода.

Запускает различные типы проверок:
- Линтинг
- Проверка типов
- Безопасность
- Сложность кода
- Документация
- Импорты
- Мертвый код
"""
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
import json

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Печатает заголовок секции."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    """Печатает успешное сообщение."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text: str):
    """Печатает предупреждение."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text: str):
    """Печатает ошибку."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def run_command(cmd: List[str], description: str, required: bool = False) -> tuple[bool, str]:
    """
    Запускает команду и возвращает результат.
    
    Args:
        cmd: Команда для запуска
        description: Описание команды
        required: Обязательна ли команда (если False, отсутствие инструмента не критично)
    
    Returns:
        (success, output) - успех выполнения и вывод
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print_success(f"{description}: OK")
            return True, result.stdout
        else:
            print_error(f"{description}: FAILED")
            if result.stderr:
                print(f"  {result.stderr}")
            return False, result.stderr
    except FileNotFoundError:
        if required:
            print_error(f"{description}: инструмент не установлен (обязательный)")
        else:
            print_warning(f"{description}: инструмент не установлен (опциональный)")
        return False, "Tool not found"
    except subprocess.TimeoutExpired:
        print_error(f"{description}: TIMEOUT (превышено время ожидания)")
        return False, "Timeout"
    except Exception as e:
        print_error(f"{description}: ERROR - {e}")
        return False, str(e)

def check_linting(file_path: Path) -> Dict[str, bool]:
    """Проверяет код линтерами."""
    print_header("1. ЛИНТИНГ")
    
    results = {}
    
    # Ruff (быстрый современный линтер)
    if file_path.is_file():
        cmd = ["ruff", "check", str(file_path)]
    else:
        cmd = ["ruff", "check", str(file_path)]
    results["ruff"] = run_command(cmd, "Ruff linting", required=False)[0]
    
    # Flake8 (классический линтер)
    if file_path.is_file():
        cmd = ["flake8", str(file_path), "--max-line-length=120", "--ignore=E203,W503"]
    else:
        cmd = ["flake8", str(file_path), "--max-line-length=120", "--ignore=E203,W503"]
    results["flake8"] = run_command(cmd, "Flake8 linting", required=False)[0]
    
    return results

def check_types(file_path: Path) -> Dict[str, bool]:
    """Проверяет типы."""
    print_header("2. ПРОВЕРКА ТИПОВ")
    
    results = {}
    
    # Mypy
    if file_path.is_file():
        cmd = ["mypy", str(file_path), "--ignore-missing-imports", "--no-strict-optional"]
    else:
        cmd = ["mypy", str(file_path), "--ignore-missing-imports", "--no-strict-optional"]
    results["mypy"] = run_command(cmd, "Mypy type checking", required=False)[0]
    
    return results

def check_security(file_path: Path) -> Dict[str, bool]:
    """Проверяет безопасность."""
    print_header("3. ПРОВЕРКА БЕЗОПАСНОСТИ")
    
    results = {}
    
    # Bandit
    if file_path.is_file():
        cmd = ["bandit", "-r", str(file_path), "-f", "json"]
    else:
        cmd = ["bandit", "-r", str(file_path), "-f", "json"]
    success, output = run_command(cmd, "Bandit security scan", required=False)
    results["bandit"] = success
    
    if success and output:
        try:
            data = json.loads(output)
            if data.get("metrics", {}).get("_totals", {}).get("high_severity", 0) > 0:
                print_warning(f"Найдено {data['metrics']['_totals']['high_severity']} проблем высокой важности")
        except:
            pass
    
    return results

def check_complexity(file_path: Path) -> Dict[str, bool]:
    """Проверяет сложность кода."""
    print_header("4. АНАЛИЗ СЛОЖНОСТИ")
    
    results = {}
    
    # Radon - цикломатическая сложность
    if file_path.is_file():
        cmd = ["radon", "cc", str(file_path), "-a"]
    else:
        cmd = ["radon", "cc", str(file_path), "-a"]
    results["radon_cc"] = run_command(cmd, "Radon cyclomatic complexity", required=False)[0]
    
    # Radon - индекс поддерживаемости
    if file_path.is_file():
        cmd = ["radon", "mi", str(file_path)]
    else:
        cmd = ["radon", "mi", str(file_path)]
    results["radon_mi"] = run_command(cmd, "Radon maintainability index", required=False)[0]
    
    return results

def check_documentation(file_path: Path) -> Dict[str, bool]:
    """Проверяет документацию."""
    print_header("5. ПРОВЕРКА ДОКУМЕНТАЦИИ")
    
    results = {}
    
    # Pydocstyle
    if file_path.is_file():
        cmd = ["pydocstyle", str(file_path), "--convention=google"]
    else:
        cmd = ["pydocstyle", str(file_path), "--convention=google"]
    results["pydocstyle"] = run_command(cmd, "Pydocstyle docstring check", required=False)[0]
    
    return results

def check_imports(file_path: Path) -> Dict[str, bool]:
    """Проверяет импорты."""
    print_header("6. ПРОВЕРКА ИМПОРТОВ")
    
    results = {}
    
    # isort
    if file_path.is_file():
        cmd = ["isort", "--check-only", "--diff", str(file_path)]
    else:
        cmd = ["isort", "--check-only", "--diff", str(file_path)]
    results["isort"] = run_command(cmd, "isort import sorting", required=False)[0]
    
    return results

def check_dead_code(file_path: Path) -> Dict[str, bool]:
    """Проверяет мертвый код."""
    print_header("7. ПОИСК МЕРТВОГО КОДА")
    
    results = {}
    
    # Vulture
    if file_path.is_file():
        cmd = ["vulture", str(file_path), "--min-confidence", "80"]
    else:
        cmd = ["vulture", str(file_path), "--min-confidence", "80"]
    results["vulture"] = run_command(cmd, "Vulture dead code detection", required=False)[0]
    
    return results

def check_formatting(file_path: Path) -> Dict[str, bool]:
    """Проверяет форматирование."""
    print_header("8. ПРОВЕРКА ФОРМАТИРОВАНИЯ")
    
    results = {}
    
    # Ruff format
    if file_path.is_file():
        cmd = ["ruff", "format", "--check", str(file_path)]
    else:
        cmd = ["ruff", "format", "--check", str(file_path)]
    results["ruff_format"] = run_command(cmd, "Ruff format check", required=False)[0]
    
    # Black (если ruff недоступен)
    if not results.get("ruff_format"):
        if file_path.is_file():
            cmd = ["black", "--check", str(file_path)]
        else:
            cmd = ["black", "--check", str(file_path)]
        results["black"] = run_command(cmd, "Black format check", required=False)[0]
    
    return results

def print_summary(all_results: Dict[str, Dict[str, bool]]):
    """Печатает итоговую сводку."""
    print_header("ИТОГОВАЯ СВОДКА")
    
    total_checks = 0
    passed_checks = 0
    
    for category, results in all_results.items():
        category_passed = sum(1 for v in results.values() if v)
        category_total = len(results)
        total_checks += category_total
        passed_checks += category_passed
        
        status = "✓" if category_passed == category_total else "⚠"
        print(f"{status} {category}: {category_passed}/{category_total}")
    
    print(f"\n{Colors.BOLD}Всего проверок: {passed_checks}/{total_checks}{Colors.RESET}")
    
    if passed_checks == total_checks:
        print_success("Все проверки пройдены!")
    else:
        print_warning(f"Не пройдено проверок: {total_checks - passed_checks}")

def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("Использование: python check_code_quality.py <путь_к_файлу_или_директории>")
        print("Пример: python check_code_quality.py services/reports/energy_passport/quarterly_production.py")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print_error(f"Путь не существует: {file_path}")
        sys.exit(1)
    
    print(f"\n{Colors.BOLD}Проверка качества кода: {file_path}{Colors.RESET}\n")
    
    all_results = {}
    
    # Запускаем все проверки
    all_results["Линтинг"] = check_linting(file_path)
    all_results["Типы"] = check_types(file_path)
    all_results["Безопасность"] = check_security(file_path)
    all_results["Сложность"] = check_complexity(file_path)
    all_results["Документация"] = check_documentation(file_path)
    all_results["Импорты"] = check_imports(file_path)
    all_results["Мертвый код"] = check_dead_code(file_path)
    all_results["Форматирование"] = check_formatting(file_path)
    
    # Итоговая сводка
    print_summary(all_results)

if __name__ == "__main__":
    main()

