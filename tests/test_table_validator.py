"""
Unit тесты для модуля валидации таблиц
"""
import unittest
from eaip_full_skeleton.services.ingest.utils.table_validator import (
    validate_table_structure,
    validate_tables_list,
    get_table_statistics
)


class TestTableValidator(unittest.TestCase):
    
    def test_valid_table(self):
        """Тест валидации корректной таблицы"""
        table = {
            'rows': [
                ['1', 'Товар 1', '10'],
                ['2', 'Товар 2', '5']
            ],
            'headers': ['№', 'Наименование', 'Количество'],
            'location': 'страница 1',
            'confidence': 0.95
        }
        
        result = validate_table_structure(table)
        
        self.assertTrue(result['validated'])
        self.assertEqual(result['row_count'], 2)
        self.assertEqual(result['col_count'], 3)
        self.assertEqual(len(result['rows']), 2)
        self.assertEqual(len(result['headers']), 3)
        self.assertEqual(len(result['errors']), 0)
    
    def test_table_with_mismatched_columns(self):
        """Тест исправления таблицы с разным количеством столбцов"""
        table = {
            'rows': [
                ['1', 'Товар 1'],  # Не хватает столбца
                ['2', 'Товар 2', '5', 'Лишний']  # Лишний столбец
            ],
            'headers': ['№', 'Наименование', 'Количество']
        }
        
        result = validate_table_structure(table)
        
        self.assertTrue(result['validated'])
        # Используем максимум между headers (3) и rows (4) = 4
        self.assertEqual(result['col_count'], 4)  # Максимум: headers (3) и rows (4) = 4
        # Проверяем, что все строки имеют одинаковое количество столбцов
        for row in result['rows']:
            self.assertEqual(len(row), 4)  # Все строки должны быть дополнены/обрезаны до 4
        # Должно быть предупреждение о дополнении/обрезании строк
        self.assertGreaterEqual(len(result['warnings']), 1)
    
    def test_table_with_mismatched_headers(self):
        """Тест исправления headers с неправильным количеством"""
        table = {
            'rows': [
                ['1', 'Товар 1', '10'],
                ['2', 'Товар 2', '5']
            ],
            'headers': ['№', 'Наименование']  # Не хватает столбца
        }
        
        result = validate_table_structure(table)
        
        self.assertTrue(result['validated'])
        self.assertEqual(len(result['headers']), 3)  # Должно быть дополнено до 3
        # Должно быть предупреждение о дополнении headers
        self.assertGreaterEqual(len(result['warnings']), 1)
    
    def test_table_with_empty_rows(self):
        """Тест удаления пустых строк"""
        table = {
            'rows': [
                ['1', 'Товар 1', '10'],
                ['', '', ''],  # Пустая строка
                ['   ', '   ', '   '],  # Строка с пробелами
                ['2', 'Товар 2', '5']
            ],
            'headers': ['№', 'Наименование', 'Количество']
        }
        
        result = validate_table_structure(table)
        
        self.assertTrue(result['validated'])
        self.assertEqual(result['row_count'], 2)  # Только 2 строки с данными
    
    def test_table_with_none_values(self):
        """Тест нормализации None значений"""
        table = {
            'rows': [
                ['№', 'Наименование', 'Количество'],
                ['1', None, '10'],
                ['2', 'Товар 2', None]
            ],
            'headers': ['№', 'Наименование', 'Количество']
        }
        
        result = validate_table_structure(table)
        
        self.assertTrue(result['validated'])
        # Проверяем, что None заменены на ''
        for row in result['rows']:
            for cell in row:
                self.assertIsNotNone(cell)
                self.assertIsInstance(cell, str)
    
    def test_empty_table(self):
        """Тест обработки пустой таблицы"""
        table = {
            'rows': [],
            'headers': []
        }
        
        result = validate_table_structure(table)
        
        self.assertFalse(result['validated'])
        self.assertEqual(len(result['errors']), 1)
        self.assertIn('пуста', result['errors'][0])
    
    def test_table_without_headers(self):
        """Тест создания headers автоматически"""
        table = {
            'rows': [
                ['1', 'Товар 1', '10'],
                ['2', 'Товар 2', '5']
            ],
            'headers': []
        }
        
        result = validate_table_structure(table)
        
        self.assertTrue(result['validated'])
        self.assertEqual(len(result['headers']), 3)
        self.assertEqual(result['headers'][0], 'Столбец 1')
    
    def test_validate_tables_list(self):
        """Тест валидации списка таблиц"""
        tables = [
            {
                'rows': [['1', 'Товар 1', '10']],
                'headers': ['№', 'Наименование', 'Количество']
            },
            {
                'rows': [['2', 'Товар 2', '']],  # Исправлено: дополнено до 3 столбцов
                'headers': ['№', 'Наименование', 'Количество']
            },
            {
                'rows': [],  # Пустая таблица
                'headers': []
            }
        ]
        
        result = validate_tables_list(tables)
        
        # Должны пройти валидацию первые 2 таблицы (третья пустая)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]['validated'])
        self.assertTrue(result[1]['validated'])
    
    def test_get_table_statistics(self):
        """Тест вычисления статистики таблицы"""
        table = {
            'rows': [
                ['1', 'Товар 1', '10', '1000'],
                ['2', 'Товар 2', '5', '2000']
            ],
            'headers': ['№', 'Наименование', 'Количество', 'Цена']
        }
        
        stats = get_table_statistics(table)
        
        self.assertEqual(stats['row_count'], 2)
        self.assertEqual(stats['col_count'], 4)
        self.assertEqual(stats['total_cells'], 8)
        self.assertGreater(stats['non_empty_cells'], 0)
        self.assertGreater(stats['numeric_cells'], 0)


if __name__ == '__main__':
    unittest.main()

