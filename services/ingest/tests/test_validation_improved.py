"""Тест улучшенной валидации файлов"""
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Добавляем путь к модулям
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

from main import validate_file
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_validation():
    """Тест валидации различных типов файлов"""
    print("=" * 70)
    print("ТЕСТ УЛУЧНЕННОЙ ВАЛИДАЦИИ ФАЙЛОВ")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Excel файл (.xlsx)",
            "filename": "test.xlsx",
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "expected": True
        },
        {
            "name": "Word файл (.docx) - стандартный MIME",
            "filename": "test.docx",
            "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "expected": True
        },
        {
            "name": "Word файл (.docx) - альтернативный MIME",
            "filename": "test.docx",
            "content_type": "application/octet-stream",
            "expected": True
        },
        {
            "name": "PDF файл",
            "filename": "test.pdf",
            "content_type": "application/pdf",
            "expected": True
        },
        {
            "name": "Неподдерживаемое расширение",
            "filename": "test.txt",
            "content_type": "text/plain",
            "expected": False
        },
        {
            "name": "Файл без расширения",
            "filename": "test",
            "content_type": None,
            "expected": False
        },
        {
            "name": "Файл без имени",
            "filename": None,
            "content_type": None,
            "expected": False
        }
    ]
    
    success_count = 0
    error_count = 0
    
    for test_case in test_cases:
        print(f"\n📄 Тест: {test_case['name']}")
        print(f"   Файл: {test_case['filename']}")
        print(f"   MIME: {test_case['content_type']}")
        
        # Создаем mock объект UploadFile
        mock_file = Mock()
        mock_file.filename = test_case['filename']
        mock_file.content_type = test_case['content_type']
        
        try:
            is_valid, error_msg = validate_file(mock_file)
            
            if is_valid == test_case['expected']:
                status = "✅ ПРОЙДЕН"
                if is_valid:
                    print(f"   {status}: Файл принят (ожидалось: принят)")
                else:
                    print(f"   {status}: Файл отклонен (ожидалось: отклонен)")
                    print(f"   Сообщение: {error_msg}")
                success_count += 1
            else:
                status = "❌ НЕ ПРОЙДЕН"
                expected_str = "принят" if test_case['expected'] else "отклонен"
                actual_str = "принят" if is_valid else "отклонен"
                print(f"   {status}: Ожидалось {expected_str}, получено {actual_str}")
                if error_msg:
                    print(f"   Сообщение: {error_msg}")
                error_count += 1
                
        except Exception as e:
            print(f"   ❌ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1
    
    print("\n" + "=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"   ✅ Успешно: {success_count}")
    print(f"   ❌ Ошибок: {error_count}")
    print("=" * 70)


if __name__ == "__main__":
    test_validation()

