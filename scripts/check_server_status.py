#!/usr/bin/env python3
"""Проверка статуса сервера ingest."""
import requests
import sys

BASE_URL = "http://localhost:8001"

def check_endpoint(path, method="GET", description=""):
    """Проверяет доступность эндпоинта."""
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, timeout=5)
        
        status = "✅" if response.status_code < 400 else "⚠️"
        print(f"{status} {method:4} {path:40} - Status: {response.status_code}")
        if description:
            print(f"   {description}")
        return response.status_code < 400
    except requests.exceptions.ConnectionError:
        print(f"❌ {method:4} {path:40} - Connection Error (сервер не запущен?)")
        return False
    except Exception as e:
        print(f"❌ {method:4} {path:40} - Error: {e}")
        return False

def main():
    """Проверяет основные эндпоинты сервера."""
    print("=" * 70)
    print("Проверка статуса сервера ingest")
    print("=" * 70)
    print()
    
    results = []
    
    # Основные эндпоинты
    print("📋 Основные эндпоинты:")
    results.append(check_endpoint("/health", description="Проверка здоровья сервера"))
    results.append(check_endpoint("/docs", description="Swagger документация"))
    print()
    
    # Веб-интерфейсы
    print("🌐 Веб-интерфейсы:")
    results.append(check_endpoint("/web/upload", description="Страница загрузки файлов"))
    results.append(check_endpoint("/web/results", description="Страница результатов"))
    results.append(check_endpoint("/web/normative", description="Страница нормативов"))
    print()
    
    # API эндпоинты
    print("🔌 API эндпоинты:")
    results.append(check_endpoint("/api/enterprises", description="Список предприятий"))
    results.append(check_endpoint("/api/debug/extensions", description="Доступные расширения"))
    results.append(check_endpoint("/test-xlsm", description="Тест поддержки .xlsm"))
    print()
    
    # Итоговая статистика
    print("=" * 70)
    success_count = sum(1 for r in results if r)
    total_count = len(results)
    print(f"Результат: {success_count}/{total_count} эндпоинтов доступны")
    
    if success_count == total_count:
        print("✅ Сервер работает отлично!")
        print(f"\n📝 Доступные интерфейсы:")
        print(f"   - API документация: {BASE_URL}/docs")
        print(f"   - Веб-загрузка: {BASE_URL}/web/upload")
        print(f"   - Health check: {BASE_URL}/health")
    elif success_count > 0:
        print("⚠️ Сервер работает, но некоторые эндпоинты недоступны")
    else:
        print("❌ Сервер не отвечает или не запущен")
        sys.exit(1)

if __name__ == "__main__":
    main()

