# 🧪 Как протестировать Intelligent Router

## 📋 Инструкция по тестированию

### Шаг 1: Запустите сервер

```powershell
cd C:\eaip\eaip_full_skeleton\services\ingest
uvicorn main:app --reload --port 8001
```

Или используйте существующий способ запуска сервера.

### Шаг 2: Откройте веб-интерфейс

Откройте в браузере: **http://localhost:8001**

### Шаг 3: Загрузите файл

1. Найдите форму загрузки файла на главной странице
2. Выберите файл "Навои ТЭС" (или любой другой файл)
3. Укажите предприятие (или создайте новое)
4. Нажмите "Загрузить"

### Шаг 4: Проверьте результаты

После загрузки файла вы получите ответ с `batch_id`. 

#### Вариант 1: Проверка через скрипт

```powershell
cd C:\eaip
python tools/test_intelligent_router.py [batch_id]
```

Если не указать `batch_id`, скрипт покажет последние 5 загрузок.

#### Вариант 2: Проверка в ответе API

В ответе на загрузку файла будет поле `routing_map`:

```json
{
  "batch_id": "...",
  "routing_map": {
    "analysis": {
      "document_type": "balance_act",
      "resource_type": "electricity",
      "data_type": "realization",
      "period": "2024_Q1",
      "confidence": 0.85
    },
    "routing": {
      "primary_module": "balance_sheet_node_extractor",
      "target_tables": ["node_consumption"]
    }
  }
}
```

#### Вариант 3: Проверка в БД

Routing map также сохраняется в `parsing_summary` в таблице `uploads`.

## 🔍 Что проверять

### ✅ Успешная работа Intelligent Router

1. **В логах сервера** должны быть сообщения:
   ```
   🧠 Intelligent Router: document_type=..., resource_type=..., confidence=...
   ```

2. **В ответе API** должно быть поле `routing_map` с:
   - `analysis` - результаты анализа
   - `routing` - рекомендации по обработке

3. **Точность классификации**:
   - `document_type` должен соответствовать типу файла
   - `resource_type` должен быть определен правильно
   - `confidence` должен быть > 0.7 для хорошей классификации

### ⚠️ Если что-то не работает

1. **Routing map отсутствует**:
   - Проверьте логи сервера на ошибки
   - Убедитесь, что файл был загружен после интеграции router

2. **Низкая уверенность (confidence < 0.7)**:
   - Это нормально для новых/неизвестных типов файлов
   - Router автоматически перейдет к глубокому анализу

3. **Ошибки в логах**:
   - Проверьте, что все зависимости установлены
   - Убедитесь, что `intelligent_router.py` доступен

## 📊 Примеры ожидаемых результатов

### Файл "Реализация 2024 Q1.xlsx"
```json
{
  "analysis": {
    "document_type": "balance_act",
    "resource_type": "electricity",
    "data_type": "realization",
    "period": "2024_Q1",
    "confidence": 0.9
  },
  "routing": {
    "primary_module": "balance_sheet_node_extractor",
    "target_tables": ["node_consumption"]
  }
}
```

### Файл "Энергопаспорт.xlsx"
```json
{
  "analysis": {
    "document_type": "energy_passport",
    "confidence": 0.85
  },
  "routing": {
    "primary_module": "canonical_to_passport",
    "target_tables": ["parsed_data"]
  }
}
```

## 🎯 Следующие шаги после тестирования

1. Проверить точность классификации на разных типах файлов
2. Улучшить промпты для AI-анализа (если нужно)
3. Использовать routing_map для автоматического выбора парсеров

