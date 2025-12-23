# EAIP — Full Skeleton (Cursor-ready)

Microservices (FastAPI), docker-compose, client placeholder, and Cursor config.

## Quick start (compose)
```bash
cp .env.example .env
docker compose up --build
```
Services: http://localhost:8000..8006 `/health` endpoints.

## Manual dev
Activate venv per service and run uvicorn (see each service README).

## Development roadmap
- [Development plan (Q4 2025)](DEVELOPMENT_PLAN_2025.md) — приоритеты, главные цели и очередь задач.
- [Stage 1 smoke test notes](docs/STAGE1_OBSERVATIONS.md) — результаты проверки цепочки upload → parse → edit → save. *(Баг пустой страницы `/web/results` устранён, smoke-test от 2025-11-09 пройден.)*
- [PCM №690 template roadmap](docs/PCM690_TEMPLATE_PLAN.md) — план работ по нормативным шаблонам.
- [Stage 2 progress log](docs/STAGE2_PROGRESS.md) — ход работ, источники данных и ссылки на инструменты.

## PCM №690 Templates
- Скрипт генерации: `tools/fill_energy_passport.py` (принимает `--aggregated`, `--template`, опционально `--nodes-json`, `--loss-*`).
- Заготовки: `templates/pcm690/energy_passport_template.xlsx`, `templates/pcm690/energy_audit_template.docx`.
- Инструкции: `templates/pcm690/README.md`.
- Автоматическое агрегирование при загрузке файлов: `services/ingest/utils/energy_aggregator.py`, логирование — `services/ingest/utils/aggregation_log.py`.

### Aggregation utilities (ingest service)
- `services/ingest/utils/energy_aggregator.py` — формирует поквартальные JSON из исходных таблиц.
- `services/ingest/utils/aggregation_log.py` — логирует события агрегации (jsonl). 
- `AGGREGATED_DIR` (`/data/inbox/aggregated` или значение переменной) хранит `*_aggregated.json`.

## Enterprise Type Classification (✅ 2025-11-30)
- **Автоматическое определение типа предприятия** на основе анализа загруженных файлов
- Определяет: отрасль (`industry`), тип предприятия (`enterprise_type`), тип продукции (`product_type`)
- Учитывает контекст файлов (про само предприятие vs про потребителей)
- Модуль: `services/ingest/utils/enterprise_classifier.py`
- Документация: `docs/ENTERPRISE_TYPE_FEATURE.md`

## Testing & Quality Assurance (✅ 2025-12-01)
- **Комплексное тестирование энергопаспортов** — автоматическая проверка всех листов, формул и связей
- **Тестовый скрипт:** `services/ingest/tools/comprehensive_passport_test.py`
- **Результаты:** Протестирован файл "Метин Ирода" — 1527 формул без ошибок
- **Чеклист:** `docs/STAGE2_TESTING_CHECKLIST.md` — детальные проверки для всех листов
- **Отчеты:** `docs/TESTING_REPORT_METIN_IRODA_2025_12_01.md`

## PDF Table Extraction (✅ 2025-12-01)
- **Tabula с Java** — улучшенное извлечение таблиц из PDF
- **Требования:** Java Runtime Environment (JRE) 11+ (установка через `winget install Microsoft.OpenJDK.17`)
- **Ускорение:** jpype1 для быстрой работы Tabula
- **Документация:** `docs/JAVA_INSTALLATION_GUIDE.md`

## PDF Generation

The reports service generates PDF files with full Cyrillic support using DejaVuSans TTF font.

### Generate Demo PDF

```powershell
cd infra
docker compose build reports
docker compose up -d reports
pwsh -ExecutionPolicy Bypass -File .\audit_demo.ps1
```

The script will:
1. Ingest demo data
2. Validate it
3. Run analytics forecast
4. Generate recommendations
5. Create PDF report with Cyrillic text support

Output: `infra/passport_demo1_full.pdf`

### Features

- ✅ Full Cyrillic character support in PDF documents
- ✅ Automatic font registration at service startup
- ✅ Startup readiness check for reliable script execution
- ✅ Bold text support via font family registration

See [CHANGELOG.md](CHANGELOG.md) for detailed technical information.
