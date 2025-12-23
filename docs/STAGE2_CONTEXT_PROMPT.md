# 🚀 Stage 2 — Промт для нового сеанса

**Дата создания:** 2025-11-10  
**Проект:** EAIP (Energy Audit Integration Platform)  
**Текущий этап:** Stage 2 — PCM №690 Templates

---

## 📍 Текущее состояние проекта

### ✅ Stage 1 — ЗАВЕРШЁН (2025-11-09)
- Цепочка **upload → parse → edit → save** работает через веб-интерфейс (`/web/upload`, `/web/results`).
- База SQLite (`ingest_data.db`) с таблицами `enterprises`, `uploads`, `parsed_data`.
- API endpoints: `/api/uploads/{batch_id}`, `/api/uploads/{batch_id}/editable`, `/ingest/parse/{batch_id}`.
- Автоматическая агрегация при загрузке файлов (`services/ingest/utils/energy_aggregator.py`).
- Smoke-test пройден, баг пустых полей на `/web/results` устранён.

### 🔄 Stage 2 — В РАБОТЕ
**Цель:** Создать нормативные шаблоны для энергопаспорта (Excel) и отчёта (Word) по ПКМ №690 Узбекистана с автоматическим заполнением данных.

**Ключевые документы:**
- **План:** `docs/STAGE2_ACTION_PLAN.md` — 7 шагов с оценками времени AI-работы (не календарные даты!)
- **Прогресс:** `docs/STAGE2_PROGRESS.md` — уже выполненные задачи (структура листов, узлы учёта, потери трансформатора)
- **Mapping:** `docs/METIN_passport_mapping.md` — сопоставление данных из JSON с листами энергопаспорта
- **Контекст Stage 2 (актуальное):**
  - Веб-форма загрузки: единое поле предприятия (datalist) и выпадающий список «Вид энергоресурса» (электроэнергия, газ, тепло, вода, топливо, оборудование, ограждающие конструкции, узлы учёта, прочее).
  - Дедупликация загрузок: совпадение имени, размера и SHA-1 возвращает уже существующий пакет.
  - `fill_energy_passport.py` автоматически заполняет `Equipment`, `02_Исходные данные`, `01_Узлы учета`; парсеры `ograjdayuschie_konstrukcii.xlsx`, `oborudovanie.xlsx`, `schetchiki.xlsx` формируют JSON.
  - Страница `/web/results`: сводка в одну строку, «сырые данные» загружаются по требованию, отображается выбранный ресурс.

---

## 🎯 Задачи Stage 2 (по приоритету)

### Шаг 1: Распределение потребления по видам нужд (~3-4ч AI)
- Проанализировать `pererashod.xlsx`, `otoplenie.xlsx`, `edenic na kvt.xlsx` (в `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\`).
- Определить колонки с категориями: технологические, собственные нужды, производственные, хоз-бытовые.
- Расширить `services/ingest/utils/energy_aggregator.py` функцией `aggregate_by_usage_type()`.
- Формировать JSON с поквартальными суммами по каждой категории:
  ```json
  {
    "electricity": {
      "2022-Q1": {
        "quarter_totals": {"active_kwh": 123456},
        "by_usage": {
          "technological": 80000,
          "own_needs": 20000,
          "production": 15000,
          "household": 8456
        }
      }
    }
  }
  ```

### Шаг 2: Дополнить агрегатор другими ресурсами (~2-3ч AI)
- Добавить парсинг тепловой энергии (`otoplenie.xlsx` → лист `Тепло`).
- Добавить мазут/топливо (если листы есть в исходниках).
- Расширить `_compute_quarter_totals()` для всех ресурсов.

### Шаг 3: Интегрировать ограждающие конструкции (~2ч AI)
- Парсить `ograjdayuschie_konstrukcii.xlsx` (стены, окна, крыша, пол).
- Создать `services/ingest/utils/building_envelope_parser.py`.
- Записывать JSON `{batch_id}_envelope.json` в `AGGREGATED_DIR`.

### Шаг 4: Расширить `fill_energy_passport.py` (~4-5ч AI)
- Добавить функции `fill_balans_sheet()`, `fill_dinamika_sheet()`, `fill_meropriyatiya_sheet()`.
- Заполнять листы `Balans`, `Dinamika sr`, `Meropriyatiya` формулами и данными из JSON.
- Убедиться, что нет ошибок `#REF!` в Excel.

### Шаг 5: Word-отчёт с диаграммами (~3-4ч AI)
- Создать `tools/fill_energy_audit_report.py`.
- Заменять placeholder'ы (`{{enterprise.name}}` и т.д.) на данные из JSON.
- Генерировать диаграммы (matplotlib) и вставлять в Word.

### Шаг 6: API интеграция (опционально, ~2ч AI)
- Добавить в `services/reports/main.py` endpoints:
  - `POST /reports/energy-passport` → генерирует заполненный Excel
  - `POST /reports/energy-audit` → генерирует заполненный Word

### Шаг 7: Документация и финализация (~2-3ч AI)
- Обновить `DEVELOPMENT_PLAN_2025.md`, `STAGE2_PROGRESS.md`, `README.md`.
- Создать `docs/STAGE2_TESTING_CHECKLIST.md`.
- Записать видео-демо (если требуется).

---

## 📂 Структура проекта (ключевые файлы)

```
eaip_full_skeleton_cursor_ready/
├── DEVELOPMENT_PLAN_2025.md          # Общий план Q4 2025
├── docs/
│   ├── STAGE1_OBSERVATIONS.md        # Smoke-test Stage 1 ✅
│   ├── STAGE2_ACTION_PLAN.md         # Детальный план Stage 2 🔄
│   ├── STAGE2_PROGRESS.md            # Прогресс Stage 2
│   ├── METIN_passport_mapping.md     # Mapping данных для паспорта
│   └── PCM690_TEMPLATE_PLAN.md       # План шаблонов ПКМ №690
├── eaip_full_skeleton/
│   ├── services/ingest/
│   │   ├── main.py                   # FastAPI app (upload/parse/edit/save)
│   │   ├── database.py               # SQLite (enterprises, uploads, parsed_data)
│   │   ├── file_parser.py            # Парсинг Excel/PDF/Word
│   │   ├── utils/
│   │   │   ├── energy_aggregator.py  # Агрегация поквартальных данных
│   │   │   └── aggregation_log.py    # Логирование агрегации
│   │   └── web/
│   │       ├── upload.html           # Веб-форма загрузки
│   │       └── results.html          # Страница результатов
│   ├── services/reports/            # Сервис генерации PDF/Excel/Word
│   └── infra/data/inbox/            # Загруженные файлы
├── tools/
│   └── fill_energy_passport.py       # Заполнение шаблона паспорта
├── templates/pcm690/
│   ├── energy_passport_template.xlsx # Шаблон энергопаспорта
│   └── energy_audit_template.docx    # Шаблон отчёта
└── scripts/
    └── generate_pcm690_templates.py  # Генератор шаблонов
```

---

## 📊 Данные проекта

**Местоположение в проекте:** `data/source_files/`

### Исходные файлы (audit_sinergys/)
Все файлы скопированы в проект для удобства работы:
- `pererashod.xlsx` — перерасход по категориям
- `otoplenie.xlsx` — тепловая энергия
- `edenic na  kvt.xlsx` — удельные показатели
- `gaz.xlsx` — газ (дополнительно)
- `voda.xlsx` — вода (дополнительно)
- `kotel.xlsx` — котельная
- `ograjdayuschie_konstrukcii.xlsx` — ограждающие конструкции
- `oborudovanie.xlsx` — оборудование

### Эталонные результаты (metin/)
- `aggregated_energy_2022_2024.json` — агрегированные данные (эталон)
- `EnergyPassport_PKM690_filled.xlsx` — частично заполненный паспорт (Struktura pr2, узлы учёта, потери)

**Старое расположение (бэкап):** `C:\Users\DELL\Documents\AUDIT\`

### Использование в коде

```python
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "data" / "source_files" / "audit_sinergys"
pererashod_path = SOURCE_DIR / "pererashod.xlsx"
```

---

## 🤖 AI-модели и распределение ролей

### **GPT-5**
- Архитектура JSON-схем
- Проектирование формул для Excel
- Код-ревью критических функций

### **Claude Sonnet 4.5** (основная модель)
- Парсинг Excel (openpyxl)
- Написание Python-кода (FastAPI, pandas, python-docx)
- Анализ структуры таблиц
- Документация и инструкции

### **Claude Haiku 3.5**
- Юнит-тесты (pytest)
- Проверка корректности данных
- Обновление документации (README, CHANGELOG)

### **DeepSeek Coder V3 / Qwen 2.5 Coder**
- Оптимизация производительности
- Рефакторинг (type hints, docstrings)
- Линтинг (ruff/black)

---

## 🛠️ Технический стек

- **Backend:** Python 3.11, FastAPI, SQLite, pandas, openpyxl
- **Парсинг:** openpyxl (Excel), python-docx (Word), pdfplumber (PDF), Tesseract (OCR)
- **Генерация отчётов:** ReportLab (PDF), python-docx (Word), matplotlib (графики)
- **Инфраструктура:** Docker Compose, Prometheus, Grafana, Loki
- **Веб:** HTML/JS (без React), FastAPI static files

---

## ⚠️ Важные особенности

### PowerShell команды (Windows)
**Работа с файлами данных в проекте:**
```powershell
# Из корня проекта — используем относительные пути
python -c "import pandas as pd; df=pd.read_excel('data/source_files/audit_sinergys/pererashod.xlsx'); print(df.head())"

# Или с Path (рекомендуется в скриптах)
python -c "from pathlib import Path; import pandas as pd; path = Path('data/source_files/audit_sinergys/pererashod.xlsx'); df=pd.read_excel(path); print(df.head())"
```

**Старые абсолютные пути (если нужен доступ к оригиналам):**
```powershell
# Вариант 1: raw-string (r'...')
python -c "import pandas as pd; path=r'C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\pererashod.xlsx'; df=pd.read_excel(path); print(df.head())"

# Вариант 2: двойные слэши
python -c "import pandas as pd; path='C:\\Users\\DELL\\Documents\\AUDIT\\Audit in Sinergys\\pererashod.xlsx'; df=pd.read_excel(path); print(df.head())"
```

### SQLite база данных
**Путь:** `eaip_full_skeleton/services/ingest/ingest_data.db`

**Таблицы:**
- `enterprises` — справочник предприятий
- `uploads` — метаданные загруженных файлов (batch_id, filename, status, parsing_summary)
- `parsed_data` — raw_json и editable_text (связь upload_id → uploads.id)

**Проверка данных:**
```powershell
# Из корня eaip_full_skeleton/
python -c "import sqlite3; conn=sqlite3.connect('services/ingest/ingest_data.db'); conn.row_factory=sqlite3.Row; rows=conn.execute('SELECT batch_id, filename FROM uploads ORDER BY created_at DESC LIMIT 5').fetchall(); print('\n'.join(f'{dict(row)}' for row in rows))"
```

### Агрегация данных
**Триггер:** загрузка файлов с именем, содержащим `"потребление энергоресурсов"`, `"consumption"`, `"energy_resources"`.

**Выход:** JSON в `infra/data/inbox/aggregated/{batch_id}_aggregated.json`

**Структура:**
```json
{
  "source": "путь_к_файлу.xlsx",
  "generated_at": "2025-11-10T12:00:00Z",
  "resources": {
    "electricity": {
      "2022-Q1": {
        "year": 2022,
        "quarter": 1,
        "months": [{"month": "январь", "values": {...}}],
        "quarter_totals": {"active_kwh": 123456, "reactive_kvarh": 45678}
      }
    },
    "gas": {...},
    "water": {...},
    "production": {...}
  },
  "missing_sheets": ["Мазут"]
}
```

---

## 📝 Команды для быстрого старта

### Запуск ingest-сервиса (локально)
```powershell
cd C:\eaip\eaip_full_skeleton\services\ingest
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Веб-интерфейс:** http://localhost:8001/web/upload  
**API docs:** http://localhost:8001/docs

### Запуск через Docker Compose
```powershell
cd C:\eaip\eaip_full_skeleton\infra
docker compose up -d ingest
docker logs eaip-ingest-local --tail 50
```

### Заполнение шаблона паспорта
```powershell
python tools/fill_energy_passport.py `
  --template "C:\Users\DELL\Documents\AUDIT\METIN\EnergyPassport_PKM690_Template_v1.1.2.xlsx" `
  --aggregated "C:\Users\DELL\Documents\AUDIT\METIN\aggregated_energy_2022_2024.json" `
  --output "C:\Users\DELL\Documents\AUDIT\METIN\EnergyPassport_PKM690_filled.xlsx" `
  --loss-active-month 3200 `
  --loss-reactive-month 13600 `
  --transformer-power 630
```

---

## 🎯 С чего начать новый сеанс?

### Вариант 1: Продолжить с Шага 1 (рекомендуется)
```
Привет! Продолжаю Stage 2 проекта EAIP. Прочитай `docs/STAGE2_CONTEXT_PROMPT.md` 
и `docs/STAGE2_ACTION_PLAN.md`. Начни с Шага 1: проанализируй структуру файла 
`pererashod.xlsx` (путь: `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\pererashod.xlsx`) 
и определи колонки с категориями потребления (технологические/собственные/производственные/хоз-бытовые).
```

### Вариант 2: Продолжить с конкретного шага
```
Привет! Продолжаю Stage 2, Шаг N проекта EAIP. Контекст: `docs/STAGE2_CONTEXT_PROMPT.md`. 
Выполни задачу: [описание подзадачи из STAGE2_ACTION_PLAN.md].
```

### Вариант 3: Проверить текущее состояние
```
Привет! Покажи статус Stage 2 проекта EAIP: прочитай `docs/STAGE2_PROGRESS.md` 
и `docs/STAGE2_ACTION_PLAN.md`, выведи список выполненных и оставшихся задач.
```

---

## ✅ Критерии завершения Stage 2

- [ ] Агрегатор поддерживает 5+ ресурсов (electricity, gas, water, heat, fuel).
- [ ] Данные распределены по категориям использования (tech/own/production/household).
- [ ] Все листы энергопаспорта заполняются автоматически (Struktura pr2, Balans, Dinamika, Meropriyatiya).
- [ ] Word-отчёт генерируется с диаграммами и корректными данными.
- [ ] Данные ограждающих конструкций интегрированы (`ograjdayuschie_konstrukcii.xlsx`).
- [ ] API endpoints `/reports/energy-passport` и `/reports/energy-audit` работают (опционально).
- [ ] Документация обновлена (4+ файла: DEVELOPMENT_PLAN, STAGE2_PROGRESS, README, PCM690_TEMPLATE_PLAN).
- [ ] Чеклист тестирования создан и пройден.

---

## 📞 Контакты и ссылки

- **Проект:** EAIP (Energy Audit Integration Platform)
- **Нормативная база:** ПКМ №690 (Узбекистан)
- **Репозиторий:** `C:\eaip\` ✨ (перенесён 2025-11-10)
- **Старое расположение (бэкап):** `C:\Users\DELL\Downloads\eaip_full_skeleton_cursor_ready\`
- **AI-модель для Stage 2:** Claude Sonnet 4.5 (основная), GPT-5 (архитектура)
- **Дата создания промта:** 2025-11-10
- **Последнее обновление:** 2025-11-10 (перенос в корень диска)

---

**Готов продолжать Stage 2! 🚀**

