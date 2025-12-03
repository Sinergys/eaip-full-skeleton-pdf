# 🤖 План интеграции ИИ для распознавания и обработки файлов

## 🎯 Цели интеграции ИИ

1. **Распознавание документов** - использование Vision API вместо/в дополнение к Tesseract OCR
2. **Структурирование данных** - извлечение структурированных данных из неструктурированных документов
3. **Валидация данных** - интеллектуальная проверка данных на соответствие требованиям
4. **Генерация отчетов** - создание отчетов с помощью ИИ на основе обработанных данных

## 🔄 Текущий процесс vs ИИ-процесс

### Текущий процесс:
1. Загрузка файла → `ingest` service
2. Парсинг (PyPDF2, pdfplumber, openpyxl) → извлечение текста
3. OCR (Tesseract) → для сканированных документов
4. Валидация → `validate` service (базовая)
5. Генерация отчета → `reports` service (шаблонный)

### ИИ-процесс (предлагаемый):
1. Загрузка файла → `ingest` service
2. **ИИ Vision API** → распознавание и извлечение данных из любых форматов
3. **ИИ структурирование** → преобразование в нужный формат (JSON/структура)
4. **ИИ валидация** → интеллектуальная проверка данных
5. **ИИ генерация отчета** → создание отчета на основе данных

## 🛠️ Варианты ИИ API

### 1. OpenAI (GPT-4 Vision + GPT-4)
- **Плюсы:** Отличное качество, поддержка изображений, хорошая документация
- **Минусы:** Платный, требует API ключ
- **Использование:**
  - `gpt-4-vision-preview` для распознавания изображений/PDF
  - `gpt-4` для структурирования и генерации отчетов

### 2. Anthropic Claude (Claude 3 Vision)
- **Плюсы:** Хорошее качество, большой контекст
- **Минусы:** Платный, требует API ключ
- **Использование:** Аналогично OpenAI

### 3. Google Gemini Pro Vision
- **Плюсы:** Бесплатный tier, хорошее качество
- **Минусы:** Ограничения на бесплатном плане
- **Использование:** Vision API для распознавания

### 4. DeepSeek API
- **Плюсы:** 
  - Совместим с OpenAI API (легкая интеграция)
  - Дешевле чем OpenAI
  - Хорошее качество распознавания
  - Поддержка Vision API
- **Минусы:** 
  - Может быть менее стабилен чем OpenAI
  - Ограниченная документация на английском
- **Использование:**
  - Использует OpenAI-совместимый API
  - Модели: `deepseek-chat`, `deepseek-v2`
  - Vision через base64 изображения

### 5. Локальные модели (Ollama, LocalAI)
- **Плюсы:** Бесплатно, приватно, нет лимитов
- **Минусы:** Требует мощный сервер, может быть медленнее
- **Использование:** Для приватных данных

## 📋 План реализации

### Этап 1: Интеграция ИИ в ingest service

#### 1.1. Создать модуль AI распознавания

**Файл:** `services/ingest/ai_parser.py`

```python
"""
Модуль для распознавания файлов с помощью ИИ
Поддерживает OpenAI, Anthropic, Gemini
"""
import os
import base64
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Поддержка разных провайдеров
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # openai, anthropic, gemini, local

class AIParser:
    def __init__(self):
        self.provider = AI_PROVIDER
        self.setup_provider()
    
    def setup_provider(self):
        """Настройка провайдера ИИ"""
        if self.provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY не установлен")
            self.client = OpenAI(api_key=api_key)
            self.model_vision = "gpt-4-vision-preview"
            self.model_text = "gpt-4"
        
        elif self.provider == "anthropic":
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY не установлен")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_vision = "claude-3-opus-20240229"
            self.model_text = "claude-3-opus-20240229"
        
        elif self.provider == "deepseek":
            from openai import OpenAI
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY не установлен")
            # DeepSeek использует OpenAI-совместимый API
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"  # DeepSeek endpoint
            )
            self.model_vision = "deepseek-chat"  # или deepseek-v2
            self.model_text = "deepseek-chat"
        
        # ... другие провайдеры
    
    def recognize_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Распознавание документа с помощью ИИ Vision API
        
        Args:
            file_path: Путь к файлу
            file_type: Тип файла (pdf, image, etc.)
        
        Returns:
            Распознанные данные
        """
        # Конвертация файла в изображение/base64
        # Отправка в Vision API
        # Получение структурированных данных
        pass
    
    def structure_data(self, raw_text: str, template: Optional[str] = None) -> Dict[str, Any]:
        """
        Структурирование данных с помощью ИИ
        
        Args:
            raw_text: Извлеченный текст
            template: Шаблон структуры (опционально)
        
        Returns:
            Структурированные данные в JSON
        """
        # Промпт для структурирования
        # Отправка в LLM
        # Парсинг JSON ответа
        pass
```

#### 1.2. Обновить file_parser.py

Добавить возможность использования ИИ вместо/в дополнение к традиционному парсингу:

```python
# В file_parser.py
def parse_file_with_ai(file_path: str, use_ai: bool = True) -> Dict[str, Any]:
    """
    Парсинг файла с использованием ИИ
    """
    if use_ai and os.getenv("AI_PROVIDER"):
        ai_parser = AIParser()
        return ai_parser.recognize_document(file_path, detect_file_type(file_path))
    else:
        # Fallback на традиционный парсинг
        return parse_file(file_path)
```

#### 1.3. Обновить requirements.txt

```txt
# ИИ провайдеры (опционально)
openai>=1.0.0
anthropic>=0.18.0
google-generativeai>=0.3.0
```

### Этап 2: Интеграция ИИ в validate service

#### 2.1. Интеллектуальная валидация

**Файл:** `services/validate/ai_validator.py`

```python
"""
ИИ валидация данных
"""
def validate_with_ai(data: Dict[str, Any], requirements: str) -> Dict[str, Any]:
    """
    Валидация данных с помощью ИИ
    
    Args:
        data: Данные для валидации
        requirements: Требования к данным (текст)
    
    Returns:
        Результаты валидации с рекомендациями
    """
    # Промпт для валидации
    # Отправка в LLM
    # Получение результатов валидации
    pass
```

### Этап 3: Интеграция ИИ в reports service

#### 3.1. Генерация отчетов с ИИ

**Файл:** `services/reports/ai_report_generator.py`

```python
"""
Генерация отчетов с помощью ИИ
"""
def generate_report_with_ai(audit_data: Dict[str, Any], template: Optional[str] = None) -> str:
    """
    Генерация текста отчета с помощью ИИ
    
    Args:
        audit_data: Данные аудита
        template: Шаблон отчета (опционально)
    
    Returns:
        Текст отчета
    """
    # Промпт для генерации отчета
    # Отправка в LLM
    # Получение текста отчета
    # Форматирование в PDF
    pass
```

## 🔧 Конфигурация

### Переменные окружения

**Файл:** `infra/.env.example` (дополнить)

```env
# AI Configuration
AI_PROVIDER=deepseek  # openai, anthropic, gemini, deepseek, local
AI_ENABLED=true

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL_VISION=gpt-4-vision-preview
OPENAI_MODEL_TEXT=gpt-4

# DeepSeek (OpenAI-совместимый API)
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_MODEL=deepseek-chat  # или deepseek-v2
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229

# Gemini
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-pro-vision

# Local AI (Ollama)
LOCAL_AI_URL=http://localhost:11434
LOCAL_AI_MODEL=llama2
```

### Docker Compose (дополнить)

```yaml
ingest:
  environment:
    - AI_PROVIDER=${AI_PROVIDER}
    - AI_ENABLED=${AI_ENABLED}
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    # ... другие переменные
```

## 📊 Архитектура с ИИ

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  gateway-auth   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│  ingest service  │─────▶│  AI Vision   │
│                  │      │     API      │
│  - Upload file   │      │              │
│  - Parse/OCR     │      │  (OpenAI/    │
│  - AI recognize  │      │  Claude/     │
│  - Structure     │      │  Gemini)     │
└──────┬──────────┘      └──────────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│ validate service│─────▶│  AI Text     │
│                  │      │     API      │
│  - Validate      │      │              │
│  - AI check      │      │  (GPT-4/     │
│  - Recommendations│     │  Claude)     │
└──────┬──────────┘      └──────────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│ reports service  │─────▶│  AI Text     │
│                  │      │     API      │
│  - Generate      │      │              │
│  - AI report      │      │  (GPT-4/     │
│  - PDF export     │      │  Claude)     │
└──────────────────┘      └──────────────┘
```

## 🚀 Поэтапная реализация

### Фаза 1: Базовая интеграция (MVP)
- [ ] Добавить поддержку OpenAI Vision API в ingest
- [ ] Создать модуль `ai_parser.py`
- [ ] Добавить переменные окружения
- [ ] Обновить docker-compose
- [ ] Тестирование на простых PDF

### Фаза 2: Структурирование данных
- [ ] Интеграция структурирования через ИИ
- [ ] Поддержка шаблонов (EnergyPassport)
- [ ] Валидация структурированных данных

### Фаза 3: Интеллектуальная валидация
- [ ] ИИ валидация в validate service
- [ ] Генерация рекомендаций
- [ ] Улучшение качества данных

### Фаза 4: Генерация отчетов
- [ ] ИИ генерация текста отчетов
- [ ] Интеграция с PDF генерацией
- [ ] Кастомизация отчетов

### Фаза 5: Оптимизация
- [ ] Кэширование результатов
- [ ] Batch обработка
- [ ] Поддержка локальных моделей
- [ ] Fallback на традиционные методы

## 💰 Стоимость (примерная)

### OpenAI GPT-4 Vision
- Vision API: ~$0.01-0.03 за изображение
- GPT-4: ~$0.03 за 1K токенов
- **Пример:** 10 страниц PDF ≈ $0.30-0.50

### DeepSeek API
- Chat: ~$0.00014 за 1K токенов (в 200+ раз дешевле GPT-4!)
- Vision: через chat модель с base64 изображениями
- **Пример:** 10 страниц PDF ≈ $0.01-0.05
- **Преимущество:** Очень дешево, OpenAI-совместимый API

### Anthropic Claude
- Vision: ~$0.015 за изображение
- Text: ~$0.015 за 1K токенов
- **Пример:** 10 страниц PDF ≈ $0.20-0.40

### Google Gemini
- Бесплатный tier: 60 запросов/мин
- Pro: ~$0.001 за изображение
- **Пример:** 10 страниц PDF ≈ $0.01-0.05

## 🔒 Безопасность

1. **API ключи:** Хранить в переменных окружения, не коммитить
2. **Приватные данные:** Рассмотреть локальные модели для чувствительных данных
3. **Rate limiting:** Ограничение запросов к API
4. **Логирование:** Не логировать чувствительные данные
5. **Шифрование:** Использовать HTTPS для API запросов

## 📝 Следующие шаги

1. **Выбрать провайдера ИИ** (OpenAI/Anthropic/Gemini)
2. **Создать модуль ai_parser.py** с базовой интеграцией
3. **Добавить конфигурацию** в .env и docker-compose
4. **Протестировать** на простых файлах
5. **Интегрировать** в существующий workflow
6. **Добавить fallback** на традиционные методы

## 🎯 Рекомендации

1. **Начать с DeepSeek** - дешевле в 200+ раз чем OpenAI, OpenAI-совместимый API
2. **Использовать гибридный подход** - ИИ + традиционные методы
3. **Кэшировать результаты** - для экономии средств
4. **Мониторить использование** - отслеживать расходы
5. **Иметь fallback** - на случай недоступности API
6. **OpenAI как альтернатива** - если нужна максимальная точность

## ✅ DeepSeek API - Особенности

### Преимущества:
- ✅ **Очень дешево** - в 200+ раз дешевле OpenAI
- ✅ **OpenAI-совместимый** - легко интегрировать (меняем только base_url)
- ✅ **Хорошее качество** - сравним с GPT-3.5
- ✅ **Поддержка Vision** - через base64 изображения в chat модели

### Интеграция:
```python
# Использование DeepSeek с OpenAI библиотекой
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"
)

# Работает точно так же как OpenAI API!
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...]
)
```

### Ограничения:
- Может быть менее стабилен чем OpenAI
- Меньше документации на английском
- Vision через base64 (не отдельный Vision API)

