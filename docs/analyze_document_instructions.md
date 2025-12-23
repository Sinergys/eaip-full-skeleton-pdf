ь скрипт  который все сделает # Инструкции по анализу документа

## Вариант 1: Скопировать файл в рабочее пространство

1. Скопируйте файл `test full.docx` в папку проекта:
   ```
   eaip_full_skeleton/services/validate/test_full.docx
   ```

2. Запустите анализ через Python:
```python
import asyncio
from services.orchestrator import OrchestratorService
from core.config import Settings

async def analyze_document():
    # Настройка конфигурации
    settings = Settings()
    
    # Инициализация оркестратора
    orchestrator = OrchestratorService(settings)
    
    # Анализ документа
    result_path = await orchestrator.process_report(
        file_path="eaip_full_skeleton/services/validate/test_full.docx",
        file_hash="calculated_hash",
        original_filename="test full.docx"
    )
    
    print(f"Анализ завершен. Результат: {result_path}")

# Запуск
asyncio.run(analyze_document())
```

## Вариант 2: Использовать API (рекомендуется)

### Шаг 1: Запуск сервиса

```bash
cd eaip_full_skeleton/services/validate
uvicorn main:app --reload --port 8003
```

### Шаг 2: Отправка файла через API

```bash
curl -X POST "http://localhost:8003/api/v1/check-report/" \
  -F "file=@C:/Users/DELL/Desktop/Navoiy IES/test full.docx"
```

### Шаг 3: Получение результата

Сервис вернет JSON с информацией:
```json
{
  "message": "Обработка завершена",
  "file_path": "/path/to/test full_Проверенный.docx",
  "from_cache": false,
  "processing_time_seconds": 245.3,
  "file_hash": "a1b2c3..."
}
```

## Возможности анализа

Система автоматически найдет:

### ❌ Ошибки соответствия ПКМ 690
- Отсутствующие обязательные разделы
- Неправильная структура документа
- Нарушения требований к оформлению

### ❌ Орфографические ошибки
- Ошибки правописания
- Пунктуационные ошибки
- Стилистические недочеты

### ❌ Проблемы с формулами
- Неправильное оформление формул
- Отсутствующие единицы измерения
- Неточности в расчетах

### 💡 Рекомендации по улучшению
- Структурные улучшения
- Стилистические предложения
- Оптимизация представления данных

## Требования к системе

### Обязательные переменные окружения:
```bash
DEEPSEEK_API_KEY=your_api_key_here
```

### Опциональные настройки:
```bash
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3-coder:480b-cloud
CACHE_ENABLED=true
MAX_FILE_SIZE_MB=100
```

## Поддержка

- Логи: `logs/word_validator.log`
- Документация API: http://localhost:8003/docs
- Health check: http://localhost:8003/api/v1/health