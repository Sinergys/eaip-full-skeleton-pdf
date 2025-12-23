"""Утилита для загрузки контекстных файлов агентов"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
DOCS_DIR = PROJECT_ROOT / "docs"

# Добавляем путь для импорта file_size_manager
sys.path.insert(0, str(PROJECT_ROOT))

# Обязательные файлы при старте
CRITICAL_FILES = {
    "context": DOCS_DIR / "AGENT_CONTEXT.json",
    "tasks": DOCS_DIR / "AGENT_TASKS_UNIFIED.json"
}

# Опциональные файлы (загружать по требованию)
OPTIONAL_FILES = {
    "task_status": DOCS_DIR / "AGENT_TASK_STATUS.json",
    "locks": DOCS_DIR / "AGENT_LOCKS.json",
    "session_state": DOCS_DIR / "AGENT_SESSION_STATE.json",
    "knowledge_base": DOCS_DIR / "AGENT_KNOWLEDGE_BASE.md",
    "critical_settings": DOCS_DIR / "PROJECT_CRITICAL_SETTINGS.md"
}


def load_critical_context(check_size: bool = True, auto_optimize: bool = True, warn_threshold: float = 0.8) -> Dict[str, Any]:
    """
    Загружает обязательные файлы контекста при старте работы агента.
    Автоматически проверяет размер файлов и оптимизирует при необходимости.
    
    Args:
        check_size: Проверять ли размер файлов перед загрузкой
        auto_optimize: Автоматически оптимизировать файлы, превышающие лимит
        warn_threshold: Порог предупреждения (0.8 = 80% от лимита)
    
    Returns:
        Словарь с загруженными данными:
        {
            "context": {...},  # AGENT_CONTEXT.json
            "tasks": {...}      # AGENT_TASKS_UNIFIED.json
        }
    
    Raises:
        FileNotFoundError: Если обязательный файл не найден
    """
    result = {}
    warnings = []
    
    # Импортируем функции проверки размера
    try:
        from tools.file_size_manager import check_file_size, optimize_file_if_needed
    except ImportError:
        # Если file_size_manager недоступен, продолжаем без проверки
        check_size = False
        auto_optimize = False
    
    # Загружаем AGENT_CONTEXT.json
    context_file = CRITICAL_FILES["context"]
    if not context_file.exists():
        raise FileNotFoundError(f"Критический файл не найден: {context_file}")
    
    # Проверяем размер перед загрузкой
    if check_size:
        file_info = check_file_size(context_file)
        
        # Предупреждение при приближении к лимиту
        if file_info["percentage_used"] > warn_threshold * 100:
            warnings.append(f"⚠️ {context_file.name}: {file_info['percentage_used']:.1f}% лимита ({file_info['size_kb']} КБ / {file_info['limit_kb']} КБ)")
        
        # Автоматическая оптимизация при превышении лимита
        if auto_optimize and file_info["exceeds_limit"]:
            archive_path = optimize_file_if_needed(context_file, force=False)
            if archive_path:
                warnings.append(f"✅ {context_file.name}: старые данные архивированы в {archive_path.name}")
                # Перепроверяем размер после оптимизации
                file_info = check_file_size(context_file)
    
    with open(context_file, 'r', encoding='utf-8') as f:
        result["context"] = json.load(f)
    
    # Загружаем AGENT_TASKS_UNIFIED.json
    tasks_file = CRITICAL_FILES["tasks"]
    if not tasks_file.exists():
        raise FileNotFoundError(f"Критический файл не найден: {tasks_file}")
    
    # Проверяем размер перед загрузкой
    if check_size:
        file_info = check_file_size(tasks_file)
        
        # Предупреждение при приближении к лимиту
        if file_info["percentage_used"] > warn_threshold * 100:
            warnings.append(f"⚠️ {tasks_file.name}: {file_info['percentage_used']:.1f}% лимита ({file_info['size_kb']} КБ / {file_info['limit_kb']} КБ)")
        
        # Автоматическая оптимизация при превышении лимита
        if auto_optimize and file_info["exceeds_limit"]:
            archive_path = optimize_file_if_needed(tasks_file, force=False)
            if archive_path:
                warnings.append(f"✅ {tasks_file.name}: старые данные архивированы в {archive_path.name}")
                # Перепроверяем размер после оптимизации
                file_info = check_file_size(tasks_file)
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        result["tasks"] = json.load(f)
    
    # Выводим предупреждения, если есть
    if warnings:
        print("\n" + "=" * 70)
        print("ПРОВЕРКА РАЗМЕРОВ ФАЙЛОВ ПРИ СТАРТЕ")
        print("=" * 70)
        for warning in warnings:
            print(warning)
        print("=" * 70 + "\n")
    
    return result


def load_optional_file(file_key: str, check_size: bool = True, warn_threshold: float = 0.8) -> Optional[Any]:
    """
    Загружает опциональный файл по требованию с проверкой размера.
    
    Args:
        file_key: Ключ файла из OPTIONAL_FILES:
            - "task_status" - AGENT_TASK_STATUS.json
            - "locks" - AGENT_LOCKS.json
            - "session_state" - AGENT_SESSION_STATE.json
            - "knowledge_base" - AGENT_KNOWLEDGE_BASE.md (текст)
            - "critical_settings" - PROJECT_CRITICAL_SETTINGS.md (текст)
        check_size: Проверять ли размер файла перед загрузкой
        warn_threshold: Порог предупреждения (0.8 = 80% от лимита)
    
    Returns:
        Содержимое файла (dict для JSON, str для MD) или None если файл не найден
    """
    if file_key not in OPTIONAL_FILES:
        raise ValueError(f"Неизвестный ключ файла: {file_key}. Доступные: {list(OPTIONAL_FILES.keys())}")
    
    file_path = OPTIONAL_FILES[file_key]
    
    if not file_path.exists():
        return None
    
    # Проверяем размер перед загрузкой
    if check_size:
        try:
            from tools.file_size_manager import check_file_size
            
            file_info = check_file_size(file_path)
            
            # Предупреждение при приближении к лимиту
            if file_info["percentage_used"] > warn_threshold * 100:
                print(f"⚠️ {file_path.name}: {file_info['percentage_used']:.1f}% лимита ({file_info['size_kb']} КБ / {file_info['limit_kb']} КБ)")
            
            # Предупреждение при превышении лимита
            if file_info["exceeds_limit"]:
                print(f"❌ {file_path.name}: ПРЕВЫШЕН ЛИМИТ! ({file_info['size_kb']} КБ / {file_info['limit_kb']} КБ)")
        except ImportError:
            # Если file_size_manager недоступен, продолжаем без проверки
            pass
    
    # JSON файлы
    if file_path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Markdown файлы
    elif file_path.suffix == '.md':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    else:
        raise ValueError(f"Неподдерживаемый тип файла: {file_path.suffix}")


def get_file_info(file_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Получает информацию о файле(ах).
    
    Args:
        file_key: Ключ файла (None для всех файлов)
    
    Returns:
        Информация о файле(ах): размер, путь, существует ли
    """
    if file_key:
        # Информация об одном файле
        if file_key in CRITICAL_FILES:
            file_path = CRITICAL_FILES[file_key]
        elif file_key in OPTIONAL_FILES:
            file_path = OPTIONAL_FILES[file_key]
        else:
            raise ValueError(f"Неизвестный ключ файла: {file_key}")
        
        return {
            "key": file_key,
            "path": str(file_path),
            "exists": file_path.exists(),
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
            "size_kb": round(file_path.stat().st_size / 1024, 2) if file_path.exists() else 0,
            "category": "critical" if file_key in CRITICAL_FILES else "optional"
        }
    else:
        # Информация обо всех файлах
        result = {
            "critical": {},
            "optional": {}
        }
        
        for key in CRITICAL_FILES:
            result["critical"][key] = get_file_info(key)
        
        for key in OPTIONAL_FILES:
            result["optional"][key] = get_file_info(key)
        
        return result


def get_startup_summary() -> Dict[str, Any]:
    """
    Получает сводку о файлах для старта работы.
    
    Returns:
        Сводка с размерами, количеством файлов и т.д.
    """
    critical_info = get_file_info()
    optional_info = get_file_info()
    
    critical_size = sum(f["size_bytes"] for f in critical_info["critical"].values())
    optional_size = sum(f["size_bytes"] for f in optional_info["optional"].values())
    
    return {
        "critical_files": {
            "count": len(critical_info["critical"]),
            "total_size_bytes": critical_size,
            "total_size_kb": round(critical_size / 1024, 2),
            "files": critical_info["critical"]
        },
        "optional_files": {
            "count": len(optional_info["optional"]),
            "total_size_bytes": optional_size,
            "total_size_kb": round(optional_size / 1024, 2),
            "files": optional_info["optional"]
        },
        "total": {
            "count": len(critical_info["critical"]) + len(optional_info["optional"]),
            "total_size_bytes": critical_size + optional_size,
            "total_size_kb": round((critical_size + optional_size) / 1024, 2)
        }
    }


if __name__ == "__main__":
    # Пример использования
    print("=" * 70)
    print("ЗАГРУЗКА ОБЯЗАТЕЛЬНЫХ ФАЙЛОВ")
    print("=" * 70)
    
    try:
        context_data = load_critical_context()
        print("✅ Контекст загружен успешно")
        print(f"   - AGENT_CONTEXT.json: {len(str(context_data['context']))} символов")
        print(f"   - AGENT_TASKS_UNIFIED.json: {len(context_data['tasks']['tasks'])} задач")
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 70)
    print("СВОДКА О ФАЙЛАХ")
    print("=" * 70)
    
    summary = get_startup_summary()
    print(f"\nОбязательные файлы: {summary['critical_files']['count']} файлов, {summary['critical_files']['total_size_kb']} КБ")
    print(f"Опциональные файлы: {summary['optional_files']['count']} файлов, {summary['optional_files']['total_size_kb']} КБ")
    print(f"Всего: {summary['total']['count']} файлов, {summary['total']['total_size_kb']} КБ")

