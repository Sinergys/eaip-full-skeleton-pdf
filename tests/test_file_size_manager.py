"""Тесты для file_size_manager.py"""
import json
import tempfile
from pathlib import Path
from tools.file_size_manager import (
    check_file_size,
    get_file_size_limit,
    archive_old_data,
    optimize_jsonl_file,
    check_all_context_files
)


def test_get_file_size_limit():
    """Тест определения лимита размера файла"""
    # JSON файл
    json_file = Path("test.json")
    assert get_file_size_limit(json_file) == 1 * 1024 * 1024  # 1 МБ
    
    # Markdown файл
    md_file = Path("test.md")
    assert get_file_size_limit(md_file) == 500 * 1024  # 500 КБ
    
    # JSONL файл
    jsonl_file = Path("test.jsonl")
    assert get_file_size_limit(jsonl_file) == 10 * 1024 * 1024  # 10 МБ
    
    # Неизвестный тип
    unknown_file = Path("test.txt")
    assert get_file_size_limit(unknown_file) == 1 * 1024 * 1024  # 1 МБ по умолчанию


def test_check_file_size():
    """Тест проверки размера файла"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"test": "data"}')
        temp_path = Path(f.name)
    
    try:
        result = check_file_size(temp_path)
        
        assert result["exists"] == True
        assert result["size_bytes"] > 0
        assert result["size_kb"] > 0
        assert result["limit_bytes"] == 1 * 1024 * 1024
        assert result["exceeds_limit"] == False
        assert result["percentage_used"] < 100
    finally:
        temp_path.unlink()


def test_check_file_size_nonexistent():
    """Тест проверки несуществующего файла"""
    nonexistent = Path("nonexistent_file.json")
    result = check_file_size(nonexistent)
    
    assert result["exists"] == False
    assert result["size_bytes"] == 0
    assert result["exceeds_limit"] == False


def test_archive_old_data():
    """Тест архивации старых данных"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Создаём файл с историей больше лимита
        data = {
            "tasks": {
                "TEST_1": {
                    "id": "TEST_1",
                    "history": [{"timestamp": f"2025-01-{i:02d}", "action": "test"} for i in range(1, 101)]
                }
            }
        }
        json.dump(data, f, ensure_ascii=False, indent=2)
        temp_path = Path(f.name)
    
    try:
        archive_path = archive_old_data(temp_path, max_history_entries=50)
        
        # Проверяем, что архив создан
        if archive_path:
            assert archive_path.exists()
            
            # Проверяем, что история сокращена
            with open(temp_path, 'r', encoding='utf-8') as f:
                updated_data = json.load(f)
                assert len(updated_data["tasks"]["TEST_1"]["history"]) == 50
    finally:
        if temp_path.exists():
            temp_path.unlink()
        # Удаляем архив если создан
        archive_dir = Path(__file__).parent.parent / "docs" / "archive"
        for archive_file in archive_dir.glob("test_archive_*.json"):
            archive_file.unlink()


def test_optimize_jsonl_file():
    """Тест оптимизации JSONL файла"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Создаём файл с большим количеством строк
        for i in range(1500):
            f.write(json.dumps({"line": i, "data": "test"}) + "\n")
        temp_path = Path(f.name)
    
    try:
        archive_path = optimize_jsonl_file(temp_path, max_lines=1000)
        
        # Проверяем, что архив создан
        if archive_path:
            assert archive_path.exists()
            
            # Проверяем, что файл сокращён
            with open(temp_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                assert len(lines) == 1000
    finally:
        if temp_path.exists():
            temp_path.unlink()
        # Удаляем архив если создан
        archive_dir = Path(__file__).parent.parent / "docs" / "archive"
        for archive_file in archive_dir.glob("test_archive_*.jsonl"):
            archive_file.unlink()


def test_check_all_context_files():
    """Тест проверки всех контекстных файлов"""
    results = check_all_context_files()
    
    assert "check_date" in results
    assert "files" in results
    assert "summary" in results
    assert results["summary"]["total_files"] > 0
    assert isinstance(results["summary"]["total_size_kb"], (int, float))


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

