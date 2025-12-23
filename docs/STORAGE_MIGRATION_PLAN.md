# 🎯 План интеграции Redis/PostgreSQL для постоянного хранения

## 📊 Текущее состояние

### ✅ Что есть:
- **SQLite** (`ingest_data.db`) - работает, но не масштабируется
- **PostgreSQL** - настроен в Docker, есть `init.sql`, но не используется
- **Redis** - настроен в Docker, используется только для AI-кэша
- **Connection Pool** - модуль `connection_pool.py` готов, но не подключен

### ❌ Проблемы:
- Все данные в SQLite (не подходит для продакшена)
- In-memory кэш теряется при перезапуске
- Нет репликации и масштабирования
- PostgreSQL и Redis не используются для основных данных

---

## 🎯 Цель миграции

**Заменить SQLite на PostgreSQL для постоянного хранения + использовать Redis для кэша**

---

## 📋 План действий (пошагово)

### Этап 1: Подготовка (1-2 часа)

#### 1.1 Проверить текущие данные SQLite
```bash
# Проверить размер и количество записей
python -c "
import sqlite3
conn = sqlite3.connect('eaip_full_skeleton/services/ingest/ingest_data.db')
cursor = conn.execute('SELECT COUNT(*) FROM uploads')
print(f'Записей в uploads: {cursor.fetchone()[0]}')
cursor = conn.execute('SELECT COUNT(*) FROM parsed_data')
print(f'Записей в parsed_data: {cursor.fetchone()[0]}')
conn.close()
"
```

#### 1.2 Убедиться, что PostgreSQL запущен
```bash
cd infra
docker compose up -d postgres redis
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\dt"
```

#### 1.3 Создать скрипт миграции данных из SQLite в PostgreSQL
- Экспорт из SQLite
- Импорт в PostgreSQL
- Проверка целостности

---

### Этап 2: Адаптация database.py (2-3 часа)

#### 2.1 Создать абстракцию для БД
**Файл:** `eaip_full_skeleton/services/ingest/database_adapter.py`

```python
"""
Адаптер для работы с БД (SQLite или PostgreSQL)
Автоматически выбирает БД на основе переменных окружения
"""
import os
from typing import Optional, Dict, Any
from contextlib import contextmanager

# Определяем тип БД
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()  # sqlite или postgres

if DB_TYPE == "postgres":
    from utils.connection_pool import get_db_pool
    USE_POSTGRES = True
else:
    USE_POSTGRES = False
    import sqlite3
    DB_PATH = os.getenv("INGEST_DB_PATH", "ingest_data.db")

@contextmanager
def get_connection():
    """Универсальный контекстный менеджер для БД"""
    if USE_POSTGRES:
        pool = get_db_pool()
        with pool.get_postgres_connection() as conn:
            yield conn
    else:
        # SQLite (fallback)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
```

#### 2.2 Адаптировать SQL запросы
**Изменения в `database.py`:**

1. **Заменить `get_connection()`** на использование адаптера
2. **Адаптировать SQL синтаксис:**
   - SQLite: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - PostgreSQL: `SERIAL PRIMARY KEY` или `BIGSERIAL`
   - SQLite: `TEXT`
   - PostgreSQL: `VARCHAR` или `TEXT`
   - SQLite: `?` (placeholders)
   - PostgreSQL: `%s` (placeholders)

3. **Пример адаптации:**
```python
# Было (SQLite):
conn.execute("SELECT * FROM uploads WHERE batch_id = ?", (batch_id,))

# Станет (универсально):
if USE_POSTGRES:
    conn.execute("SELECT * FROM uploads WHERE batch_id = %s", (batch_id,))
else:
    conn.execute("SELECT * FROM uploads WHERE batch_id = ?", (batch_id,))
```

#### 2.3 Создать миграцию схемы
**Файл:** `tools/migrate_sqlite_to_postgres.py`

Скрипт для:
- Экспорта данных из SQLite
- Преобразования типов данных
- Импорта в PostgreSQL
- Валидации миграции

---

### Этап 3: Интеграция Redis для кэша (1-2 часа)

#### 3.1 Заменить in-memory кэш на Redis
**Файл:** `eaip_full_skeleton/services/ingest/main.py`

```python
# Было:
parsing_results_cache: Dict[str, Dict[str, Any]] = {}

# Станет:
from utils.redis_cache import RedisCache
parsing_cache = RedisCache(prefix="parsing:", ttl=3600)

# Использование:
# Сохранение
parsing_cache.set(batch_id, data)

# Получение
data = parsing_cache.get(batch_id)
if not data:
    # Загрузить из PostgreSQL
    data = database.get_upload_by_batch(batch_id)
    parsing_cache.set(batch_id, data)
```

#### 3.2 Создать модуль Redis кэша
**Файл:** `eaip_full_skeleton/services/ingest/utils/redis_cache.py`

```python
"""
Универсальный Redis кэш с fallback на in-memory
"""
import json
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

class RedisCache:
    def __init__(self, prefix: str = "cache:", ttl: int = 3600):
        self.prefix = prefix
        self.ttl = ttl
        self.redis_client = None
        self.memory_cache: Dict[str, Any] = {}
        
        if HAS_REDIS:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    password=os.getenv("REDIS_PASSWORD"),
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("Redis кэш подключен")
            except Exception as e:
                logger.warning(f"Redis недоступен, используется memory: {e}")
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        cache_key = f"{self.prefix}{key}"
        if self.redis_client:
            data = self.redis_client.get(cache_key)
            if data:
                return json.loads(data)
        return self.memory_cache.get(cache_key)
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        cache_key = f"{self.prefix}{key}"
        if self.redis_client:
            self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(value, ensure_ascii=False)
            )
        else:
            self.memory_cache[cache_key] = value
```

---

### Этап 4: Тестирование (1-2 часа)

#### 4.1 Тесты миграции
- Проверить все CRUD операции
- Сравнить данные SQLite vs PostgreSQL
- Проверить производительность

#### 4.2 Тесты Redis кэша
- Проверить кэширование
- Проверить TTL
- Проверить fallback на memory

#### 4.3 Интеграционные тесты
- Полный цикл: загрузка → парсинг → сохранение → получение
- Проверить при перезапуске сервиса

---

### Этап 5: Переключение (30 минут)

#### 5.1 Переменные окружения
```bash
# .env
DB_TYPE=postgres  # или sqlite для fallback
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=eaip_user
POSTGRES_PASSWORD=eaip_password
POSTGRES_DB=eaip_db

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=  # опционально
```

#### 5.2 Постепенное переключение
1. Запустить с `DB_TYPE=sqlite` (текущее состояние)
2. Протестировать миграцию данных
3. Переключить на `DB_TYPE=postgres`
4. Мониторить ошибки
5. При проблемах - откат на SQLite

---

## 🔄 Стратегия миграции

### Вариант A: Big Bang (быстро, рискованно)
- Остановить сервис
- Мигрировать все данные
- Переключить на PostgreSQL
- Запустить сервис

**Плюсы:** Быстро  
**Минусы:** Риск потери данных при ошибке

### Вариант B: Dual Write (безопасно, медленно) ⭐ РЕКОМЕНДУЕТСЯ
- Писать в обе БД одновременно
- Читать из PostgreSQL
- После проверки - отключить SQLite

**Плюсы:** Безопасно, можно откатиться  
**Минусы:** Дольше, больше нагрузка

### Вариант C: Read Replica (для продакшена)
- SQLite остается primary
- PostgreSQL - replica для чтения
- Постепенно переключать запись

**Плюсы:** Минимальный риск  
**Минусы:** Сложнее реализация

---

## 📝 Чеклист выполнения

### Подготовка
- [ ] Проверить данные в SQLite
- [ ] Убедиться, что PostgreSQL запущен
- [ ] Проверить схему БД в PostgreSQL

### Разработка
- [ ] Создать `database_adapter.py`
- [ ] Адаптировать `database.py` для PostgreSQL
- [ ] Создать скрипт миграции данных
- [ ] Создать `redis_cache.py`
- [ ] Заменить in-memory кэш на Redis

### Тестирование
- [ ] Тесты CRUD операций
- [ ] Тесты миграции данных
- [ ] Тесты Redis кэша
- [ ] Интеграционные тесты

### Деплой
- [ ] Настроить переменные окружения
- [ ] Выполнить миграцию данных
- [ ] Переключить на PostgreSQL
- [ ] Мониторить ошибки
- [ ] Документировать изменения

---

## ⚠️ Риски и митигация

### Риск 1: Потеря данных при миграции
**Митигация:**
- Полный бэкап SQLite перед миграцией
- Dual write режим
- Валидация данных после миграции

### Риск 2: Проблемы с производительностью
**Митигация:**
- Connection pooling
- Индексы в PostgreSQL
- Мониторинг производительности

### Риск 3: Несовместимость SQL
**Митигация:**
- Тестирование всех запросов
- Использование SQLAlchemy ORM (опционально)
- Fallback на SQLite

---

## 🎯 Итоговый результат

После миграции:
- ✅ Все данные в PostgreSQL (постоянное хранение)
- ✅ Redis для кэша (быстрый доступ)
- ✅ Масштабируемость (множественные инстансы)
- ✅ Резервное копирование (PostgreSQL бэкапы)
- ✅ Высокая доступность (репликация)

---

## 📚 Дополнительные ресурсы

- [PostgreSQL Migration Guide](https://www.postgresql.org/docs/current/migration.html)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [SQLAlchemy Connection Pooling](https://docs.sqlalchemy.org/en/14/core/pooling.html)

