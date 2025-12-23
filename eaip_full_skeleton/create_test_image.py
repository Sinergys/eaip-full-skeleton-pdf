"""
Скрипт для создания тестового изображения с текстом для проверки OCR
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(output_path: str = "test_image.jpg"):
    """Создает тестовое изображение с русским и английским текстом"""
    
    # Создаем изображение
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Текст для тестирования OCR
    text_lines = [
        "ТЕСТОВЫЙ ДОКУМЕНТ ДЛЯ OCR",
        "",
        "Энергоаудит предприятия",
        "Год: 2024",
        "",
        "Потребление электроэнергии:",
        "  - Квартал 1: 15,000 кВт·ч",
        "  - Квартал 2: 18,500 кВт·ч",
        "  - Квартал 3: 20,000 кВт·ч",
        "  - Квартал 4: 16,800 кВт·ч",
        "",
        "Итого за год: 70,300 кВт·ч",
        "",
        "Test Document for OCR",
        "Energy Audit Report",
        "Total consumption: 70,300 kWh",
        "",
        "Дата составления: 15.11.2024",
        "Подпись: _______________"
    ]
    
    # Пробуем использовать системный шрифт
    try:
        # Windows
        font_path = "C:/Windows/Fonts/arial.ttf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 32)
        else:
            # Linux
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 32)
            else:
                # macOS
                font_path = "/System/Library/Fonts/Helvetica.ttc"
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 32)
                else:
                    # Fallback на стандартный шрифт
                    font = ImageFont.load_default()
    except Exception:
        # Если не удалось загрузить шрифт, используем стандартный
        font = ImageFont.load_default()
    
    # Рисуем текст
    y_position = 50
    line_height = 45
    
    for line in text_lines:
        if line:
            draw.text((50, y_position), line, fill='black', font=font)
        y_position += line_height
    
    # Сохраняем изображение
    img.save(output_path, quality=95)
    print(f"✅ Тестовое изображение создано: {output_path}")
    print(f"   Размер: {width}x{height} пикселей")
    print(f"   Размер файла: {os.path.getsize(output_path) / 1024:.2f} КБ")
    print("\n💡 Теперь можно протестировать OCR:")
    print(f"   python test_image_ocr.py {output_path}")


if __name__ == "__main__":
    create_test_image()

