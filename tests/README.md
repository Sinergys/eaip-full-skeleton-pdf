# ТЕСТЫ OCR МОДУЛЯ

## Структура тестов

```
tests/
├── README.md                    # Этот файл
├── test_fix_string_content.py   # Unit-тесты для fix_string_content()
├── test_confidence_thresholds.py # Unit-тесты для порогов confidence
├── test_gemini_retry.py         # Integration-тесты для retry логики
└── test_ocr_integration.py      # Integration-тесты для полного пайплайна
```

## Запуск тестов локально

### Предварительные требования

1. Установлены зависимости:
   ```bash
   pip install pytest pytest-cov google-generativeai pillow pytesseract pdf2image
   ```

2. Настроен Tesseract OCR (для локальных тестов)

3. Настроен API ключ Gemini (для integration-тестов):
   - Ключ должен быть в `eaip_full_skeleton/services/ingest/utils/gemini_vision_ocr.py`

### Запуск всех тестов

```bash
# Из корня проекта
pytest tests/ -v

# С покрытием кода
pytest tests/ --cov=eaip_full_skeleton/services/ingest --cov-report=html
```

### Запуск конкретного теста

```bash
# Unit-тесты
pytest tests/test_fix_string_content.py -v

# Integration-тесты
pytest tests/test_ocr_integration.py -v
```

### Запуск с фильтрацией

```bash
# Только быстрые тесты (без API вызовов)
pytest tests/ -v -m "not slow"

# Только тесты с API
pytest tests/ -v -m "api"
```

## Запуск в CI

### GitHub Actions (пример)

```yaml
name: OCR Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov
```

### Локальный CI-симулятор

```bash
# Запуск с теми же параметрами, что в CI
pytest tests/ -v --cov --cov-report=xml --junitxml=test-results.xml
```

## Структура тестового кейса

```python
import pytest
from eaip_full_skeleton.services.ingest.utils.gemini_vision_ocr import extract_with_gemini_vision

class TestExample:
    def test_basic_case(self):
        """Описание теста"""
        # Arrange
        input_data = "..."
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_output
```

## Маркеры тестов

- `@pytest.mark.unit` - Unit-тесты (быстрые, без внешних зависимостей)
- `@pytest.mark.integration` - Integration-тесты (требуют API/файлы)
- `@pytest.mark.slow` - Медленные тесты (API вызовы, большие файлы)
- `@pytest.mark.api` - Тесты с внешними API

## Отладка тестов

```bash
# Запуск с выводом print()
pytest tests/ -v -s

# Запуск конкретного теста с отладкой
pytest tests/test_example.py::TestClass::test_method -v -s

# Остановка на первой ошибке
pytest tests/ -v -x
```

## Покрытие кода

```bash
# Генерация HTML отчёта
pytest tests/ --cov=eaip_full_skeleton/services/ingest --cov-report=html

# Открыть отчёт
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

## Известные проблемы

1. **Tesseract не найден:** Убедитесь, что Tesseract установлен и доступен в PATH
2. **Gemini API таймаут:** Некоторые тесты могут падать из-за таймаутов API
3. **Зависимости:** Все зависимости должны быть установлены перед запуском

## Контакты

При проблемах с тестами проверьте:
- Логи в `reports/ocr/`
- Конфигурацию в `config/ocr.yml`
- Статус внешних сервисов (Gemini API)

