<#
.SYNOPSIS
    Комплексная диагностика системы для оценки возможности запуска Ollama.

.DESCRIPTION
    Скрипт собирает детальную информацию о системе Windows для оценки возможности 
    запуска и оптимизации работы Ollama (локальной LLM платформы).
    
    Собирает информацию о:
    - Процессоре (CPU): модель, ядра, частота, виртуализация
    - Оперативной памяти (RAM): объем, скорость, использование
    - Графических процессорах (GPU): модель, VRAM, драйверы
    - Дисковой подсистеме: объем, свободное пространство, файловые системы
    - Процессах: топ-10 по CPU и памяти
    - Сетевых интерфейсах: активные адаптеры и их характеристики
    - Зависимостях: установленные версии .NET Framework
    
    Автоматически запрашивает права администратора для полного доступа к системной информации.
    Результаты сохраняются в файл system_audit.txt в кодировке UTF-8.

.PARAMETER SkipElevation
    Пропустить автоматическое повышение прав администратора.
    Используется для тестирования или когда повышение прав невозможно.
    Некоторые данные могут быть недоступны без прав администратора.

.PARAMETER SkipReportViewer
    Не открывать отчет автоматически в Notepad после завершения аудита.
    Полезно при автоматизированном запуске скрипта.

.EXAMPLE
    .\system_audit.ps1
    
    Запускает полный аудит системы с автоматическим повышением прав и открытием отчета.

.EXAMPLE
    .\system_audit.ps1 -SkipElevation
    
    Запускает аудит без повышения прав (для тестирования).

.EXAMPLE
    .\system_audit.ps1 -SkipElevation -SkipReportViewer
    
    Запускает аудит без повышения прав и без открытия отчета (для автоматизации).

.OUTPUTS
    Файл system_audit.txt в текущей директории с полным отчетом о системе.

.NOTES
    Автор: Система аудита для Ollama
    Версия: 1.0
    Требования: Windows PowerShell 5.1+ или PowerShell Core 7+
    Права: Рекомендуется запуск с правами администратора для полного доступа к данным
    
    Оценка системы для Ollama:
    - ≥16 GB RAM: отлично, большинство моделей доступны
    - ≥8 GB RAM: средние модели (3B-7B параметров)
    - <8 GB RAM: только маленькие модели (1B-3B параметров)
    
    Дискретная видеокарта (≥2GB VRAM) значительно ускорит работу Ollama.

.LINK
    https://ollama.ai - Официальный сайт Ollama
#>

param(
    [switch]$SkipElevation,
    [switch]$SkipReportViewer
)

# Проверка прав администратора
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $SkipElevation -and -not $isAdmin) {
    Write-Host "Запуск с правами администратора..." -ForegroundColor Yellow
    try {
        $currentShellPath = (Get-Process -Id $PID -ErrorAction Stop).Path
    } catch {
        $currentShellPath = "powershell.exe"
    }

    try {
        Start-Process -FilePath $currentShellPath -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs | Out-Null
        exit
    } catch {
        Write-Warning "Не удалось перезапустить скрипт с повышенными правами: $($_.Exception.Message)"
        Write-Host "Продолжаю выполнение без повышения привилегий." -ForegroundColor Yellow
    }
} elseif ($SkipElevation -and -not $isAdmin) {
    Write-Host "Запуск без повышения прав по запросу пользователя." -ForegroundColor Yellow
}

Write-Host "=== СБОР ДАННЫХ СИСТЕМЫ ДЛЯ OLLAMA ===" -ForegroundColor Green
Write-Host "Начало аудита в: $(Get-Date)" -ForegroundColor Cyan

# Создаем или перезаписываем файл отчета
$auditFile = "system_audit.txt"
"=== ОТЧЕТ АУДИТА СИСТЕМЫ ДЛЯ OLLAMA ===" | Out-File -FilePath $auditFile -Encoding UTF8
"Время создания: $(Get-Date)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"========================================" | Out-File -FilePath $auditFile -Append -Encoding UTF8

# 1. СБОР ОСНОВНОЙ ИНФОРМАЦИИ О СИСТЕМЕ
Write-Host "1. Сбор основной информации о системе..." -ForegroundColor Yellow

$computerSystem = Get-CimInstance -ClassName Win32_ComputerSystem
$operatingSystem = Get-CimInstance -ClassName Win32_OperatingSystem
$computerName = $env:COMPUTERNAME

"`n=== ОСНОВНАЯ ИНФОРМАЦИЯ О СИСТЕМЕ ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Имя компьютера: $computerName" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Производитель: $($computerSystem.Manufacturer)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Модель: $($computerSystem.Model)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
$uptime = if ($operatingSystem.LastBootUpTime) { (Get-Date) - $operatingSystem.LastBootUpTime } else { $null }
if ($uptime) {
    "Время работы системы: $($uptime.ToString('dd\.hh\:mm\:ss'))" | Out-File -FilePath $auditFile -Append -Encoding UTF8
} else {
    "Время работы системы: нет данных" | Out-File -FilePath $auditFile -Append -Encoding UTF8
}

# 2. ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПРОЦЕССОРЕ
Write-Host "2. Анализ процессора..." -ForegroundColor Yellow

$processors = Get-CimInstance -ClassName Win32_Processor
$processorInfo = $processors | Select-Object -First 1

"`n=== ПРОЦЕССОР (CPU) ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Модель: $($processorInfo.Name)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Архитектура: $($processorInfo.AddressWidth)-бит" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Количество ядер: $($processorInfo.NumberOfCores)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Количество логических процессоров: $($processorInfo.NumberOfLogicalProcessors)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Текущая частота: $([math]::Round($processorInfo.CurrentClockSpeed / 1000, 2)) GHz" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Максимальная частота: $([math]::Round($processorInfo.MaxClockSpeed / 1000, 2)) GHz" | Out-File -FilePath $auditFile -Append -Encoding UTF8
$virtualizationSupport = switch ($processorInfo.VirtualizationFirmwareEnabled) {
    $true { 'Да' }
    $false { 'Нет' }
    default { 'Нет данных' }
}
"Поддержка виртуализации: $virtualizationSupport" | Out-File -FilePath $auditFile -Append -Encoding UTF8

# 3. ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПАМЯТИ (ОЗУ)
Write-Host "3. Анализ оперативной памяти..." -ForegroundColor Yellow

$memory = @(Get-CimInstance -ClassName Win32_PhysicalMemory)
$memorySlots = $memory.Count
$totalMemoryBytes = ($memory | Measure-Object -Property Capacity -Sum).Sum
$totalMemory = if ($totalMemoryBytes) { $totalMemoryBytes / 1GB } else { 0 }
$totalMemoryRounded = [math]::Round($totalMemory, 2)

"`n=== ОПЕРАТИВНАЯ ПАМЯТЬ (RAM) ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Всего слотов памяти: $memorySlots" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Общий объем памяти: $totalMemoryRounded GB" | Out-File -FilePath $auditFile -Append -Encoding UTF8
if ($memorySlots -gt 0 -and $memory[0].Speed) {
    "Скорость памяти: $($memory[0].Speed) MHz" | Out-File -FilePath $auditFile -Append -Encoding UTF8
} else {
    "Скорость памяти: нет данных" | Out-File -FilePath $auditFile -Append -Encoding UTF8
}

# Информация об использовании памяти
$osMemory = Get-CimInstance -ClassName Win32_OperatingSystem
$freeMemoryGB = if ($osMemory.FreePhysicalMemory) {
    [math]::Round(($osMemory.FreePhysicalMemory * 1KB) / 1GB, 2)
} else {
    0
}
$usedMemoryGB = if ($totalMemory -gt 0) {
    [math]::Round([math]::Max($totalMemory - $freeMemoryGB, 0), 2)
} else {
    0
}
"Доступно памяти: $freeMemoryGB GB" | Out-File -FilePath $auditFile -Append -Encoding UTF8
"Используется памяти: $usedMemoryGB GB" | Out-File -FilePath $auditFile -Append -Encoding UTF8

# 4. ИНФОРМАЦИЯ О ГРАФИЧЕСКОМ ПРОЦЕССОРЕ (GPU)
Write-Host "4. Анализ графических процессоров..." -ForegroundColor Yellow

$gpus = @(Get-CimInstance -ClassName Win32_VideoController | Where-Object { $_.Name -notlike "*Remote*" -and $_.Name -notlike "*Basic*" })

"`n=== ГРАФИЧЕСКИЕ ПРОЦЕССОРЫ (GPU) ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
if ($gpus.Count -eq 0) {
    "Графические адаптеры не обнаружены." | Out-File -FilePath $auditFile -Append -Encoding UTF8
} else {
    $gpuIndex = 1
    foreach ($gpu in $gpus) {
        "GPU #$($gpuIndex):" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        "  Модель: $($gpu.Name)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        if ($gpu.AdapterRAM) {
            "  VRAM: $([math]::Round($gpu.AdapterRAM / 1GB, 2)) GB" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        } else {
            "  VRAM: нет данных" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        }
        "  Драйвер: $($gpu.DriverVersion)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        $gpuIndex++
    }
}

# 5. ИНФОРМАЦИЯ О ДИСКОВОЙ ПОДСИСТЕМЕ
Write-Host "5. Анализ дискового пространства..." -ForegroundColor Yellow

$disks = @(Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 })

"`n=== ДИСКОВАЯ ПОДСИСТЕМА ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
if ($disks.Count -eq 0) {
    "Локальные диски не обнаружены." | Out-File -FilePath $auditFile -Append -Encoding UTF8
} else {
    foreach ($disk in $disks) {
        "Диск $($disk.DeviceID):" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        if ($disk.Size) {
            "  Общий объем: $([math]::Round($disk.Size / 1GB, 2)) GB" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        } else {
            "  Общий объем: нет данных" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        }
        if ($disk.FreeSpace) {
            "  Свободно: $([math]::Round($disk.FreeSpace / 1GB, 2)) GB" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        } else {
            "  Свободно: нет данных" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        }
        "  Тип файловой системы: $($disk.FileSystem)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
    }
}

# 6. ПРОЦЕССЫ ПОТРЕБЛЯЮЩИЕ РЕСУРСЫ
Write-Host "6. Анализ процессов..." -ForegroundColor Yellow

$topProcessesByCPU = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet, Id
$topProcessesByMemory = Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 Name, CPU, @{Name = "WorkingSet(MB)"; Expression = { [math]::Round($_.WorkingSet / 1MB, 2) } }, Id

"`n=== ТОП-10 ПРОЦЕССОВ ПО ИСПОЛЬЗОВАНИЮ CPU ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
$topProcessesByCPU | Format-Table -AutoSize | Out-String -Width 200 | Out-File -FilePath $auditFile -Append -Encoding UTF8

"`n=== ТОП-10 ПРОЦЕССОВ ПО ИСПОЛЬЗОВАНИЮ ПАМЯТИ ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
$topProcessesByMemory | Format-Table -AutoSize | Out-String -Width 200 | Out-File -FilePath $auditFile -Append -Encoding UTF8

# 7. СЕТЕВЫЕ ИНТЕРФЕЙСЫ
Write-Host "7. Анализ сетевых интерфейсов..." -ForegroundColor Yellow

# Используем Get-NetAdapter если доступен (более детальная информация),
# иначе fallback на WMI Win32_NetworkAdapter
$networkAdapters = @()
$getNetAdapterCmd = Get-Command -Name Get-NetAdapter -ErrorAction SilentlyContinue
if ($getNetAdapterCmd) {
    # PowerShell 5.1+ с модулем NetAdapter
    $networkAdapters = @(Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'Up' })
} else {
    # Fallback на WMI для совместимости
    $networkAdapters = @(Get-CimInstance -ClassName Win32_NetworkAdapter | Where-Object { $_.NetEnabled -eq $true })
}

"`n=== СЕТЕВЫЕ ИНТЕРФЕЙСЫ ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
if ($networkAdapters.Count -eq 0) {
    "Активные сетевые интерфейсы не обнаружены." | Out-File -FilePath $auditFile -Append -Encoding UTF8
} else {
    foreach ($adapter in $networkAdapters) {
        "Адаптер: $($adapter.Name)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        if ($adapter.PSObject.Properties.Match('Status')) {
            "  Состояние: $($adapter.Status)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        } elseif ($adapter.NetConnectionStatus) {
            "  Состояние: $($adapter.NetConnectionStatus)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        }

        if ($adapter.PSObject.Properties.Match('LinkSpeed')) {
            "  Скорость: $($adapter.LinkSpeed)" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        } elseif ($adapter.PSObject.Properties.Match('Speed') -and $adapter.Speed) {
            $speedMbps = [math]::Round($adapter.Speed / 1e6, 2)
            "  Скорость: $speedMbps Mbps" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        } else {
            "  Скорость: нет данных" | Out-File -FilePath $auditFile -Append -Encoding UTF8
        }
    }
}

# 8. ПРОВЕРКА УСТАНОВЛЕННЫХ ВЕРСИЙ .NET И ДРУГИХ ЗАВИСИМОСТЕЙ
Write-Host "8. Проверка зависимостей..." -ForegroundColor Yellow

"`n=== ЗАВИСИМОСТИ ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8
# Проверка версий .NET
try {
    $dotNetVersions = Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP' -Recurse -ErrorAction Stop |
        Get-ItemProperty -Name Version -ErrorAction SilentlyContinue |
        Where-Object { $_.PSChildName -match '^(?!S)\p{L}' } |
        Select-Object -ExpandProperty Version -Unique
} catch {
    $dotNetVersions = @()
    Write-Warning "Не удалось получить список версий .NET: $($_.Exception.Message)"
}

"Установленные версии .NET:" | Out-File -FilePath $auditFile -Append -Encoding UTF8
if ($dotNetVersions -and $dotNetVersions.Count -gt 0) {
    $dotNetVersions | ForEach-Object { "  $_" } | Out-File -FilePath $auditFile -Append -Encoding UTF8
} else {
    "  Версии .NET не обнаружены или доступ запрещен." | Out-File -FilePath $auditFile -Append -Encoding UTF8
}

# ЗАКЛЮЧЕНИЕ
Write-Host "9. Формирование заключения..." -ForegroundColor Yellow

"`n=== ЗАКЛЮЧЕНИЕ И ПЕРВОНАЧАЛЬНАЯ ОЦЕНКА ===" | Out-File -FilePath $auditFile -Append -Encoding UTF8

# Простая эвристика для оценки возможности запуска Ollama
# Используем округленное значение памяти для оценки
$totalRAM = $totalMemoryRounded

# Определяем наличие дискретной видеокарты:
# - VRAM >= 2GB (достаточно для моделей)
# - Исключаем интегрированные GPU (Intel, Microsoft Basic)
$hasDiscreteGPU = ($gpus | Where-Object {
        $_.AdapterRAM -and $_.AdapterRAM -ge 2GB -and
        $_.Name -notlike "*Intel*" -and
        $_.Name -notlike "*Microsoft Basic Display Adapter*"
    }).Count -gt 0

if ($totalRAM -ge 16) {
    "✓ ОЦЕНКА: Отлично! Система имеет достаточно памяти для запуска большинства моделей Ollama." | Out-File -FilePath $auditFile -Append -Encoding UTF8
} elseif ($totalRAM -ge 8) {
    "⚠ ОЦЕНКА: Система может запускать небольшие и средние модели Ollama (3B-7B параметров)." | Out-File -FilePath $auditFile -Append -Encoding UTF8
} elseif ($totalRAM -gt 0) {
    "⚠ ОЦЕНКА: ОЗУ ограничено. Рекомендуется использовать только маленькие модели (1B-3B параметров)." | Out-File -FilePath $auditFile -Append -Encoding UTF8
} else {
    "⚠ ОЦЕНКА: Не удалось определить объем доступной памяти. Проверьте права доступа или повторите аудит." | Out-File -FilePath $auditFile -Append -Encoding UTF8
}

if ($hasDiscreteGPU) {
    "✓ Обнаружена дискретная видеокарта. Это значительно ускорит работу Ollama." | Out-File -FilePath $auditFile -Append -Encoding UTF8
} else {
    "⚠ Дискретная видеокарта не обнаружена. Ollama будет работать на CPU." | Out-File -FilePath $auditFile -Append -Encoding UTF8
}

Write-Host "`nАудит завершен!" -ForegroundColor Green
Write-Host "Отчет сохранен в файл: $auditFile" -ForegroundColor Cyan
Write-Host "Следующий шаг: передать этот файл мне для анализа и рекомендаций по оптимизации." -ForegroundColor Yellow

# Открываем файл для просмотра
if (-not $SkipReportViewer) {
    Write-Host "`nОткрываю файл отчета..." -ForegroundColor Magenta
    try {
        Start-Process notepad.exe $auditFile | Out-Null
    } catch {
        Write-Warning "Не удалось открыть отчет автоматически: $($_.Exception.Message)"
    }
} else {
    Write-Host "Пропускаю автоматическое открытие отчета по запросу пользователя." -ForegroundColor Yellow
}

