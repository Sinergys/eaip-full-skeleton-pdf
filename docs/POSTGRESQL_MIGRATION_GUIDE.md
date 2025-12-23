# 🗄️ Руководство по миграции SQLite → PostgreSQL

**Дата создания:** 2025-01-16  
**Версия:** 1.0

---

## 📋 Обзор

Это руководство описывает процесс полной миграции данных из SQLite в PostgreSQL для ingest сервиса.

---

## ✅ Подготовка

### 1. Установка зависимостей

Добавьте `psycopg2` в `requirements.txt`:

```bash
pip install psycopg2-binary
```

Или добавьте в `eaip_full_skeleton/services/ingest/requirements.txt`:

```
psycopg2-binary>=2.9.0
```

### 2. Проверка PostgreSQL

Убедитесь, что PostgreSQL запущен и доступен:

```bash
# Через Docker Compose
cd eaip_full_skeleton/infra
docker compose up -d postgres

# Проверка подключения
docker compose exec postgres psql -U eaip_user -d eaip_db -c "SELECT version();"
```

### 3. Переменные окружения

Настройте переменные окружения для подключения к PostgreSQL:

```bash
# .env файл в корне проекта или в eaip_full_skeleton/services/ingest/
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eaip_db
POSTGRES_USER=eaip_user
POSTGRES_PASSWORD=eaip_password
```

---

## 📝 Шаг 1: Создание таблиц в PostgreSQL

### Автоматически (через init.sql)

Таблицы будут созданы автоматически при первом запуске PostgreSQL через Docker Compose.

### Вручную

Если нужно создать таблицы вручную:

```bash
cd eaip_full_skeleton/infra
docker compose exec postgres psql -U eaip_user -d eaip_db -f /docker-entrypoint-initdb.d/init.sql
```

Или используйте скрипт миграции:

```bash
cd eaip_full_skeleton/infra/db
docker compose exec -T postgres psql -U eaip_user -d eaip_db < migrate_sqlite_to_postgres.sql
```

---

## 🔄 Шаг 2: Миграция данных

### Вариант 1: Автоматическая миграция (рекомендуется)

Используйте готовый скрипт миграции:

```bash
# Из корня проекта
python tools/migrate_sqlite_to_postgres.py
```

Скрипт:
- ✅ Автоматически подключается к обеим БД
- ✅ Сохраняет связи между таблицами
- ✅ Логирует весь процесс
- ✅ Обрабатывает ошибки

### Вариант 2: Ручная миграция

Если нужен больше контроля, можете мигрировать таблицы по отдельности:

```python
import sqlite3
import psycopg2

# Подключения
sqlite_conn = sqlite3.connect('ingest_data.db')
pg_conn = psycopg2.connect(
    host='localhost',
    database='eaip_db',
    user='eaip_user',
    password='password'
)

# Миграция данных...
```

---

## 📊 Порядок миграции таблиц

Миграция должна происходить в правильном порядке (с учетом foreign keys):

1. **enterprises** - Предприятия (без зависимостей)
2. **normative_documents** - Нормативные документы (без зависимостей)
3. **uploads** - Загрузки (зависит от enterprises)
4. **parsed_data** - Распарсенные данные (зависит от uploads)
5. **uploads_storage** - Метаданные файлов (зависит от uploads)
6. **normative_rules** - Правила (зависит от normative_documents)
7. **normative_references** - Связи правил (зависит от normative_rules)
8. **normative_violations** - Нарушения (зависит от enterprises, normative_rules)
9. **aggregated_data** - Агрегированные данные (зависит от enterprises)
10. **node_consumption** - Потребление по узлам (зависит от enterprises)

---

## ⚙️ Шаг 3: Обновление кода

### 3.1 Обновить database.py

Замените SQLite на PostgreSQL в `eaip_full_skeleton/services/ingest/database.py`:

```python
# Было:
import sqlite3
conn = sqlite3.connect(DB_PATH)

# Станет:
import psycopg2
from psycopg2.extras import RealDictCursor
conn = psycopg2.connect(DATABASE_URL)
```

### 3.2 Изменить SQL запросы

**SQLite:**
```python
cursor.execute("SELECT * FROM enterprises WHERE id = ?", (id,))
```

**PostgreSQL:**
```python
cursor.execute("SELECT * FROM enterprises WHERE id = %s", (id,))
```

**Основные изменения:**
- `?` → `%s` (placeholders)
- `TEXT` → `JSONB` (для JSON данных)
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
- `DATETIME` → `TIMESTAMP`

### 3.3 Использовать JSONB

Преимущества JSONB:
- Индексы на JSON поля
- Быстрый поиск внутри JSON
- Валидация JSON

```python
# Было:
raw_json TEXT

# Стало:
raw_json JSONB
```

---

## 🧪 Шаг 4: Тестирование

### 4.1 Проверка данных

```bash
# Подключиться к PostgreSQL
docker compose exec postgres psql -U eaip_user -d eaip_db

# Проверить количество записей
SELECT COUNT(*) FROM enterprises;
SELECT COUNT(*) FROM uploads;
SELECT COUNT(*) FROM parsed_data;

# Сравнить с SQLite
sqlite3 ingest_data.db "SELECT COUNT(*) FROM enterprises;"
```

### 4.2 Проверка связей

```sql
-- Проверить foreign keys
SELECT 
    e.name,
    COUNT(u.id) as uploads_count
FROM enterprises e
LEFT JOIN uploads u ON u.enterprise_id = e.id
GROUP BY e.id, e.name;
```

### 4.3 Тестовый запуск сервиса

```bash
cd eaip_full_skeleton/services/ingest
uvicorn main:app --reload --port 8001
```

Проверить:
- ✅ Загрузка файлов работает
- ✅ Парсинг сохраняется в БД
- ✅ Запросы к API возвращают данные

---

## 🔧 Обновление database.py

### Пример обновления функции

**Было (SQLite):**
```python
def get_enterprise_by_id(enterprise_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, created_at FROM enterprises WHERE id = ?",
            (enterprise_id,),
        ).fetchone()
        return dict(row) if row else None
```

**Стало (PostgreSQL):**
```python
def get_enterprise_by_id(enterprise_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id, name, created_at FROM enterprises WHERE id = %s",
                (enterprise_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
```

---

## 🚨 Проблемы и решения

### Проблема: Ошибка подключения к PostgreSQL

**Решение:**
```bash
# Проверить, что PostgreSQL запущен
docker compose ps

# Проверить логи
docker compose logs postgres

# Проверить переменные окружения
echo $POSTGRES_HOST
echo $POSTGRES_PASSWORD
```

### Проблема: Ошибка при миграции JSON

**Решение:**
Убедитесь, что JSON валидный:
```python
import json
json.loads(json_string)  # Должен работать без ошибок
```

### Проблема: Несовпадение ID после миграции

**Решение:**
Скрипт миграции создает маппинг старых ID на новые. Используйте batch_id или другие уникальные поля для связи.

---

## 📊 Сравнение производительности

| Операция | SQLite | PostgreSQL |
|----------|--------|------------|
| SELECT (1 запись) | ~1ms | ~2ms |
| INSERT | ~2ms | ~3ms |
| JSON поиск | Медленно (full scan) | Быстро (индексы) |
| Конкурентность | Ограничена | Отличная |
| Размер БД | До 140TB | Неограничен |

---

## ✅ Чеклист миграции

- [ ] Установлен psycopg2-binary
- [ ] PostgreSQL запущен и доступен
- [ ] Переменные окружения настроены
- [ ] Таблицы созданы в PostgreSQL
- [ ] Данные мигрированы (скрипт выполнен)
- [ ] Проверено количество записей
- [ ] Проверены связи между таблицами
- [ ] Обновлен database.py
- [ ] Обновлены SQL запросы
- [ ] Протестирован сервис
- [ ] Все тесты проходят

---

## 🔄 Откат миграции

Если нужно вернуться к SQLite:

1. Остановите ingest сервис
2. Измените `database.py` обратно на SQLite
3. Перезапустите сервис

**Важно:** Данные в PostgreSQL останутся, но не будут использоваться.

---

## 📚 Дополнительные ресурсы

- [Документация psycopg2](https://www.psycopg.org/docs/)
- [PostgreSQL JSONB документация](https://www.postgresql.org/docs/current/datatype-json.html)
- [SQLAlchemy для async (альтернатива)](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

**Дата создания:** 2025-01-16  
**Последнее обновление:** 2025-01-16
