import json
import os
from docx import Document
import PyPDF2

# --- КОНФИГУРАЦИЯ ---
PROJECT_ROOT = r"C:\eaip\eaip_full_skeleton" # !!! Должен совпадать с Фазой 1 !!!
INPUT_JSON_FILE = "documentation_metadata.json"
OUTPUT_JSON_FILE = "deepseek_payload.json"
MAX_CONTENT_LENGTH = 3000  # Максимальное количество символов для извлечения (для экономии токенов)
CRITICAL_EXTENSIONS = ['.md', '.docx', '.pdf', '.txt', '.py']

# --- ФУНКЦИИ ИЗВЛЕЧЕНИЯ ---

def extract_from_markdown(file_path):
    """Извлекает текст из MD и TXT файлов."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"ERROR_READING_MD: {e}"

def extract_from_docx(file_path):
    """Извлекает текст из DOCX файлов."""
    try:
        document = Document(file_path)
        content = "\n".join([paragraph.text for paragraph in document.paragraphs])
        return content
    except Exception as e:
        return f"ERROR_READING_DOCX: {e}"

def extract_from_pdf(file_path):
    """Извлекает текст из PDF файлов (только текстовый слой)."""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"ERROR_READING_PDF: {e}"

def get_file_content(relative_path, ext):
    """Вызывает соответствующую функцию извлечения и обрезает контент."""
    full_path = os.path.join(PROJECT_ROOT, relative_path)
    content = ""
    
    if ext in ['.md', '.txt', '.json', '.yaml', '.yml', '.py']:
        content = extract_from_markdown(full_path)
    elif ext == '.docx':
        content = extract_from_docx(full_path)
    elif ext == '.pdf':
        content = extract_from_pdf(full_path)
    
    # Обрезка контента для экономии токенов
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "\n... [CONTENT_TRUNCATED] ..."
    
    # Удаляем лишние пробелы и табуляцию
    return ' '.join(content.split())

# --- ОСНОВНОЙ КОД ---

def run_phase2():
    try:
        with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
            metadata_manifest = json.load(f)
    except FileNotFoundError:
        print(f"❌ Ошибка: Файл {INPUT_JSON_FILE} не найден. Запустите сначала Фазу 1.")
        return

    print(f"\n🎯 СТАРТ ФАЗЫ 2: ИЗВЛЕЧЕНИЕ СОДЕРЖИМОГО")
    print("=======================================")
    
    deepseek_payload = []
    
    for item in metadata_manifest:
        ext = item['ext'].lower()
        if ext in CRITICAL_EXTENSIONS:
            content = get_file_content(item['path'], ext)
            
            # Добавляем извлеченное содержимое в объект
            payload_item = {
                'file_id': item['path'],
                'size_human': item['size_human'],
                'last_modified': item['last_modified'],
                'pre_classification': item['pre_classification'],
                'content_snippet': content
            }
            deepseek_payload.append(payload_item)
            
            print(f"✅ Извлечено: {item['path']} ({item['size_human']})")
        else:
            # Для некритичных файлов просто оставляем метаданные
            deepseek_payload.append({
                'file_id': item['path'],
                'size_human': item['size_human'],
                'last_modified': item['last_modified'],
                'pre_classification': item['pre_classification'],
                'content_snippet': f"Content skipped (Extension: {ext})"
            })
            
    # Сохранение финального JSON для DeepSeek
    with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(deepseek_payload, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Успех: Извлеченное содержимое для {len(deepseek_payload)} документов сохранено.")
    print(f"   Файл для анализа DeepSeek: {OUTPUT_JSON_FILE}")
    print("\n💡 СЛЕДУЮЩИЙ ШАГ: Сформировать промпт для DeepSeek (Фаза 3).")

if __name__ == "__main__":
    run_phase2()