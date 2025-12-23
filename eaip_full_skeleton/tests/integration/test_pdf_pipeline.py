"""
Интеграционные тесты для пайплайна обработки PDF
"""
import pytest
import os
from unittest.mock import patch
import tempfile


class TestPDFProcessingPipeline:
    """Интеграционные тесты пайплайна обработки PDF"""
    
    @pytest.fixture
    def sample_pdf(self, temp_dir):
        """Создает тестовый PDF файл"""
        pdf_path = temp_dir / "test.pdf"
        # Минимальный валидный PDF
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000206 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
300
%%EOF"""
        pdf_path.write_bytes(pdf_content)
        return str(pdf_path)
    
    @patch('file_parser.get_ai_parser')
    def test_pdf_processing_without_ai(self, mock_get_parser):
        """Тест обработки PDF без AI"""
        mock_get_parser.return_value = None
        
        from file_parser import parse_pdf_file
        
        # Создаем временный PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"%PDF-1.4\n")
            pdf_path = f.name
        
        try:
            result = parse_pdf_file(pdf_path)
            
            assert "parsed" in result
            assert "data" in result
        finally:
            os.unlink(pdf_path)
    
    @patch('file_parser.get_ai_parser')
    def test_pdf_processing_with_ocr(self, mock_get_parser):
        """Тест обработки PDF с OCR"""
        mock_get_parser.return_value = None
        
        from file_parser import parse_pdf_file
        
        # Создаем временный PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"%PDF-1.4\n")
            pdf_path = f.name
        
        try:
            result = parse_pdf_file(pdf_path, batch_id="test_batch")
            
            assert "parsed" in result
            # OCR может быть недоступен, но структура должна быть правильной
            if "data" in result:
                assert "ocr_attempted" in result["data"] or "text" in result["data"]
        finally:
            os.unlink(pdf_path)
    
    def test_pdf_classification(self, sample_pdf):
        """Тест классификации PDF"""
        from utils.pdf_classifier import classify_pdf_type
        
        classification = classify_pdf_type(sample_pdf)
        
        assert "pdf_type" in classification
        assert "has_text" in classification
        assert "is_scanned" in classification
    
    def test_table_extraction_from_pdf(self, sample_pdf):
        """Тест извлечения таблиц из PDF"""
        from utils.table_detector import extract_tables_from_pdf
        
        # Может вернуть пустой список если таблиц нет
        tables = extract_tables_from_pdf(sample_pdf)
        
        assert isinstance(tables, list)

