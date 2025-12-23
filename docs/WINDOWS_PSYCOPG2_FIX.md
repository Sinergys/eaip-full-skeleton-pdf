# 🔧 Решение проблемы psycopg2 на Windows

## Проблема

Ошибка: `'utf-8' codec can't decode byte 0xc2 in position 61`

Это известный баг psycopg2 на Windows - он неправильно читает переменные окружения при инициализации.

## ✅ Решение от продвинутых программистов

### Вариант 1: Использовать Docker для миграции (рекомендуется)

Обходим проблему полностью, используя PostgreSQL внутри Docker:

```bash
# Экспортируем данные через Python (SQLite работает)
python export_data.py

# Импортируем через Docker exec (PostgreSQL работает)
docker compose exec -T postgres psql -U eaip_user -d eaip_db < import.sql
```

### Вариант 2: Исправить системную локаль Windows

```powershell
# Временно установить UTF-8 локаль
$env:LC_ALL = "C.UTF-8"
$env:LANG = "C.UTF-8"

# Или через реестр (требует админ прав)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage" -Name "ACP" -Value "65001"
```

### Вариант 3: Использовать чистую среду

```powershell
# Создать новый venv
python -m venv venv_postgres
.\venv_postgres\Scripts\Activate.ps1

# Установить только нужные пакеты
pip install psycopg2-binary

# Запустить миграцию в чистом окружении
```

## Рекомендация

**Использовать вариант 1 (Docker exec)** - это самый надежный способ, который работает всегда.

