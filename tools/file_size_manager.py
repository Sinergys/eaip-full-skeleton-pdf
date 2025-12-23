"""Утилита для управления размером файлов контекста"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
DOCS_DIR = PROJECT_ROOT / "docs"
ARCHIVE_DIR = DOCS_DIR / "archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# Лимиты размеров файлов (в байтах)
FILE_SIZE_LIMITS = {
    "json": 1 * 1024 * 1024,  # 1 МБ
    "md": 500 * 1024,  # 500 КБ
    "jsonl": 10 * 1024 * 1024,  # 10 МБ
    "default": 1 * 1024 * 1024  # 1 МБ по умолчанию
}


def get_file_size_limit(file_path: Path) -> int:
    """Определяет лимит размера для файла на основе его расширения"""
    ext = file_path.suffix.lower().lstrip('.')
    return FILE_SIZE_LIMITS.get(ext, FILE_SIZE_LIMITS["default"])


def check_file_size(file_path: Path) -> Dict[str, Any]:
    """
    Проверяет размер файла и возвращает информацию о нём.
    
    Returns:
        {
            "path": str,
            "exists": bool,
            "size_bytes": int,
            "size_kb": float,
            "limit_bytes": int,
            "limit_kb": float,
            "exceeds_limit": bool,
            "percentage_used": float
        }
    """
    result = {
        "path": str(file_path),
        "exists": file_path.exists(),
        "size_bytes": 0,
        "size_kb": 0.0,
        "limit_bytes": get_file_size_limit(file_path),
        "limit_kb": 0.0,
        "exceeds_limit": False,
        "percentage_used": 0.0
    }
    
    if file_path.exists():
        size = file_path.stat().st_size
        limit = result["limit_bytes"]
        
        result["size_bytes"] = size
        result["size_kb"] = round(size / 1024, 2)
        result["limit_kb"] = round(limit / 1024, 2)
        result["exceeds_limit"] = size > limit
        result["percentage_used"] = round((size / limit) * 100, 2) if limit > 0 else 0
    
    return result


def archive_old_data(file_path: Path, max_history_entries: int = 50) -> Optional[Path]:
    """
    Архивирует старые данные из JSON файла, оставляя только последние N записей.
    
    Args:
        file_path: Путь к JSON файлу
        max_history_entries: Максимальное количество записей истории для сохранения
    
    Returns:
        Путь к архивированному файлу или None
    """
    if not file_path.exists() or file_path.suffix.lower() != '.json':
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем, есть ли история для архивации
        archived = False
        archive_data = {}
        
        # Для файлов с историей (например, AGENT_TASKS_UNIFIED.json)
        if "tasks" in data:
            for task_id, task in data["tasks"].items():
                if "history" in task and len(task["history"]) > max_history_entries:
                    # Сохраняем старые записи в архив
                    old_history = task["history"][:-max_history_entries]
                    if task_id not in archive_data:
                        archive_data[task_id] = {"history": []}
                    archive_data[task_id]["history"] = old_history
                    
                    # Оставляем только последние записи
                    task["history"] = task["history"][-max_history_entries:]
                    archived = True
        
        # Для файлов с массивом истории
        if "history" in data and isinstance(data["history"], list):
            if len(data["history"]) > max_history_entries:
                archive_data["history"] = data["history"][:-max_history_entries]
                data["history"] = data["history"][-max_history_entries:]
                archived = True
        
        if archived:
            # Сохраняем архив
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = ARCHIVE_DIR / f"{file_path.stem}_archive_{timestamp}.json"
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, ensure_ascii=False, indent=2)
            
            # Сохраняем обновлённый файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return archive_path
        
        return None
    
    except Exception as e:
        print(f"Ошибка при архивации {file_path}: {e}")
        return None


def optimize_jsonl_file(file_path: Path, max_lines: int = 1000) -> Optional[Path]:
    """
    Оптимизирует JSONL файл, оставляя только последние N строк.
    
    Args:
        file_path: Путь к JSONL файлу
        max_lines: Максимальное количество строк для сохранения
    
    Returns:
        Путь к архивированному файлу или None
    """
    if not file_path.exists() or file_path.suffix.lower() != '.jsonl':
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) <= max_lines:
            return None  # Файл не превышает лимит
        
        # Сохраняем старые строки в архив
        old_lines = lines[:-max_lines]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = ARCHIVE_DIR / f"{file_path.stem}_archive_{timestamp}.jsonl"
        
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.writelines(old_lines)
        
        # Сохраняем только последние строки
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[-max_lines:])
        
        return archive_path
    
    except Exception as e:
        print(f"Ошибка при оптимизации JSONL {file_path}: {e}")
        return None


def check_all_context_files() -> Dict[str, Any]:
    """
    Проверяет размеры всех контекстных файлов.
    
    Returns:
        Словарь с результатами проверки
    """
    context_files = [
        DOCS_DIR / "AGENT_CONTEXT.json",
        DOCS_DIR / "AGENT_TASKS_UNIFIED.json",
        DOCS_DIR / "AGENT_SESSION_STATE.json",
        DOCS_DIR / "AGENT_TASK_STATUS.json",
        DOCS_DIR / "AGENT_LOCKS.json",
        DOCS_DIR / "AGENT_WORK_LOG.jsonl",
        DOCS_DIR / "AGENT_KNOWLEDGE_BASE.md",
        DOCS_DIR / "PROJECT_CRITICAL_SETTINGS.md"
    ]
    
    results = {
        "check_date": datetime.now().isoformat(),
        "files": [],
        "summary": {
            "total_files": 0,
            "files_exceeding_limit": 0,
            "total_size_bytes": 0,
            "total_size_kb": 0.0
        }
    }
    
    for file_path in context_files:
        file_info = check_file_size(file_path)
        results["files"].append(file_info)
        results["summary"]["total_files"] += 1
        results["summary"]["total_size_bytes"] += file_info["size_bytes"]
        
        if file_info["exceeds_limit"]:
            results["summary"]["files_exceeding_limit"] += 1
    
    results["summary"]["total_size_kb"] = round(results["summary"]["total_size_bytes"] / 1024, 2)
    
    return results


def optimize_file_if_needed(file_path: Path, force: bool = False) -> Optional[Path]:
    """
    Оптимизирует файл, если он превышает лимит размера.
    
    Args:
        file_path: Путь к файлу
        force: Принудительная оптимизация даже если не превышает лимит
    
    Returns:
        Путь к архивированному файлу или None
    """
    file_info = check_file_size(file_path)
    
    if not file_info["exists"]:
        return None
    
    # Проверяем, нужно ли оптимизировать
    if not force and not file_info["exceeds_limit"]:
        return None
    
    # Оптимизируем в зависимости от типа файла
    if file_path.suffix.lower() == '.json':
        return archive_old_data(file_path)
    elif file_path.suffix.lower() == '.jsonl':
        return optimize_jsonl_file(file_path)
    else:
        # Для других типов файлов просто предупреждаем
        print(f"⚠️ Файл {file_path.name} превышает лимит, но автоматическая оптимизация не поддерживается")
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("ПРОВЕРКА РАЗМЕРОВ КОНТЕКСТНЫХ ФАЙЛОВ")
    print("=" * 70)
    
    results = check_all_context_files()
    
    print(f"\nДата проверки: {results['check_date']}")
    print(f"Всего файлов: {results['summary']['total_files']}")
    print(f"Превышают лимит: {results['summary']['files_exceeding_limit']}")
    print(f"Общий размер: {results['summary']['total_size_kb']} КБ")
    
    print("\n" + "=" * 70)
    print("ДЕТАЛИ ПО ФАЙЛАМ:")
    print("=" * 70)
    
    for file_info in results["files"]:
        status = "❌ ПРЕВЫШАЕТ" if file_info["exceeds_limit"] else "✅ OK"
        print(f"\n{status} {Path(file_info['path']).name}")
        print(f"   Размер: {file_info['size_kb']} КБ / {file_info['limit_kb']} КБ ({file_info['percentage_used']}%)")
        print(f"   Путь: {file_info['path']}")
    
    # Проверяем, нужно ли оптимизировать
    if results["summary"]["files_exceeding_limit"] > 0:
        print("\n" + "=" * 70)
        print("⚠️ ОБНАРУЖЕНЫ ФАЙЛЫ, ПРЕВЫШАЮЩИЕ ЛИМИТ!")
        print("=" * 70)
        print("Рекомендуется выполнить оптимизацию.")
    else:
        print("\n" + "=" * 70)
        print("✅ ВСЕ ФАЙЛЫ В ПРЕДЕЛАХ ЛИМИТОВ")
        print("=" * 70)
    
    # Сохраняем результаты
    output_file = PROJECT_ROOT / "reports" / "file_size_check.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Результаты сохранены: {output_file}")

