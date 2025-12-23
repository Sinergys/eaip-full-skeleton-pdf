import os
import json
import datetime
import mimetypes
from pathlib import Path

# --- КОНФИГУРАЦИЯ ---
PROJECT_ROOT = r"C:\eaip\eaip_full_skeleton"  # !!! Установите ваш корневой путь здесь !!!
OUTPUT_JSON_FILE = "documentation_metadata.json"
EXCLUDE_DIRS = ['venv', '__pycache__', '.git', '.vs', '.idea', 'node_modules', 'logs']

# Настройка цветов (ANSI-коды для терминала)
COLOR_CYAN = '\033[96m'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_RED = '\033[91m'
COLOR_MAGENTA = '\033[95m'
COLOR_WHITE = '\033[97m'
COLOR_GRAY = '\033[90m'
COLOR_END = '\033[0m'

# Ключевые слова для предварительной классификации
CLASSIFICATION_KEYWORDS = {
    'audit': ['audit', 'аудит', 'отчет', 'report', 'review', 'проверк'],
    'spec': ['spec', 'api', 'технич', 'specification', 'sp', 'тз'],
    'setup': ['setup', 'install', 'настройка', 'deploy', 'руководство', 'guide'],
    'historical': ['old', 'старый', '2023', 'archive', 'статус'],
    'config': ['config', 'конфиг', 'settings', 'env']
}

# --- ФУНКЦИИ ---

def format_size(size_bytes):
    """Преобразование байтов в читаемый формат (KB, MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def classify_by_name(filename):
    """Предварительная классификация документа по его имени."""
    filename_lower = filename.lower()
    found_categories = set()
    for category, keywords in CLASSIFICATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in filename_lower:
                found_categories.add(category)
    return list(found_categories) if found_categories else ['unknown']

def scan_project_metadata(root_path):
    """Сканирует проект и собирает метаданные документации."""
    print(f"\n{COLOR_CYAN}🎯 СТАРТ АУДИТА МЕТАДАННЫХ ДОКУМЕНТАЦИИ {COLOR_END}")
    print(f"========================================================{COLOR_END}")
    print(f"{COLOR_GREEN}📁 Проект: {root_path}{COLOR_END}")
    
    doc_manifest = []
    total_files = 0
    total_size = 0
    file_types = {}

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        # Исключаем нежелательные директории
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            total_files += 1
            file_path = Path(dirpath) / filename
            
            try:
                stat = file_path.stat()
                file_size = stat.st_size
                mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
                
                # Определение типа файла
                mime_type, _ = mimetypes.guess_type(file_path)
                ext = file_path.suffix.lower()
                
                # Фильтрация по документации (ключевые типы)
                if ext not in ['.md', '.txt', '.py', '.json', '.yaml', '.yml', '.docx', '.xlsx', '.pdf', '.doc']:
                    continue # Пропускаем не-документацию
                
                if ext not in file_types:
                    file_types[ext] = 0
                file_types[ext] += 1
                total_size += file_size
                
                relative_path = str(file_path.relative_to(root_path))
                
                # Сбор данных
                data = {
                    'path': relative_path,
                    'name': filename,
                    'ext': ext,
                    'size_bytes': file_size,
                    'size_human': format_size(file_size),
                    'last_modified': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'mod_timestamp': stat.st_mtime,
                    'pre_classification': classify_by_name(filename)
                }
                doc_manifest.append(data)
                
            except Exception as e:
                print(f"{COLOR_RED}❌ Ошибка доступа к файлу {filename}: {e}{COLOR_END}")
                
    return doc_manifest, total_files, total_size, file_types

# --- ОСНОВНОЙ КОД ---
if __name__ == "__main__":
    if not os.path.exists(PROJECT_ROOT):
        print(f"{COLOR_RED}❌ Ошибка: Указанный путь проекта не существует!{COLOR_END}")
        print(f"{COLOR_YELLOW}   Проверьте переменную PROJECT_ROOT в коде.{COLOR_END}")
    else:
        # 1. Сканирование
        manifest, total_scanned, total_size, file_types = scan_project_metadata(PROJECT_ROOT)
        
        # 2. Вывод статистики
        print(f"\n{COLOR_CYAN}2. 📊 СТАТИСТИКА СКАНИРОВАНИЯ {COLOR_END}")
        print(f"========================================={COLOR_END}")
        
        doc_count = len(manifest)
        print(f"{COLOR_WHITE}   📄 Документов найдено (ключевые типы):{COLOR_END} {COLOR_GREEN}{doc_count}{COLOR_END} из {total_scanned} файлов")
        print(f"{COLOR_WHITE}   📏 Общий объем документации:{COLOR_END} {COLOR_GREEN}{format_size(total_size)}{COLOR_END}")
        
        print(f"{COLOR_WHITE}   Типы файлов:{COLOR_END}")
        for ext, count in sorted(file_types.items(), key=lambda item: item[1], reverse=True):
            print(f"      • {ext}: {count} шт.")
            
        # 3. Примеры найденных файлов
        print(f"\n{COLOR_CYAN}3. 🔎 5 САМЫХ СТАРЫХ ФАЙЛОВ (ПОСЛЕДНЕЕ ИЗМЕНЕНИЕ) {COLOR_END}")
        print(f"======================================================{COLOR_END}")
        oldest_files = sorted(manifest, key=lambda x: x['mod_timestamp'])[:5]
        for item in oldest_files:
            cats = ", ".join(item['pre_classification'])
            print(f"{COLOR_GRAY}   {item['last_modified']} ({item['size_human']}) {COLOR_END} | {COLOR_WHITE}{item['path']} {COLOR_END}({COLOR_MAGENTA}{cats}{COLOR_END})")

        
        print(f"\n{COLOR_CYAN}4. 💾 ПОДГОТОВКА ДЛЯ ФАЗЫ 2 (AI-АНАЛИЗ) {COLOR_END}")
        print(f"======================================================{COLOR_END}")
        
        # 4. Сохранение JSON для следующей фазы
        with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=4)
            
        print(f"{COLOR_GREEN}✅ Успех: Метаданные ({doc_count} документов) сохранены в файл:{COLOR_END} {COLOR_WHITE}{OUTPUT_JSON_FILE}{COLOR_END}")
        
        print(f"\n{COLOR_YELLOW}💡 СЛЕДУЮЩИЙ ШАГ: Выполнить Фазу 2. Необходимо доработать скрипт для извлечения содержимого и отправки его в DeepSeek.{COLOR_END}")