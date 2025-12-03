"""
Простой тест подключения к DeepSeek API через httpx
"""
import httpx

DEEPSEEK_API_KEY = "sk-fa4d5adfd79d4307809a34b153fc0ab7"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

def test_deepseek_direct():
    """Прямой тест через httpx"""
    print("=" * 60)
    print("🧪 ПРЯМОЙ ТЕСТ DEEPSEEK API")
    print("=" * 60)
    print()
    
    print(f"📡 Подключение к: {DEEPSEEK_BASE_URL}")
    print(f"🔑 API Key: {DEEPSEEK_API_KEY[:10]}...{DEEPSEEK_API_KEY[-4:]}")
    print()
    
    # Тестовый запрос
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "Привет! Ответь одним словом: работает?"
            }
        ],
        "max_tokens": 50
    }
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Отправляю запрос...")
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers=headers,
                json=payload
            )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            print("=" * 60)
            print("✅ ПОДКЛЮЧЕНИЕ РАБОТАЕТ!")
            print("=" * 60)
            print()
            print(f"📝 Ответ DeepSeek: {answer}")
            print()
            print("📋 Детали ответа:")
            print(f"   Модель: {data.get('model', 'N/A')}")
            print(f"   Использовано токенов: {data.get('usage', {}).get('total_tokens', 'N/A')}")
            print()
            print("💡 API ключ валидный и работает!")
            print()
            print("📝 Для использования в проекте добавьте в .env:")
            print(f"   DEEPSEEK_API_KEY={DEEPSEEK_API_KEY}")
            print("   AI_PROVIDER=deepseek")
            print("   AI_ENABLED=true")
            print()
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"   Ответ: {response.text[:500]}")
            return False
            
    except httpx.ConnectError as e:
        print(f"❌ Ошибка подключения: {e}")
        print("   Проверьте интернет-соединение")
        return False
    except httpx.TimeoutException:
        print("❌ Таймаут запроса")
        print("   Сервер не отвечает")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_deepseek_direct()

