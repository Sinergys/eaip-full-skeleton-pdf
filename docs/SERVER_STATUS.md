# Статус сервера

## 🚀 Запущен сервис

**Сервис:** `ingest` (EAIP Ingest Service)  
**Порт:** 8001  
**URL:** http://localhost:8001

## 📋 Доступные эндпоинты

### Основные:
- **Swagger UI (документация API):** http://localhost:8001/docs
- **Health check:** http://localhost:8001/health
- **Upload interface:** http://localhost:8001/web/upload

### API эндпоинты:
- `POST /ingest/upload` - загрузка файлов
- `GET /api/progress/{batch_id}` - статус обработки
- `GET /ingest/parse/{batch_id}/summary` - результаты парсинга
- `POST /ingest/validate` - валидация данных
- `GET /api/diagnose/pdf` - диагностика PDF

## 🔧 Управление сервером

### Остановка:
Нажмите `Ctrl+C` в терминале, где запущен сервер

### Перезапуск:
```bash
cd C:\eaip\eaip_full_skeleton\services\ingest
python -m uvicorn main:app --reload --port 8001
```

### Проверка статуса:
```bash
curl http://localhost:8001/health
```

## 📝 Логи

Сервер работает с автоматической перезагрузкой (`--reload`), изменения в коде применяются автоматически.

## 🌐 Другие сервисы

При необходимости можно запустить другие сервисы:

- **gateway-auth:** порт 8000
- **reports:** порт (см. README)
- **management:** порт 8006
- **analytics:** порт (см. README)
- **validate:** порт (см. README)
- **recommend:** порт (см. README)

