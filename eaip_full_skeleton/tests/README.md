# 🧪 Тестовый пакет проекта АТЛАС

## 📋 Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Конфигурация pytest и фикстуры
├── pytest.ini              # Настройки pytest
├── requirements.txt        # Зависимости для тестов
├── unit/                   # Unit-тесты
│   ├── test_ai_parser.py
│   ├── test_ai_anomaly_detector.py
│   ├── test_ai_data_validator.py
│   ├── test_ai_compliance_checker.py
│   ├── test_ai_efficiency_analyzer.py
│   ├── test_ai_energy_verifier.py
│   ├── test_ai_ocr_enhancer.py
│   ├── test_ai_table_parser.py
│   ├── test_ai_quality_reporter.py
│   ├── test_ai_base_client.py
│   ├── test_ai_client_factory.py
│   └── test_ai_config.py
├── integration/            # Интеграционные тесты
│   └── test_pdf_pipeline.py
├── performance/            # Тесты производительности
│   ├── test_ocr_performance.py
│   └── test_ai_performance.py
└── fixtures/               # Mock-данные
    └── mock_energy_passport_data.py
```

## 🚀 Запуск тестов

### Установка зависимостей

```bash
cd tests
pip install -r requirements.txt
```

### Запуск всех тестов

```bash
# Из корня проекта
pytest tests/

# С покрытием кода
pytest tests/ --cov=services/ingest --cov-report=html
```

### Запуск конкретных тестов

```bash
# Только unit-тесты
pytest tests/unit/ -m unit

# Только интеграционные тесты
pytest tests/integration/ -m integration

# Только тесты производительности
pytest tests/performance/ -m performance

# Конкретный тест
pytest tests/unit/test_ai_parser.py::TestAIParser::test_init_deepseek
```

### Запуск с verbose выводом

```bash
pytest tests/ -v
```

## 📊 Покрытие кода

```bash
# Генерация отчета о покрытии
pytest tests/ --cov=services/ingest --cov-report=term-missing

# HTML отчет
pytest tests/ --cov=services/ingest --cov-report=html
# Откройте htmlcov/index.html в браузере
```

## 🔧 Настройка тестов

### Переменные окружения

Тесты используют тестовые переменные окружения из `conftest.py`:

```python
os.environ.setdefault("AI_ENABLED", "false")
os.environ.setdefault("POSTGRES_USER", "test_user")
```

### Mock-данные

Используйте фикстуры из `conftest.py`:

```python
def test_example(sample_energy_passport_data, mock_ai_client):
    # Используйте mock-данные
    data = sample_energy_passport_data
    # Используйте mock AI клиент
    client = mock_ai_client
```

## 📝 Написание новых тестов

### Структура теста

```python
import pytest
from unittest.mock import Mock, patch

class TestMyModule:
    """Тесты для MyModule"""
    
    @pytest.fixture
    def my_fixture(self):
        """Фикстура для теста"""
        return {"test": "data"}
    
    def test_basic_functionality(self, my_fixture):
        """Тест базовой функциональности"""
        assert my_fixture["test"] == "data"
    
    @patch('module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Тест с моком"""
        mock_dependency.return_value = "mocked"
        result = function_under_test()
        assert result == "mocked"
```

### Маркеры тестов

Используйте маркеры для категоризации:

```python
@pytest.mark.unit
def test_unit():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.performance
def test_performance():
    pass

@pytest.mark.slow
def test_slow():
    pass
```

## 🎯 Цели покрытия

- **Unit-тесты**: > 80% покрытие всех модулей
- **Интеграционные тесты**: Все основные пайплайны
- **Тесты производительности**: Критические операции

## 🔍 Отладка тестов

```bash
# Запуск с отладкой
pytest tests/ --pdb

# Остановка на первой ошибке
pytest tests/ -x

# Детальный вывод
pytest tests/ -vv
```

## 📚 Дополнительная информация

- [Документация pytest](https://docs.pytest.org/)
- [Mock объекты](https://docs.python.org/3/library/unittest.mock.html)
- [Fixtures](https://docs.pytest.org/en/stable/fixture.html)

