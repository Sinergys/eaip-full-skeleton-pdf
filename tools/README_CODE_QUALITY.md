# Проверка качества кода

## Быстрый старт

### 1. Установка инструментов

```bash
pip install -r requirements-dev.txt
```

### 2. Запуск комплексной проверки

```bash
# Проверка одного файла
python tools/check_code_quality.py services/reports/energy_passport/quarterly_production.py

# Проверка директории
python tools/check_code_quality.py services/reports/energy_passport/
```

## Отдельные проверки

### Линтинг
```bash
ruff check services/reports/energy_passport/
flake8 services/reports/energy_passport/
```

### Проверка типов
```bash
mypy services/reports/energy_passport/quarterly_production.py
```

### Безопасность
```bash
bandit -r services/reports/energy_passport/
```

### Сложность кода
```bash
radon cc services/reports/energy_passport/quarterly_production.py
radon mi services/reports/energy_passport/quarterly_production.py
```

### Документация
```bash
pydocstyle services/reports/energy_passport/quarterly_production.py
```

### Импорты
```bash
isort --check-only services/reports/energy_passport/quarterly_production.py
```

### Мертвый код
```bash
vulture services/reports/energy_passport/
```

### Форматирование
```bash
ruff format --check services/reports/energy_passport/
black --check services/reports/energy_passport/
```

## Автоматическое исправление

### Форматирование
```bash
ruff format services/reports/energy_passport/
black services/reports/energy_passport/
```

### Импорты
```bash
isort services/reports/energy_passport/
```

### Удаление неиспользуемых импортов
```bash
autoflake --in-place --remove-all-unused-imports services/reports/energy_passport/quarterly_production.py
```

## Интеграция в IDE

### VS Code
Установите расширения:
- Python (Microsoft)
- Ruff
- Pylance (для mypy)
- Error Lens

### PyCharm
Настройте внешние инструменты:
- File → Settings → Tools → External Tools
- Добавьте ruff, mypy, black как внешние инструменты

## Pre-commit hooks

Создайте `.pre-commit-config.yaml`:

```yaml
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
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
```

Установка:
```bash
pip install pre-commit
pre-commit install
```

