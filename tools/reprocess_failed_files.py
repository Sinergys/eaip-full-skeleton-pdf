"""Переобработка файлов, которые не загрузились из-за ошибки datetime serialization"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

from batch_upload_from_folder import batch_upload_from_folder

# Список файлов с ошибками
failed_files = [
    "Август 2023 Навоийазотдан ташкари.xlsx",
    "Апрел 2023 Навоийазотдан ташкари.xlsx",
    "Баланс кичкина 2022 Навоий.xlsx",
    "Баланс кичкина 2022.xlsx",
    "Декабр 2022 Навоийазотдан ташкари.xlsx",
    "Декабр 2023 Навоийазотдан ташкари.xlsx",
    "Июль 2023 Навоийазотдан ташкари.xlsx",
    "Июнь 2023 Навоийазотдан ташкари.xlsx",
    "Май 2023 Навоийазотдан ташкари.xlsx",
    "Март 2023 Навоийазотдан ташкари.xlsx",
    "Ноябр 2023 Навоийазотдан ташкари.xlsx",
    "Октябр 2022 Навоийазотдан ташкари.xlsx",
    "Октябр 2023 Навоийазотдан ташкари.xlsx",
    "Сентябр 2023 Навоийазотдан ташкари.xlsx",
    "Феврал 2023 Навоийазотдан ташкари.xlsx",
    "Январ 2022 Навоийазотдан ташкари.xlsx",
    "Январ 2023 Навоийазотдан ташкари.xlsx",
]

folder_path = r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX"
folder = Path(folder_path)

print("=" * 80)
print("🔄 ПЕРЕОБРАБОТКА ФАЙЛОВ С ОШИБКАМИ")
print("=" * 80)

# Находим файлы
files_to_process = []
for filename in failed_files:
    file_path = folder / filename
    if file_path.exists():
        files_to_process.append(file_path)
        print(f"✅ Найден: {filename}")
    else:
        print(f"❌ Не найден: {filename}")

print(f"\n📄 Найдено файлов для переобработки: {len(files_to_process)}")

if files_to_process:
    # Создаем временную папку с этими файлами
    import tempfile
    import shutil
    
    temp_dir = Path(tempfile.mkdtemp())
    print(f"\n📂 Временная папка: {temp_dir}")
    
    for file_path in files_to_process:
        shutil.copy2(file_path, temp_dir / file_path.name)
        print(f"   ✅ Скопирован: {file_path.name}")
    
    # Загружаем из временной папки
    print(f"\n🚀 Начинаем загрузку...")
    stats = batch_upload_from_folder(str(temp_dir), "Navoiy IES", "debug")
    
    # Удаляем временную папку
    shutil.rmtree(temp_dir)
    print(f"\n✅ Временная папка удалена")
    
    print(f"\n📊 Результат:")
    print(f"   Успешно: {stats['success']}")
    print(f"   Ошибок: {stats['error']}")
else:
    print("\n❌ Файлы для переобработки не найдены")

