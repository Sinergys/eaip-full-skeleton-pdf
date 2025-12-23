# Типы проверок кода Python

Помимо линтера, существует множество других типов проверок кода для обеспечения качества, безопасности и поддерживаемости.

## 1. Линтеры (Linters)

Проверяют стиль кода, базовые ошибки и соответствие стандартам PEP.

### Инструменты:
- **pylint** - комплексная проверка стиля и ошибок
- **flake8** - комбинация pycodestyle, pyflakes, mccabe
- **ruff** - быстрый современный линтер (Rust-based)
- **pycodestyle** (pep8) - проверка соответствия PEP 8

### Пример использования:
```bash
pylint services/reports/energy_passport/quarterly_production.py
flake8 services/reports/energy_passport/quarterly_production.py
ruff check services/reports/energy_passport/quarterly_production.py
```

## 2. Проверка типов (Type Checking)

Проверяют корректность использования типов и аннотаций.

### Инструменты:
- **mypy** - статический анализатор типов
- **pyright** - быстрый анализатор типов от Microsoft
- **pyre** - анализатор типов от Facebook

### Пример использования:
```bash
mypy services/reports/energy_passport/quarterly_production.py
pyright services/reports/energy_passport/quarterly_production.py
```

### Что проверяет:
- Соответствие типов в аннотациях
- Неправильное использование типов
- Отсутствующие аннотации типов
- Несовместимость типов

## 3. Форматтеры кода (Code Formatters)

Автоматически форматируют код по стандартам.

### Инструменты:
- **black** - популярный форматтер (строгий стиль)
- **autopep8** - форматирует по PEP 8
- **yapf** - форматтер от Google
- **ruff format** - форматирование (часть ruff)

### Пример использования:
```bash
black services/reports/energy_passport/quarterly_production.py
autopep8 --in-place services/reports/energy_passport/quarterly_production.py
```

## 4. Проверка безопасности (Security Scanners)

Ищут уязвимости и проблемы безопасности.

### Инструменты:
- **bandit** - поиск уязвимостей в Python коде
- **safety** - проверка уязвимостей в зависимостях
- **pip-audit** - аудит зависимостей
- **semgrep** - статический анализ безопасности

### Пример использования:
```bash
bandit -r services/reports/energy_passport/
safety check
pip-audit
```

### Что проверяет:
- SQL-инъекции
- XSS уязвимости
- Небезопасное использование eval/exec
- Устаревшие/уязвимые зависимости
- Хардкод паролей и ключей

## 5. Анализ сложности кода (Complexity Analysis)

Измеряют сложность кода для оценки поддерживаемости.

### Инструменты:
- **radon** - метрики сложности (cyclomatic, maintainability)
- **mccabe** - цикломатическая сложность
- **xenon** - мониторинг сложности кода

### Пример использования:
```bash
radon cc services/reports/energy_passport/quarterly_production.py
radon mi services/reports/energy_passport/quarterly_production.py
xenon --max-absolute B --max-modules A --max-average A services/reports/energy_passport/
```

### Метрики:
- **Cyclomatic Complexity** - количество независимых путей выполнения
- **Maintainability Index** - индекс поддерживаемости (0-100)
- **Halstead Complexity** - метрики сложности алгоритма

## 6. Покрытие тестами (Test Coverage)

Проверяют, какая часть кода покрыта тестами.

### Инструменты:
- **coverage.py** - измерение покрытия
- **pytest-cov** - интеграция с pytest
- **coveralls** - сервис для отслеживания покрытия

### Пример использования:
```bash
coverage run -m pytest tests/
coverage report
coverage html  # Генерирует HTML отчет
```

### Метрики:
- **Line Coverage** - покрытие строк
- **Branch Coverage** - покрытие ветвлений
- **Function Coverage** - покрытие функций

## 7. Проверка документации (Documentation Checkers)

Проверяют наличие и качество документации.

### Инструменты:
- **pydocstyle** - проверка docstrings по PEP 257
- **darglint** - проверка docstrings для аргументов
- **pylint** (с опцией --docstring-min-length)

### Пример использования:
```bash
pydocstyle services/reports/energy_passport/quarterly_production.py
darglint services/reports/energy_passport/quarterly_production.py
```

## 8. Проверка импортов (Import Checkers)

Проверяют и сортируют импорты.

### Инструменты:
- **isort** - сортировка и форматирование импортов
- **import-linter** - проверка архитектуры импортов

### Пример использования:
```bash
isort services/reports/energy_passport/quarterly_production.py
isort --check-only services/reports/energy_passport/quarterly_production.py
```

## 9. Поиск неиспользуемого кода (Dead Code Detection)

Находят неиспользуемые функции, переменные, импорты.

### Инструменты:
- **vulture** - поиск мертвого кода
- **pylint** (unused-import, unused-variable)
- **autoflake** - удаление неиспользуемых импортов

### Пример использования:
```bash
vulture services/reports/energy_passport/
autoflake --in-place --remove-all-unused-imports services/reports/energy_passport/quarterly_production.py
```

## 10. Проверка зависимостей (Dependency Checkers)

Анализируют зависимости проекта.

### Инструменты:
- **pipdeptree** - дерево зависимостей
- **pip-audit** - аудит безопасности зависимостей
- **pip-check** - проверка устаревших пакетов
- **pipreqs** - генерация requirements.txt

### Пример использования:
```bash
pipdeptree
pip-audit
pipreqs . --force
```

## 11. Проверка производительности (Performance Analysis)

Анализируют производительность кода.

### Инструменты:
- **py-spy** - профилирование работающего процесса
- **cProfile** - встроенный профилировщик
- **line_profiler** - построчное профилирование
- **memory_profiler** - профилирование памяти

### Пример использования:
```bash
python -m cProfile -o profile.stats script.py
py-spy record -o profile.svg -- python script.py
```

## 12. Проверка совместимости (Compatibility Checkers)

Проверяют совместимость с разными версиями Python.

### Инструменты:
- **python-future** - проверка совместимости Python 2/3
- **pyupgrade** - автоматическое обновление синтаксиса
- **ruff** (с опцией --target)

### Пример использования:
```bash
pyupgrade --py39-plus services/reports/energy_passport/quarterly_production.py
```

## Рекомендуемый набор инструментов для проекта

### Минимальный набор:
1. **ruff** - линтер и форматтер (быстрый, современный)
2. **mypy** - проверка типов
3. **bandit** - безопасность
4. **coverage.py** - покрытие тестами

### Расширенный набор:
1. **ruff** - линтер и форматтер
2. **mypy** - проверка типов
3. **bandit** - безопасность
4. **coverage.py** - покрытие тестами
5. **radon** - анализ сложности
6. **pydocstyle** - документация
7. **isort** - сортировка импортов
8. **vulture** - мертвый код

## Интеграция в CI/CD

Рекомендуется настроить автоматические проверки в CI/CD пайплайне:

```yaml
# Пример для GitHub Actions
- name: Lint
  run: ruff check .

- name: Type check
  run: mypy .

- name: Security check
  run: bandit -r .

- name: Test coverage
  run: pytest --cov=services --cov-report=xml

- name: Format check
  run: ruff format --check .
```

## Настройка pre-commit hooks

Можно настроить автоматические проверки перед коммитом:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
```

