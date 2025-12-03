"""
Unit-тесты для ai_compliance_checker.py
"""
import pytest
from unittest.mock import Mock, patch


class TestComplianceChecker:
    """Тесты для класса ComplianceChecker"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера"""
        parser = Mock()
        parser.enabled = True
        return parser
    
    @patch('ai_compliance_checker.get_ai_parser')
    def test_check_compliance(self, mock_get_parser, mock_ai_parser):
        """Тест проверки соответствия требованиям"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_compliance_checker import ComplianceChecker
        checker = ComplianceChecker()
        
        energy_data = {
            "resources": {
                "electricity": {
                    "Q1": {"consumption": 1000.0, "cost": 5000.0}
                }
            }
        }
        
        result = checker.check_compliance(energy_data, "PKM690")
        
        assert "is_compliant" in result
        assert "violations" in result
        assert result["ai_used"] is True

