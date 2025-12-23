"""
Полный словарь дополнительных MIME-типов для всех поддерживаемых расширений файлов.
Этот словарь содержит альтернативные MIME-типы, которые браузеры могут отправлять
вместо стандартных типов.
"""

# Полный словарь EXTRA_MIME_MAP для всех поддерживаемых расширений
EXTRA_MIME_MAP = {
    # Дополнительные MIME-типы для Word документов
    ".docx": [
        "application/msword",                    # Старые версии Word
        "application/octet-stream",              # Общий тип для неизвестных файлов
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # Стандартный XLSX
        "application/zip",                       # DOCX - это ZIP архив
    ],
    
    # Дополнительные MIME-типы для Excel файлов с макросами
    ".xlsm": [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Стандартный XLSX
        "application/vnd.ms-excel.sheet.macroEnabled.12",  # Официальный XLSM
        "application/octet-stream",              # Общий тип
        "application/zip",                       # XLSM - это ZIP архив
        "application/vnd.ms-excel.sheet.12",    # Альтернативный тип
    ],
    
    # Дополнительные MIME-типы для обычных Excel файлов
    ".xlsx": [
        "application/vnd.ms-excel",             # Старый формат Excel
        "application/octet-stream",             # Общий тип
        "application/zip",                      # XLSX - это ZIP архив
        "application/vnd.ms-excel.sheet.12",   # Альтернативный тип
    ],
    
    # Дополнительные MIME-типы для PDF файлов
    ".pdf": [
        "application/octet-stream",             # Общий тип
        "application/x-pdf",                    # Альтернативный тип
        "text/pdf",                            # Текстовый PDF
        "application/acrobat",                  # Старый Acrobat
    ],
    
    # Дополнительные MIME-типы для JPEG изображений
    ".jpg": [
        "image/jpeg",                          # Стандартный JPEG
        "image/pjpeg",                        # Прогрессивный JPEG
        "image/jpg",                          # Альтернативное расширение
        "application/octet-stream",           # Общий тип
    ],
    
    # Дополнительные MIME-типы для JPEG изображений
    ".jpeg": [
        "image/jpeg",                         # Стандартный JPEG
        "image/pjpeg",                       # Прогрессивный JPEG
        "image/jpg",                         # Альтернативное расширение
        "application/octet-stream",          # Общий тип
    ],
    
    # Дополнительные MIME-типы для PNG изображений
    ".png": [
        "image/png",                         # Стандартный PNG
        "image/x-png",                      # Альтернативный тип
        "application/octet-stream",         # Общий тип
        "image/png",                        # Дублирование для совместимости
    ],
}

# Пример использования в коде:
"""
# В начале функции validate_file() добавить:
EXTRA_MIME_MAP = {
    ".docx": [
        "application/msword",
        "application/octet-stream",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
    ],
    ".xlsm": [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel.sheet.macroEnabled.12",
        "application/octet-stream",
        "application/zip",
        "application/vnd.ms-excel.sheet.12",
    ],
    ".xlsx": [
        "application/vnd.ms-excel",
        "application/octet-stream",
        "application/zip",
        "application/vnd.ms-excel.sheet.12",
    ],
    ".pdf": [
        "application/octet-stream",
        "application/x-pdf",
        "text/pdf",
        "application/acrobat",
    ],
    ".jpg": [
        "image/jpeg",
        "image/pjpeg",
        "image/jpg",
        "application/octet-stream",
    ],
    ".jpeg": [
        "image/jpeg",
        "image/pjpeg",
        "image/jpg",
        "application/octet-stream",
    ],
    ".png": [
        "image/png",
        "image/x-png",
        "application/octet-stream",
        "image/png",
    ],
}
"""

print("✅ Словарь EXTRA_MIME_MAP готов!")
print(f"📊 Поддерживаемых расширений: {len(EXTRA_MIME_MAP)}")
for ext, types in EXTRA_MIME_MAP.items():
    print(f"   {ext}: {len(types)} MIME-типов")