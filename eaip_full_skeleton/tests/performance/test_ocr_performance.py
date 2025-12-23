"""
Тесты производительности для OCR
"""
import pytest
import time
from PIL import Image


class TestOCRPerformance:
    """Тесты производительности OCR"""
    
    @pytest.fixture
    def sample_image(self, temp_dir):
        """Создает тестовое изображение"""
        img = Image.new('RGB', (800, 600), color='white')
        img_path = temp_dir / "test_ocr.jpg"
        img.save(img_path)
        return str(img_path)
    
    @pytest.mark.performance
    def test_ocr_speed(self, sample_image):
        """Тест скорости OCR обработки"""
        from file_parser import apply_ocr_to_image
        
        start_time = time.time()
        result = apply_ocr_to_image(sample_image, languages="rus+eng")
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # OCR должен обработать изображение за разумное время
        # Для тестового изображения это должно быть < 10 секунд
        assert processing_time < 10.0, f"OCR занял слишком много времени: {processing_time:.2f}с"
        assert "text" in result or "error" in result
    
    @pytest.mark.performance
    def test_ocr_memory_usage(self, sample_image):
        """Тест использования памяти при OCR"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        from file_parser import apply_ocr_to_image
        
        # Выполняем OCR
        apply_ocr_to_image(sample_image)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Увеличение памяти не должно быть критическим (< 500 MB для одного изображения)
        assert memory_increase < 500, f"Слишком большое использование памяти: {memory_increase:.2f} MB"
    
    @pytest.mark.performance
    def test_batch_ocr_performance(self, temp_dir):
        """Тест производительности батчевой обработки OCR"""
        # Создаем несколько тестовых изображений
        images = []
        for i in range(5):
            img = Image.new('RGB', (400, 300), color='white')
            img_path = temp_dir / f"test_{i}.jpg"
            img.save(img_path)
            images.append(str(img_path))
        
        from file_parser import apply_ocr_to_image
        
        start_time = time.time()
        results = []
        for img_path in images:
            result = apply_ocr_to_image(img_path)
            results.append(result)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_image = total_time / len(images)
        
        # Среднее время на изображение должно быть разумным
        assert avg_time_per_image < 5.0, f"Слишком долгая обработка: {avg_time_per_image:.2f}с на изображение"

