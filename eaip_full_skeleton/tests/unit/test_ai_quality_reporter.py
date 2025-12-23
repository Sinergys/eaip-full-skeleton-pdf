"""
Unit-тесты для ai_quality_reporter.py
"""
import pytest
from unittest.mock import Mock, patch


class TestDataQualityReporter:
    """Тесты для класса DataQualityReporter"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера"""
        parser = Mock()
        parser.enabled = True
        return parser
    
    @patch('ai_quality_reporter.get_ai_parser')
    def test_generate_quality_report(self, mock_get_parser, mock_ai_parser):
        """Тест генерации отчета о качестве данных"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_quality_reporter import DataQualityReporter
        reporter = DataQualityReporter()
        
        energy_data = {
            "resources": {
                "electricity": {
                    "Q1": {"consumption": 1000.0}
                }
            }
        }
        
        result = reporter.generate_quality_report(energy_data)
        
        assert "quality_score" in result
        assert "completeness" in result
        assert "accuracy" in result
        assert result["ai_used"] is True

