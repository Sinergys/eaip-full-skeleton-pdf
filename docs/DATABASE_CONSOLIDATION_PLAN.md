# 🗄️ План консолидации баз данных

## Текущая ситуация

### SQLite (ingest_data.db) - АКТИВНО ИСПОЛЬЗУЕТСЯ
- ✅ enterprises
- ✅ uploads  
- ✅ parsed_data
- ✅ normative_documents
- ✅ normative_rules
- ✅ aggregated_data
- ✅ node_consumption
- ✅ И ещё ~10 таблиц

### PostgreSQL - ЕСТЬ, НО НЕ ИСПОЛЬЗУЕТСЯ ingest
- Только базовые таблицы для других сервисов
- ingest сервис его почти не трогает

---

## ✅ Решение: Оставить PostgreSQL

### Почему PostgreSQL?

1. **Production-ready** ✅
   - Лучше для продакшена
   - Лучшая конкурентность
   - Масштабируемость

2. **Уже есть в проекте** ✅
   - Docker-compose готов
   - Инфраструктура настроена

3. **Единая БД** ✅
   - Все сервисы в одном месте
   - Проще управлять
   - Проще бэкапы

4. **Преимущества** ✅
   - JSONB тип для гибких данных
   - Лучшие индексы
   - Репликация
   - Пул соединений

---

## 📋 План миграции

### Шаг 1: Создать таблицы в PostgreSQL (1-2 часа)
Перенести структуру из SQLite в PostgreSQL:

```sql
-- Вместо SQLite таблиц создать PostgreSQL версии
CREATE TABLE enterprises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    industry TEXT,
    enterprise_type TEXT,
    product_type TEXT
);

CREATE TABLE uploads (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(255) NOT NULL UNIQUE,
    enterprise_id INTEGER NOT NULL REFERENCES enterprises(id),
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    status VARCHAR(50) NOT NULL,
    parsing_summary TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE parsed_data (
    upload_id INTEGER PRIMARY KEY REFERENCES uploads(id),
    raw_json JSONB,  -- JSONB вместо TEXT!
    editable_text TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- И так далее для всех таблиц...
```

### Шаг 2: Миграция данных (2-3 часа)
Скрипт для переноса данных из SQLite в PostgreSQL:

```python
# migrate_sqlite_to_postgres.py
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# Подключения
sqlite_conn = sqlite3.connect('ingest_data.db')
pg_conn = psycopg2.connect(
    host='localhost',
    database='eaip_db',
    user='eaip_user',
    password='password'
)

# Миграция enterprises
sqlite_data = sqlite_conn.execute('SELECT * FROM enterprises').fetchall()
# Вставить в PostgreSQL...

# Миграция uploads
# И так далее...
```

### Шаг 3: Изменить код (4-6 часов)
Заменить `database.py`:

```python
# Было:
import sqlite3
conn = sqlite3.connect(DB_PATH)

# Станет:
import psycopg2
from psycopg2.extras import RealDictCursor
conn = psycopg2.connect(DATABASE_URL)
```

### Шаг 4: Тестирование (2-3 часа)
- Проверить все функции
- Сравнить данные
- Тесты

---

## ⚠️ Важные моменты

### 1. JSONB вместо TEXT
```sql
-- SQLite:
raw_json TEXT

-- PostgreSQL:
raw_json JSONB  -- Лучше: индексы, поиск, валидация
```

### 2. Типы данных
```sql
-- SQLite:
id INTEGER PRIMARY KEY AUTOINCREMENT

-- PostgreSQL:
id SERIAL PRIMARY KEY  -- или BIGSERIAL для больших таблиц
```

### 3. Timestamps
```sql
-- SQLite:
created_at TEXT NOT NULL

-- PostgreSQL:
created_at TIMESTAMP NOT NULL DEFAULT NOW()
```

### 4. Connection Pooling
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## 📊 Преимущества после миграции

| Параметр | SQLite | PostgreSQL |
|----------|--------|------------|
| Конкурентность | ⚠️ Ограничена | ✅ Высокая |
| Production | ❌ Не для прода | ✅ Да |
| Масштабируемость | ⚠️ Ограничена | ✅ Хорошая |
| JSON поддержка | ⚠️ Текст | ✅ JSONB |
| Репликация | ❌ Нет | ✅ Да |
| Бэкапы | ⚠️ Файл | ✅ pg_dump |

---

## ⏱️ Оценка времени

- **Создание схемы:** 1-2 часа
- **Миграция данных:** 2-3 часа  
- **Изменение кода:** 4-6 часов
- **Тестирование:** 2-3 часа

**Итого: 9-14 часов работы**

---

## ✅ Рекомендация

**Да, оставляем PostgreSQL.**

Это правильное решение для production. SQLite подходит только для разработки или простых задач.

---

## 🚀 Быстрый старт миграции

1. **Оставить SQLite для разработки** (можно)
2. **Использовать PostgreSQL для production** (правильно)
3. **Или мигрировать полностью** (лучше)

Что выбираем?
