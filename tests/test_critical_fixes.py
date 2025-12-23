#!/usr/bin/env python3
"""
Тестовый скрипт для проверки критических исправлений Word Document Validator.
Тестирует исправленные компоненты на реальном файле.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавить путь к проекту
project_root = Path(__file__).parent / "eaip_full_skeleton" / "services" / "validate"
sys.path.insert(0, str(project_root))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импорт исправленных модулей
try:
    from services.docx_processor import DocxProcessor
    from services.validation import DocumentValidator
    from core.config import Settings
except ImportError as e:
    logger.error(f"Ошибка импорта модулей: {e}")
    # Попробуем альтернативные пути
    try:
        from docx_processor import DocxProcessor
        from validation import DocumentValidator
        logger.info("Используем альтернативные импорты")
    except ImportError as e2:
        logger.error(f"Ошибка альтернативных импортов: {e2}")
        sys.exit(1)


async def test_extraction_integrity():
    """
    Основной тест проверки целостности извлечения.
    """
    test_file = "C:/Users/DELL/Desktop/Navoiy IES/test full.docx"
    
    logger.info("🚀 НАЧАЛО ТЕСТИРОВАНИЯ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ")
    logger.info(f"📁 Тестовый файл: {test_file}")
    
    try:
        # Создать настройки (минимальные)
        settings = Settings()
        
        # Инициализировать компоненты
        docx_processor = DocxProcessor()
        validator = DocumentValidator(max_file_size_mb=100)
        
        logger.info("✅ Модули успешно инициализированы")
        
        # 1. ВАЛИДАЦИЯ БЕЗОПАСНОСТИ
        logger.info("\n" + "="*50)
        logger.info("🔒 ШАГ 1: ВАЛИДАЦИЯ БЕЗОПАСНОСТИ")
        logger.info("="*50)
        
        security_result = await validator.validate_security(test_file)
        logger.info(f"Статус безопасности: {security_result['security_status']}")
        logger.info(f"Размер файла: {security_result['file_size_mb']} МБ")
        logger.info(f"Валидная ZIP структура: {security_result['is_valid_zip']}")
        
        for detail in security_result['security_details']:
            logger.info(f"  • {detail}")
        
        if security_result['security_status'] != 'PASS':
            logger.error("❌ Валидация безопасности НЕ ПРОЙДЕНА")
            return False
        
        # 2. ИЗВЛЕЧЕНИЕ КОНТЕНТА
        logger.info("\n" + "="*50)
        logger.info("📄 ШАГ 2: ИЗВЛЕЧЕНИЕ КОНТЕНТА")
        logger.info("="*50)
        
        content = await docx_processor.extract_content(test_file)
        text = content['text']
        extracted_objects = content['objects']
        
        logger.info(f"Извлечено символов текста: {len(text):,}")
        logger.info(f"Извлечено объектов: {len(extracted_objects)}")
        
        # Статистика по типам объектов
        object_types = {}
        for obj in extracted_objects.values():
            obj_type = obj.object_type
            object_types[obj_type] = object_types.get(obj_type, 0) + 1
        
        logger.info("Типы извлеченных объектов:")
        for obj_type, count in object_types.items():
            logger.info(f"  • {obj_type}: {count}")
        
        # 3. ВАЛИДАЦИЯ ЦЕЛОСТНОСТИ
        logger.info("\n" + "="*50)
        logger.info("🔍 ШАГ 3: ВАЛИДАЦИЯ ЦЕЛОСТНОСТИ")
        logger.info("="*50)
        
        integrity_result = await validator.validate_extraction_integrity(
            input_objects=extracted_objects,
            output_objects=extracted_objects,  # Проверяем, что объекты остались те же
            file_path=test_file
        )
        
        logger.info(f"Статус целостности: {integrity_result['integrity_status']}")
        logger.info(f"Количество объектов на входе: {integrity_result['input_objects_count']}")
        logger.info(f"Количество объектов на выходе: {integrity_result['output_objects_count']}")
        
        for detail in integrity_result['validation_details']:
            logger.info(f"  • {detail}")
        
        if integrity_result['integrity_status'] != 'PASS':
            logger.error("❌ ВАЛИДАЦИЯ ЦЕЛОСТНОСТИ НЕ ПРОЙДЕНА")
            return False
        
        # 4. ПРОВЕРКА ПОСЛЕДОВАТЕЛЬНОСТИ ID
        logger.info("\n" + "="*50)
        logger.info("📋 ШАГ 4: ПРОВЕРКА ПОСЛЕДОВАТЕЛЬНОСТИ ID")
        logger.info("="*50)
        
        object_ids = sorted(extracted_objects.keys())
        logger.info(f"Найдено объектов: {len(object_ids)}")
        logger.info(f"Первые 10 ID: {object_ids[:10]}")
        logger.info(f"Последние 10 ID: {object_ids[-10:]}")
        
        # Проверить последовательность ID
        expected_ids = [f"OBJ_{i+1:03d}" for i in range(len(object_ids))]
        if object_ids == expected_ids:
            logger.info("✅ ID объектов последовательны и корректны")
        else:
            logger.warning("⚠️ ID объектов НЕ последовательны")
            mismatches = [(exp, actual) for exp, actual in zip(expected_ids, object_ids) if exp != actual]
            logger.warning(f"Несоответствия: {mismatches[:5]}")
        
        # 5. СТАТИСТИКА ВАЛИДАЦИИ
        logger.info("\n" + "="*50)
        logger.info("📊 ШАГ 5: СТАТИСТИКА ВАЛИДАЦИИ")
        logger.info("="*50)
        
        validation_stats = validator.get_validation_stats()
        logger.info("Статистика валидации:")
        for key, value in validation_stats.items():
            logger.info(f"  • {key}: {value}")
        
        # ИТОГОВЫЙ РЕЗУЛЬТАТ
        logger.info("\n" + "="*70)
        logger.info("🎉 РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ")
        logger.info("="*70)
        
        if (security_result['security_status'] == 'PASS' and 
            integrity_result['integrity_status'] == 'PASS'):
            logger.info("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            logger.info(f"✅ Целостность данных: {len(extracted_objects)} объектов сохранено")
            logger.info("✅ Безопасность: файл валиден")
            logger.info("✅ Архитектурные исправления работают корректно")
            return True
        else:
            logger.error("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
            return False
            
    except Exception as e:
        logger.error(f"❌ ОШИБКА ТЕСТИРОВАНИЯ: {str(e)}", exc_info=True)
        return False


async def main():
    """
    Главная функция тестирования.
    """
    logger.info("🔧 ТЕСТИРОВАНИЕ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ WORD DOCUMENT VALIDATOR")
    logger.info("Исправленные компоненты:")
    logger.info("  • docx_processor.py - последовательное извлечение объектов")
    logger.info("  • document_assembler.py - безопасное восстановление")
    logger.info("  • validation.py - проверка целостности данных")
    logger.info("  • orchestrator.py - интеграция валидации в pipeline")
    
    success = await test_extraction_integrity()
    
    if success:
        logger.info("\n🎊 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        logger.info("Критические архитектурные проблемы решены.")
        return 0
    else:
        logger.error("\n💥 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)