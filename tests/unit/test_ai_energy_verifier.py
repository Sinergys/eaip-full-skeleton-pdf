"""
Unit-тесты для ai_energy_verifier.py
"""
import pytest
from unittest.mock import Mock, patch


class TestEnergyDataVerifier:
    """Тесты для класса EnergyDataVerifier"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера"""
        parser = Mock()
        parser.enabled = True
        return parser
    
    @patch('ai_energy_verifier.get_ai_parser')
    def test_verify_energy_data(self, mock_get_parser, mock_ai_parser):
        """Тест верификации энергетических данных"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_energy_verifier import EnergyDataVerifier
        verifier = EnergyDataVerifier()
        
        energy_data = {
            "resources": {
                "electricity": {
                    "Q1": {"consumption": 1000.0, "cost": 5000.0}
                }
            }
        }
        
        result = verifier.verify_energy_data(energy_data)
        
        assert "is_verified" in result
        assert "confidence" in result
        assert result["ai_used"] is True

