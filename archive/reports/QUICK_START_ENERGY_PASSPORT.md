# Быстрый старт: Генерация энергопаспорта

## Использование

```python
from pathlib import Path
from services.reports.energy_passport import generate_energy_passport

# Пути
template_path = Path("data/source_files/audit_sinergys/Энергопаспорт Метин Ирода_с_объемами_и_месяцами.xlsx")
output_path = Path("output/generated_passport.xlsx")

# Данные
aggregated_data = {
    "resources": {
        "gas": {
            "2023-Q1": {
                "year": 2023,
                "quarter": 1,
                "months": [
                    {"month": "Январь", "values": {"volume_m3": 4800.0}},
                    {"month": "Февраль", "values": {"volume_m3": 5100.0}},
                    {"month": "Март", "values": {"volume_m3": 4919.0}},
                ],
            },
        },
    }
}

enterprise_data = {"id": "metin-iroda", "name": "Метин Ирода"}
building_data = {"area_m2": 5000.0}

# Генерация
result = generate_energy_passport(
    enterprise_id="metin-iroda",
    year=2023,
    template_path=template_path,
    output_path=output_path,
    aggregated_data=aggregated_data,
    enterprise_data=enterprise_data,
    building_data=building_data,
)

print(f"Паспорт создан: {result}")
```

## Что заполняется автоматически

1. **Лист "Структура пр 2":**
   - Газ по кварталам (из помесячных данных, в тысячах м³)
   - Разбивка газа: собственные нужды (432 м³/мес) и хоз-быт
   - Электроэнергия по видам продукции (5 видов)
   - Электроэнергия активная/реактивная

2. **Лист "Удельный расход газа":**
   - Удельный расход на 1 м² здания
   - Удельный расход на условную единицу продукции
   - Отклонения от нормативов

## Важные моменты

- ✅ Газ рассчитывается из помесячных данных (гарантирует правильность сумм)
- ✅ Значения газа записываются в тысячах м³
- ✅ Формулы в шаблоне сохраняются
- ✅ E32 (2023 Q1 газ) = 14.819 (рассчитывается из 4800+5100+4919 м³)

## Пример

См. `examples/generate_metin_passport.py` для полного примера.

