# 🔄 Требования к пересборке Docker образов

**Дата:** 2025-01-27  
**Причина:** Множественные изменения кода, сделанные когда Docker не был запущен

---

## 📊 Анализ Dockerfile

Все сервисы используют `COPY . .`, что означает:
- **Код копируется в образ при сборке**
- **Изменения в коде НЕ попадают в уже собранные образы**
- **Требуется пересборка образов после изменений кода**

---

## 🔍 Какие сервисы нужно пересобрать

### Все сервисы используют `COPY . .`:

| Сервис | Dockerfile | COPY команда | Нужна пересборка |
|--------|-----------|--------------|------------------|
| `ingest` | ✅ | `COPY . .` | ✅ **ДА** |
| `reports` | ✅ | `COPY . .` | ✅ **ДА** |
| `gateway-auth` | ✅ | `COPY . .` | ✅ **ДА** |
| `validate` | ✅ | `COPY . .` | ✅ **ДА** |
| `analytics` | ✅ | `COPY . .` | ✅ **ДА** |
| `recommend` | ✅ | `COPY . .` | ✅ **ДА** |
| `management` | ✅ | `COPY . .` | ✅ **ДА** |

---

## 📝 Изменения, которые были сделаны

### 1. Сервис `reports` (energy_passport)
- ✅ Изменения в `services/reports/energy_passport/`
- ✅ Генерация паспорта, заполнение данных
- ✅ Модуль `quarterly_production.py`
- ✅ Исправления в `data_collector.py`, `generator.py`

**Требуется пересборка:** ✅ **ДА**

### 2. Сервис `ingest`
- ✅ Изменения в парсинге и агрегации
- ✅ Обновления в `energy_aggregator.py`
- ✅ Исправления в `resource_classifier.py`
- ✅ Изменения в `main.py`

**Требуется пересборка:** ✅ **ДА**

### 3. Другие сервисы
- ⚠️ Возможны изменения для качества кода
- ⚠️ Исправления форматирования, типов, документации

**Требуется пересборка:** ✅ **ДА** (для всех, чтобы быть уверенными)

---

## 🚀 Как пересобрать образы

### Вариант 1: Пересобрать все сервисы (рекомендуется)

```bash
cd eaip_full_skeleton/infra

# Пересобрать все образы без кэша
docker compose build --no-cache

# Или пересобрать только измененные (с кэшем)
docker compose build
```

### Вариант 2: Пересобрать только конкретные сервисы

```bash
cd eaip_full_skeleton/infra

# Пересобрать только ingest
docker compose build ingest

# Пересобрать только reports
docker compose build reports

# Пересобрать ingest и reports
docker compose build ingest reports
```

### Вариант 3: Пересобрать и перезапустить

```bash
cd eaip_full_skeleton/infra

# Пересобрать и перезапустить все сервисы
docker compose up -d --build

# Или только конкретные
docker compose up -d --build ingest reports
```

---

## ⚠️ Важные замечания

### 1. Использование кэша

**С кэшем (быстрее):**
```bash
docker compose build
```
- Использует кэш для слоев, которые не изменились
- Быстрее, но может пропустить некоторые изменения

**Без кэша (надежнее):**
```bash
docker compose build --no-cache
```
- Пересобирает все с нуля
- Гарантирует, что все изменения попадут в образ
- Медленнее (10-20 минут)

### 2. Порядок пересборки

Если сервисы зависят друг от друга, порядок не важен - Docker Compose сам разберется.

### 3. Время пересборки

- **С кэшем:** 2-5 минут
- **Без кэша:** 10-20 минут
- **ingest** дольше всего (из-за системных зависимостей: Tesseract, Poppler, Java)

---

## 📋 Рекомендуемый план действий

### Шаг 1: Остановить текущие контейнеры (если запущены)

```bash
cd eaip_full_skeleton/infra
docker compose down
```

### Шаг 2: Пересобрать образы

**Вариант A (быстро, с кэшем):**
```bash
docker compose build
```

**Вариант B (надежно, без кэша):**
```bash
docker compose build --no-cache
```

### Шаг 3: Запустить сервисы

```bash
docker compose up -d
```

### Шаг 4: Проверить статус

```bash
# Проверить запущенные контейнеры
docker compose ps

# Проверить логи
docker compose logs -f ingest
docker compose logs -f reports
```

---

## 🔍 Проверка после пересборки

### 1. Проверить, что образы обновились

```bash
docker images | grep eaip
```

### 2. Проверить, что контейнеры запущены

```bash
docker compose ps
```

### 3. Проверить health endpoints

```bash
# Ingest
curl http://localhost:8001/health

# Reports
curl http://localhost:8005/health

# Gateway
curl http://localhost:8000/health
```

---

## ⚡ Быстрая команда (все в одном)

```bash
cd eaip_full_skeleton/infra

# Остановить, пересобрать и запустить
docker compose down
docker compose build
docker compose up -d

# Проверить статус
docker compose ps
```

---

## 🎯 Итоговая рекомендация

**✅ ДА, нужно пересобрать все образы**

**Причина:**
- Все сервисы используют `COPY . .`
- Были изменения в коде (особенно в `ingest` и `reports`)
- Изменения не попадут в уже собранные образы

**Рекомендуемая команда:**
```bash
cd eaip_full_skeleton/infra
docker compose build
docker compose up -d
```

**Время:** ~5-10 минут (с кэшем) или ~15-20 минут (без кэша)

---

*Отчет создан на основе анализа Dockerfile и истории изменений*

