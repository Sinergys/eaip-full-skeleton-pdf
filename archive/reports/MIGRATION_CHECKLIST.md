# ✅ Чеклист миграции на PostgreSQL

**Дата:** 2025-01-16  
**Статус:** В процессе

---

## 📋 Предварительные шаги

- [ ] **Резервное копирование SQLite БД**
  ```bash
  cp eaip_full_skeleton/services/ingest/ingest_data.db eaip_full_skeleton/services/ingest/ingest_data.db.backup
  ```

- [ ] **Установка зависимостей**
  ```bash
  pip install psycopg2-binary>=2.9.0
  ```

- [ ] **Проверка PostgreSQL**
  ```bash
  cd eaip_full_skeleton/infra
  docker compose up -d postgres
  docker compose exec postgres psql -U eaip_user -d eaip_db -c "SELECT version();"
  ```

- [ ] **Настройка переменных окружения**
  - POSTGRES_HOST
  - POSTGRES_PORT
  - POSTGRES_DB
  - POSTGRES_USER
  - POSTGRES_PASSWORD

---

## 🗄️ Шаг 1: Создание таблиц

- [ ] **Создать SQL скрипт для таблиц PostgreSQL**
  - Файл: `eaip_full_skeleton/infra/db/migrate_sqlite_to_postgres.sql`
  - Статус: ✅ Создан

- [ ] **Применить SQL скрипт**
  ```bash
  cd eaip_full_skeleton/infra/db
  docker compose exec -T postgres psql -U eaip_user -d eaip_db < migrate_sqlite_to_postgres.sql
  ```

- [ ] **Проверить создание таблиц**
  ```sql
  \dt
  SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
  ```

---

## 🔄 Шаг 2: Миграция данных

- [ ] **Создать скрипт миграции**
  - Файл: `tools/migrate_sqlite_to_postgres.py`
  - Статус: ✅ Создан

- [ ] **Выполнить миграцию**
  ```bash
  python tools/migrate_sqlite_to_postgres.py
  ```

- [ ] **Проверить количество записей**
  ```sql
  -- PostgreSQL
  SELECT 'enterprises' as table_name, COUNT(*) FROM enterprises
  UNION ALL SELECT 'uploads', COUNT(*) FROM uploads
  UNION ALL SELECT 'parsed_data', COUNT(*) FROM parsed_data;
  
  -- SQLite (для сравнения)
  sqlite3 ingest_data.db "SELECT 'enterprises' as table_name, COUNT(*) FROM enterprises UNION ALL SELECT 'uploads', COUNT(*) FROM uploads;"
  ```

- [ ] **Проверить связи между таблицами**
  ```sql
  SELECT 
      e.name,
      COUNT(u.id) as uploads_count
  FROM enterprises e
  LEFT JOIN uploads u ON u.enterprise_id = e.id
  GROUP BY e.id, e.name;
  ```

---

## 💻 Шаг 3: Обновление кода

- [ ] **Обновить database.py**
  - Заменить `sqlite3` на `psycopg2`
  - Изменить placeholders: `?` → `%s`
  - Использовать `RealDictCursor` для результатов

- [ ] **Обновить SQL запросы**
  - INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL PRIMARY KEY
  - TEXT для JSON → JSONB
  - DATETIME → TIMESTAMP

- [ ] **Обновить requirements.txt**
  - Добавить `psycopg2-binary>=2.9.0`
  - Статус: ✅ Добавлен

- [ ] **Обновить импорты в main.py**
  - Проверить все импорты из database.py

---

## 🧪 Шаг 4: Тестирование

- [ ] **Тест подключения к PostgreSQL**
  ```python
  import psycopg2
  conn = psycopg2.connect(...)
  print("✓ Подключение успешно")
  ```

- [ ] **Тест чтения данных**
  ```python
  cursor.execute("SELECT * FROM enterprises LIMIT 5")
  rows = cursor.fetchall()
  print(f"✓ Найдено {len(rows)} предприятий")
  ```

- [ ] **Тест записи данных**
  ```python
  cursor.execute("INSERT INTO enterprises (name) VALUES ('Тест') RETURNING id")
  id = cursor.fetchone()[0]
  print(f"✓ Создано предприятие с ID {id}")
  ```

- [ ] **Тест API endpoints**
  - [ ] GET /api/enterprises
  - [ ] POST /api/upload
  - [ ] GET /api/upload/{batch_id}

- [ ] **Тест полного цикла**
  - Загрузить файл
  - Проверить парсинг
  - Проверить сохранение в БД
  - Проверить генерацию паспорта

---

## 📊 Шаг 5: Валидация данных

- [ ] **Сравнить данные в SQLite и PostgreSQL**
  - Количество записей
  - Содержимое записей (выборочно)
  - Связи между таблицами

- [ ] **Проверить JSON данные**
  ```sql
  SELECT 
      upload_id,
      jsonb_typeof(raw_json) as json_type,
      raw_json->>'sheets' as has_sheets
  FROM parsed_data
  WHERE raw_json IS NOT NULL
  LIMIT 10;
  ```

- [ ] **Проверить индексы**
  ```sql
  SELECT 
      tablename,
      indexname,
      indexdef
  FROM pg_indexes
  WHERE schemaname = 'public'
  ORDER BY tablename, indexname;
  ```

---

## 🔧 Шаг 6: Оптимизация

- [ ] **Настроить connection pooling**
  ```python
  from sqlalchemy import create_engine
  engine = create_engine(..., pool_size=10, max_overflow=20)
  ```

- [ ] **Добавить индексы для часто используемых запросов**
  ```sql
  CREATE INDEX IF NOT EXISTS idx_uploads_enterprise_status 
  ON uploads(enterprise_id, status);
  ```

- [ ] **Настроить autovacuum для JSONB**
  ```sql
  ALTER TABLE parsed_data SET (autovacuum_vacuum_scale_factor = 0.05);
  ```

---

## ✅ Финальная проверка

- [ ] **Все тесты проходят**
- [ ] **Нет ошибок в логах**
- [ ] **Производительность не хуже SQLite**
- [ ] **Документация обновлена**
- [ ] **Резервная копия сохранена**

---

## 🚀 После миграции

- [ ] **Удалить SQLite файл** (опционально, после проверки)
  ```bash
  mv ingest_data.db ingest_data.db.old
  ```

- [ ] **Обновить документацию**
  - README.md
  - DEPLOYMENT_GUIDE.md

- [ ] **Уведомить команду**
  - Изменения в БД
  - Новые зависимости
  - Обновление переменных окружения

---

## 📝 Заметки

- Дата начала: 2025-01-16
- Ответственный: AI Assistant
- Статус: В процессе

---

**Следующий шаг:** Выполнить миграцию данных
