# БАТЧ-ТЕСТИРОВАНИЕ OCR

## Назначение

Этот каталог содержит скрипты и конфигурации для батч-тестирования OCR модуля на больших наборах файлов (20-50+ файлов).

## Структура

```
tools/batch_test/
├── README.md              # Этот файл
├── config.yaml            # Конфигурация батч-тестов
├── batch_runner.py        # Основной скрипт для запуска батчей
└── results/               # Результаты батч-тестов (создаётся автоматически)
```

## Конфигурация

Создайте `config.yaml` с параметрами:

```yaml
batch:
  size: 5                    # Размер батча (файлов)
  pause_between_batches: 10  # Пауза между батчами (секунды)
  
api:
  timeout_seconds: 600
  retry_attempts: 3
  backoff_base_seconds: 2

paths:
  input_dir: "C:/AUDIT/OBJECTS/Navoiy IES/INBOX"
  output_dir: "tools/batch_test/results"
  log_dir: "reports/ocr"
```

## Запуск батч-теста

```bash
# Из корня проекта
python tools/batch_test/batch_runner.py --config tools/batch_test/config.yaml

# С указанием конкретной папки
python tools/batch_test/batch_runner.py --input "C:/path/to/files" --batch-size 5

# С прогресс-баром
python tools/batch_test/batch_runner.py --input "C:/path/to/files" --progress
```

## Результаты

После выполнения батч-теста создаются:

- `results/batch_YYYYMMDD_HHMMSS.json` - JSON с результатами
- `results/batch_YYYYMMDD_HHMMSS.log` - Детальный лог
- `reports/ocr/batch_run.log` - Агрегированный лог

## Метрики

Батч-тест собирает следующие метрики:

- `total_time` - Общее время обработки
- `avg_time_per_page` - Среднее время на страницу
- `errors_count` - Количество ошибок
- `low_confidence_count` - Количество записей с низким confidence
- `gemini_retries_count` - Количество retry для Gemini API
- `success_rate` - Процент успешных обработок

## Мониторинг

Во время выполнения батч-теста можно мониторить:

- Прогресс через прогресс-бар (если включен)
- Логи в реальном времени: `tail -f reports/ocr/batch_run.log`
- Статус в JSON файле результатов

## Остановка и возобновление

```bash
# Остановка (Ctrl+C) - текущий батч завершится, результаты сохранятся
# Возобновление - запустите снова с теми же параметрами (пропустит обработанные)
python tools/batch_test/batch_runner.py --resume --checkpoint results/checkpoint.json
```

## Рекомендации

1. **Размер батча:** Начните с 5 файлов, увеличьте до 10-20 при стабильной работе
2. **Паузы:** Используйте паузы между батчами для избежания rate limits
3. **Мониторинг:** Следите за логами на предмет ошибок и таймаутов
4. **Резервное копирование:** Сохраняйте результаты после каждого батча

