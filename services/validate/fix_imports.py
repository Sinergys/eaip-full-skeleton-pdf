"""
Fix imports script - заменяет относительные импорты на абсолютные.
"""
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path):
    """Исправить импорты в файле."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Замены
    replacements = {
        'from ..core.': 'from core.',
        'from ..utils.': 'from utils.',
        'from ..services.': 'from services.',
        'from ..db.': 'from db.',
    }
    
    original = content
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {file_path.name}")
        return True
    else:
        print(f"⏭️ Skipped: {file_path.name}")
        return False

if __name__ == "__main__":
    base_dir = Path(__file__).parent
    
    # Файлы для исправления
    files_to_fix = [
        base_dir / "services" / "orchestrator.py",
        base_dir / "services" / "docx_processor.py",
        base_dir / "services" / "ai_processor.py",
        base_dir / "services" / "document_assembler.py",
    ]
    
    print("🔧 Fixing imports...")
    fixed_count = 0
    
    for file_path in files_to_fix:
        if file_path.exists():
            if fix_imports_in_file(file_path):
                fixed_count += 1
        else:
            print(f"❌ Not found: {file_path}")
    
    print(f"\n✅ Fixed {fixed_count} files")
    print("🚀 Try running: python main.py")
