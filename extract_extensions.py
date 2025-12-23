#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для извлечения расширений файлов из deepseek_payload.json
"""
import json
import re
from collections import Counter

def extract_extensions():
    """Извлекает расширения файлов из JSON"""
    try:
        with open('deepseek_payload.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        extensions = []
        file_ids = []
        
        for item in data:
            if 'file_id' in item:
                file_id = item['file_id']
                file_ids.append(file_id)
                
                # Извлекаем расширение
                if '.' in file_id:
                    extension = file_id.split('.')[-1].lower()
                    extensions.append(extension)
        
        # Подсчитываем расширения
        extension_counts = Counter(extensions)
        
        print(f"=== АНАЛИЗ РАСШИРЕНИЙ ФАЙЛОВ ===")
        print(f"Общее количество файлов: {len(file_ids)}")
        print(f"Обнаружено уникальных расширений: {len(extension_counts)}")
        print()
        
        print("=== РАСПРЕДЕЛЕНИЕ ПО РАСШИРЕНИЯМ ===")
        for ext, count in extension_counts.most_common():
            percentage = (count / len(file_ids)) * 100
            print(f"{ext:>8}: {count:>3} файлов ({percentage:5.1f}%)")
        
        print()
        print("=== СПИСОК РАСШИРЕНИЙ (алфавитный) ===")
        for ext in sorted(extension_counts.keys()):
            print(ext)
        
        print()
        print("=== ПРИМЕРЫ ФАЙЛОВ ПО РАСШИРЕНИЯМ ===")
        examples = {}
        for item in data:
            if 'file_id' in item:
                file_id = item['file_id']
                if '.' in file_id:
                    ext = file_id.split('.')[-1].lower()
                    if ext not in examples:
                        examples[ext] = []
                    if len(examples[ext]) < 3:  # Максимум 3 примера
                        examples[ext].append(file_id)
        
        for ext in sorted(examples.keys()):
            print(f"{ext}:")
            for example in examples[ext]:
                print(f"  - {example}")
            print()
        
        return extension_counts, file_ids
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return None, None

if __name__ == "__main__":
    extract_extensions()