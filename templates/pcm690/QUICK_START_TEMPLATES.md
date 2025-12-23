# 🚀 Быстрый старт: Использование шаблонов

## Выбор шаблона при генерации паспорта

### Через API (рекомендуется)

```bash
# Новый шаблон
POST /api/generate-passport/{batch_id}?template_name=new_energy_passport

# Старый шаблон (Metin)
POST /api/generate-passport/{batch_id}?template_name=metin

# Дефолтный шаблон
POST /api/generate-passport/{batch_id}
```

### Через командную строку

```bash
# Новый шаблон
python tools/fill_energy_passport.py \
  --template-name new_energy_passport \
  --aggregated data.json \
  --output passport.xlsx

# Старый шаблон
python tools/fill_energy_passport.py \
  --template-name metin \
  --aggregated data.json \
  --output passport.xlsx
```

## Доступные шаблоны

- `new_energy_passport` или `new` - Новый шаблон
- `metin` или `template_metin` - Старый шаблон (Metin)
- `default` или `energy_passport_template` - Дефолтный шаблон

## Проверка доступных шаблонов

```python
from templates.pcm690.templates_config import list_available_templates

templates = list_available_templates()
print(templates)
```

