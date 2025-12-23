"""
Unit-тесты для проверки порогов confidence и fallback-логики
"""
import pytest
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import _check_confidence, _log_low_confidence, _load_config


class TestConfidenceThresholds:
    """Тесты для порогов confidence"""
    
    def test_high_confidence_no_flag(self):
        """Тест 1: Высокий confidence - validation_flag не добавляется"""
        result = {
            "text": "Тестовый текст",
            "tables": [],
            "confidence": 0.95
        }
        
        with patch('gemini_vision_ocr._log_low_confidence') as mock_log:
            checked = _check_confidence(result, "test_path", page_num=1)
            
            # validation_flag не должен быть добавлен
            assert 'validation_flag' not in checked
            # Логирование не должно вызываться
            mock_log.assert_not_called()
    
    def test_low_confidence_flag_added(self):
        """Тест 2: Низкий confidence - validation_flag добавляется"""
        result = {
            "text": "Тестовый текст",
            "tables": [],
            "confidence": 0.20  # Ниже порога 0.30
        }
        
        with patch('gemini_vision_ocr._log_low_confidence') as mock_log:
            checked = _check_confidence(result, "test_path", page_num=1)
            
            # validation_flag должен быть добавлен
            assert 'validation_flag' in checked
            assert 'low_confidence' in checked['validation_flag']
            # Логирование должно быть вызвано
            mock_log.assert_called_once()
    
    def test_table_low_confidence(self):
        """Тест 3: Низкий confidence таблицы - флаг для таблицы"""
        result = {
            "text": "Тестовый текст",
            "tables": [
                {
                    "rows": [["1", "2"]],
                    "headers": ["A", "B"],
                    "confidence": 0.50  # Ниже порога 0.70 для таблиц
                }
            ],
            "confidence": 0.90
        }
        
        with patch('gemini_vision_ocr._log_low_confidence') as mock_log:
            checked = _check_confidence(result, "test_path", page_num=1)
            
            # validation_flag должен содержать флаг для таблицы
            assert 'validation_flag' in checked
            assert 'low_confidence_table_0' in checked['validation_flag']
            # Логирование должно быть вызвано для таблицы
            assert mock_log.call_count == 1


class TestLogLowConfidence:
    """Тесты для логирования low_confidence"""
    
    def test_log_writes_to_file(self):
        """Тест: Логирование записывается в файл"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "low_confidence.log"
            
            # Мокаем конфиг
            with patch('gemini_vision_ocr._load_config') as mock_config:
                mock_config.return_value = {
                    'logging': {
                        'low_confidence_log': str(log_path),
                        'enabled': True
                    }
                }
                
                # Вызываем логирование
                _log_low_confidence("test_doc.pdf", 1, "overall", 0.25, 0.30)
                
                # Проверяем, что файл создан и содержит запись
                assert log_path.exists()
                content = log_path.read_text(encoding='utf-8')
                assert "test_doc.pdf" in content
                assert "page_1" in content
                assert "overall" in content
                assert "confidence=0.25" in content
                assert "threshold=0.30" in content


class TestConfigLoading:
    """Тесты для загрузки конфигурации"""
    
    def test_default_thresholds(self):
        """Тест: Используются пороги по умолчанию если конфиг не найден"""
        with patch('pathlib.Path.exists', return_value=False):
            config = _load_config()
            
            assert config['confidence_thresholds']['text'] == 0.30
            assert config['confidence_thresholds']['numbers'] == 0.60
            assert config['confidence_thresholds']['dates'] == 0.80
            assert config['confidence_thresholds']['tables'] == 0.70


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

