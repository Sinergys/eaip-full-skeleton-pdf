"""
Unit-тесты для ai_client_factory.py
"""
from unittest.mock import Mock, patch


class TestAIClientFactory:
    """Тесты для класса AIClientFactory"""
    
    @patch('ai_client_factory.is_ai_enabled')
    def test_create_client_disabled(self, mock_enabled):
        """Тест создания клиента когда AI отключен"""
        mock_enabled.return_value = False
        
        from ai_client_factory import AIClientFactory
        factory = AIClientFactory()
        
        client = factory.create_client("openai")
        assert client is None
    
    @patch('ai_client_factory.is_ai_enabled')
    @patch('ai_client_factory.OpenAIClient')
    def test_create_openai_client(self, mock_client_class, mock_enabled):
        """Тест создания OpenAI клиента"""
        mock_enabled.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        from ai_client_factory import AIClientFactory
        factory = AIClientFactory()
        
        client = factory.create_client("openai")
        assert client is not None

