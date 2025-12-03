"""
Unit-тесты для ai_efficiency_analyzer.py
"""
import pytest
from unittest.mock import Mock, patch


class TestEnergyEfficiencyAnalyzer:
    """Тесты для класса EnergyEfficiencyAnalyzer"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера"""
        parser = Mock()
        parser.enabled = True
        return parser
    
    @patch('ai_efficiency_analyzer.get_ai_parser')
    def test_analyze_efficiency(self, mock_get_parser, mock_ai_parser):
        """Тест анализа энергоэффективности"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_efficiency_analyzer import EnergyEfficiencyAnalyzer
        analyzer = EnergyEfficiencyAnalyzer()
        
        energy_data = {
            "resources": {
                "electricity": {
                    "Q1": {"consumption": 1000.0},
                    "Q2": {"consumption": 1200.0},
                    "Q3": {"consumption": 1100.0},
                    "Q4": {"consumption": 1300.0}
                }
            },
            "equipment": [
                {"power_kw": 10.0, "quantity": 5}
            ]
        }
        
        result = analyzer.analyze_efficiency(energy_data)
        
        assert "efficiency_class" in result
        assert "recommendations" in result
        assert result["ai_used"] is True

