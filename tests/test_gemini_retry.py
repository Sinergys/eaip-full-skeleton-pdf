"""
Unit и integration тесты для retry логики Gemini API
"""
import pytest
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import _is_retryable_error, _log_gemini_error, extract_with_gemini_vision


class TestRetryableError:
    """Тесты для определения повторяемых ошибок"""
    
    def test_504_timeout_is_retryable(self):
        """Тест 1: 504 Deadline Exceeded - повторяемая ошибка"""
        error = Exception("504 Deadline Exceeded")
        assert _is_retryable_error(error) == True
    
    def test_500_is_retryable(self):
        """Тест 2: 500 Internal Server Error - повторяемая ошибка"""
        error = Exception("500 Internal Server Error")
        assert _is_retryable_error(error) == True
    
    def test_401_is_not_retryable(self):
        """Тест 3: 401 Unauthorized - неповторяемая ошибка"""
        error = Exception("401 Unauthorized")
        assert _is_retryable_error(error) == False
    
    def test_400_is_not_retryable(self):
        """Тест 4: 400 Bad Request - неповторяемая ошибка"""
        error = Exception("400 Bad Request")
        assert _is_retryable_error(error) == False


class TestLogGeminiError:
    """Тесты для логирования ошибок"""
    
    def test_log_writes_to_file(self):
        """Тест: Логирование записывается в файл"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "gemini_errors.log"
            
            # Мокаем конфиг
            with patch('gemini_vision_ocr._load_config') as mock_config:
                mock_config.return_value = {
                    'api': {
                        'errors_log': str(log_path)
                    }
                }
                
                # Вызываем логирование
                error = Exception("504 Deadline Exceeded")
                _log_gemini_error("test_doc.pdf", 1, 1, error)
                
                # Проверяем, что файл создан и содержит запись
                assert log_path.exists()
                content = log_path.read_text(encoding='utf-8')
                assert "test_doc.pdf" in content
                assert "page_1" in content
                assert "attempt_1" in content
                assert "timeout_504" in content or "504" in content


class TestRetryMechanism:
    """Тесты для механизма retry"""
    
    @patch('gemini_vision_ocr.genai.GenerativeModel')
    @patch('gemini_vision_ocr.Image.open')
    @patch('gemini_vision_ocr._check_confidence')
    def test_successful_request_no_retry(self, mock_check, mock_image, mock_model):
        """Тест: Успешный запрос не требует retry"""
        # Настраиваем моки
        mock_image_instance = MagicMock()
        mock_image.return_value = mock_image_instance
        
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"text": "test", "tables": [], "confidence": 0.9}'
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        mock_check.return_value = {"text": "test", "tables": [], "confidence": 0.9}
        
        # Вызываем функцию
        result = extract_with_gemini_vision("test.png", page_num=1)
        
        # Проверяем, что запрос был выполнен только один раз
        assert mock_model_instance.generate_content.call_count == 1
        assert result["text"] == "test"
    
    @patch('gemini_vision_ocr.genai.GenerativeModel')
    @patch('gemini_vision_ocr.Image.open')
    @patch('time.sleep')  # Мокаем sleep для ускорения теста
    def test_retry_on_504_error(self, mock_sleep, mock_image, mock_model):
        """Тест: Retry при ошибке 504"""
        # Настраиваем моки
        mock_image_instance = MagicMock()
        mock_image.return_value = mock_image_instance
        
        mock_model_instance = MagicMock()
        
        # Первые две попытки - ошибка 504, третья - успех
        error_504 = Exception("504 Deadline Exceeded")
        mock_response = MagicMock()
        mock_response.text = '{"text": "test", "tables": [], "confidence": 0.9}'
        
        mock_model_instance.generate_content.side_effect = [
            error_504,
            error_504,
            mock_response
        ]
        mock_model.return_value = mock_model_instance
        
        # Мокаем _check_confidence и другие функции
        with patch('gemini_vision_ocr._check_confidence') as mock_check, \
             patch('gemini_vision_ocr._log_gemini_error') as mock_log:
            
            mock_check.return_value = {"text": "test", "tables": [], "confidence": 0.9}
            
            # Вызываем функцию
            result = extract_with_gemini_vision("test.png", page_num=1)
            
            # Проверяем, что было 3 попытки
            assert mock_model_instance.generate_content.call_count == 3
            # Проверяем, что sleep был вызван 2 раза (между попытками)
            assert mock_sleep.call_count == 2
            # Проверяем, что ошибки были залогированы
            assert mock_log.call_count == 2
    
    @patch('gemini_vision_ocr.genai.GenerativeModel')
    @patch('gemini_vision_ocr.Image.open')
    @patch('time.sleep')
    def test_no_retry_on_401_error(self, mock_sleep, mock_image, mock_model):
        """Тест: Нет retry при ошибке 401 (неповторяемая)"""
        # Настраиваем моки
        mock_image_instance = MagicMock()
        mock_image.return_value = mock_image_instance
        
        mock_model_instance = MagicMock()
        error_401 = Exception("401 Unauthorized")
        mock_model_instance.generate_content.side_effect = error_401
        mock_model.return_value = mock_model_instance
        
        # Вызываем функцию - должна сразу выбросить исключение
        with pytest.raises(Exception) as exc_info:
            extract_with_gemini_vision("test.png", page_num=1)
        
        # Проверяем, что была только одна попытка
        assert mock_model_instance.generate_content.call_count == 1
        # Проверяем, что sleep не вызывался
        assert mock_sleep.call_count == 0
        assert "401" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

