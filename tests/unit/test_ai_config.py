"""
Unit-тесты для ai_config.py
"""
import os
from unittest.mock import patch


class TestAIConfig:
    """Тесты для конфигурации AI"""
    
    def test_get_ai_config(self):
        """Тест получения конфигурации AI"""
        from ai_config import get_ai_config
        
        config = get_ai_config()
        
        assert "preferred_provider" in config
        assert "enabled" in config
        assert "api_providers" in config
    
    def test_get_preferred_provider(self):
        """Тест получения предпочтительного провайдера"""
        from ai_config import get_preferred_provider
        
        provider = get_preferred_provider()
        assert isinstance(provider, str)
    
    @patch.dict(os.environ, {"AI_ENABLED": "true"})
    def test_is_ai_enabled_true(self):
        """Тест проверки включенности AI"""
        
        # Перезагружаем модуль для применения новых переменных окружения
        import importlib
        import ai_config
        importlib.reload(ai_config)
        
        assert ai_config.is_ai_enabled() is True
    
    @patch.dict(os.environ, {"AI_ENABLED": "false"})
    def test_is_ai_enabled_false(self):
        """Тест проверки отключенности AI"""
        
        # Перезагружаем модуль
        import importlib
        import ai_config
        importlib.reload(ai_config)
        
        assert ai_config.is_ai_enabled() is False
    
    def test_get_api_provider_config(self):
        """Тест получения конфигурации провайдера"""
        from ai_config import get_api_provider_config
        
        config = get_api_provider_config("openai")
        assert config is not None
        assert "api_key" in config or config is None
        
        config = get_api_provider_config("nonexistent")
        assert config is None

