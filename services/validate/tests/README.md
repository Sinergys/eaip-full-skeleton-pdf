# Validate Service Tests

Интеграционные тесты для validate service.

## Установка зависимостей

```powershell
cd C:\eaip\eaip_full_skeleton\services\validate\tests
pip install -r requirements-test.txt
```

## Запуск тестов

### Все тесты (кроме integration)
```powershell
cd C:\eaip\eaip_full_skeleton\services\validate
pytest tests/ -m "not integration" -v
```

### Только API тесты
```powershell
pytest tests/test_validate_api.py -v
```

### С интеграционными тестами (требуется запущенный сервис)
```powershell
# Сначала запустить validate service
python main.py

# В другом терминале
pytest tests/ -v
```

### С подробным выводом
```powershell
pytest tests/ -v -s
```

## Структура тестов

- `conftest.py` - Конфигурация pytest и фикстуры
- `test_validate_api.py` - Тесты API endpoints
- `test_web_integration.py` - Тесты интеграции с веб-интерфейсом
- `pytest.ini` - Настройки pytest
- `test_data/` - Тестовые файлы

## Маркеры

- `@pytest.mark.integration` - Интеграционные тесты (требуют запущенных сервисов)
- `@pytest.mark.slow` - Медленные тесты (обработка AI может занимать время)

## Примечания

- Selenium тесты отключены по умолчанию (требуют установки WebDriver)
- Для полных тестов требуется запущенный validate service на порту 8002
- Тесты с AI обработкой могут занимать до 5 минут
