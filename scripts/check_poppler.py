"""Проверка и настройка Poppler для OCR"""

import os
from pathlib import Path

def find_poppler_bin():
    """Поиск папки bin с исполняемыми файлами Poppler"""
    possible_paths = [
        r"C:\poppler\bin",
        r"C:\poppler\Library\bin",
        r"C:\poppler\poppler\bin",
        r"C:\Program Files\poppler\bin",
        r"C:\Program Files (x86)\poppler\bin",
    ]
    
    print("=" * 80)
    print("ПОИСК POPPLER")
    print("=" * 80)
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Найдена папка: {path}")
            # Проверяем наличие pdftoppm.exe
            pdftoppm = os.path.join(path, "pdftoppm.exe")
            if os.path.exists(pdftoppm):
                print("   ✅ pdftoppm.exe найден")
                return path
            else:
                print("   ⚠ pdftoppm.exe не найден")
                # Показываем что есть в папке
                exes = [f for f in os.listdir(path) if f.endswith('.exe')]
                if exes:
                    print(f"   Найдены EXE: {exes[:5]}")
        else:
            print(f"❌ Не найдена: {path}")
    
    # Рекурсивный поиск
    print("\n🔍 Рекурсивный поиск pdftoppm.exe в C:\\poppler...")
    poppler_root = Path(r"C:\poppler")
    if poppler_root.exists():
        for exe_file in poppler_root.rglob("pdftoppm.exe"):
            print(f"✅ Найден: {exe_file}")
            return str(exe_file.parent)
    
    return None

def test_pdf2image(poppler_path=None):
    """Тестирование pdf2image с указанным путем"""
    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ PDF2IMAGE")
    print("=" * 80)
    
    try:
        from pdf2image import convert_from_path
        
        if poppler_path:
            print(f"Используется путь: {poppler_path}")
            # Устанавливаем путь для pdf2image
            os.environ['PATH'] = poppler_path + os.pathsep + os.environ.get('PATH', '')
        
        # Пробуем найти тестовый PDF
        test_pdf = Path(r"C:\eaip\eaip_full_skeleton\infra\data\inbox")
        pdf_files = list(test_pdf.glob("*.pdf")) if test_pdf.exists() else []
        
        if pdf_files:
            test_file = pdf_files[0]
            print(f"\nТестирование на файле: {test_file.name}")
            print("Конвертация PDF в изображение (первая страница)...")
            
            try:
                images = convert_from_path(str(test_file), first_page=1, last_page=1, dpi=150)
                print(f"✅ Успешно! Конвертировано {len(images)} изображений")
                print(f"   Размер изображения: {images[0].size}")
                return True
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                return False
        else:
            print("⚠ Тестовые PDF файлы не найдены")
            print("   Попробуем просто импортировать...")
            return True
            
    except ImportError as e:
        print(f"❌ pdf2image не установлен: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    # Поиск Poppler
    poppler_bin = find_poppler_bin()
    
    if poppler_bin:
        print(f"\n✅ Poppler найден в: {poppler_bin}")
        print("\n📝 Для использования добавьте в PATH:")
        print(f"   {poppler_bin}")
        print("\nИли используйте в коде:")
        print(f"   os.environ['PATH'] = r'{poppler_bin}' + os.pathsep + os.environ.get('PATH', '')")
    else:
        print("\n❌ Poppler не найден!")
        print("\nРекомендации:")
        print("1. Проверьте путь установки Poppler")
        print("2. Скачайте с: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("3. Распакуйте и убедитесь что есть папка bin с pdftoppm.exe")
        return
    
    # Тестирование
    test_pdf2image(poppler_bin)

if __name__ == "__main__":
    main()

