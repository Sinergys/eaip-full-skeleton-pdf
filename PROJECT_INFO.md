# 📍 EAIP Project Location

**Новое расположение:** `C:\eaip\` ✨

**Дата переноса:** 2025-11-10  
**Старое расположение:** `C:\Users\DELL\Downloads\eaip_full_skeleton_cursor_ready\`

---

## ⚡ Быстрый старт

### Командная строка
```powershell
# Перейти в проект
cd C:\eaip

# Открыть в редакторе
code .  # VS Code
cursor .  # Cursor

# Запустить сервис
cd eaip_full_skeleton\services\ingest
uvicorn main:app --reload --port 8001
```

### Батники (в корне проекта)
- `quick_start.bat` — интерактивное меню
- `open_project.bat` — открыть в Cursor/VS Code

---

## 📂 Структура проекта

```
C:\eaip\
├── data/                          # Данные проекта
│   ├── source_files/             # Исходные файлы (НЕ в git)
│   │   ├── audit_sinergys/       # 9 файлов: pererashod, otoplenie, gaz...
│   │   └── metin/                # aggregated_energy_2022_2024.json
│   ├── aggregated/               # Результаты агрегации
│   └── README.md                 # Описание структуры данных
├── docs/                          # Документация
│   ├── STAGE2_CONTEXT_PROMPT.md  # Контекст для нового сеанса
│   ├── STAGE2_PROGRESS.md        # Прогресс Stage 2
│   └── STAGE2_ACTION_PLAN.md     # План действий
├── eaip_full_skeleton/           # Основной код
│   └── services/
│       ├── ingest/               # Сервис загрузки данных
│       └── reports/              # Сервис генерации отчётов
├── tools/                         # Утилиты
│   └── fill_energy_passport.py   # Заполнение паспорта
├── scripts/                       # Вспомогательные скрипты
│   └── test_data_paths.py        # Проверка путей
└── templates/                     # Шаблоны
    └── pcm690/                    # Шаблоны ПКМ №690
```

---

## 🎯 Текущий этап

**Stage 2:** PCM №690 Templates  
**Статус:** В работе

**Завершённые функции:**
- ✅ Парсинг категорий потребления (pererashod.xlsx)
- ✅ Функции `aggregate_usage_categories()` и `distribute_categories_by_quarter()`
- ✅ **Intelligent Router** - автоматический анализ и маршрутизация файлов
- ✅ **Переключатель режимов** - debug/production для обработки дубликатов
- ✅ **Улучшенная обработка изображений** - OCR анализ для JPG/PNG

**Следующий шаг:**
- 🔄 Добавить парсинг тепловой энергии (otoplenie.xlsx)
- 🔄 Интегрировать газ, воду, другие ресурсы

---

## 🔗 Ссылки

- **Главный документ:** [STAGE2_CONTEXT_PROMPT.md](docs/STAGE2_CONTEXT_PROMPT.md)
- **Прогресс:** [STAGE2_PROGRESS.md](docs/STAGE2_PROGRESS.md)
- **План:** [DEVELOPMENT_PLAN_2025.md](DEVELOPMENT_PLAN_2025.md)

---

## ⚙️ Преимущества нового расположения

✅ **Короткий путь:** 7 символов вместо 55  
✅ **Быстрый доступ:** `cd C:\eaip`  
✅ **Нет проблем с лимитом 260 символов Windows**  
✅ **Удобнее для AI-ассистентов**

---

## 🆕 Последние обновления (2025-12-01)

### 🧠 Intelligent Router
- Автоматический анализ и маршрутизация файлов
- Определение типа документа, ресурса, данных
- Генерация routing map с рекомендациями
- См. `docs/INTELLIGENT_ROUTER_IMPLEMENTATION.md`

### 🔧 Переключатель режимов работы
- **DEBUG:** всегда переобрабатывать файлы (для разработки)
- **PRODUCTION:** пропускать файлы без изменений (для работы)
- Доступен в веб-интерфейсе на странице загрузки
- См. `docs/SYSTEM_MODE_SWITCH.md`

### 🖼️ Улучшенная обработка изображений
- Правильное определение типа документа для JPG/PNG
- Анализ OCR-текста для определения ресурса
- Повышенная точность классификации показаний счетчиков
- См. `docs/IMAGE_PROCESSING_IMPROVEMENTS.md`

**Подробности:** [PROJECT_UPDATE_2025_12_01.md](docs/PROJECT_UPDATE_2025_12_01.md)

---

**Последнее обновление:** 2025-12-01

