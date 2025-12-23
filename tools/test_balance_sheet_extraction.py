#!/usr/bin/env python3
"""
Тестовый скрипт для проверки извлечения данных по узлам учёта из актов балансов.
Согласно рекомендации QA Engineer: "Тестировать на нескольких файлах сначала"
"""
import sys
import logging
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton"))

from services.ingest.utils.balance_sheet_detector import (
    is_balance_sheet_file,
    get_balance_sheet_type
)
from services.ingest.utils.balance_sheet_node_extractor import (
    extract_node_consumption_from_balance_sheet
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_file_detection(file_path: Path) -> bool:
    """Тестирует определение акта баланса."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Тест 1: Определение акта баланса")
    logger.info(f"{'='*60}")
    logger.info(f"Файл: {file_path.name}")
    
    try:
        is_balance = is_balance_sheet_file(str(file_path))
        balance_type = get_balance_sheet_type(str(file_path)) if is_balance else None
        
        logger.info(f"  Результат: {'✅ Акт баланса' if is_balance else '❌ Не акт баланса'}")
        if balance_type:
            logger.info(f"  Тип акта: {balance_type}")
        
        return is_balance
    except Exception as e:
        logger.error(f"  Ошибка: {e}")
        return False


def test_node_extraction(file_path: Path) -> list:
    """Тестирует извлечение данных по узлам учёта."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Тест 2: Извлечение данных по узлам учёта")
    logger.info(f"{'='*60}")
    logger.info(f"Файл: {file_path.name}")
    
    try:
        # Извлекаем данные
        node_data = extract_node_consumption_from_balance_sheet(
            file_path=str(file_path),
            batch_id="test_batch_001",
            enterprise_id=1,
            raw_json=None  # Будет загружен автоматически для Excel/Word
        )
        
        logger.info(f"  Извлечено записей: {len(node_data)}")
        
        if node_data:
            logger.info(f"\n  Примеры извлеченных данных:")
            for idx, node in enumerate(node_data[:3], 1):  # Показываем первые 3
                logger.info(f"    {idx}. Узел: {node.get('node_name')}")
                logger.info(f"       Период: {node.get('period')}")
                logger.info(f"       Активная энергия: {node.get('active_energy_kwh')} кВт·ч")
                logger.info(f"       Реактивная энергия: {node.get('reactive_energy_kvarh')} кВар·ч")
                logger.info(f"       Стоимость: {node.get('cost_sum')} сум")
        
        return node_data
    except Exception as e:
        logger.error(f"  Ошибка извлечения: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def main():
    """Основная функция тестирования."""
    logger.info("="*60)
    logger.info("ТЕСТИРОВАНИЕ ИЗВЛЕЧЕНИЯ ДАННЫХ ПО УЗЛАМ ИЗ АКТОВ БАЛАНСОВ")
    logger.info("="*60)
    
    # Определяем пути к тестовым файлам
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "source_files" / "audit_sinergys"
    aggregated_dir = project_root / "data" / "aggregated"
    
    # Список потенциальных файлов для тестирования
    test_files = [
        data_dir / "schetchiki.xlsx",  # Счетчики (узлы учёта)
        data_dir / "electro act react.xlsx",  # Электроэнергия активная и реактивная
        aggregated_dir / "test_nodes.xlsx",  # Тестовый файл узлов
    ]
    
    # Проверяем существование файлов
    existing_files = [f for f in test_files if f.exists()]
    
    if not existing_files:
        logger.warning("⚠️ Тестовые файлы не найдены!")
        logger.info(f"Ожидаемые пути:")
        for f in test_files:
            logger.info(f"  - {f}")
        return
    
    logger.info(f"\nНайдено {len(existing_files)} файлов для тестирования\n")
    
    # Тестируем каждый файл
    results = []
    for file_path in existing_files:
        logger.info(f"\n{'#'*60}")
        logger.info(f"Обработка файла: {file_path.name}")
        logger.info(f"{'#'*60}")
        
        # Тест 1: Определение акта баланса
        is_balance = test_file_detection(file_path)
        
        # Тест 2: Извлечение данных (даже если не определен как акт баланса)
        node_data = test_node_extraction(file_path)
        
        results.append({
            "file": file_path.name,
            "is_balance": is_balance,
            "nodes_count": len(node_data),
            "node_data": node_data
        })
    
    # Итоговый отчет
    logger.info(f"\n{'='*60}")
    logger.info("ИТОГОВЫЙ ОТЧЕТ")
    logger.info(f"{'='*60}")
    
    total_nodes = sum(r["nodes_count"] for r in results)
    balance_files = sum(1 for r in results if r["is_balance"])
    
    logger.info(f"\nОбработано файлов: {len(results)}")
    logger.info(f"Определено как акты балансов: {balance_files}")
    logger.info(f"Всего извлечено записей по узлам: {total_nodes}")
    
    logger.info(f"\nДетали по файлам:")
    for r in results:
        status = "✅ Акт баланса" if r["is_balance"] else "❌ Не акт баланса"
        logger.info(f"  • {r['file']}: {status}, узлов: {r['nodes_count']}")
    
    logger.info(f"\n{'='*60}")
    logger.info("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()

