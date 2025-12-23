# 🔧 КРИТИЧЕСКИ ВАЖНЫЕ НАСТРОЙКИ ПРОЕКТА EAIP

**Дата создания:** 2025-11-30  
**Статус:** ✅ ОБЯЗАТЕЛЬНО ДЛЯ ВСЕХ АГЕНТОВ

---

## ⚠️ ВАЖНО: ЭТИ НАСТРОЙКИ ДОЛЖНЫ БЫТЬ ДОСТУПНЫ ВСЕМ АГЕНТАМ

Все агенты должны знать эти настройки и использовать их из файлов, а не из контекста сеанса.

---

## 📍 ПУТИ К ФАЙЛАМ И ДИРЕКТОРИЯМ

### Корневая директория проекта
```
C:\eaip\
```

### Критические пути:
- **База данных SQLite:** `eaip_full_skeleton/services/ingest/ingest_data.db`
  - Переменная окружения: `INGEST_DB_PATH` (по умолчанию: `ingest_data.db` в текущей директории)
  
- **Агрегированные данные:** `C:\eaip\eaip_full_skeleton\services\ingest\data\inbox\aggregated\`
  
- **Исходные файлы:** `C:\AUDIT\OBJECTS\Navoiy IES\INBOX\`
  
- **Конфигурация OCR:** `config/ocr.yml`
  
- **Единый файл задач:** `docs/AGENT_TASKS_UNIFIED.json`
  
- **Файлы синхронизации:**
  - `docs/AGENT_TASK_STATUS.json`
  - `docs/AGENT_LOCKS.json`
  - `docs/AGENT_WORK_LOG.jsonl`

---

## 🔑 API КЛЮЧИ И ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ

### ⚠️ ВАЖНО: API ключи НЕ должны быть в коде!

### DeepSeek API (для ИИ обработки)
- **Переменная:** `DEEPSEEK_API_KEY`
- **Файл:** `infra/.env` (НЕ в git!)
- **Модель:** `deepseek-chat`
- **Документация:** `eaip_full_skeleton/services/ingest/AI_SETUP.md`

### Google Gemini API (для OCR)
- **Переменная:** `GOOGLE_API_KEY`
- **Файл:** `infra/.env` (НЕ в git!)
- **Модель:** `gemini-2.0-flash`
- **Использование:** `eaip_full_skeleton/services/ingest/utils/gemini_vision_ocr.py`

### PostgreSQL (для production)
- **Переменные:**
  - `POSTGRES_USER=eaip_user`
  - `POSTGRES_PASSWORD` (генерируется)
  - `POSTGRES_DB=eaip_db`
  - `POSTGRES_HOST=postgres`
- **Файл:** `infra/.env`

### MinIO (для хранения файлов)
- **Переменные:**
  - `MINIO_ROOT_USER=minioadmin`
  - `MINIO_ROOT_PASSWORD` (генерируется)
- **Файл:** `infra/.env`

---

## ⚙️ КОНФИГУРАЦИЯ OCR

### Файл: `config/ocr.yml`

**Критические настройки:**

```yaml
confidence_thresholds:
  text: 0.30      # Минимальный порог для текста (30%)
  numbers: 0.60   # Минимальный порог для числовых значений (60%)
  dates: 0.80     # Минимальный порог для дат (80%)
  tables: 0.70   # Минимальный порог для таблиц (70%)

api:
  timeout_seconds: 600        # Таймаут запроса (10 минут)
  retry_attempts: 3          # Количество попыток при ошибке
  backoff_base_seconds: 2    # Базовое время задержки

adaptive_processing:
  enabled: true              # Включить адаптивную обработку
  min_confidence: 0.70       # Минимальный порог confidence для повторной попытки
  max_retry_attempts: 1      # Максимальное количество повторных попыток
```

**Использование:**
- Все агенты должны читать эти настройки из файла `config/ocr.yml`
- НЕ использовать хардкод значений в коде!

---

## 🗄️ БАЗА ДАННЫХ

### SQLite (локальная разработка)
- **Путь:** `eaip_full_skeleton/services/ingest/ingest_data.db`
- **Переменная:** `INGEST_DB_PATH`
- **Инициализация:** `eaip_full_skeleton/services/ingest/database.py::init_db()`

### Таблицы:
- `enterprises` - предприятия
- `uploads` - загруженные файлы
- `parsed_data` - распарсенные данные
- `aggregated_data` - агрегированные данные

---

## 📂 СТРУКТУРА ДИРЕКТОРИЙ

### Важные директории:
```
C:\eaip\
├── docs/                          # Документация
│   ├── AGENT_TASKS_UNIFIED.json   # Единый файл задач
│   ├── AGENT_TASK_STATUS.json     # Статус задач
│   ├── AGENT_LOCKS.json           # Блокировки
│   └── AGENT_WORK_LOG.jsonl       # Лог работы
├── config/                         # Конфигурация
│   └── ocr.yml                    # Настройки OCR
├── tools/                          # Утилиты
├── reports/                        # Отчёты
│   └── ocr/                       # Отчёты OCR
└── eaip_full_skeleton/            # Основной код
    └── services/
        └── ingest/
            ├── database.py        # Работа с БД
            ├── ingest_data.db     # SQLite БД
            └── utils/
                └── gemini_vision_ocr.py  # OCR модуль
```

---

## 🔄 ПРАВИЛА ИСПОЛЬЗОВАНИЯ

### ✅ ПРАВИЛЬНО:
1. Читать настройки из файлов (`config/ocr.yml`, `.env`)
2. Использовать переменные окружения для API ключей
3. Читать пути из конфигурационных файлов
4. Использовать `PROJECT_ROOT` для относительных путей

### ❌ НЕПРАВИЛЬНО:
1. Хардкодить API ключи в коде
2. Хардкодить пути к файлам
3. Использовать абсолютные пути без переменных
4. Хранить настройки в контексте сеанса

---

## 📝 ОБНОВЛЕНИЕ НАСТРОЕК

Если настройки изменяются:
1. Обновить соответствующий файл (`config/ocr.yml`, `.env`)
2. Обновить этот документ
3. Уведомить всех агентов через `docs/AGENT_TASKS_UNIFIED.json`
4. Добавить запись в историю изменений

---

**Дата последнего обновления:** 2025-11-30  
**Версия:** 1.0

