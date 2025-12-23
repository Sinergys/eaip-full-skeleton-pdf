"""
Вариант 2: Headers приоритетны - если есть headers, используем их количество
"""
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def validate_table_structure_variant2(table):
    """Вариант 2: Headers приоритетны"""
    rows = table.get('rows', [])
    headers = table.get('headers', [])
    warnings = []
    
    if not rows:
        return {
            'rows': [],
            'headers': headers,
            'row_count': 0,
            'col_count': 0,
            'validated': False,
            'warnings': ['Таблица пуста']
        }
    
    # Определяем ожидаемое количество столбцов
    max_cols_in_rows = max(len(row) for row in rows) if rows else 0
    headers_cols = len(headers) if headers and isinstance(headers, list) else 0
    
    # ВАРИАНТ 2: Если есть headers, используем их количество как приоритетное
    if headers_cols > 0:
        expected_cols = headers_cols  # Headers приоритетны
        if max_cols_in_rows > headers_cols:
            warnings.append(f'Rows имеют больше столбцов ({max_cols_in_rows}), чем headers ({headers_cols}), будет обрезано до {headers_cols}')
    else:
        expected_cols = max_cols_in_rows
        if max_cols_in_rows > 0:
            warnings.append(f'Количество столбцов определено автоматически: {max_cols_in_rows}')
    
    # Исправляем строки
    for i, row in enumerate(rows):
        if len(row) != expected_cols:
            if len(row) < expected_cols:
                rows[i] = row + [''] * (expected_cols - len(row))
                warnings.append(f'Строка {i} дополнена до {expected_cols} столбцов')
            else:
                rows[i] = row[:expected_cols]
                warnings.append(f'Строка {i} обрезана до {expected_cols} столбцов')
    
    # Headers уже правильные (используем их как есть)
    if not headers:
        headers = [f'Столбец {i+1}' for i in range(expected_cols)]
        warnings.append(f'Headers созданы автоматически: {expected_cols} столбцов')
    
    # Удаляем пустые строки
    rows = [row for row in rows if any(cell and str(cell).strip() for cell in row)]
    
    return {
        'rows': rows,
        'headers': headers,
        'row_count': len(rows),
        'col_count': expected_cols,
        'validated': len(rows) > 0 and expected_cols > 0,
        'warnings': warnings
    }


def test_variant_2_headers_priority():
    """Тест варианта 2: Headers приоритетны"""
    # Тест 1: Headers меньше rows (данные должны быть обрезаны)
    table1 = {
        'rows': [
            ['1', 'Товар 1', '10'],
            ['2', 'Товар 2', '5']
        ],
        'headers': ['№', 'Наименование']
    }
    result1 = validate_table_structure_variant2(table1)
    assert result1['col_count'] == 2, "Тест 1: Ожидалось 2 колонки (по заголовкам)"
    assert len(result1['headers']) == 2, "Тест 1: Длина заголовков должна быть 2"
    assert len(result1['rows'][0]) == 2, "Тест 1: Длина строки должна быть обрезана до 2"
    assert result1['validated'] is True, "Тест 1: Валидация должна пройти"
    assert 'Rows имеют больше столбцов (3), чем headers (2)' in result1['warnings'][0], "Тест 1: Должно быть предупреждение об обрезке"

    # Тест 2: Headers больше rows (строки должны быть дополнены)
    table2 = {
        'rows': [
            ['1', 'Товар 1'],
            ['2', 'Товар 2']
        ],
        'headers': ['№', 'Наименование', 'Количество']
    }
    result2 = validate_table_structure_variant2(table2)
    assert result2['col_count'] == 3, "Тест 2: Ожидалось 3 колонки (по заголовкам)"
    assert len(result2['headers']) == 3, "Тест 2: Длина заголовков должна быть 3"
    assert len(result2['rows'][0]) == 3, "Тест 2: Длина строки должна быть дополнена до 3"
    assert result2['validated'] is True, "Тест 2: Валидация должна пройти"
    assert 'Строка 0 дополнена до 3 столбцов' in result2['warnings'], "Тест 2: Должно быть предупреждение о дополнении"

    # Тест 3: Разное количество столбцов в rows (все приводится к headers)
    table3 = {
        'rows': [
            ['1', 'Товар 1'],
            ['2', 'Товар 2', '5', 'Лишний']
        ],
        'headers': ['№', 'Наименование', 'Количество']
    }
    result3 = validate_table_structure_variant2(table3)
    assert result3['col_count'] == 3, "Тест 3: Ожидалось 3 колонки (по заголовкам)"
    assert len(result3['headers']) == 3, "Тест 3: Длина заголовков должна быть 3"
    assert len(result3['rows'][0]) == 3, "Тест 3: Первая строка должна быть дополнена до 3"
    assert len(result3['rows'][1]) == 3, "Тест 3: Вторая строка должна быть обрезана до 3"
    assert result3['validated'] is True, "Тест 3: Валидация должна пройти"
    assert 'Строка 0 дополнена до 3 столбцов' in result3['warnings'], "Тест 3: Должно быть предупреждение о дополнении"
    assert 'Строка 1 обрезана до 3 столбцов' in result3['warnings'], "Тест 3: Должно быть предупреждение об обрезке"


if __name__ == '__main__':
    results_v2 = test_variant_2_headers_priority()
    
    print("\n" + "="*80)
    print("СРАВНЕНИЕ ВАРИАНТОВ")
    print("="*80)
    
    print("\nВАРИАНТ 1 (МАКСИМУМ):")
    print("  ✅ Сохраняет максимум данных")
    print("  ✅ Гибко обрабатывает разные случаи")
    print("  ⚠️ Может дополнять headers пустыми значениями")
    print("  ⚠️ Может не соответствовать ожиданиям (headers игнорируются)")
    
    print("\nВАРИАНТ 2 (HEADERS ПРИОРИТЕТНЫ):")
    print("  ✅ Соответствует ожиданиям (headers используются)")
    print("  ✅ Логически понятно (headers определяют структуру)")
    print("  ❌ ПОТЕРЯ ДАННЫХ: обрезает rows до headers")
    print("  ❌ Менее гибкий (не учитывает максимум в rows)")
    
    print("\n" + "="*80)
    print("РЕКОМЕНДАЦИЯ: ВАРИАНТ 1 (МАКСИМУМ) - ЛУЧШИЙ")
    print("="*80)
    print("Причина: Сохранение данных важнее соответствия ожиданиям")
    print("Решение: Исправить тест, чтобы он ожидал максимум (4), а не headers (3)")

