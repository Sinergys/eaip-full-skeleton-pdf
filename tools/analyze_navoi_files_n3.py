#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ файлов по Навои для шага N3.0
Группировка файлов по типам и определение статуса (новый/ранее учтён)
"""

import json
import re
from collections import defaultdict
from pathlib import Path

# Файлы, уже учтённые в N1.1 и N1R.1
KNOWN_FILES_N1 = [
    "Навоий ИЭС потери по теплосети.xlsx",
    "ЦЦР паспорт здании.xlsx",
    "акт баланс Навоий 2020-2025.rar",
    "газ 1-квнавои ТЭС.docx",
    "ГСМ Новаий ТЭС.docx",
    "Атмосфера маълумоти 3 йиллик.docx",
    "Автотранспорт_цехи_тўғрисида_МАЪЛУМОТ.docx",
    "ИТЦ қувурлари хақида маълумот.docx",
    "Маълумот газ қувури ва ГРПлар.docx",
    "комрессор атлос копко.docx",
    "2022-2024 темир йёл.PDF",
    "2025 YIL BOSH REJA.PDF",
]

KNOWN_FILES_N1R = [
    "01 01 2023 31 07 2023.xls",
    "10.30 -01 01 2024 31 12 2024 г.xls",
    "10.30 -01 08 2023 31 12 2023 г.xls",
]

def normalize_filename(name):
    """Нормализация имени файла для сравнения"""
    return name.strip().lower()

def categorize_file(name, path):
    """Определение категории файла по имени и пути"""
    name_lower = name.lower()
    path_lower = path.lower()
    
    # Акты балансов
    if 'акт баланс' in name_lower or 'акт бал' in name_lower:
        return "Акты балансов по месяцам"
    
    # Отчёты по месяцам (xisoboti)
    if 'xisoboti' in name_lower or 'хисоботи' in name_lower:
        return "Отчёты по потреблению (ежемесячные)"
    
    # Данные по узлам учёта
    if '10.30' in name or 'уз' in name_lower:
        return "Данные коммерческого учёта электроэнергии"
    
    # Газ
    if 'газ' in name_lower or 'газ' in path_lower:
        return "Данные по газу"
    
    # Выработка, реализация
    if 'реализация' in name_lower or 'выработка' in name_lower:
        return "Данные по продукции (выработка энергии)"
    
    # Нормативы
    if 'норматив' in name_lower or 'норма' in name_lower:
        return "Нормативные показатели"
    
    # Прогнозы
    if 'прогноз' in name_lower:
        return "Прогнозные данные"
    
    # Счёт-фактуры
    if 'faktura' in name_lower or 'счёт фактура' in name_lower or 'счет фактура' in name_lower:
        return "Счёт-фактуры"
    
    # Акты выполненных работ
    if 'акт выполненных работ' in name_lower or 'акт выполненных работ' in path_lower:
        return "Акты выполненных работ"
    
    # Программы энергоаудита
    if 'программа' in name_lower and 'энергоаудит' in name_lower:
        return "Программы энергоаудита"
    
    # Энергопаспорт
    if 'энергопаспорт' in name_lower or 'зэп' in name_lower:
        return "Энергопаспорт (готовый документ)"
    
    # Спецификации оборудования
    if 'спецификация' in name_lower or 'specification' in path_lower:
        return "Спецификации оборудования"
    
    # Проектная документация (HVAC, схемы)
    if 'hvac' in path_lower or 'схема' in name_lower:
        return "Проектная документация (HVAC, схемы)"
    
    # ХВО (химводоочистка)
    if 'хво' in name_lower:
        return "Данные по системе ХВО (химводоочистка)"
    
    # Потери
    if 'потери' in name_lower or 'потерия' in name_lower:
        return "Данные по потерям энергии"
    
    # Хозяйственные нужды
    if 'хоз' in name_lower or 'хозяйственн' in name_lower:
        return "Данные по хозяйственно-бытовым нуждам"
    
    # Ремонтные работы
    if 'таьмир' in name_lower or 'ремонт' in name_lower:
        return "Данные по ремонтным работам и затратам"
    
    # Балансы, сводные данные
    if 'баланс' in name_lower and 'акт' not in name_lower:
        return "Сводные балансы и отчёты"
    
    # Нормативные документы (РД, правила)
    if name_lower.startswith('рд') or 'правил' in name_lower:
        return "Нормативные документы (РД, правила)"
    
    # Общие отчёты
    if 'отчёт' in name_lower or 'отчет' in name_lower:
        return "Итоговые отчёты"
    
    return "Прочие файлы"

def main():
    # Загрузка списка файлов
    with open('temp_navoi_files_n3.json', 'r', encoding='utf-8') as f:
        files = json.load(f)
    
    print(f"Всего файлов загружено: {len(files)}")
    
    # Нормализация известных файлов
    known_normalized = set()
    for f in KNOWN_FILES_N1 + KNOWN_FILES_N1R:
        known_normalized.add(normalize_filename(f))
    
    # Группировка по типам
    by_type = defaultdict(list)
    
    for f in files:
        name = f.get('Name', '')
        path = f.get('FullName', '')
        ext = f.get('Extension', '')
        
        # Определение статуса
        status = "ранее учтён" if normalize_filename(name) in known_normalized else "новый"
        
        # Категоризация
        file_type = categorize_file(name, path)
        
        by_type[file_type].append({
            'name': name,
            'ext': ext,
            'path': path,
            'status': status
        })
    
    # Формирование результата
    result = []
    
    for file_type, file_list in sorted(by_type.items()):
        # Сортировка: сначала новые, потом ранее учтённые
        file_list.sort(key=lambda x: (x['status'] == 'ранее учтён', x['name']))
        
        # Для типов с большим количеством файлов - агрегирование
        if len(file_list) > 20:
            # Разделение на новые и ранее учтённые
            new_files = [f for f in file_list if f['status'] == 'новый']
            known_files = [f for f in file_list if f['status'] == 'ранее учтён']
            
            # Примеры новых файлов
            examples_new = new_files[:5]
            examples_known = known_files[:3] if known_files else []
            
            # Агрегированная запись
            result.append({
                'type': file_type,
                'files': examples_new + examples_known,
                'total_new': len(new_files),
                'total_known': len(known_files),
                'note': f"Всего: {len(file_list)} файлов ({len(new_files)} новых, {len(known_files)} ранее учтённых)"
            })
        else:
            result.append({
                'type': file_type,
                'files': file_list,
                'total_new': len([f for f in file_list if f['status'] == 'новый']),
                'total_known': len([f for f in file_list if f['status'] == 'ранее учтён']),
                'note': None
            })
    
    # Сохранение результата
    with open('temp_navoi_analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nТипов файлов: {len(result)}")
    print("\nТипы файлов:")
    for item in result:
        print(f"  - {item['type']}: {len(item['files'])} примеров (новых: {item['total_new']}, учтённых: {item['total_known']})")
    
    print("\nРезультат сохранён в temp_navoi_analysis_result.json")

if __name__ == '__main__':
    main()

