# 🔧 Исправление проблемы кодировки Windows для psycopg2

## Проблема

Ошибка: `'utf-8' codec can't decode byte 0xc2 in position 61: invalid continuation byte`

Это известная проблема psycopg2 на Windows при чтении переменных окружения.

## ✅ Решения от продвинутых программистов

### Решение 1: Использовать SQLAlchemy (рекомендуется)

SQLAlchemy правильно обрабатывает кодировку и обходит проблему psycopg2:

```python
from sqlalchemy import create_engine, text

engine = create_engine(
    'postgresql://eaip_user:eaip_password@localhost:5432/eaip_db',
    pool_pre_ping=True
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
```

### Решение 2: Использовать asyncpg (альтернатива)

```python
import asyncpg

conn = await asyncpg.connect(
    host='localhost',
    port=5432,
    database='eaip_db',
    user='eaip_user',
    password='eaip_password'
)
```

### Решение 3: Обход через Docker exec

Экспортировать данные через Python, импортировать через Docker:

```bash
# Экспорт
python export_sqlite.py > data.json

# Импорт через Docker
docker compose exec -T postgres psql -U eaip_user -d eaip_db < import.sql
```

### Решение 4: Исправить системную локаль Windows

```powershell
# Установить UTF-8 как системную локаль
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage" -Name "ACP" -Value "65001"
# Требует перезагрузки
```

## Рекомендация

**Использовать SQLAlchemy** - это стандартный подход, который используют все продвинутые программисты для работы с PostgreSQL в Python.

