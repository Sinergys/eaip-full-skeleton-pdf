"""
Тесты производительности для AI-анализа
"""
import pytest
import time
from unittest.mock import Mock, patch


class TestAIPerformance:
    """Тесты производительности AI-модулей"""
    
    @pytest.fixture
    def mock_ai_parser(self):
        """Мок AI парсера с задержкой"""
        parser = Mock()
        parser.enabled = True
        
        def mock_structure_data(text):
            time.sleep(0.1)  # Имитация задержки API
            return {"document_type": "test", "fields": {}}
        
        parser.structure_data = mock_structure_data
        return parser
    
    @pytest.mark.performance
    @patch('ai_anomaly_detector.get_ai_parser')
    def test_anomaly_detection_performance(self, mock_get_parser, mock_ai_parser):
        """Тест производительности детекции аномалий"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        
        structured_data = {
            "resources": {
                "electricity": {
                    f"Q{i}": {"consumption": 1000.0 + i * 100}
                    for i in range(1, 5)
                }
            }
        }
        
        start_time = time.time()
        result = detector.detect_data_anomalies(structured_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Детекция аномалий должна быть быстрой (< 2 секунды)
        assert processing_time < 2.0, f"Слишком долгая обработка: {processing_time:.2f}с"
        assert "anomalies" in result
    
    @pytest.mark.performance
    @patch('ai_data_validator.get_ai_parser')
    def test_validation_performance(self, mock_get_parser, mock_ai_parser):
        """Тест производительности валидации"""
        mock_get_parser.return_value = mock_ai_parser
        
        from ai_data_validator import AIDataValidator
        validator = AIDataValidator()
        
        extracted_data = "Электроэнергия: 1000 кВт*ч, Стоимость: 5000 руб" * 10
        
        start_time = time.time()
        result = validator.validate_extracted_data(extracted_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Валидация должна быть быстрой (< 1 секунда)
        assert processing_time < 1.0, f"Слишком долгая валидация: {processing_time:.2f}с"
        assert "is_valid" in result

