# Stage 2 — План действий с распределением ролей AI (2025-11-10)

## 🎯 Цели Stage 2
1. Распределить квартальное потребление энергоресурсов по видам нужд (технологические, собственные, производственные, хоз-бытовые).
2. Дополнить агрегатор данными по теплу, мазуту, топливу из соответствующих таблиц.
3. Интегрировать данные по ограждающим конструкциям (`ograjdayuschie_konstrukcii.xlsx`).
4. Автоматизировать заполнение всех листов шаблона энергопаспорта (включая `Balans`, `Dinamika sr`, `Meropriyatiya`).
5. Подготовить Word-шаблон отчёта и модуль для его автоматической генерации.

---

## 🤖 Распределение по AI-ролям

Для максимальной эффективности используем специализацию моделей:

### **GPT-5** (архитектура и сложная логика)
- Проектирование структуры JSON-схем для агрегации.
- Разработка алгоритмов распределения по категориям.
- Код-ревью критических функций (расчёт формул, валидация).
- Проектирование формул для листов энергопаспорта.

### **Claude Sonnet 4.5** (разработка Python-кода и анализ)
- Написание парсеров Excel (`usage_type_aggregator.py`, `building_envelope_parser.py`).
- Расширение `fill_energy_passport.py` новыми функциями.
- Создание `fill_energy_audit_report.py` для Word.
- Интеграция в `reports` сервис (FastAPI endpoints).
- Анализ структуры исходных таблиц (`pererashod.xlsx`, `otoplenie.xlsx`).
- Написание детальной документации по шаблонам ПКМ №690.

### **Claude Haiku 3.5** (тестирование и рутинные задачи)
- Написание юнит-тестов (pytest для агрегаторов).
- Проверка корректности агрегации (сравнение сумм с оригиналом).
- Обновление документации (README, STAGE2_PROGRESS.md).
- Генерация тестовых JSON-файлов.

### **DeepSeek Coder V3 / Qwen 2.5 Coder** (оптимизация и рефакторинг)
- Оптимизация производительности парсинга больших Excel-файлов.
- Рефакторинг дублирующегося кода в `main.py`.
- Добавление типизации (type hints) и docstrings.
- Линтинг (ruff/black) и исправление code smells.

---

## 📅 Детальный план (по шагам)

> **Примечание:** Все задачи выполняет AI (Claude Sonnet 4.5 / GPT-5) по запросу пользователя. Сроки указаны как ориентировочное время работы AI, а не календарные даты.

### Шаг 1: Распределение потребления по видам нужд
**Оценка времени:** ~3-4 часа AI-работы  
**AI-роль:** Claude Sonnet 4.5 (анализ + код)

#### Подзадачи:
1. **Анализ исходных таблиц** (Claude Sonnet 4.5):
   - Прочитать `pererashod.xlsx`, `otoplenie.xlsx`, `edenic na kvt.xlsx`.
   - Определить колонки с категориями потребления (tech/own/production/household).
   - Составить mapping: `{"колонка": "категория"}`.
   - Документировать особенности (merged cells, пропуски данных).

2. **Расширение агрегатора** (Claude Sonnet 4.5):
   - Создать функцию `aggregate_by_usage_type(workbook_path)` в `services/ingest/utils/energy_aggregator.py`.
   - Парсить листы с разбивкой по категориям.
   - Формировать поквартальные суммы для каждой категории:
     ```python
     {
       "electricity": {
         "2022-Q1": {
           "quarter_totals": {"active_kwh": 123456, "reactive_kvarh": 45678},
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
   - Добавить валидацию: сумма `by_usage` ≈ `quarter_totals` (±1% допуск).

3. **Тестирование** (Claude Haiku 3.5):
   - Написать pytest для `aggregate_by_usage_type`.
   - Создать mock Excel-файл с тестовыми данными.
   - Проверить, что суммы сходятся с ручным расчётом.

4. **Документация** (Claude Sonnet 4.5):
   - Обновить `docs/STAGE2_PROGRESS.md` — зафиксировать mapping категорий.
   - Добавить примеры JSON-схем в `templates/pcm690/README.md`.

**Выходные файлы:**
- `services/ingest/utils/usage_type_aggregator.py` (или расширенный `energy_aggregator.py`).
- `tests/test_usage_aggregation.py` (новый).
- `C:\Users\DELL\Documents\AUDIT\METIN\aggregated_with_usage_2022_2024.json`.
- Обновлённый `docs/STAGE2_PROGRESS.md`.

**Команды для проверки:**
```powershell
python -c "from services.ingest.utils.energy_aggregator import aggregate_by_usage_type; import json; result = aggregate_by_usage_type(r'C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\pererashod.xlsx'); print(json.dumps(result, indent=2, ensure_ascii=False))"
```

---

### Шаг 2: Дополнить агрегатор другими ресурсами
**Оценка времени:** ~2-3 часа AI-работы  
**AI-роль:** Claude Sonnet 4.5 (код) + Claude Haiku 3.5 (тесты)

#### Подзадачи:
1. **Парсинг тепловой энергии** (Claude Sonnet 4.5):
   - Открыть `otoplenie.xlsx`, изучить листы (`Тепло`, `Котельная`).
   - Добавить в `energy_aggregator.py` раздел `"heat"`:
     ```python
     if "Тепло" in workbook.sheetnames:
         sheet = workbook["Тепло"]
         # ... парсинг аналогично ЭЛЕКТР/ГАЗ
         aggregate_months(result["heat"], current_year, first_cell, {
             "cost_sum": row[1],
             "gcal": row[2],  # Гкал
         })
     ```

2. **Парсинг мазута и других видов топлива** (Claude Sonnet 4.5):
   - Проверить наличие листов `Мазут`, `Топливо` в исходных файлах.
   - Добавить `"fuel"` в `result` с полями `{"volume_tons": ..., "cost_sum": ...}`.

3. **Обновление `_compute_quarter_totals`** (Claude Sonnet 4.5):
   - Расширить функцию для поддержки всех новых ресурсов (`heat`, `fuel`).

4. **Тестирование** (Claude Haiku 3.5):
   - Проверить, что агрегация работает на реальных файлах.
   - Записать `aggregated_full_resources_2022_2024.json` и сравнить с оригинальными таблицами.

**Выходные файлы:**
- Обновлённый `services/ingest/utils/energy_aggregator.py` с 5+ ресурсами.
- JSON с разделами `"electricity"`, `"gas"`, `"water"`, `"heat"`, `"fuel"`.

**Команды для проверки:**
```powershell
python -c "from services.ingest.utils.energy_aggregator import aggregate_energy_data; import json; result = aggregate_energy_data(r'C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\otoplenie.xlsx'); print(json.dumps(result, indent=2, ensure_ascii=False))"
```

---

### Шаг 3: Интегрировать данные ограждающих конструкций
**Оценка времени:** ~2 часа AI-работы  
**AI-роль:** Claude Sonnet 4.5 (анализ + код)

#### Подзадачи:
1. **Анализ структуры** (Claude Sonnet 4.5):
   - Прочитать `ograjdayuschie_konstrukcii.xlsx`.
   - Определить листы: `Стены`, `Окна`, `Крыша`, `Пол` (или аналогичные).
   - Определить колонки: тип конструкции, площадь (м²), U-значение (Вт/(м²·°C)), материал.
   - Документировать в `docs/ENVELOPE_DATA_STRUCTURE.md`.

2. **Создание парсера** (Claude Sonnet 4.5):
   - Модуль `services/ingest/utils/building_envelope_parser.py`:
     ```python
     def parse_envelope_data(xlsx_path: Path) -> Dict[str, List[Dict]]:
         wb = load_workbook(xlsx_path, data_only=True)
         result = {"walls": [], "windows": [], "roof": [], "floor": []}
         
         if "Стены" in wb.sheetnames:
             sheet = wb["Стены"]
             for row in sheet.iter_rows(min_row=2, values_only=True):
                 result["walls"].append({
                     "type": row[0],
                     "area_m2": row[1],
                     "u_value": row[2],
                     "material": row[3],
                 })
         # ... аналогично для windows, roof, floor
         return result
     ```

3. **Интеграция в ingest** (Claude Sonnet 4.5):
   - В `main.py` добавить проверку имени файла:
     ```python
     if "ograjdayuschie" in safe_filename.lower() or "konstrukcii" in safe_filename.lower():
         envelope_data = parse_envelope_data(dst)
         envelope_file = write_envelope_json(batch_id, envelope_data, AGGREGATED_DIR)
         response_data["envelope_file"] = envelope_file.name
     ```

4. **Тестирование** (Claude Haiku 3.5):
   - Загрузить `ograjdayuschie_konstrukcii.xlsx` через веб-интерфейс.
   - Проверить, что `{batch_id}_envelope.json` создан и содержит корректные данные.

**Выходные файлы:**
- `services/ingest/utils/building_envelope_parser.py`.
- `docs/ENVELOPE_DATA_STRUCTURE.md`.
- JSON с данными ограждающих конструкций.

---

### Шаг 4: Расширить `fill_energy_passport.py` для всех листов
**Оценка времени:** ~4-5 часов AI-работы  
**AI-роль:** GPT-5 (архитектура формул) + Claude Sonnet 4.5 (код)

#### Подзадачи:
1. **Проектирование формул** (GPT-5):
   - Определить структуру листов `Balans`, `Dinamika sr`, `Meropriyatiya`.
   - Составить mapping: какие ячейки должны содержать формулы, какие — значения из JSON.
   - Документировать в `docs/PASSPORT_FORMULAS_SPEC.md`.

2. **Функция `fill_balans_sheet`** (Claude Sonnet 4.5):
   ```python
   def fill_balans_sheet(ws, agg_data: Dict, usage_data: Dict):
       # Пример: строки 10-13 — категории, колонки C-F — кварталы 2022
       for quarter, (row_tech, row_own, row_prod, row_house) in BALANS_MAPPING.items():
           elec = agg_data["electricity"].get(quarter, {})
           usage = elec.get("by_usage", {})
           
           ws.cell(row=row_tech, column=3).value = usage.get("technological", 0)
           ws.cell(row=row_own, column=3).value = usage.get("own_needs", 0)
           ws.cell(row=row_prod, column=3).value = usage.get("production", 0)
           ws.cell(row=row_house, column=3).value = usage.get("household", 0)
           
       # Формула итога: =SUM(C10:C13)
       ws.cell(row=14, column=3).value = "=SUM(C10:C13)"
   ```

3. **Функция `fill_dinamika_sheet`** (Claude Sonnet 4.5):
   - Заполнить таблицу: год, квартал, потребление (по каждому ресурсу).
   - Рассчитать удельные показатели:
     ```python
     specific_consumption = total_kwh / production_kg
     ws.cell(row=row_idx, column=5).value = f"={total_kwh_cell}/{production_cell}"
     ```

4. **Функция `fill_meropriyatiya_sheet`** (Claude Sonnet 4.5):
   - Вставить шаблонные строки мероприятий (placeholder для будущих AI-рекомендаций):
     ```python
     measures = [
         {"name": "Замена ламп накаливания на LED", "savings_kwh": 15000, "cost_usd": 5000},
         {"name": "Утепление стен", "savings_gcal": 120, "cost_usd": 20000},
     ]
     for idx, measure in enumerate(measures, start=2):
         ws.cell(row=idx, column=1).value = measure["name"]
         ws.cell(row=idx, column=2).value = measure.get("savings_kwh") or measure.get("savings_gcal")
         ws.cell(row=idx, column=3).value = measure["cost_usd"]
     ```

5. **Обновление `main()`** (Claude Sonnet 4.5):
   - Добавить вызовы новых функций:
     ```python
     if "Balans" in workbook.sheetnames:
         fill_balans_sheet(workbook["Balans"], agg_data, usage_data)
     if "Dinamika sr" in workbook.sheetnames:
         fill_dinamika_sheet(workbook["Dinamika sr"], agg_data)
     if "Meropriyatiya" in workbook.sheetnames:
         fill_meropriyatiya_sheet(workbook["Meropriyatiya"])
     ```

6. **Тестирование** (Claude Haiku 3.5):
   - Запустить скрипт:
     ```powershell
     python tools/fill_energy_passport.py --template "C:\Users\DELL\Documents\AUDIT\METIN\EnergyPassport_PKM690_Template_v1.1.2.xlsx" --aggregated "C:\Users\DELL\Documents\AUDIT\METIN\aggregated_with_usage_2022_2024.json" --output "C:\Users\DELL\Documents\AUDIT\METIN\EnergyPassport_PKM690_full_filled.xlsx" --loss-active-month 3200 --loss-reactive-month 13600 --transformer-power 630
     ```
   - Открыть результат в Excel, проверить:
     - [ ] Все листы заполнены без `#REF!` ошибок.
     - [ ] Формулы корректно считаются (итоги, проценты).
     - [ ] Квартальные суммы сходятся с исходными таблицами.

**Выходные файлы:**
- Обновлённый `tools/fill_energy_passport.py` с 3 новыми функциями.
- `docs/PASSPORT_FORMULAS_SPEC.md`.
- `EnergyPassport_PKM690_full_filled.xlsx`.

---

### Шаг 5: Автоматизировать заполнение Word-отчёта
**Оценка времени:** ~3-4 часа AI-работы  
**AI-роль:** Claude Sonnet 4.5 (код + текст)

#### Подзадачи:
1. **Создание модуля** (Claude Sonnet 4.5):
   - Файл `tools/fill_energy_audit_report.py`:
     ```python
     from docx import Document
     from pathlib import Path
     import json
     
     def replace_placeholders(doc: Document, data: dict):
         for paragraph in doc.paragraphs:
             for key, value in data.items():
                 placeholder = f"{{{{{key}}}}}"
                 if placeholder in paragraph.text:
                     paragraph.text = paragraph.text.replace(placeholder, str(value))
         
         for table in doc.tables:
             for row in table.rows:
                 for cell in row.cells:
                     for key, value in data.items():
                         placeholder = f"{{{{{key}}}}}"
                         if placeholder in cell.text:
                             cell.text = cell.text.replace(placeholder, str(value))
     
     def main():
         parser = argparse.ArgumentParser()
         parser.add_argument("--template", required=True)
         parser.add_argument("--data", required=True)
         parser.add_argument("--output", required=True)
         args = parser.parse_args()
         
         doc = Document(args.template)
         data = json.loads(Path(args.data).read_text(encoding="utf-8"))
         
         placeholders = {
             "enterprise.name": data.get("enterprise_name", "ООО Синергис"),
             "period.start": "2022-01-01",
             "period.end": "2024-12-31",
             "analytics.gas.total_volume": sum(q.get("quarter_totals", {}).get("volume_m3", 0) 
                                                for q in data["resources"]["gas"].values()),
             # ... остальные placeholder'ы
         }
         
         replace_placeholders(doc, placeholders)
         doc.save(args.output)
         print(f"Report saved to {args.output}")
     ```

2. **Генерация диаграмм** (Claude Sonnet 4.5):
   - Создать функцию `generate_charts(agg_data) -> List[Path]`:
     ```python
     import matplotlib.pyplot as plt
     
     def generate_charts(agg_data: dict, output_dir: Path) -> List[Path]:
         charts = []
         
         # График потребления газа по кварталам
         quarters = list(agg_data["gas"].keys())
         volumes = [agg_data["gas"][q]["quarter_totals"]["volume_m3"] for q in quarters]
         
         plt.figure(figsize=(10, 6))
         plt.bar(quarters, volumes)
         plt.title("Потребление газа по кварталам (м³)")
         plt.xlabel("Квартал")
         plt.ylabel("м³")
         chart_path = output_dir / "gas_consumption.png"
         plt.savefig(chart_path)
         charts.append(chart_path)
         
         # Аналогично для электроэнергии, воды и т.д.
         return charts
     ```

3. **Вставка диаграмм в Word** (Claude Sonnet 4.5):
   ```python
   from docx.shared import Inches
   
   charts = generate_charts(agg_data, Path("./temp_charts"))
   for chart_path in charts:
       doc.add_picture(str(chart_path), width=Inches(5))
   ```

4. **Текстовые формулировки** (Claude Sonnet 4.5):
   - Подготовить шаблонные тексты для разделов отчёта (вводная часть, выводы, рекомендации).
   - Добавить в JSON:
     ```json
     {
       "report": {
         "goal": "Проведение энергоаудита в соответствии с ПКМ №690 для выявления резервов энергосбережения.",
         "findings": "Выявлено превышение норматива по газу на 12% в Q2 2023. Потери в трансформаторе составили 3.2 МВт·ч/месяц.",
         "recommendations": "Рекомендуется: 1) Модернизация котельной, 2) Утепление стен, 3) Замена ламп на LED."
       }
     }
     ```

5. **Тестирование** (Claude Haiku 3.5):
   ```powershell
   python tools/fill_energy_audit_report.py --template "templates/pcm690/energy_audit_template.docx" --data "C:\Users\DELL\Documents\AUDIT\METIN\aggregated_with_usage_2022_2024.json" --output "C:\Users\DELL\Documents\AUDIT\METIN\EnergyAudit_PKM690_2022_2024.docx"
   ```
   - Открыть `EnergyAudit_PKM690_2022_2024.docx`, проверить:
     - [ ] Все placeholder'ы заменены реальными данными.
     - [ ] Диаграммы вставлены и отображаются корректно.
     - [ ] Таблицы заполнены без пустых ячеек.

**Выходные файлы:**
- `tools/fill_energy_audit_report.py`.
- `EnergyAudit_PKM690_2022_2024.docx`.

---

### Шаг 6: Интеграция в `reports` сервис (опционально)
**Оценка времени:** ~2 часа AI-работы  
**AI-роль:** Claude Sonnet 4.5 (FastAPI endpoints)

#### Подзадачи:
1. **Endpoint для энергопаспорта** (Claude Sonnet 4.5):
   ```python
   @app.post("/reports/energy-passport")
   async def generate_energy_passport(batch_id: str):
       # Загрузить aggregated JSON из ingest
       agg_data = await fetch_aggregated_data(batch_id)
       
       # Запустить fill_energy_passport.py через subprocess
       result = subprocess.run([
           "python", "tools/fill_energy_passport.py",
           "--template", "templates/pcm690/energy_passport_template.xlsx",
           "--aggregated", f"/tmp/{batch_id}_aggregated.json",
           "--output", f"/tmp/{batch_id}_passport.xlsx",
           "--loss-active-month", "3200",
           "--loss-reactive-month", "13600",
           "--transformer-power", "630",
       ])
       
       if result.returncode != 0:
           raise HTTPException(status_code=500, detail="Passport generation failed")
       
       return {"file": f"{batch_id}_passport.xlsx", "download_url": f"/downloads/{batch_id}_passport.xlsx"}
   ```

2. **Endpoint для Word-отчёта** (Claude Sonnet 4.5):
   - Аналогично для `/reports/energy-audit`.

3. **Обновление `requirements.txt`** (Claude Haiku 3.5):
   - Добавить `openpyxl`, `python-docx`, `matplotlib` если нет.

4. **Тестирование через Swagger UI**:
   - Запустить `uvicorn services.reports.main:app --reload --port 8005`.
   - Открыть `http://localhost:8005/docs`.
   - Вызвать `POST /reports/energy-passport` с `batch_id`.
   - Скачать сгенерированный файл.

**Выходные файлы:**
- Обновлённый `services/reports/main.py` с 2 новыми endpoint'ами.

---

### Шаг 7: Документация и финализация
**Оценка времени:** ~2-3 часа AI-работы  
**AI-роль:** Claude Sonnet 4.5 (документация + чеклисты)

#### Подзадачи:
1. **Обновление документации** (Claude Sonnet 4.5):
   - `docs/STAGE2_PROGRESS.md` — зафиксировать выполненные шаги, ссылки на файлы.
   - `DEVELOPMENT_PLAN_2025.md` — проставить галочки по P1.2, P1.3, P1.4.
   - `templates/pcm690/README.md` — добавить инструкции по использованию скриптов.
   - `README.md` — обновить секцию "PCM №690 Templates" с примерами команд.

2. **Чеклист тестирования** (Claude Sonnet 4.5):
   - Создать `docs/STAGE2_TESTING_CHECKLIST.md`:
     ```markdown
     - [ ] Агрегация всех ресурсов корректна (electricity, gas, water, heat, fuel).
     - [ ] Распределение по категориям (tech/own/production/household) суммируется в 100%.
     - [ ] Все листы энергопаспорта заполнены без `#REF!` ошибок.
     - [ ] Word-отчёт генерируется без placeholder'ов.
     - [ ] Формулы в Excel работают (итоги, проценты, динамика).
     - [ ] Диаграммы в Word отображаются корректно.
     - [ ] Данные ограждающих конструкций парсятся и сохраняются в JSON.
     - [ ] API endpoints `/reports/energy-passport` и `/reports/energy-audit` возвращают файлы.
     ```

3. **Видео-демо** (человек + AI-ассистент):
   - Записать скринкаст полного цикла:
     1. Загрузка файлов через веб-интерфейс.
     2. Проверка агрегированных JSON.
     3. Генерация энергопаспорта и Word-отчёта.
     4. Открытие результатов в Excel/Word.
   - Загрузить на внутренний сервер или YouTube (unlisted).

**Выходные файлы:**
- Обновлённые `docs/STAGE2_PROGRESS.md`, `DEVELOPMENT_PLAN_2025.md`, `README.md`.
- `docs/STAGE2_TESTING_CHECKLIST.md`.
- Видео-демо (ссылка в `docs/STAGE2_PROGRESS.md`).

---

## 📦 Итоговые артефакты Stage 2

- ✅ `services/ingest/utils/usage_type_aggregator.py` — распределение по видам нужд.
- ✅ `services/ingest/utils/building_envelope_parser.py` — парсер ограждающих конструкций.
- ✅ `tools/fill_energy_passport.py` (расширенный) — заполнение всех листов паспорта.
- ✅ `tools/fill_energy_audit_report.py` — генерация Word-отчёта с диаграммами.
- ✅ `aggregated_with_usage_2022_2024.json` — полный JSON с данными по всем ресурсам и категориям.
- ✅ `EnergyPassport_PKM690_full_filled.xlsx` — энергопаспорт без пустых полей.
- ✅ `EnergyAudit_PKM690_2022_2024.docx` — готовый отчёт по ПКМ №690.
- ✅ Обновлённая документация (4 файла).
- ✅ Тестовые скрипты (pytest для агрегаторов).
- ✅ API endpoints в `reports` сервисе.

---

## ⚠️ Риски и зависимости

1. **Недостаточная структура исходных таблиц**: если в `pererashod.xlsx` нет чёткой разбивки по категориям, потребуется ручная разметка или уточнение у заказчика.
   - **Решение AI**: Claude 3.5 проанализирует структуру и предложит mapping или укажет, где нужна ручная разметка.

2. **Отсутствие формул в шаблоне**: если в `EnergyPassport_PKM690_Template_v1.1.2.xlsx` листы `Balans`, `Dinamika` не содержат готовых формул, придётся создавать их программно.
   - **Решение AI**: GPT-4 спроектирует формулы на основе требований ПКМ №690, GPT-4o реализует их в коде.

3. **Внешние файлы вне репозитория**: все таблицы в `C:\Users\DELL\Documents\AUDIT\` — переносимость затруднена.
   - **Решение**: скопировать в `infra/data/sources/` или создать символические ссылки, добавить в `.gitignore`.

4. **AI API для рекомендаций**: DeepSeek/OpenAI пока не задействованы — лист `Meropriyatiya` будет с шаблонными данными.
   - **Решение (Stage 3)**: интегрировать AI-модуль для генерации рекомендаций на основе отклонений от нормативов.

5. **Производительность парсинга больших файлов**: если Excel-файлы >50 МБ, `openpyxl` может работать медленно.
   - **Решение AI**: DeepSeek Coder оптимизирует код (использование `read_only=True`, `data_only=True`, пагинация).

---

## 🚀 Следующие шаги после Stage 2

- **Stage 3**: Тестирование и CI/CD
  - pytest для всех модулей (покрытие >70%).
  - GitHub Actions для автотестов, линтеров (ruff/black), сборки Docker-образов.
  
- **Stage 4**: Миграция на PostgreSQL и RBAC
  - Перенос ingest БД с SQLite на Postgres.
  - Alembic для миграций схемы.
  - JWT-авторизация в `gateway-auth`, middleware для проверки ролей.

- **Stage 5**: AI-интеграция
  - DeepSeek/OpenAI для автоматических рекомендаций (лист `Meropriyatiya`).
  - Выявление аномалий в потреблении.
  - Предсказание энергопотребления (ML-модель в `analytics` сервисе).

- **Stage 6**: Локализация (рус/узб)
  - i18n для веб-интерфейса.
  - Двуязычные шаблоны отчётов.
  - Словарь терминов ПКМ №690.

---

## 🤖 Почему такое распределение ролей AI?

### GPT-4 / Claude 3.5 Sonnet → Архитектура
- Сильны в проектировании структур данных, формул, сложных алгоритмов.
- Хорошо документируют решения и объясняют логику.
- Идеальны для code review и рефакторинга.

### GPT-4o / Claude Sonnet → Разработка
- Быстро пишут Python-код с минимальными ошибками.
- Хорошо работают с библиотеками (openpyxl, python-docx, pandas).
- Могут интегрировать новые модули в существующую кодовую базу.

### GPT-4o-mini / o3-mini → Тесты и рутина
- Эффективны для написания юнит-тестов (pytest).
- Быстро проверяют корректность данных (сравнение JSON, сумм).
- Дёшевы в использовании для рутинных задач (обновление документации).

### DeepSeek Coder → Оптимизация
- Специализируется на производительности и качестве кода.
- Хорошо рефакторит дублирующийся код, добавляет type hints.
- Быстро обнаруживает code smells и предлагает улучшения.

### Claude 3.5 Sonnet → Текстовая аналитика
- Отлично анализирует структуру Excel-таблиц и документов.
- Формулирует требования и описывает бизнес-логику.
- Пишет качественную документацию и инструкции.

---

## 📊 Метрики успеха Stage 2

- [ ] Все 7 шагов завершены в срок (до 2025-11-17).
- [ ] Агрегатор поддерживает 5+ видов ресурсов + распределение по категориям.
- [ ] Энергопаспорт заполняется автоматически (все листы, формулы работают).
- [ ] Word-отчёт генерируется с диаграммами и корректными данными.
- [ ] API endpoints в `reports` сервисе работают (можно скачать файлы).
- [ ] Чеклист тестирования пройден на 100%.
- [ ] Документация обновлена (4+ файла).
- [ ] Видео-демо записано и доступно команде.

---

**Автор:** AI Assistant (Claude 3.5 Sonnet)  
**Дата:** 2025-11-10  
**Статус:** Согласован с распределением AI-ролей  
**Следующий шаг:** Начать с Шага 1 (анализ структуры таблиц)

