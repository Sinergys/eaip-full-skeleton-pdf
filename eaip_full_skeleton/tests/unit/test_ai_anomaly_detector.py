"""
Unit-тесты для ai_anomaly_detector.py
"""
import pytest
from unittest.mock import Mock, patch


class TestAnomalyDetector:
    """Тесты для класса AnomalyDetector"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера"""
        parser = Mock()
        parser.enabled = True
        parser.structure_data.return_value = {
            "anomalies": [
                {"type": "outlier", "severity": "warning", "field": "consumption"}
            ]
        }
        return parser
    
    @patch('ai_anomaly_detector.get_ai_parser')
    def test_init_with_ai(self, mock_get_parser, mock_ai_parser):
        """Тест инициализации с доступным AI"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        
        assert detector.enabled is True
        assert detector.ai_parser is not None
    
    @patch('ai_anomaly_detector.get_ai_parser')
    def test_init_without_ai(self, mock_get_parser):
        """Тест инициализации без AI"""
        mock_get_parser.return_value = None
        
        from ai_anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        
        assert detector.enabled is False
    
    @patch('ai_anomaly_detector.get_ai_parser')
    def test_detect_data_anomalies_with_ai(self, mock_get_parser, mock_ai_parser):
        """Тест детекции аномалий с AI"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        
        structured_data = {
            "resources": {
                "electricity": {
                    "Q1": {"consumption": 1000.0},
                    "Q2": {"consumption": 5000.0},  # Аномалия
                    "Q3": {"consumption": 1100.0},
                    "Q4": {"consumption": 1200.0}
                }
            }
        }
        
        result = detector.detect_data_anomalies(structured_data)
        
        assert "anomalies" in result
        assert "anomaly_count" in result
        assert result["ai_used"] is True
    
    @patch('ai_anomaly_detector.get_ai_parser')
    def test_detect_data_anomalies_without_ai(self, mock_get_parser):
        """Тест детекции аномалий без AI"""
        mock_get_parser.return_value = None
        
        from ai_anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        
        structured_data = {"resources": {}}
        result = detector.detect_data_anomalies(structured_data)
        
        assert result["ai_used"] is False
        assert result["anomaly_count"] == 0
    
    @patch('ai_anomaly_detector.get_ai_parser')
    def test_statistical_anomaly_detection(self, mock_get_parser):
        """Тест статистической детекции аномалий"""
        mock_get_parser.return_value = None
        
        from ai_anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        
        structured_data = {
            "resources": {
                "electricity": {
                    "Q1": {"consumption": 1000.0},
                    "Q2": {"consumption": 5000.0},  # Аномалия (5x больше)
                    "Q3": {"consumption": 1100.0},
                    "Q4": {"consumption": 1200.0}
                }
            }
        }
        
        anomalies = detector._statistical_anomaly_detection(structured_data)
        
        # Должна быть обнаружена аномалия в Q2
        assert len(anomalies) > 0

