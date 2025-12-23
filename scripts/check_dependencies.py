"""Проверка установленных зависимостей для парсинга"""

dependencies = {
    "camelot": "camelot-py",
    "tabula": "tabula-py",
    "pdfplumber": "pdfplumber",
    "pdf2image": "pdf2image",
    "pytesseract": "pytesseract",
    "cv2": "opencv-python-headless"
}

print("=" * 60)
print("ПРОВЕРКА ЗАВИСИМОСТЕЙ")
print("=" * 60)

installed = []
missing = []

for module, package in dependencies.items():
    try:
        __import__(module)
        installed.append(f"✅ {package}")
    except ImportError:
        missing.append(f"❌ {package}")

print("\nУстановлено:")
for item in installed:
    print(f"  {item}")

if missing:
    print("\nОтсутствует:")
    for item in missing:
        print(f"  {item}")
    print("\nДля установки выполните:")
    print(f"  pip install {' '.join([dependencies[m.split()[1]] for m in missing])}")
else:
    print("\n✅ Все зависимости установлены!")

