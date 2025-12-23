"""
Unit-тесты для ai_data_validator.py
"""
import pytest
from unittest.mock import Mock, patch


class TestAIDataValidator:
    """Тесты для класса AIDataValidator"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера"""
        parser = Mock()
        parser.enabled = True
        parser.structure_data.return_value = {
            "is_valid": True,
            "issues": [],
            "confidence": 0.9
        }
        return parser
    
    @patch('ai_data_validator.get_ai_parser')
    def test_init_with_ai(self, mock_get_parser, mock_ai_parser):
        """Тест инициализации с доступным AI"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_data_validator import AIDataValidator
        validator = AIDataValidator()
        
        assert validator.enabled is True
    
    @patch('ai_data_validator.get_ai_parser')
    def test_validate_extracted_data_valid(self, mock_get_parser, mock_ai_parser):
        """Тест валидации валидных данных"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_data_validator import AIDataValidator
        validator = AIDataValidator()
        
        extracted_data = "Электроэнергия: 1000 кВт*ч, Стоимость: 5000 руб"
        result = validator.validate_extracted_data(extracted_data, "energy_passport")
        
        assert result["is_valid"] is True
        assert result["ai_used"] is True
        assert "confidence" in result
    
    @patch('ai_data_validator.get_ai_parser')
    def test_validate_extracted_data_invalid(self, mock_get_parser, mock_ai_parser):
        """Тест валидации невалидных данных"""
        mock_get_parser.return_value = mock_ai_parser
        
        # Мок возвращает невалидные данные
        mock_ai_parser.structure_data.return_value = {
            "is_valid": False,
            "issues": ["Отрицательное потребление", "Некорректная дата"],
            "confidence": 0.3
        }
        
        from ai_data_validator import AIDataValidator
        validator = AIDataValidator()
        
        extracted_data = "Электроэнергия: -1000 кВт*ч"
        result = validator.validate_extracted_data(extracted_data)
        
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0
    
    @patch('ai_data_validator.get_ai_parser')
    def test_regex_validation(self, mock_get_parser):
        """Тест валидации через регулярные выражения"""
        mock_get_parser.return_value = None
        
        from ai_data_validator import AIDataValidator
        validator = AIDataValidator()
        
        # Тест с отрицательными значениями
        extracted_data = "Потребление: -1000 кВт*ч"
        issues = validator._regex_validation(extracted_data)
        
        # Должна быть обнаружена проблема с отрицательным значением
        assert len(issues) > 0

