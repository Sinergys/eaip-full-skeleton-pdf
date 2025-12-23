"""
Скрипт для копирования шаблона energy_passport_template.xlsx в template_metin.xlsx
"""
from pathlib import Path
import shutil

def copy_template():
    """Копирует energy_passport_template.xlsx в template_metin.xlsx"""
    templates_dir = Path(__file__).parent.parent / "templates" / "pcm690"
    source = templates_dir / "energy_passport_template.xlsx"
    destination = templates_dir / "template_metin.xlsx"
    
    if not source.exists():
        print(f"❌ Исходный шаблон не найден: {source}")
        return False
    
    try:
        shutil.copy2(source, destination)
        print(f"✅ Шаблон скопирован: {source} -> {destination}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при копировании: {e}")
        return False

if __name__ == "__main__":
    copy_template()

