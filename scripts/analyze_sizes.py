#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для анализа размеров файлов проекта EAIP
"""
import json
import re
from collections import defaultdict

def parse_size(size_str):
    """Парсит размер в человеко-читаемом формате в байты"""
    if not size_str or size_str == "N/A":
        return 0
    
    # Извлекаем число и единицу измерения
    match = re.match(r'([\d.]+)\s*(\w+)', size_str.strip())
    if not match:
        return 0
    
    number = float(match.group(1))
    unit = match.group(2).lower()
    
    # Конвертируем в байты
    multipliers = {
        'b': 1,
        'kb': 1024,
        'mb': 1024**2,
        'gb': 1024**3
    }
    
    return int(number * multipliers.get(unit, 1))

def analyze_file_sizes():
    """Анализирует размеры файлов"""
    try:
        with open('deepseek_payload.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sizes = []
        size_categories = defaultdict(list)
        
        print("=== АНАЛИЗ РАЗМЕРОВ ФАЙЛОВ ===")
        print(f"Общее количество файлов: {len(data)}")
        print()
        
        # Собираем данные о размерах
        for item in data:
            if 'file_id' in item and 'size_human' in item:
                file_id = item['file_id']
                size_human = item['size_human']
                size_bytes = parse_size(size_human)
                
                sizes.append({
                    'file': file_id,
                    'size_human': size_human,
                    'size_bytes': size_bytes,
                    'extension': file_id.split('.')[-1].lower() if '.' in file_id else 'no_ext'
                })
        
        # Сортируем по размеру
        sizes.sort(key=lambda x: x['size_bytes'], reverse=True)
        
        # Общая статистика
        total_size = sum(s['size_bytes'] for s in sizes)
        avg_size = total_size / len(sizes) if sizes else 0
        
        print("=== ОБЩАЯ СТАТИСТИКА ===")
        print(f"Общий размер проекта: {total_size / (1024**2):.2f} MB")
        print(f"Средний размер файла: {avg_size / 1024:.2f} KB")
        print()
        
        # Топ-10 самых больших файлов
        print("=== ТОП-10 САМЫХ БОЛЬШИХ ФАЙЛОВ ===")
        for i, file_info in enumerate(sizes[:10], 1):
            print(f"{i:>2}. {file_info['size_human']:>10} - {file_info['file']}")
        print()
        
        # Топ-10 самых маленьких файлов
        print("=== ТОП-10 САМЫХ МАЛЕНЬКИХ ФАЙЛОВ ===")
        for i, file_info in enumerate(sizes[-10:], 1):
            print(f"{i:>2}. {file_info['size_human']:>10} - {file_info['file']}")
        print()
        
        # Анализ по расширениям
        print("=== РАЗМЕРЫ ПО РАСШИРЕНИЯМ ===")
        ext_stats = defaultdict(list)
        
        for file_info in sizes:
            ext_stats[file_info['extension']].append(file_info)
        
        for ext in sorted(ext_stats.keys()):
            files = ext_stats[ext]
            total_size_ext = sum(f['size_bytes'] for f in files)
            avg_size_ext = total_size_ext / len(files) if files else 0
            max_size_ext = max(f['size_bytes'] for f in files) if files else 0
            min_size_ext = min(f['size_bytes'] for f in files) if files else 0
            
            print(f"{ext:>6}: {len(files):>3} файлов, "
                  f"средний: {avg_size_ext/1024:>6.1f} KB, "
                  f"макс: {max_size_ext/1024:>6.1f} KB, "
                  f"мин: {min_size_ext/1024:>6.1f} KB")
        print()
        
        # Распределение по размерам
        print("=== РАСПРЕДЕЛЕНИЕ ПО РАЗМЕРАМ ===")
        size_ranges = {
            'Очень маленькие (< 1 KB)': 0,
            'Маленькие (1-10 KB)': 0,
            'Средние (10-100 KB)': 0,
            'Большие (100 KB - 1 MB)': 0,
            'Очень большие (> 1 MB)': 0
        }
        
        for file_info in sizes:
            size_kb = file_info['size_bytes'] / 1024
            if size_kb < 1:
                size_ranges['Очень маленькие (< 1 KB)'] += 1
            elif size_kb < 10:
                size_ranges['Маленькие (1-10 KB)'] += 1
            elif size_kb < 100:
                size_ranges['Средние (10-100 KB)'] += 1
            elif size_kb < 1024:
                size_ranges['Большие (100 KB - 1 MB)'] += 1
            else:
                size_ranges['Очень большие (> 1 MB)'] += 1
        
        for range_name, count in size_ranges.items():
            percentage = (count / len(sizes)) * 100
            print(f"{range_name:>25}: {count:>3} файлов ({percentage:5.1f}%)")
        print()
        
        # Находим аномалии
        print("=== АНОМАЛИИ РАЗМЕРОВ ===")
        
        # Очень большие файлы для их типа
        for ext in ['md', 'py', 'json']:
            if ext in ext_stats:
                files = ext_stats[ext]
                avg_size_ext = sum(f['size_bytes'] for f in files) / len(files)
                large_files = [f for f in files if f['size_bytes'] > avg_size_ext * 5]
                
                if large_files:
                    print(f"Необычно большие {ext} файлы:")
                    for file_info in large_files[:3]:  # Показываем первые 3
                        ratio = file_info['size_bytes'] / avg_size_ext
                        print(f"  {file_info['size_human']:>10} - {file_info['file']} "
                              f"({ratio:.1f}x больше среднего)")
                    print()
        
        return sizes
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return None

if __name__ == "__main__":
    analyze_file_sizes()