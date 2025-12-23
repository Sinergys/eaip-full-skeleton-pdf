# ✅ Отчет об интеграции нового шаблона Excel

## 🎯 Выполненные задачи

### 1. ✅ Сохранение старого шаблона
- Старый шаблон `energy_passport_template.xlsx` сохранен как `template_metin.xlsx`
- Расположение: `templates/pcm690/template_metin.xlsx`
- Скрипт: `scripts/copy_template.py`

### 2. ✅ Добавление нового шаблона
- Новый шаблон скопирован из `C:\Users\DELL\Downloads\Telegram Desktop\энергопаспорт (3) (10) (2).xlsx`
- Сохранен как: `templates/pcm690/new_energy_passport.xlsx`

### 3. ✅ Создание файла конфигурации
- Создан файл: `templates/pcm690/templates_config.py`
- Реализованы функции:
  - `get_template_path(template_name)` - получение пути к шаблону по имени
  - `list_available_templates()` - список доступных шаблонов
  - `register_template(name, file_path)` - регистрация нового шаблона

### 4. ✅ Реализация выбора шаблона
- Обновлен `tools/fill_energy_passport.py`:
  - Добавлен параметр `--template-name` для выбора шаблона по имени
  - Сохранена обратная совместимость с `--template` (путь к файлу)
  - Интеграция с `templates_config.py`

### 5. ✅ Обновление API endpoint
- Обновлен `eaip_full_skeleton/services/ingest/main.py`:
  - Endpoint `/api/generate-passport/{batch_id}` теперь принимает параметр `template_name`
  - Поддержка выбора шаблона через Query параметр
  - Fallback на дефолтный шаблон, если имя не указано или не найдено

### 6. ✅ Вспомогательная функция
- Создан `tools/generate_passport.py`:
  - Функция `generate_passport()` с поддержкой выбора шаблона
  - Удобный интерфейс для генерации паспортов из кода

### 7. ✅ Документация
- Создан `templates/pcm690/README_TEMPLATES.md`:
  - Руководство по использованию шаблонов
  - Примеры использования через CLI и API
  - Инструкции по регистрации новых шаблонов

---

## 📋 Зарегистрированные шаблоны

| Имя шаблона | Алиасы | Файл | Описание |
|-------------|--------|------|----------|
| `new_energy_passport` | `new` | `new_energy_passport.xlsx` | Новый шаблон энергопаспорта |
| `metin` | `template_metin` | `template_metin.xlsx` | Старый шаблон (Metin) |
| `default` | `energy_passport_template` | `energy_passport_template.xlsx` | Дефолтный шаблон |

---

## 🚀 Примеры использования

### Через командную строку

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
```

### Через API

```bash
# Генерация с новым шаблоном
curl -X POST "http://localhost:8001/api/generate-passport/{batch_id}?template_name=new_energy_passport"

# Генерация со старым шаблоном (Metin)
curl -X POST "http://localhost:8001/api/generate-passport/{batch_id}?template_name=metin"

# Генерация с дефолтным шаблоном
curl -X POST "http://localhost:8001/api/generate-passport/{batch_id}"
```

### Через Python код

```python
from tools.generate_passport import generate_passport
from pathlib import Path

# Генерация с новым шаблоном
generate_passport(
    aggregated_data=aggregated,
    enterprise_data=enterprise,
    output_path=Path("output/passport.xlsx"),
    template_name="new_energy_passport"
)
```

---

## 📂 Структура файлов

```
templates/pcm690/
├── templates_config.py          # ✅ Конфигурация шаблонов
├── new_energy_passport.xlsx     # ✅ Новый шаблон
├── template_metin.xlsx          # ✅ Старый шаблон (Metin)
├── energy_passport_template.xlsx # Дефолтный шаблон
└── README_TEMPLATES.md          # ✅ Документация

tools/
├── fill_energy_passport.py      # ✅ Обновлен (поддержка --template-name)
└── generate_passport.py          # ✅ Новая функция

scripts/
└── copy_template.py             # ✅ Скрипт копирования шаблона

eaip_full_skeleton/services/ingest/
└── main.py                      # ✅ Обновлен API endpoint
```

---

## ✅ Проверка работоспособности

### Тест 1: Проверка конфигурации

```python
from templates.pcm690.templates_config import get_template_path, list_available_templates

# Получить путь к новому шаблону
path = get_template_path("new_energy_passport")
print(f"Новый шаблон: {path}")

# Список доступных шаблонов
templates = list_available_templates()
print(f"Доступные шаблоны: {templates}")
```

### Тест 2: Генерация через CLI

```bash
python tools/fill_energy_passport.py \
  --template-name new_energy_passport \
  --aggregated data/aggregated/test.json \
  --output test_output.xlsx
```

### Тест 3: Генерация через API

```bash
# Проверить доступность endpoint
curl http://localhost:8001/api/generate-passport/{batch_id}?template_name=new_energy_passport
```

---

## 🔧 Дополнительные возможности

### Регистрация нового шаблона

```python
from templates.pcm690.templates_config import register_template

# Регистрация нового шаблона
register_template("custom_template", "my_custom_template.xlsx")
```

### Получение списка шаблонов

```python
from templates.pcm690.templates_config import list_available_templates

templates = list_available_templates()
for name, path in templates.items():
    print(f"{name}: {path}")
```

---

## 📝 Примечания

1. **Обратная совместимость**: Старый параметр `--template` (путь к файлу) все еще поддерживается
2. **Дефолтное поведение**: Если `template_name` не указан, используется дефолтный шаблон
3. **Обработка ошибок**: Система автоматически проверяет существование файлов и выдает понятные ошибки
4. **Логирование**: Все операции с шаблонами логируются для отладки

---

## ✅ Статус: ГОТОВО

Все задачи выполнены:
- ✅ Старый шаблон сохранен
- ✅ Новый шаблон добавлен
- ✅ Конфигурация создана
- ✅ Выбор шаблона реализован
- ✅ API обновлен
- ✅ Документация создана

**Система готова к использованию нового шаблона!** 🎉

