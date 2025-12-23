# PCM №690 Templates

Конфигурация шаблонов находится в `templates_config.py`. Подробное руководство см. в `README_TEMPLATES.md`.

## Доступные шаблоны

- **`metin.xlsx`** (по умолчанию) — шаблон с кириллическими названиями листов ("Структура пр 2", "Баланс", "Узел учета" и т.д.)
- **`new_energy_passport.xlsx`** — новый шаблон
- **`energy_passport_template.xlsx`** — дефолтный шаблон (fallback)

## Использование

Шаблоны выбираются по имени через параметр `template_name` в API:

```bash
POST /api/generate-passport/{batch_id}?template_name=metin
```

Если `template_name` не указан, используется шаблон `"metin"` по умолчанию.

## Конфигурация

Все шаблоны регистрируются в `templates_config.py` через `TEMPLATE_MAPPING`. Для добавления нового шаблона см. `README_TEMPLATES.md`.
