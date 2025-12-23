# Скрипт для копирования шаблонов энергопаспортов и примерных отчётов в проект EAIP
# Шаг B.1 — Подготовка базовых файлов шаблона энергопаспорта и отчётов

$ErrorActionPreference = "Continue"

# Исходные каталоги (проверяем оба: указанный и родительский)
$SourceDirSpecified = "C:\Users\DELL\Downloads\Telegram Desktop\ТЭС"
$SourceDirParent = "C:\Users\DELL\Downloads\Telegram Desktop"

# Определяем рабочий каталог: сначала проверяем указанный, затем родительский
$SourceDir = $null
if (Test-Path -Path $SourceDirSpecified -PathType Container) {
    # Проверяем, есть ли нужные файлы в указанном каталоге
    $TestFile = Join-Path -Path $SourceDirSpecified -ChildPath "энергопаспорт (3) (10) (2).xlsx"
    if (Test-Path -Path $TestFile -PathType Leaf) {
        $SourceDir = $SourceDirSpecified
        Write-Host "Используется указанный каталог: $SourceDirSpecified" -ForegroundColor Green
    }
}

# Если в указанном каталоге нет файлов, проверяем родительский
if ($null -eq $SourceDir) {
    if (Test-Path -Path $SourceDirParent -PathType Container) {
        $TestFile = Join-Path -Path $SourceDirParent -ChildPath "энергопаспорт (3) (10) (2).xlsx"
        if (Test-Path -Path $TestFile -PathType Leaf) {
            $SourceDir = $SourceDirParent
            Write-Host "Файлы не найдены в указанном каталоге, используется родительский: $SourceDirParent" -ForegroundColor Yellow
        }
    }
}

# Целевые каталоги в проекте
$TargetTemplatesDir = "docs\input_templates"
$TargetExamplesDir = "docs\input_examples"

# Списки файлов для копирования
$Templates = @(
    "энергопаспорт (3) (10) (2).xlsx",
    "энергопаспорт (3) (10) (2)нев.xlsx",
    "Энергопаспорт ХАмкор нур.xlsx",
    "Энергопаспорт Метин Ирода.xlsm"
)

$Reports = @(
    "МЕТИН ИРОДА ОТЧЕТ.docx",
    "МЕТИН ИРОДА ОТЧЕТ (4).docx",
    "Навои ТЭС.docx"
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Копирование шаблонов и отчётов для EAIP" -ForegroundColor Cyan
Write-Host "Шаг B.1" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Проверка определения рабочего каталога
if ($null -eq $SourceDir) {
    Write-Host "ОШИБКА: Не удалось найти исходные файлы ни в указанном каталоге, ни в родительском." -ForegroundColor Red
    Write-Host "Проверенные пути:" -ForegroundColor Yellow
    Write-Host "  1. $SourceDirSpecified" -ForegroundColor Yellow
    Write-Host "  2. $SourceDirParent" -ForegroundColor Yellow
    Write-Host "Проверьте пути и повторите попытку." -ForegroundColor Yellow
    exit 1
}

Write-Host "Исходный каталог определён: $SourceDir" -ForegroundColor Green
Write-Host ""

# Создание целевых директорий при необходимости
if (-not (Test-Path -Path $TargetTemplatesDir -PathType Container)) {
    New-Item -ItemType Directory -Path $TargetTemplatesDir -Force | Out-Null
    Write-Host "Создана директория: $TargetTemplatesDir" -ForegroundColor Yellow
}

if (-not (Test-Path -Path $TargetExamplesDir -PathType Container)) {
    New-Item -ItemType Directory -Path $TargetExamplesDir -Force | Out-Null
    Write-Host "Создана директория: $TargetExamplesDir" -ForegroundColor Yellow
}

Write-Host ""

# Статистика
$CopiedCount = 0
$SkippedCount = 0
$NotFoundCount = 0
$ErrorCount = 0

# Копирование шаблонов (Excel)
Write-Host "--- Копирование шаблонов энергопаспортов ---" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $Templates) {
    $SourcePath = Join-Path -Path $SourceDir -ChildPath $file
    $TargetPath = Join-Path -Path $TargetTemplatesDir -ChildPath $file
    
    if (-not (Test-Path -Path $SourcePath -PathType Leaf)) {
        Write-Host "  ❌ НЕ НАЙДЕН: $file" -ForegroundColor Red
        $NotFoundCount++
        continue
    }
    
    if (Test-Path -Path $TargetPath -PathType Leaf) {
        Write-Host "  ⏭️  ПРОПУЩЕН (уже существует): $file" -ForegroundColor Yellow
        $SkippedCount++
        continue
    }
    
    try {
        Copy-Item -Path $SourcePath -Destination $TargetPath -Force
        $FileSize = (Get-Item -Path $SourcePath).Length
        $FileSizeKB = [math]::Round($FileSize / 1KB, 1)
        Write-Host "  ✅ СКОПИРОВАН: $file ($FileSizeKB КБ)" -ForegroundColor Green
        $CopiedCount++
    }
    catch {
        Write-Host "  ❌ ОШИБКА при копировании $file : $_" -ForegroundColor Red
        $ErrorCount++
    }
}

Write-Host ""

# Копирование отчётов (Word)
Write-Host "--- Копирование примерных отчётов ---" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $Reports) {
    $SourcePath = Join-Path -Path $SourceDir -ChildPath $file
    $TargetPath = Join-Path -Path $TargetExamplesDir -ChildPath $file
    
    if (-not (Test-Path -Path $SourcePath -PathType Leaf)) {
        Write-Host "  ❌ НЕ НАЙДЕН: $file" -ForegroundColor Red
        $NotFoundCount++
        continue
    }
    
    if (Test-Path -Path $TargetPath -PathType Leaf) {
        Write-Host "  ⏭️  ПРОПУЩЕН (уже существует): $file" -ForegroundColor Yellow
        $SkippedCount++
        continue
    }
    
    try {
        Copy-Item -Path $SourcePath -Destination $TargetPath -Force
        $FileSize = (Get-Item -Path $SourcePath).Length
        $FileSizeMB = [math]::Round($FileSize / 1MB, 2)
        Write-Host "  ✅ СКОПИРОВАН: $file ($FileSizeMB МБ)" -ForegroundColor Green
        $CopiedCount++
    }
    catch {
        Write-Host "  ❌ ОШИБКА при копировании $file : $_" -ForegroundColor Red
        $ErrorCount++
    }
}

# Итоговая статистика
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Итоги копирования:" -ForegroundColor Cyan
Write-Host "  ✅ Скопировано: $CopiedCount" -ForegroundColor Green
Write-Host "  ⏭️  Пропущено (уже существуют): $SkippedCount" -ForegroundColor Yellow
Write-Host "  ❌ Не найдено: $NotFoundCount" -ForegroundColor Red
Write-Host "  ❌ Ошибок: $ErrorCount" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Cyan

if ($NotFoundCount -gt 0 -or $ErrorCount -gt 0) {
    Write-Host ""
    Write-Host "ВНИМАНИЕ: Некоторые файлы не были скопированы. Проверьте исходный путь и права доступа." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Копирование завершено успешно!" -ForegroundColor Green

