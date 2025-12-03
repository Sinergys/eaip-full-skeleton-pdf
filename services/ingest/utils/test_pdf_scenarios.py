"""
Создание тестовых сценариев для проверки обработки PDF
"""

from typing import List, Dict, Any


def create_test_scenarios() -> List[Dict[str, Any]]:
    """
    Возвращает список тестовых сценариев для проверки обработки PDF
    """
    scenarios = [
        {
            "name": "Чисто текстовый PDF",
            "description": "PDF с текстовым слоем, должен парситься без OCR",
            "expected_behavior": {
                "is_scanned": False,
                "ocr_attempted": False,
                "avg_chars_per_page": "> 50",
                "processing_method": "text_extraction",
            },
            "how_to_create": "Создать PDF из Word/текстового редактора или экспортировать из любого приложения",
        },
        {
            "name": "Отсканированный PDF",
            "description": "PDF со сканами страниц, должен запускать OCR",
            "expected_behavior": {
                "is_scanned": True,
                "ocr_attempted": True,
                "avg_chars_per_page": "< 50",
                "processing_method": "OCR",
            },
            "how_to_create": "Отсканировать документ и сохранить как PDF, или использовать pdf2image для создания",
        },
        {
            "name": "Гибридный PDF",
            "description": "PDF содержит и текст, и изображения",
            "expected_behavior": {
                "is_scanned": False,  # Если текста достаточно
                "ocr_attempted": False,
                "avg_chars_per_page": "> 50",
                "processing_method": "text_extraction (с возможным дополнением OCR для изображений)",
            },
            "how_to_create": "Создать PDF с текстом и вставленными изображениями",
        },
        {
            "name": "PDF с минимальным текстом",
            "description": "PDF с очень малым количеством текста (< 10 символов/страницу)",
            "expected_behavior": {
                "is_scanned": True,
                "ocr_attempted": True,
                "ocr_error": "poppler_not_installed (если poppler не установлен)",
                "avg_chars_per_page": "< 10",
            },
            "how_to_create": "PDF с только изображениями без текстового слоя",
        },
        {
            "name": "Поврежденный PDF",
            "description": "PDF с ошибками структуры",
            "expected_behavior": {
                "error_handling": "graceful",
                "fallback": "PyPDF2 если pdfplumber не работает",
            },
            "how_to_create": "Повредить структуру PDF файла",
        },
        {
            "name": "Многостраничный сканированный PDF",
            "description": "Большой PDF со многими отсканированными страницами",
            "expected_behavior": {
                "is_scanned": True,
                "ocr_attempted": True,
                "processing_time": "может быть длительным",
                "memory_usage": "контролируется",
            },
            "how_to_create": "Отсканировать многостраничный документ",
        },
    ]

    return scenarios


def print_test_scenarios():
    """
    Выводит список тестовых сценариев
    """
    scenarios = create_test_scenarios()

    print("=" * 80)
    print("ТЕСТОВЫЕ СЦЕНАРИИ ДЛЯ ПРОВЕРКИ ОБРАБОТКИ PDF")
    print("=" * 80)

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Описание: {scenario['description']}")
        print("   Ожидаемое поведение:")
        for key, value in scenario["expected_behavior"].items():
            print(f"     - {key}: {value}")
        print(f"   Как создать: {scenario['how_to_create']}")

    print("\n" + "=" * 80)
    print("ИНСТРУКЦИИ ПО ТЕСТИРОВАНИЮ")
    print("=" * 80)
    print("""
1. Создайте тестовые PDF файлы для каждого сценария
2. Загрузите их через веб-интерфейс или API
3. Проверьте логи обработки
4. Используйте pdf_diagnostics.py для детального анализа:
   python utils/pdf_diagnostics.py <путь_к_pdf>
5. Проверьте результаты в базе данных и на странице результатов
    """)


if __name__ == "__main__":
    print_test_scenarios()
