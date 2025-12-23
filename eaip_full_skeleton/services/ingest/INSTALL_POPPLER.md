# Установка Poppler для OCR PDF

## Проблема
При обработке сканированных PDF файлов возникает ошибка:
```
Unable to get page count. Is poppler installed and in PATH?
```

Это означает, что `poppler` не установлен или не найден в системном PATH.

## Решение для Windows

### Вариант 1: Установка через Chocolatey (рекомендуется)
```powershell
choco install poppler
```

### Вариант 2: Ручная установка
1. Скачайте poppler для Windows:
   - https://github.com/oschwartz10612/poppler-windows/releases/
   - Или: https://blog.alivate.com.au/poppler-windows/

2. Распакуйте архив (например, в `C:\poppler`)

3. Добавьте папку `bin` в системный PATH:
   - Откройте "Переменные среды" (Environment Variables)
   - Добавьте путь к `bin` (например, `C:\poppler\Library\bin`) в переменную `Path`
   - Перезапустите терминал/IDE

4. Проверьте установку:
   ```powershell
   pdftoppm -h
   ```

### Вариант 3: Установка через Conda
```bash
conda install -c conda-forge poppler
```

### Вариант 4: Указание пути в коде (временное решение)
Если не хотите добавлять в PATH, можно указать путь напрямую в коде:
```python
from pdf2image import convert_from_path

# Укажите путь к poppler
images = convert_from_path(
    pdf_path, 
    dpi=300,
    poppler_path=r"C:\poppler\Library\bin"  # Ваш путь
)
```

## Решение для Linux
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

## Решение для macOS
```bash
brew install poppler
```

## Проверка установки
После установки перезапустите сервер и попробуйте загрузить сканированный PDF снова.

## Примечание
- Poppler нужен только для OCR сканированных PDF
- Обычные PDF (с текстовым слоем) обрабатываются без poppler
- Если poppler не установлен, система продолжит работу, но OCR для PDF будет недоступен

