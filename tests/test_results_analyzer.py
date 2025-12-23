"""Скрипт для анализа результатов тестирования"""

import json
from pathlib import Path

def analyze_test_results():
    """Анализ результатов теста."""
    print("=" * 80)
    print("АНАЛИЗ РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
    print("=" * 80)
    
    # Чтение отчета о заполнении
    fill_report_path = Path("test_output_extended/filled_template.fill_report.json")
    if not fill_report_path.exists():
        # Пробуем альтернативный путь
        fill_report_path = Path("test_output/filled_template.fill_report.json")
    
    if fill_report_path.exists():
        fill_data = json.loads(fill_report_path.read_text(encoding="utf-8"))
        results = fill_data["results"]
        
        print("\n📊 ТЕСТ 1: БАЗОВОЕ ЗАПОЛНЕНИЕ")
        print("-" * 80)
        print(f"✅ Заполнено ячеек: {results['filled_cells']}")
        print(f"⚠️  Пропущено ячеек: {results['skipped_cells']}")
        total = results['filled_cells'] + results['skipped_cells']
        success_rate = (results['filled_cells'] / total * 100) if total > 0 else 0
        print(f"📈 Успешность заполнения: {success_rate:.1f}%")
        print(f"❌ Ошибок: {len(results['errors'])}")
        print(f"⚠️  Предупреждений: {len(results['warnings'])}")
        
        print("\n📝 Заполненные ячейки:")
        for item in results['filled_addresses'][:10]:  # Показываем первые 10
            print(f"  ✅ {item['sheet']}!{item['address']} = {item['value']}")
            print(f"     Данные: {item['data_path']}")
        
        if len(results['filled_addresses']) > 10:
            print(f"  ... и еще {len(results['filled_addresses']) - 10} ячеек")
        
        if results['skipped_cells'] > 0:
            print(f"\n⚠️  Пропущенные ячейки (низкая уверенность маппинга): {results['skipped_cells']}")
    
    # Чтение отчета валидации
    validation_report_path = Path("test_output_extended/validation_report.json")
    if not validation_report_path.exists():
        validation_report_path = Path("test_output/validation_report.json")
    
    if validation_report_path.exists():
        validation_data = json.loads(validation_report_path.read_text(encoding="utf-8"))
        
        print("\n\n📊 ТЕСТ 2: ВАЛИДАЦИЯ РЕЗУЛЬТАТОВ")
        print("-" * 80)
        print(f"✅ Статус: {validation_data['status']}")
        print(f"📈 Оценка: {validation_data['score']:.2%}")
        print(f"❌ Проблем: {len(validation_data['issues'])}")
        print(f"⚠️  Предупреждений: {len(validation_data['warnings'])}")
        
        validations = validation_data['validations']
        print("\n🔍 Детали валидации:")
        print(f"  Структура: {validations['structural']['status']}")
        print(f"  Заполнение: {validations['filling']['status']} "
              f"({validations['filling']['details'].get('fill_rate', 0):.1f}%)")
        print(f"  Форматы: {validations['formats']['status']}")
        print(f"  Единицы: {validations['units']['status']}")
        if 'semantic' in validations:
            semantic = validations['semantic']
            print(f"  Семантика: {semantic['status']} "
                  f"(маппинг: {semantic['details'].get('mapping_rate', 0):.1f}%)")
    
    # Чтение сводки
    summary_path = Path("test_output_extended/integration_summary.json")
    if not summary_path.exists():
        summary_path = Path("test_output/integration_summary.json")
    
    if summary_path.exists():
        summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
        
        print("\n\n📊 ИТОГОВАЯ СВОДКА")
        print("-" * 80)
        overall = summary_data['overall_summary']
        print(f"✅ Статус заполнения: {overall['filling_success_rate']:.1f}%")
        print(f"✅ Статус валидации: {overall['validation_status']} ({overall['validation_score']:.2%})")
        print(f"✅ Общий статус: {overall['overall_status']}")
        print(f"{'✅' if overall['ready_for_use'] else '❌'} Готов к использованию: {'Да' if overall['ready_for_use'] else 'Нет'}")
    
    # Анализ семантического маппинга
    mapping_paths = [
        Path("hybrid_analysis/semantic/extended_semantic_mapping.json"),
        Path("hybrid_analysis/semantic/semantic_mapping.json")
    ]
    
    for mapping_path in mapping_paths:
        if mapping_path.exists():
            mapping_data = json.loads(mapping_path.read_text(encoding="utf-8"))
            
            print(f"\n\n📊 АНАЛИЗ СЕМАНТИЧЕСКОГО МАППИНГА ({mapping_path.name})")
            print("-" * 80)
            mappings = mapping_data['mappings']
            print(f"Всего маппингов: {len(mappings)}")
            
            high_confidence = [m for m in mappings if m.get('confidence', 0) >= 0.3]
            low_confidence = [m for m in mappings if m.get('confidence', 0) < 0.3]
            
            print(f"✅ Маппинги с confidence >= 0.3: {len(high_confidence)}")
            print(f"⚠️  Маппинги с confidence < 0.3: {len(low_confidence)}")
            
            # Распределение по листам
            sheets_distribution = {}
            for m in mappings:
                sheet = m.get('sheet', 'unknown')
                sheets_distribution[sheet] = sheets_distribution.get(sheet, 0) + 1
            
            print("\n📊 Распределение по листам:")
            for sheet, count in sheets_distribution.items():
                print(f"  {sheet}: {count} маппингов")
            
            if low_confidence and len(low_confidence) <= 10:
                print("\n⚠️  Маппинги с низкой уверенностью (пропущены):")
                for m in low_confidence:
                    print(f"  - {m['sheet']}!{m['cell_address']} - {m['semantic_type']} "
                          f"(confidence: {m.get('confidence', 0):.3f})")
            break
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_test_results()

