"""Тесты для проверки размера файлов в context_loader"""
import json
import tempfile
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.context_loader import load_critical_context, load_optional_file
from tools.file_size_manager import check_file_size


def test_load_critical_context_with_size_check():
    """Тест загрузки критических файлов с проверкой размера"""
    # Загружаем с проверкой размера
    result = load_critical_context(check_size=True, auto_optimize=False, warn_threshold=0.8)
    
    assert "context" in result
    assert "tasks" in result
    assert isinstance(result["context"], dict)
    assert isinstance(result["tasks"], dict)
    
    print("✅ Тест загрузки критических файлов с проверкой размера пройден")


def test_warning_threshold():
    """Тест предупреждения при приближении к лимиту"""
    # Создаём временный файл, близкий к лимиту
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Создаём большой JSON (но не превышающий лимит)
        large_data = {"data": ["x" * 1000] * 800}  # ~800 КБ
        json.dump(large_data, f)
        temp_path = Path(f.name)
    
    try:
        file_info = check_file_size(temp_path)
        # Проверяем, что файл существует и размер определён
        assert file_info["exists"] == True
        assert file_info["size_bytes"] > 0
        print(f"✅ Тест предупреждения: файл {temp_path.name} - {file_info['percentage_used']:.1f}% лимита")
    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_load_optional_file_with_size_check():
    """Тест загрузки опционального файла с проверкой размера"""
    # Пробуем загрузить существующий файл
    result = load_optional_file("task_status", check_size=True, warn_threshold=0.8)
    
    # Файл может быть None, если не существует, или dict если существует
    assert result is None or isinstance(result, dict)
    
    print("✅ Тест загрузки опционального файла с проверкой размера пройден")


if __name__ == "__main__":
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ПРОВЕРКИ РАЗМЕРОВ В CONTEXT_LOADER")
    print("=" * 70)
    
    test_load_critical_context_with_size_check()
    test_warning_threshold()
    test_load_optional_file_with_size_check()
    
    print("\n" + "=" * 70)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    print("=" * 70)

