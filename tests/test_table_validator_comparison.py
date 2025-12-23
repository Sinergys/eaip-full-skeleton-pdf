"""
Сравнение двух вариантов логики валидации таблиц
"""
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eaip_full_skeleton.services.ingest.utils.table_validator import validate_table_structure


def test_variant_1_headers_priority():
    """
    Вариант 1: Тестирование логики, где приоритет у максимального количества столбцов.
    """
    # Тест 1: Headers (2) < Rows (3) -> Ожидаем 3 столбца
    table1 = {
        'rows': [
            ['1', 'Товар 1', '10'],
            ['2', 'Товар 2', '5']
        ],
        'headers': ['№', 'Наименование']
    }
    result1 = validate_table_structure(table1)
    assert result1['col_count'] == 3, "Тест 1: Ожидалось 3 колонки (максимум из строк и заголовков)"
    assert len(result1['headers']) == 3, "Тест 1: Заголовки должны быть дополнены до 3"
    assert len(result1['rows'][0]) == 3, "Тест 1: Строки должны иметь 3 колонки"
    assert result1['validated'] is True, "Тест 1: Валидация должна пройти"

    # Тест 2: Headers (3) > Rows (2) -> Ожидаем 3 столбца
    table2 = {
        'rows': [
            ['1', 'Товар 1'],
            ['2', 'Товар 2']
        ],
        'headers': ['№', 'Наименование', 'Количество']
    }
    result2 = validate_table_structure(table2)
    assert result2['col_count'] == 3, "Тест 2: Ожидалось 3 колонки (максимум из строк и заголовков)"
    assert len(result2['headers']) == 3, "Тест 2: Длина заголовков должна быть 3"
    assert len(result2['rows'][0]) == 3, "Тест 2: Строки должны быть дополнены до 3"
    assert result2['validated'] is True, "Тест 2: Валидация должна пройти"

    # Тест 3: Разное количество столбцов: Headers (3), Rows (2 и 4) -> Ожидаем 4 столбца
    table3 = {
        'rows': [
            ['1', 'Товар 1'],
            ['2', 'Товар 2', '5', 'Лишний']
        ],
        'headers': ['№', 'Наименование', 'Количество']
    }
    result3 = validate_table_structure(table3)
    assert result3['col_count'] == 4, "Тест 3: Ожидалось 4 колонки (максимум из строк и заголовков)"
    assert len(result3['headers']) == 4, "Тест 3: Заголовки должны быть дополнены до 4"
    assert len(result3['rows'][0]) == 4, "Тест 3: Первая строка должна быть дополнена до 4"
    assert len(result3['rows'][1]) == 4, "Тест 3: Вторая строка должна иметь 4 колонки"
    assert result3['validated'] is True, "Тест 3: Валидация должна пройти"
    
    # Возвращаем результаты для анализа в __main__
    return {
        'test1': result1,
        'test2': result2,
        'test3': result3
    }


def analyze_results(variant_name, results):
    """Анализ результатов варианта"""
    print(f"\n{'='*80}")
    print(f"АНАЛИЗ ВАРИАНТА: {variant_name}")
    print(f"{'='*80}")
    
    # Критерии оценки
    criteria = {
        'preserves_data': 0,  # Сохраняет ли данные
        'logical_consistency': 0,  # Логическая согласованность
        'user_expectations': 0,  # Соответствие ожиданиям пользователя
        'flexibility': 0  # Гибкость обработки
    }
    
    # Тест 1: Headers < Rows
    if results['test1']['col_count'] == 3:
        criteria['preserves_data'] += 1  # Сохранили все данные rows
        criteria['logical_consistency'] += 1  # Логично дополнять headers
        print("✅ Тест 1: Сохранены все данные rows, headers дополнены")
    else:
        print("❌ Тест 1: Потеря данных")
    
    # Тест 2: Headers > Rows
    if results['test2']['col_count'] == 3:
        criteria['preserves_data'] += 1  # Сохранили headers
        criteria['logical_consistency'] += 1  # Логично дополнять rows
        print("✅ Тест 2: Сохранены headers, rows дополнены")
    else:
        print("❌ Тест 2: Потеря данных")
    
    # Тест 3: Разное количество
    if results['test3']['col_count'] == 4:
        criteria['preserves_data'] += 1  # Сохранили максимум
        criteria['flexibility'] += 1  # Гибко обработали
        print("✅ Тест 3: Сохранен максимум данных")
    elif results['test3']['col_count'] == 3:
        criteria['user_expectations'] += 1  # Соответствует headers
        print("⚠️ Тест 3: Использованы headers, часть данных обрезана")
    else:
        print("❌ Тест 3: Неожиданный результат")
    
    total_score = sum(criteria.values())
    print(f"\nОценка: {total_score}/4")
    print(f"  Сохранение данных: {criteria['preserves_data']}/1")
    print(f"  Логическая согласованность: {criteria['logical_consistency']}/1")
    print(f"  Соответствие ожиданиям: {criteria['user_expectations']}/1")
    print(f"  Гибкость: {criteria['flexibility']}/1")
    
    return total_score, criteria


if __name__ == '__main__':
    print("\n" + "="*80)
    print("СРАВНЕНИЕ ВАРИАНТОВ ЛОГИКИ ВАЛИДАЦИИ ТАБЛИЦ")
    print("="*80)
    
    # Текущая реализация (вариант: максимум)
    results_current = test_variant_1_headers_priority()
    score_current, criteria_current = analyze_results("ТЕКУЩИЙ (МАКСИМУМ)", results_current)
    
    print("\n" + "="*80)
    print("ВЫВОДЫ")
    print("="*80)
    
    print(f"\nТекущая реализация (максимум):")
    print(f"  Оценка: {score_current}/4")
    print(f"  Преимущества:")
    print(f"    - Сохраняет максимум данных")
    print(f"    - Гибко обрабатывает разные случаи")
    print(f"  Недостатки:")
    print(f"    - Может не соответствовать ожиданиям (headers игнорируются)")
    print(f"    - Может дополнять headers пустыми значениями")
    
    print(f"\nРекомендация:")
    if score_current >= 3:
        print(f"  ✅ Текущая реализация (максимум) - ЛУЧШИЙ ВАРИАНТ")
        print(f"  Причина: Сохраняет максимум данных, гибко обрабатывает")
    else:
        print(f"  ⚠️ Текущая реализация требует улучшения")
    
    print("\n" + "="*80)

