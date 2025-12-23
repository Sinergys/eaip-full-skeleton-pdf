# 📋 Руководство по использованию шаблонов энергопаспортов

## 🎯 Доступные шаблоны

Система поддерживает несколько шаблонов энергопаспортов. Выбор шаблона осуществляется через имя в конфигурации.

### Зарегистрированные шаблоны:

1. **`new_energy_passport`** (или `new`)
   - Новый шаблон энергопаспорта
   - Файл: `new_energy_passport.xlsx`

2. **`metin`** (или `template_metin`)
   - Старый шаблон (Metin) с кириллическими названиями листов
   - Файл: `metin.xlsx`
   - Листы: "Структура пр 2", "Баланс", "Узел учета ", "03_Оборудование", "Динамика ср", "мазут,уголь 5 ", "паспорт здание ", "Расход  на ед.п", "Мероприятия", "Объемы продукции", "Продукция"

3. **`default`** (или `energy_passport_template`)
   - Дефолтный шаблон
   - Файл: `energy_passport_template.xlsx`

## 📝 Использование

### Через командную строку (fill_energy_passport.py)

```bash
# Использование нового шаблона
python tools/fill_energy_passport.py \
  --template-name new_energy_passport \
  --aggregated data/aggregated/aggregated_full_resources_2022_2024.json \
  --output output/passport.xlsx

# Использование старого шаблона (Metin)
python tools/fill_energy_passport.py \
  --template-name metin \
  --aggregated data/aggregated/aggregated_full_resources_2022_2024.json \
  --output output/passport_metin.xlsx

# Использование дефолтного шаблона
python tools/fill_energy_passport.py \
  --template-name default \
  --aggregated data/aggregated/aggregated_full_resources_2022_2024.json \
  --output output/passport_default.xlsx
```

### Через API (ingest service)

```bash
# Генерация с новым шаблоном
curl -X POST "http://localhost:8001/api/generate-passport/{batch_id}?template_name=new_energy_passport"

# Генерация со старым шаблоном (Metin)
curl -X POST "http://localhost:8001/api/generate-passport/{batch_id}?template_name=metin"

# Генерация с дефолтным шаблоном (если template_name не указан, используется "metin" по умолчанию)
curl -X POST "http://localhost:8001/api/generate-passport/{batch_id}"
```

### Через Python код

```python
from pathlib import Path
import sys

# Добавляем путь к templates_config
templates_config_path = Path("templates/pcm690")
sys.path.insert(0, str(templates_config_path))

from templates_config import get_template_path, list_available_templates

# Получить путь к шаблону по имени
template_path = get_template_path("new_energy_passport")
print(f"Шаблон: {template_path}")

# Список всех доступных шаблонов
available = list_available_templates()
print(f"Доступные шаблоны: {available}")
```

## 🔧 Регистрация нового шаблона

Для добавления нового шаблона:

1. Поместите файл шаблона в директорию `templates/pcm690/`
2. Зарегистрируйте его в коде:

```python
from templates_config import register_template

# Регистрация нового шаблона
register_template("my_custom_template", "my_template.xlsx")
```

Или отредактируйте `templates_config.py` напрямую:

```python
TEMPLATE_MAPPING: Dict[str, Path] = {
    # ... существующие шаблоны ...
    "my_custom_template": TEMPLATES_DIR / "my_template.xlsx",
}
```

## 📂 Структура файлов

```
templates/pcm690/
├── templates_config.py          # Конфигурация шаблонов
├── new_energy_passport.xlsx     # Новый шаблон
├── metin.xlsx                   # Старый шаблон (Metin) - используется по умолчанию
├── energy_passport_template.xlsx # Дефолтный шаблон (fallback)
└── README_TEMPLATES.md          # Это руководство
```

## ⚠️ Важные замечания

1. **Обратная совместимость**: Старый параметр `--template` (путь к файлу) все еще поддерживается, но рекомендуется использовать `--template-name`

2. **Проверка существования**: Система автоматически проверяет существование файла шаблона. Если файл не найден, будет выброшено исключение

3. **Дефолтный шаблон**: Если `template_name` не указан или указана пустая строка, используется шаблон `"metin"` по умолчанию. Если `metin` недоступен, используется дефолтный шаблон из списка кандидатов

4. **Регистрация**: Все шаблоны должны быть зарегистрированы в `TEMPLATE_MAPPING` для использования по имени

## 🔍 Отладка

Для проверки доступных шаблонов:

```python
from templates_config import list_available_templates

templates = list_available_templates()
for name, path in templates.items():
    print(f"{name}: {path}")
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте, что файл шаблона существует в `templates/pcm690/`
2. Убедитесь, что шаблон зарегистрирован в `templates_config.py`
3. Проверьте логи для детальной информации об ошибках

