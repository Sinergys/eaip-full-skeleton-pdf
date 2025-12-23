#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для функциональной группировки файлов проекта EAIP
"""
import json
import re
from collections import defaultdict

def categorize_files():
    """Группирует файлы по функциональному назначению"""
    try:
        with open('deepseek_payload.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Определяем категории и ключевые слова для каждой категории
        categories = {
            'Документация': {
                'keywords': ['README', 'GUIDE', 'MANUAL', 'DOCUMENT', 'CHANGELOG', 'AUDIT', 'REPORT', 'ANALYSIS'],
                'extensions': ['md', 'txt'],
                'files': []
            },
            'Код (Python)': {
                'keywords': ['py', 'test', 'utils', 'main', 'app', 'service'],
                'extensions': ['py'],
                'files': []
            },
            'Конфигурация': {
                'keywords': ['config', 'yml', 'yaml', 'json', 'env', 'docker', 'compose'],
                'extensions': ['yml', 'json'],
                'files': []
            },
            'Скрипты/Утилиты': {
                'keywords': ['script', 'tool', 'batch', 'shell', 'install', 'setup', 'deploy'],
                'extensions': ['py', 'bat', 'sh'],
                'files': []
            },
            'Данные/Шаблоны': {
                'keywords': ['template', 'data', 'example', 'sample', 'test_data'],
                'extensions': ['xlsx', 'pdf', 'docx', 'json'],
                'files': []
            },
            'CI/CD': {
                'keywords': ['workflow', 'action', 'github', 'ci', 'cd', 'deploy'],
                'extensions': ['yml'],
                'files': []
            },
            'Логи/Отчеты': {
                'keywords': ['log', 'result', 'output', 'report', 'test_'],
                'extensions': ['txt', 'json'],
                'files': []
            }
        }
        
        # Распределяем файлы по категориям
        for item in data:
            if 'file_id' in item:
                file_id = item['file_id']
                file_lower = file_id.lower()
                extension = file_id.split('.')[-1].lower() if '.' in file_id else ''
                
                categorized = False
                
                # Проверяем каждую категорию
                for category_name, category_info in categories.items():
                    # Проверяем ключевые слова
                    for keyword in category_info['keywords']:
                        if keyword.lower() in file_lower:
                            categories[category_name]['files'].append(file_id)
                            categorized = True
                            break
                    
                    if categorized:
                        break
                    
                    # Проверяем расширения
                    if extension in category_info['extensions']:
                        categories[category_name]['files'].append(file_id)
                        categorized = True
                        break
                
                # Если файл не попал ни в одну категорию, добавляем в "Прочее"
                if not categorized:
                    if 'Прочее' not in categories:
                        categories['Прочее'] = {'files': []}
                    categories['Прочее']['files'].append(file_id)
        
        # Выводим результаты
        print("=== ФУНКЦИОНАЛЬНАЯ ГРУППИРОВКА ФАЙЛОВ ===")
        print(f"Общее количество файлов: {len(data)}")
        print()
        
        total_categorized = 0
        for category_name, category_info in categories.items():
            file_count = len(category_info['files'])
            total_categorized += file_count
            percentage = (file_count / len(data)) * 100
            
            print(f"{category_name:>20}: {file_count:>3} файлов ({percentage:5.1f}%)")
            
            # Показываем примеры (первые 5)
            if file_count > 0:
                print("    Примеры:")
                for i, example in enumerate(category_info['files'][:5]):
                    print(f"      {i+1}. {example}")
                if file_count > 5:
                    print(f"      ... и еще {file_count - 5} файлов")
            print()
        
        print(f"Всего категоризировано: {total_categorized} файлов")
        
        # Анализируем самые распространенные типы
        print("\n=== АНАЛИЗ РАСПРОСТРАНЕННЫХ ТИПОВ ===")
        
        # Анализируем Python файлы
        py_files = [f for f in categories['Код (Python)']['files'] if f.endswith('.py')]
        print(f"Python файлы ({len(py_files)}):")
        
        py_patterns = defaultdict(int)
        for py_file in py_files:
            file_lower = py_file.lower()
            if 'test' in file_lower:
                py_patterns['Тесты'] += 1
            elif 'main' in file_lower:
                py_patterns['Основные модули'] += 1
            elif 'utils' in file_lower or 'tool' in file_lower:
                py_patterns['Утилиты'] += 1
            elif 'service' in file_lower:
                py_patterns['Сервисы'] += 1
            else:
                py_patterns['Прочие'] += 1
        
        for pattern, count in py_patterns.items():
            print(f"  {pattern}: {count} файлов")
        
        return categories
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return None

if __name__ == "__main__":
    categorize_files()