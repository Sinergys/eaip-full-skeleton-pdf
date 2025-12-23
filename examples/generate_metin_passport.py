"""
Пример использования функции generate_energy_passport для генерации энергопаспорта Метин Ирода.
"""
from pathlib import Path
import sys

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.reports.energy_passport import generate_energy_passport

# Пути к файлам
template_path = Path("data/source_files/audit_sinergys/Энергопаспорт Метин Ирода_с_объемами_и_месяцами.xlsx")
output_path = Path("test_output_metin/generated_passport.xlsx")

# Тестовые данные предприятия
enterprise_data = {
    "id": "metin-iroda",
    "name": "Метин Ирода",
    "inn": "123456789",
}

# Данные о здании
building_data = {
    "area_m2": 5000.0,  # 5000 м²
}

# Агрегированные данные (пример)
aggregated_data = {
    "resources": {
        "gas": {
            "2022-Q1": {
                "year": 2022,
                "quarter": 1,
                "months": [
                    {"month": "Январь", "values": {"volume_m3": 2500.0}},
                    {"month": "Февраль", "values": {"volume_m3": 2400.0}},
                    {"month": "Март", "values": {"volume_m3": 2600.0}},
                ],
                "quarter_totals": {"volume_m3": 7500.0},
            },
            "2022-Q2": {
                "year": 2022,
                "quarter": 2,
                "months": [
                    {"month": "Апрель", "values": {"volume_m3": 2200.0}},
                    {"month": "Май", "values": {"volume_m3": 2100.0}},
                    {"month": "Июнь", "values": {"volume_m3": 2300.0}},
                ],
                "quarter_totals": {"volume_m3": 6600.0},
            },
            "2022-Q3": {
                "year": 2022,
                "quarter": 3,
                "months": [
                    {"month": "Июль", "values": {"volume_m3": 2000.0}},
                    {"month": "Август", "values": {"volume_m3": 1900.0}},
                    {"month": "Сентябрь", "values": {"volume_m3": 2100.0}},
                ],
                "quarter_totals": {"volume_m3": 6000.0},
            },
            "2022-Q4": {
                "year": 2022,
                "quarter": 4,
                "months": [
                    {"month": "Октябрь", "values": {"volume_m3": 2400.0}},
                    {"month": "Ноябрь", "values": {"volume_m3": 2500.0}},
                    {"month": "Декабрь", "values": {"volume_m3": 2600.0}},
                ],
                "quarter_totals": {"volume_m3": 7500.0},
            },
            "2023-Q1": {
                "year": 2023,
                "quarter": 1,
                "months": [
                    {"month": "Январь", "values": {"volume_m3": 4800.0}},
                    {"month": "Февраль", "values": {"volume_m3": 5100.0}},
                    {"month": "Март", "values": {"volume_m3": 4919.0}},
                ],
                "quarter_totals": {"volume_m3": 14819.0},  # Должно быть 14.819 тыс. м³
            },
            "2023-Q2": {
                "year": 2023,
                "quarter": 2,
                "months": [
                    {"month": "Апрель", "values": {"volume_m3": 4500.0}},
                    {"month": "Май", "values": {"volume_m3": 4400.0}},
                    {"month": "Июнь", "values": {"volume_m3": 4600.0}},
                ],
                "quarter_totals": {"volume_m3": 13500.0},
            },
            "2023-Q3": {
                "year": 2023,
                "quarter": 3,
                "months": [
                    {"month": "Июль", "values": {"volume_m3": 4200.0}},
                    {"month": "Август", "values": {"volume_m3": 4100.0}},
                    {"month": "Сентябрь", "values": {"volume_m3": 4300.0}},
                ],
                "quarter_totals": {"volume_m3": 12600.0},
            },
            "2023-Q4": {
                "year": 2023,
                "quarter": 4,
                "months": [
                    {"month": "Октябрь", "values": {"volume_m3": 4700.0}},
                    {"month": "Ноябрь", "values": {"volume_m3": 4800.0}},
                    {"month": "Декабрь", "values": {"volume_m3": 4900.0}},
                ],
                "quarter_totals": {"volume_m3": 14400.0},
            },
        },
        "electricity": {
            "2022-Q1": {
                "year": 2022,
                "quarter": 1,
                "quarter_totals": {"active_kwh": 100000.0, "reactive_kvarh": 50000.0},
            },
        },
    }
}

if __name__ == "__main__":
    print("=" * 80)
    print("ГЕНЕРАЦИЯ ЭНЕРГОПАСПОРТА МЕТИН ИРОДА")
    print("=" * 80)
    print(f"Шаблон: {template_path}")
    print(f"Выходной файл: {output_path}")
    print()
    
    try:
        result_path = generate_energy_passport(
            enterprise_id=enterprise_data["id"],
            year=2023,
            template_path=template_path,
            output_path=output_path,
            aggregated_data=aggregated_data,
            enterprise_data=enterprise_data,
            building_data=building_data,
        )
        
        print(f"✅ Энергопаспорт успешно сгенерирован: {result_path}")
        print()
        print("Проверьте следующие значения:")
        print("  - E32 (2023 Q1 газ): должно быть 14.819 тыс. м³")
        print("  - Годовой газ 2022: 27.6 тыс. м³ (7.5 + 6.6 + 6.0 + 7.5)")
        print("  - Годовой газ 2023: 55.319 тыс. м³ (14.819 + 13.5 + 12.6 + 14.4)")
        print("  - Удельный расход газа на м²: рассчитан автоматически")
        print("  - Электроэнергия по видам продукции: заполнена")
        
    except Exception as e:
        print(f"❌ Ошибка при генерации: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

