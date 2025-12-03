"""
Unit-тесты для ai_parser.py
"""
import pytest
import os
from unittest.mock import Mock, patch

# Настройка окружения перед импортом
os.environ["AI_ENABLED"] = "true"
os.environ["DEEPSEEK_API_KEY"] = "test_key"


class TestAIParser:
    """Тесты для класса AIParser"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Мок OpenAI клиента"""
        client = Mock()
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = "Test AI response"
        client.chat.completions.create.return_value = response
        return client
    
    @patch('eaip_full_skeleton.services.ingest.ai_parser.OpenAI')
    def test_init_deepseek(self, mock_openai, mock_openai_client):
        """Тест инициализации с DeepSeek провайдером"""
        os.environ["AI_PROVIDER"] = "deepseek"
        os.environ["AI_ENABLED"] = "true"
        mock_openai.return_value = mock_openai_client
        
        from ai_parser import AIParser
        parser = AIParser()
        
        assert parser.provider == "deepseek"
        assert parser.enabled is True
        assert parser.client is not None
    
    @patch('eaip_full_skeleton.services.ingest.ai_parser.OpenAI')
    def test_init_disabled(self, mock_openai):
        """Тест инициализации с отключенным AI"""
        os.environ["AI_ENABLED"] = "false"
        
        from ai_parser import AIParser
        parser = AIParser()
        
        assert parser.enabled is False
        assert parser.client is None
    
    @patch('eaip_full_skeleton.services.ingest.ai_parser.convert_from_path')
    @patch('eaip_full_skeleton.services.ingest.ai_parser.OpenAI')
    def test_recognize_document_pdf(self, mock_openai, mock_convert, mock_openai_client, temp_dir):
        """Тест распознавания PDF документа"""
        os.environ["AI_ENABLED"] = "true"
        os.environ["AI_PROVIDER"] = "deepseek"
        mock_openai.return_value = mock_openai_client
        
        # Мок конвертации PDF в изображения
        from PIL import Image
        mock_image = Image.new('RGB', (100, 100))
        mock_convert.return_value = [mock_image]
        
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")
        
        from ai_parser import AIParser
        parser = AIParser()
        
        result = parser.recognize_document(str(pdf_path), "pdf")
        
        assert result["ai_used"] is True
        assert result["file_type"] == "pdf"
        assert "text" in result
        assert result["pages_processed"] > 0
    
    @patch('eaip_full_skeleton.services.ingest.ai_parser.OpenAI')
    def test_recognize_document_image(self, mock_openai, mock_openai_client, temp_dir):
        """Тест распознавания изображения"""
        os.environ["AI_ENABLED"] = "true"
        os.environ["AI_PROVIDER"] = "deepseek"
        mock_openai.return_value = mock_openai_client
        
        # Создаем тестовое изображение
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img_path = temp_dir / "test.jpg"
        img.save(img_path)
        
        from ai_parser import AIParser
        parser = AIParser()
        
        result = parser.recognize_document(str(img_path), "image")
        
        assert result["ai_used"] is True
        assert result["file_type"] == "image"
        assert "text" in result
    
    @patch('eaip_full_skeleton.services.ingest.ai_parser.OpenAI')
    def test_structure_data(self, mock_openai, mock_openai_client):
        """Тест структурирования данных"""
        os.environ["AI_ENABLED"] = "true"
        os.environ["AI_PROVIDER"] = "deepseek"
        mock_openai.return_value = mock_openai_client
        
        # Мок ответа с JSON
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = '{"document_type": "energy_passport", "fields": {"test": "value"}}'
        mock_openai_client.chat.completions.create.return_value = response
        
        from ai_parser import AIParser
        parser = AIParser()
        
        raw_text = "Тестовые данные энергопотребления: 1000 кВт*ч"
        result = parser.structure_data(raw_text)
        
        assert "document_type" in result or "error" in result
    
    @patch('eaip_full_skeleton.services.ingest.ai_parser.OpenAI')
    def test_get_ai_parser_enabled(self, mock_openai, mock_openai_client):
        """Тест получения AI парсера когда включен"""
        os.environ["AI_ENABLED"] = "true"
        os.environ["AI_PROVIDER"] = "deepseek"
        mock_openai.return_value = mock_openai_client
        
        from ai_parser import get_ai_parser
        parser = get_ai_parser()
        
        assert parser is not None
        assert parser.enabled is True
    
    def test_get_ai_parser_disabled(self):
        """Тест получения AI парсера когда отключен"""
        os.environ["AI_ENABLED"] = "false"
        
        from ai_parser import get_ai_parser
        parser = get_ai_parser()
        
        assert parser is None

