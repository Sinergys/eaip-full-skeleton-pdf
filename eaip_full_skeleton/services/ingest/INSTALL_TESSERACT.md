# Установка Tesseract OCR для Windows

## Проблема
При обработке сканированных PDF/изображений возникает ошибка:
```
tesseract is not installed or it's not in your PATH
```

## Решение для Windows

### ⭐ Вариант 1: Установка через установщик (РЕКОМЕНДУЕТСЯ)

1. **Скачайте установщик Tesseract:**
   - **Прямая ссылка:** https://digi.bib.uni-mannheim.de/tesseract/
   - Или через GitHub: https://github.com/UB-Mannheim/tesseract/wiki
   - Выберите последнюю версию для Windows 64-bit
   - Файл будет называться примерно: `tesseract-ocr-w64-setup-5.4.0.20240619.exe` (или новее)

2. **Установите Tesseract:**
   - Запустите скачанный `.exe` файл
   - **ВАЖНО:** При установке отметьте опцию **"Add to PATH"** или **"Add Tesseract to PATH"**
   - Выберите путь установки (по умолчанию: `C:\Program Files\Tesseract-OCR`)
   - **Обязательно установите языковые пакеты:**
     - ✅ **English** (обязательно, уже включен)
     - ✅ **Russian** (для распознавания русского текста)
     - Можно установить и другие языки при необходимости

3. **Проверьте установку:**
   ```powershell
   # Откройте НОВЫЙ терминал (важно!)
   tesseract --version
   ```
   
   Должно вывести что-то вроде:
   ```
   tesseract 5.4.0
    leptonica-1.84.1
    ...
   ```

4. **Проверьте доступные языки:**
   ```powershell
   tesseract --list-langs
   ```
   
   Должны быть: `eng` и `rus` (если установили русский)

5. **Перезапустите терминал/IDE/сервер** после установки
   - Это важно, чтобы изменения PATH вступили в силу

### Вариант 2: Установка через Chocolatey (если установлен)

**Сначала установите Chocolatey** (если еще не установлен):
```powershell
# Запустите PowerShell от имени администратора
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Затем установите Tesseract:
```powershell
choco install tesseract
choco install tesseract-languages  # Для поддержки русского языка
```

### Вариант 3: Указание пути в коде (временное решение)

Если Tesseract установлен, но не в PATH, можно указать путь напрямую:

```python
import pytesseract

# Укажите путь к tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Проверка установки

После установки проверьте:

```powershell
# Проверка версии
tesseract --version

# Проверка доступных языков
tesseract --list-langs
```

Должны быть доступны: `eng` и `rus` (если установили русский пакет).

## Решение для Linux

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-rus  # Для русского языка
```

## Решение для macOS

```bash
brew install tesseract
brew install tesseract-lang  # Для поддержки языков
```

## После установки

1. **Перезапустите сервер/скрипт** - изменения PATH применяются только после перезапуска
2. **Проверьте работу OCR:**
   ```python
   import pytesseract
   from PIL import Image
   
   # Тестовое изображение
   image = Image.open("test.png")
   text = pytesseract.image_to_string(image, lang='rus+eng')
   print(text)
   ```

## Примечание

- **Poppler уже работает** (судя по выводу процесса, PDF успешно конвертируется в изображения)
- **Tesseract нужно установить** для выполнения OCR распознавания
- После установки Tesseract OCR будет работать автоматически

---

**Последнее обновление:** 2025-01-13

