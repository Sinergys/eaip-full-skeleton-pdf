"""
Unit-тесты для ai_ocr_enhancer.py
"""
import pytest
from unittest.mock import Mock, patch
from PIL import Image


class TestOCRAIEnhancer:
    """Тесты для класса OCRAIEnhancer"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера"""
        parser = Mock()
        parser.enabled = True
        return parser
    
    @pytest.fixture
    def sample_image(self):
        """Тестовое изображение"""
        return Image.new('RGB', (200, 200), color='white')
    
    @patch('ai_ocr_enhancer.get_ai_parser')
    def test_enhance_ocr_text(self, mock_get_parser, mock_ai_parser):
        """Тест улучшения OCR текста"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_ocr_enhancer import OCRAIEnhancer
        enhancer = OCRAIEnhancer()
        
        ocr_text = "Элсктроэнергия: 1000 кВт*ч"  # Опечатка
        result = enhancer.enhance_ocr_text(ocr_text)
        
        assert "enhanced_text" in result
        assert result["ai_used"] is True
    
    @patch('ai_ocr_enhancer.get_ai_parser')
    def test_correct_ocr_errors(self, mock_get_parser, mock_ai_parser):
        """Тест исправления ошибок OCR"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_ocr_enhancer import OCRAIEnhancer
        enhancer = OCRAIEnhancer()
        
        ocr_text = "Элсктроэнергия: 1000 кВт*ч"
        result = enhancer.correct_ocr_errors(ocr_text)
        
        assert "corrected_text" in result
        assert "corrections" in result

