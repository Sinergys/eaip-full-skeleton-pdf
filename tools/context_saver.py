"""Утилита для безопасного сохранения контекстных файлов с проверкой размера"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Добавляем путь к tools для импорта
PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.file_size_manager import check_file_size, optimize_file_if_needed

DOCS_DIR = PROJECT_ROOT / "docs"


def save_context_safe(file_path: Path, data: Dict[str, Any], check_size: bool = True) -> bool:
    """
    Безопасно сохраняет контекстный файл с проверкой размера.
    
    Args:
        file_path: Путь к файлу для сохранения
        data: Данные для сохранения
        check_size: Проверять ли размер перед записью
    
    Returns:
        True если сохранение успешно, False в противном случае
    """
    try:
        # Проверяем размер перед записью
        if check_size:
            file_info = check_file_size(file_path)
            if file_info["exceeds_limit"]:
                # Оптимизируем файл перед записью
                archive_path = optimize_file_if_needed(file_path, force=False)
                if archive_path:
                    print(f"⚠️ Файл {file_path.name} превышал лимит, старые данные архивированы: {archive_path}")
        
        # Сохраняем файл
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            # Для других типов файлов просто записываем как текст
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        # Проверяем размер после записи
        if check_size:
            file_info = check_file_size(file_path)
            if file_info["exceeds_limit"]:
                print(f"⚠️ ВНИМАНИЕ: Файл {file_path.name} всё ещё превышает лимит после сохранения!")
                print(f"   Размер: {file_info['size_kb']} КБ / {file_info['limit_kb']} КБ")
                return False
        
        return True
    
    except Exception as e:
        print(f"❌ Ошибка при сохранении {file_path}: {e}")
        return False


def save_context_json(file_path: Path, data: Dict[str, Any]) -> bool:
    """Сохраняет JSON файл с автоматической проверкой размера"""
    return save_context_safe(file_path, data, check_size=True)


def save_context_with_warning(file_path: Path, data: Dict[str, Any], warn_threshold: float = 0.8) -> bool:
    """
    Сохраняет контекстный файл с предупреждением при приближении к лимиту.
    
    Args:
        file_path: Путь к файлу
        data: Данные для сохранения
        warn_threshold: Порог предупреждения (0.8 = 80% от лимита)
    
    Returns:
        True если сохранение успешно
    """
    # Проверяем размер перед записью
    file_info = check_file_size(file_path)
    
    if file_info["exists"] and file_info["percentage_used"] > warn_threshold * 100:
        print(f"⚠️ ВНИМАНИЕ: Файл {file_path.name} близок к лимиту!")
        print(f"   Использовано: {file_info['percentage_used']:.1f}% ({file_info['size_kb']} КБ / {file_info['limit_kb']} КБ)")
        print(f"   Рекомендуется оптимизация.")
    
    return save_context_safe(file_path, data, check_size=True)


if __name__ == "__main__":
    # Пример использования
    test_data = {
        "test": "data",
        "timestamp": datetime.now().isoformat()
    }
    
    test_file = DOCS_DIR / "test_context.json"
    result = save_context_json(test_file, test_data)
    
    if result:
        print(f"✅ Файл сохранён: {test_file}")
        # Удаляем тестовый файл
        test_file.unlink()
        print("✅ Тестовый файл удалён")
    else:
        print("❌ Ошибка при сохранении")

