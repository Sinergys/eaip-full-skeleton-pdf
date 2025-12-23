# Исправление Docker в Cursor на Windows

**Проблема:** Команды Docker зависают, модуль Docker в Cursor не установился.

## Анализ рекомендаций

Рекомендации выглядят корректно и покрывают основные проблемы Docker на Windows:

### ✅ Правильные шаги:
1. **Сеть и прокси** - часто проблема в DNS/прокси настройках
2. **WSL + Docker Desktop** - правильная последовательность установки
3. **DNS конфигурация** - важна для работы Docker Hub
4. **Настройка Cursor** - интеграция с Docker

### ⚠️ Возможные проблемы:
- Docker Desktop может быть уже установлен, но не настроен
- WSL может быть установлен, но не активирован
- Проблемы с правами администратора

## План действий (пошагово)

### Шаг 1: Диагностика текущего состояния

Выполните в PowerShell (Администратор):

```powershell
# Проверка Docker
docker version
docker info

# Проверка WSL
wsl --list --verbose

# Проверка Docker Desktop
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue

# Проверка сети
Test-NetConnection production.cloudflare.docker.com -Port 443
```

### Шаг 2: Исправление сети (если проблемы)

```powershell
# Сброс прокси и DNS
netsh winhttp reset proxy
netsh winsock reset
ipconfig /flushdns

# Проверка подключения
Test-NetConnection production.cloudflare.docker.com -Port 443
```

### Шаг 3: Установка/обновление WSL

```powershell
# Проверка текущей версии WSL
wsl --version

# Установка Ubuntu (если не установлен)
wsl --install -d Ubuntu

# Или обновление существующего
wsl --update
```

### Шаг 4: Установка Docker Desktop

```powershell
# Проверка, установлен ли Docker Desktop
Test-Path "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"

# Если не установлен, установить через winget
winget install -e --id Docker.DockerDesktop

# Или скачать с официального сайта:
# https://www.docker.com/products/docker-desktop/
```

**⚠️ ВАЖНО:** После установки Docker Desktop **перезагрузите компьютер**.

### Шаг 5: После перезагрузки - настройка Docker

```powershell
# Закрыть WSL (если запущен)
wsl --shutdown

# Переключить Docker на Linux engine
& "$Env:ProgramFiles\Docker\Docker\DockerCli.exe" -SwitchLinuxEngine

# Проверка версии Docker CLI
& "$Env:ProgramFiles\Docker\Docker\resources\com.docker.cli.exe" version

# Проверка Docker
docker version
```

### Шаг 6: Настройка DNS для Docker

Создайте файл `C:\ProgramData\Docker\config\daemon.json`:

```json
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
```

**PowerShell команда для создания:**

```powershell
# Создать директорию, если не существует
New-Item -ItemType Directory -Force -Path "C:\ProgramData\Docker\config"

# Создать файл daemon.json
@"
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
"@ | Out-File -FilePath "C:\ProgramData\Docker\config\daemon.json" -Encoding UTF8

# Перезапустить Docker Desktop
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Start-Process "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
```

**Подождите 30-60 секунд** пока Docker Desktop запустится.

### Шаг 7: Тестирование Docker

```powershell
# Простой тест
docker run --rm hello-world

# Загрузка образа
docker pull alpine:latest

# Проверка информации
docker images
docker info
```

### Шаг 8: Настройка Cursor

#### 8.1. Установка расширения Docker

```powershell
# Открыть Cursor с установкой расширения
& "$Env:LOCALAPPDATA\Programs\cursor\Cursor.exe" --install-extension ms-azuretools.vscode-docker
```

Или через интерфейс Cursor:
1. Нажмите `Ctrl+Shift+X` (открыть Extensions)
2. Найдите "Docker" от Microsoft
3. Нажмите "Install"

#### 8.2. Настройка settings.json

Откройте настройки Cursor (`Ctrl+,`) и добавьте в `settings.json`:

```json
{
  "http.proxyStrictSSL": false,
  "docker.dockerPath": "C:\\Program Files\\Docker\\Docker\\resources\\com.docker.cli.exe"
}
```

**Или через PowerShell:**

```powershell
# Путь к settings.json Cursor
$settingsPath = "$Env:APPDATA\Cursor\User\settings.json"

# Прочитать текущие настройки
$settings = Get-Content $settingsPath -Raw | ConvertFrom-Json

# Добавить/обновить настройки Docker
$settings | Add-Member -MemberType NoteProperty -Name "http.proxyStrictSSL" -Value $false -Force
$settings | Add-Member -MemberType NoteProperty -Name "docker.dockerPath" -Value "C:\Program Files\Docker\Docker\resources\com.docker.cli.exe" -Force

# Сохранить
$settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
```

#### 8.3. Перезапуск Cursor

Закройте и откройте Cursor заново.

### Шаг 9: Финальное тестирование

```powershell
# В терминале Cursor выполните:
docker pull hello-world
docker images
docker info

# Проверка docker-compose
docker compose version

# Тест проекта
cd eaip_full_skeleton/infra
docker compose ps
```

## Альтернативное решение (если проблемы продолжаются)

### Вариант 1: Использовать Docker через WSL напрямую

```powershell
# Войти в WSL
wsl

# В WSL установить Docker
sudo apt update
sudo apt install docker.io docker-compose

# Запустить Docker daemon
sudo service docker start

# Проверить
docker version
```

### Вариант 2: Использовать Podman вместо Docker

Podman - альтернатива Docker, не требует daemon:

```powershell
winget install -e --id RedHat.Podman
```

## Диагностика проблем

### Проблема: "Cannot connect to the Docker daemon"

**Решение:**
```powershell
# Проверить, запущен ли Docker Desktop
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue

# Если не запущен, запустить
Start-Process "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"

# Подождать 30 секунд и проверить
Start-Sleep -Seconds 30
docker version
```

### Проблема: "Network timeout" при pull образов

**Решение:**
1. Проверить DNS настройки (шаг 6)
2. Проверить прокси настройки Windows
3. Попробовать другой DNS (например, 8.8.4.4)

### Проблема: "WSL 2 installation is incomplete"

**Решение:**
```powershell
# Обновить WSL
wsl --update

# Установить компоненты вручную
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Перезагрузить компьютер
```

## Чеклист проверки

- [ ] Docker Desktop установлен и запущен
- [ ] WSL 2 установлен и работает
- [ ] DNS настроен в daemon.json
- [ ] Сеть работает (Test-NetConnection проходит)
- [ ] `docker version` работает без зависаний
- [ ] `docker pull hello-world` успешно выполняется
- [ ] Расширение Docker установлено в Cursor
- [ ] settings.json настроен правильно
- [ ] `docker compose ps` работает в проекте

## Отчет о проблемах

После выполнения шагов, сообщите:

1. **Где была проблема:**
   - [ ] Сеть/прокси
   - [ ] WSL не установлен/не настроен
   - [ ] Docker Desktop не установлен/не запущен
   - [ ] DNS проблемы
   - [ ] Расширение Cursor не установилось
   - [ ] Другое: ___________

2. **Что исправлено:**
   - Какие шаги помогли
   - Какие команды выполнились успешно

3. **Итог тестов:**
   - `docker version` - работает/не работает
   - `docker pull hello-world` - работает/не работает
   - `docker compose ps` - работает/не работает

## Быстрая команда для проверки всего

```powershell
Write-Host "=== Проверка Docker ===" -ForegroundColor Green
docker version
Write-Host "`n=== Проверка WSL ===" -ForegroundColor Green
wsl --list --verbose
Write-Host "`n=== Проверка Docker Desktop ===" -ForegroundColor Green
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Select-Object ProcessName, Id
Write-Host "`n=== Проверка сети ===" -ForegroundColor Green
Test-NetConnection production.cloudflare.docker.com -Port 443
Write-Host "`n=== Проверка DNS конфигурации ===" -ForegroundColor Green
Test-Path "C:\ProgramData\Docker\config\daemon.json"
if (Test-Path "C:\ProgramData\Docker\config\daemon.json") {
    Get-Content "C:\ProgramData\Docker\config\daemon.json"
}
```

## Полезные ссылки

- Docker Desktop для Windows: https://www.docker.com/products/docker-desktop/
- WSL документация: https://learn.microsoft.com/en-us/windows/wsl/
- Docker расширение для VS Code/Cursor: https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker

