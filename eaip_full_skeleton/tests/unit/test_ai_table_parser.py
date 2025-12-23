"""
Unit-тесты для ai_table_parser.py
"""
import pytest
from unittest.mock import Mock, patch


class TestAITableParser:
    """Тесты для класса AITableParser"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера"""
        parser = Mock()
        parser.enabled = True
        return parser
    
    @patch('ai_table_parser.get_ai_parser')
    def test_parse_table_from_text(self, mock_get_parser, mock_ai_parser):
        """Тест парсинга таблицы из текста"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_table_parser import AITableParser
        parser = AITableParser()
        
        table_text = """
        Месяц | Потребление | Стоимость
        Январь | 100 | 5000
        Февраль | 120 | 6000
        """
        
        result = parser.parse_table_from_text(table_text)
        
        assert "tables" in result
        assert result["ai_used"] is True

