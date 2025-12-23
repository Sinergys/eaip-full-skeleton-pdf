"""
Скрипт для тестирования OCR: загрузка PDF через API и получение результатов
"""
import requests
import json
import time
import os
from pathlib import Path

# Конфигурация
API_BASE = "http://localhost:8001"
TEST_FILES = [
    {
        "name": "CamScanner 17-04-2025 15.17.pdf",
        "path": r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf"
    },
    {
        "name": "Navoiy IES 06. 2023.PDF",
        "path": r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\Акт баланс 2023\акт реализация НЭС 2023\Navoiy IES 06. 2023.PDF"
    }
]

def check_service():
    """Проверка доступности сервиса"""
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        if resp.status_code == 200:
            print(f"✅ Сервис доступен: {resp.json()}")
            return True
    except Exception as e:
        print(f"❌ Сервис не доступен: {e}")
        print(f"   URL: {API_BASE}/health")
        return False

def upload_file(file_path, file_name, enterprise_name="Навои ИЭС Тест"):
    """Загрузка файла через API"""
    url = f"{API_BASE}/web/upload"
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return None
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f, 'application/pdf')}
            data = {'enterprise_name': enterprise_name}
            
            print(f"📤 Загрузка файла: {file_name}")
            start_time = time.time()
            
            resp = requests.post(url, files=files, data=data, timeout=600)
            
            upload_time = time.time() - start_time
            
            if resp.status_code == 200:
                result = resp.json()
                batch_id = result.get('batch_id')
                print(f"✅ Файл загружен: batch_id={batch_id}, время={upload_time:.1f}с")
                return {
                    'batch_id': batch_id,
                    'upload_time': upload_time,
                    'response': result
                }
            else:
                print(f"❌ Ошибка загрузки: {resp.status_code}")
                print(f"   Ответ: {resp.text[:500]}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        return None

def get_upload_status(batch_id):
    """Получение статуса загрузки"""
    url = f"{API_BASE}/api/uploads/{batch_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"❌ Ошибка получения статуса: {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка запроса статуса: {e}")
        return None

def get_parsing_results(batch_id):
    """Получение результатов парсинга"""
    url = f"{API_BASE}/ingest/parse/{batch_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"❌ Ошибка получения результатов: {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка запроса результатов: {e}")
        return None

def get_progress(batch_id):
    """Получение прогресса обработки"""
    url = f"{API_BASE}/api/progress/{batch_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            return None
    except Exception as e:
        return None

def main():
    print("=" * 60)
    print("БЛОК 2: OCR РАСПОЗНАВАНИЕ")
    print("=" * 60)
    
    # Проверка сервиса
    if not check_service():
        print("\n⚠️  Сервис ingest не запущен!")
        print("   Запустите сервис: cd eaip_full_skeleton/services/ingest && uvicorn main:app --port 8001")
        return
    
    results = []
    
    # Загрузка файлов
    for file_info in TEST_FILES:
        file_path = file_info['path']
        file_name = file_info['name']
        
        print(f"\n{'='*60}")
        print(f"Файл: {file_name}")
        print(f"{'='*60}")
        
        upload_result = upload_file(file_path, file_name)
        
        if not upload_result:
            continue
        
        batch_id = upload_result['batch_id']
        
        # Ждём обработки (проверяем прогресс)
        print(f"\n⏳ Ожидание обработки...")
        max_wait = 300  # 5 минут максимум
        wait_time = 0
        while wait_time < max_wait:
            progress = get_progress(batch_id)
            if progress:
                stage = progress.get('current_stage', 'unknown')
                status = progress.get('status', 'processing')
                print(f"   Прогресс: {stage}, статус: {status}")
                
                if status == 'completed':
                    break
                elif status == 'error':
                    print(f"   ❌ Ошибка обработки: {progress.get('error_message', 'неизвестная ошибка')}")
                    break
            time.sleep(5)
            wait_time += 5
        
        # Получение результатов
        print(f"\n📊 Получение результатов...")
        upload_status = get_upload_status(batch_id)
        parsing_results = get_parsing_results(batch_id)
        
        # Извлечение OCR данных
        ocr_data = {}
        if parsing_results:
            data = parsing_results.get('parsing', {}).get('data', {})
            ocr_data = {
                'ocr_used': data.get('ocr_used', False),
                'ocr_success': data.get('ocr_success', False),
                'total_characters': data.get('total_characters', 0),
                'total_tables': data.get('total_tables', 0),
                'pages': data.get('metadata', {}).get('num_pages', 0),
                'is_scanned': data.get('is_scanned', False),
            }
        
        results.append({
            'file_name': file_name,
            'batch_id': batch_id,
            'upload_time': upload_result['upload_time'],
            'upload_status': upload_status,
            'parsing_results': parsing_results,
            'ocr_data': ocr_data
        })
        
        # Вывод результатов
        print(f"\n📋 Результаты OCR для {file_name}:")
        print(f"   batch_id: {batch_id}")
        print(f"   OCR использован: {ocr_data.get('ocr_used', False)}")
        print(f"   OCR успешен: {ocr_data.get('ocr_success', False)}")
        print(f"   Распознано символов: {ocr_data.get('total_characters', 0)}")
        print(f"   Найдено таблиц: {ocr_data.get('total_tables', 0)}")
        print(f"   Страниц: {ocr_data.get('pages', 0)}")
        print(f"   Время загрузки: {upload_result['upload_time']:.1f}с")
    
    # Сохранение результатов в JSON
    output_file = "tools/ocr_test_results_block2.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Результаты сохранены: {output_file}")
    
    return results

if __name__ == "__main__":
    main()

