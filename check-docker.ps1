# Скрипт диагностики Docker на Windows
# Запуск: PowerShell (Администратор) -> .\check-docker.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Диагностика Docker на Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  ВНИМАНИЕ: Скрипт запущен не от имени администратора!" -ForegroundColor Yellow
    Write-Host "   Некоторые проверки могут не работать." -ForegroundColor Yellow
    Write-Host ""
}

# 1. Проверка Docker CLI
Write-Host "1. Проверка Docker CLI..." -ForegroundColor Green
try {
    $dockerVersion = docker version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Docker CLI доступен" -ForegroundColor Green
        $dockerVersion | Select-Object -First 3
    } else {
        Write-Host "   ❌ Docker CLI не работает" -ForegroundColor Red
        Write-Host "   Ошибка: $dockerVersion" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Docker CLI не найден" -ForegroundColor Red
    Write-Host "   Установите Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
}
Write-Host ""

# 2. Проверка Docker Desktop процесса
Write-Host "2. Проверка Docker Desktop..." -ForegroundColor Green
$dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerProcess) {
    Write-Host "   ✅ Docker Desktop запущен (PID: $($dockerProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker Desktop не запущен" -ForegroundColor Red
    $dockerPath = "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Write-Host "   💡 Docker Desktop установлен, но не запущен" -ForegroundColor Yellow
        Write-Host "   Запустите: Start-Process '$dockerPath'" -ForegroundColor Yellow
    } else {
        Write-Host "   ❌ Docker Desktop не установлен" -ForegroundColor Red
    }
}
Write-Host ""

# 3. Проверка WSL
Write-Host "3. Проверка WSL..." -ForegroundColor Green
try {
    $wslList = wsl --list --verbose 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ WSL установлен" -ForegroundColor Green
        $wslList | Select-Object -First 5
    } else {
        Write-Host "   ⚠️  WSL не установлен или не настроен" -ForegroundColor Yellow
        Write-Host "   Установите: wsl --install -d Ubuntu" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ WSL не найден" -ForegroundColor Red
}
Write-Host ""

# 4. Проверка сети
Write-Host "4. Проверка подключения к Docker Hub..." -ForegroundColor Green
try {
    $netTest = Test-NetConnection production.cloudflare.docker.com -Port 443 -WarningAction SilentlyContinue
    if ($netTest.TcpTestSucceeded) {
        Write-Host "   ✅ Подключение к Docker Hub работает" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Не удается подключиться к Docker Hub" -ForegroundColor Red
        Write-Host "   Проверьте интернет-соединение и прокси настройки" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Ошибка проверки сети: $_" -ForegroundColor Red
}
Write-Host ""

# 5. Проверка DNS конфигурации Docker
Write-Host "5. Проверка DNS конфигурации Docker..." -ForegroundColor Green
$daemonJsonPath = "C:\ProgramData\Docker\config\daemon.json"
if (Test-Path $daemonJsonPath) {
    Write-Host "   ✅ Файл daemon.json найден" -ForegroundColor Green
    try {
        $daemonConfig = Get-Content $daemonJsonPath -Raw | ConvertFrom-Json
        if ($daemonConfig.dns) {
            Write-Host "   ✅ DNS настроен: $($daemonConfig.dns -join ', ')" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  DNS не настроен в daemon.json" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ⚠️  Не удается прочитать daemon.json: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  Файл daemon.json не найден" -ForegroundColor Yellow
    Write-Host "   Создайте: C:\ProgramData\Docker\config\daemon.json" -ForegroundColor Yellow
    Write-Host "   Содержимое: { `"dns`": [`"8.8.8.8`", `"1.1.1.1`"] }" -ForegroundColor Yellow
}
Write-Host ""

# 6. Проверка расширения Docker в Cursor
Write-Host "6. Проверка расширения Docker в Cursor..." -ForegroundColor Green
$cursorExtensionsPath = "$Env:USERPROFILE\.cursor\extensions"
if (Test-Path $cursorExtensionsPath) {
    $dockerExtension = Get-ChildItem -Path $cursorExtensionsPath -Filter "*ms-azuretools.vscode-docker*" -ErrorAction SilentlyContinue
    if ($dockerExtension) {
        Write-Host "   ✅ Расширение Docker установлено" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Расширение Docker не найдено" -ForegroundColor Yellow
        Write-Host "   Установите через: Ctrl+Shift+X -> поиск 'Docker' -> Install" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  Директория расширений Cursor не найдена" -ForegroundColor Yellow
}
Write-Host ""

# 7. Тест Docker (если доступен)
Write-Host "7. Тест Docker..." -ForegroundColor Green
if ($dockerProcess) {
    Write-Host "   Попытка выполнить: docker info" -ForegroundColor Cyan
    try {
        $timeout = 10  # секунд
        $job = Start-Job -ScriptBlock { docker info 2>&1 }
        $result = Wait-Job -Job $job -Timeout $timeout
        if ($result) {
            $output = Receive-Job -Job $job
            Remove-Job -Job $job
            if ($output -match "Server Version") {
                Write-Host "   ✅ Docker daemon отвечает" -ForegroundColor Green
                $output | Select-Object -First 5
            } else {
                Write-Host "   ⚠️  Docker daemon отвечает, но есть проблемы" -ForegroundColor Yellow
                $output | Select-Object -First 3
            }
        } else {
            Write-Host "   ❌ Docker команда зависла (таймаут $timeout сек)" -ForegroundColor Red
            Stop-Job -Job $job
            Remove-Job -Job $job
            Write-Host "   💡 Проблема: Docker daemon не отвечает или зависает" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ Ошибка теста: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   ⏭️  Пропущено (Docker Desktop не запущен)" -ForegroundColor Gray
}
Write-Host ""

# Итоговые рекомендации
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Рекомендации" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$issues = @()

if (-not $dockerProcess) {
    $issues += "Docker Desktop не запущен"
}
if (-not (Test-Path $daemonJsonPath)) {
    $issues += "DNS не настроен"
}
if (-not $dockerExtension) {
    $issues += "Расширение Docker не установлено в Cursor"
}

if ($issues.Count -eq 0) {
    Write-Host "✅ Все проверки пройдены!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Следующие шаги:" -ForegroundColor Cyan
    Write-Host "1. Попробуйте: docker version" -ForegroundColor White
    Write-Host "2. Попробуйте: docker pull hello-world" -ForegroundColor White
    Write-Host "3. В проекте: cd infra && docker compose ps" -ForegroundColor White
} else {
    Write-Host "⚠️  Обнаружены проблемы:" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "   - $issue" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "См. подробные инструкции в: DOCKER_FIX_WINDOWS.md" -ForegroundColor Cyan
}

Write-Host ""

