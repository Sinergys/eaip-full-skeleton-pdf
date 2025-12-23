"""
Unit-тесты для ai_base_client.py
"""
import pytest


class TestBaseAIClient:
    """Тесты для базового класса BaseAIClient"""
    
    def test_base_class_is_abstract(self):
        """Тест что BaseAIClient является абстрактным классом"""
        from ai_base_client import BaseAIClient
        
        # Нельзя создать экземпляр абстрактного класса
        with pytest.raises(TypeError):
            BaseAIClient("test")
    
    def test_get_provider_name(self):
        """Тест получения имени провайдера"""
        from ai_base_client import BaseAIClient
        
        # Создаем конкретную реализацию для теста
        class TestClient(BaseAIClient):
            def process_prompt(self, prompt, **kwargs):
                return {"text": "test"}
            
            def process_vision_prompt(self, images, prompt, **kwargs):
                return {"text": "test"}
            
            def get_usage_metrics(self):
                return {}
            
            def is_available(self):
                return True
        
        client = TestClient("test_provider")
        assert client.get_provider_name() == "test_provider"

