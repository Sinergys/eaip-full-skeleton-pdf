# 💡 Полезные идеи из плана Bitrix24 (без интеграции)

**Дата:** 2025-12-01  
**Статус:** Идеи для улучшения текущей системы

---

## 🎯 Хорошие идеи, которые можно взять

### 1. ✅ Дашборд со статистикой

**Идея из плана:** "Следите за процессом через дашборды"

**Что добавить в EAIP:**
- Страница `/web/normative/dashboard` с:
  - Количество загруженных документов
  - Количество извлеченных правил
  - Статистика по типам документов
  - Топ-10 полей с нормативами
  - Графики и визуализация

**Реализация:**
```python
# main.py
@app.get("/api/normative/statistics")
def get_normative_statistics():
    """Статистика по нормативным документам"""
    docs = database.list_normative_documents()
    total_rules = sum(doc.get("rules_count", 0) for doc in docs)
    
    return {
        "total_documents": len(docs),
        "total_rules": total_rules,
        "by_type": {
            "PKM690": len([d for d in docs if d["document_type"] == "PKM690"]),
            "GOST": len([d for d in docs if d["document_type"] == "GOST"]),
            # ...
        },
        "top_fields": get_top_fields_with_normatives(),
    }
```

---

### 2. ✅ Статусы "Нарушение" / "Соответствует"

**Идея из плана:** "Если значение выше нормы — ставьте статус 'Нарушение'"

**Что добавить:**
- Функция сравнения факта с нормативом
- Автоматическое определение статуса
- Визуальное отображение (красный/зеленый)

**Реализация:**
```python
# normative_validator.py (новый модуль)
def validate_against_normative(
    actual_value: float,
    field_name: str,
    sheet_name: str,
    tolerance_percent: float = 10.0
) -> Dict[str, Any]:
    """Проверить соответствие фактического значения нормативу"""
    rules = database.get_normative_rules_for_field(field_name, sheet_name)
    
    if not rules:
        return {
            "status": "unknown",
            "message": "Норматив не найден"
        }
    
    # Берем норматив с наивысшей уверенностью
    normative = max(rules, key=lambda r: r.get("extraction_confidence", 0))
    normative_value = normative.get("numeric_value")
    
    if normative_value is None:
        return {"status": "unknown", "message": "Норматив не имеет числового значения"}
    
    deviation = abs(actual_value - normative_value) / normative_value * 100
    
    if actual_value > normative_value * (1 + tolerance_percent / 100):
        return {
            "status": "violation",  # Нарушение
            "actual": actual_value,
            "normative": normative_value,
            "deviation_percent": deviation,
            "message": f"Превышение норматива на {deviation:.1f}%"
        }
    else:
        return {
            "status": "compliant",  # Соответствует
            "actual": actual_value,
            "normative": normative_value,
            "deviation_percent": deviation,
            "message": "Соответствует нормативу"
        }
```

---

### 3. ✅ Уведомления о превышении нормативов

**Идея из плана:** "Отправляйте уведомление при превышении"

**Что добавить:**
- Email уведомления
- Telegram бот (опционально)
- Логирование нарушений

**Реализация:**
```python
# normative_notifier.py (новый модуль)
def notify_violation(
    field_name: str,
    actual_value: float,
    normative_value: float,
    enterprise_name: str
):
    """Отправить уведомление о нарушении норматива"""
    message = f"""
    ⚠️ ПРЕВЫШЕНИЕ НОРМАТИВА
    
    Предприятие: {enterprise_name}
    Поле: {field_name}
    Факт: {actual_value}
    Норматив: {normative_value}
    Отклонение: {((actual_value/normative_value - 1) * 100):.1f}%
    """
    
    # Email
    send_email(to="auditor@example.com", subject="Нарушение норматива", body=message)
    
    # Telegram (опционально)
    # send_telegram(message)
    
    # Логирование
    logger.warning(f"Нарушение норматива: {field_name} = {actual_value} > {normative_value}")
```

---

### 4. ✅ Мониторинг критических полей

**Идея из плана:** "Какие объекты не соответствуют нормам"

**Что добавить:**
- Список критических полей (топ-10)
- Автоматическая проверка при заполнении паспорта
- Отчет о нарушениях

**Реализация:**
```python
# critical_fields_monitor.py (новый модуль)
CRITICAL_FIELDS = [
    {"field_name": "Удельный расход электроэнергии", "sheet_name": "Динамика ср"},
    {"field_name": "Удельный расход газа", "sheet_name": "Динамика ср"},
    {"field_name": "Потери электроэнергии", "sheet_name": "08_Потери"},
    # ... остальные
]

def check_critical_fields(enterprise_id: int, batch_id: str):
    """Проверить все критические поля для предприятия"""
    violations = []
    
    for field in CRITICAL_FIELDS:
        # Получить фактическое значение из паспорта
        actual = get_field_value_from_passport(enterprise_id, field)
        
        # Проверить с нормативом
        validation = validate_against_normative(
            actual, field["field_name"], field["sheet_name"]
        )
        
        if validation["status"] == "violation":
            violations.append({
                "field": field["field_name"],
                "actual": actual,
                "normative": validation["normative"],
                "deviation": validation["deviation_percent"]
            })
    
    return {
        "enterprise_id": enterprise_id,
        "total_critical_fields": len(CRITICAL_FIELDS),
        "violations_count": len(violations),
        "violations": violations,
        "status": "compliant" if len(violations) == 0 else "has_violations"
    }
```

---

### 5. ✅ Экспорт результатов

**Идея из плана:** "Экспорт результатов (например, сравнение факта и нормы)"

**Что добавить:**
- Экспорт нормативов в Excel
- Экспорт отчета о проверках
- Экспорт в PDF

**Реализация:**
```python
# main.py
@app.get("/api/normative/export/compliance-report")
def export_compliance_report(enterprise_id: int):
    """Экспорт отчета о соответствии нормативам"""
    violations = check_critical_fields(enterprise_id)
    
    # Создать Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Соответствие нормативам"
    
    # Заголовки
    ws.append(["Поле", "Факт", "Норматив", "Отклонение %", "Статус"])
    
    # Данные
    for violation in violations["violations"]:
        ws.append([
            violation["field"],
            violation["actual"],
            violation["normative"],
            f"{violation['deviation']:.1f}%",
            "⚠️ Нарушение" if violation["deviation"] > 10 else "✅ Соответствует"
        ])
    
    # Сохранить
    filename = f"compliance_report_{enterprise_id}.xlsx"
    wb.save(filename)
    return FileResponse(filename)
```

---

### 6. ✅ Визуализация в веб-интерфейсе

**Идея из плана:** "Дашборд где будет видно..."

**Что добавить:**
- Графики соответствия нормативам
- Цветовая индикация (красный/зеленый)
- Таблицы с отклонениями

**HTML пример:**
```html
<!-- normative_dashboard.html -->
<div class="compliance-card">
    <h3>Удельный расход электроэнергии</h3>
    <div class="value">
        <span class="actual">0.18</span> кВт·ч/м²
        <span class="normative">(норматив: 0.15)</span>
    </div>
    <div class="status violation">
        ⚠️ Превышение на 20%
    </div>
    <div class="progress-bar">
        <div class="progress" style="width: 120%"></div> <!-- Красный -->
    </div>
</div>
```

---

## 📋 План реализации (приоритеты)

### P0 - Критично (1-2 дня):
1. ✅ Статусы "Нарушение" / "Соответствует"
2. ✅ Функция сравнения с нормативами
3. ✅ Логирование нарушений

### P1 - Важно (2-3 дня):
4. ✅ Дашборд со статистикой
5. ✅ Мониторинг критических полей
6. ✅ Экспорт отчетов

### P2 - Желательно (3-5 дней):
7. ✅ Email уведомления
8. ✅ Визуализация в веб-интерфейсе
9. ✅ Telegram бот (опционально)

---

## 🎯 Что реализовать первым

### 1. Функция проверки соответствия (самое важное!)

**Файл:** `domain/normative_validator.py` (новый)

```python
def validate_against_normative(actual_value, field_name, sheet_name):
    """Проверить соответствие нормативу"""
    # Получить норматив из БД
    # Сравнить с фактическим значением
    # Вернуть статус: "compliant" или "violation"
```

**Использование:**
```python
# При заполнении паспорта
validation = validate_against_normative(0.18, "Удельный расход", "Динамика ср")
if validation["status"] == "violation":
    logger.warning(f"Превышение норматива: {validation['message']}")
```

---

### 2. Дашборд со статистикой

**Файл:** `web/normative_dashboard.html` (новый)

**Показывать:**
- Количество документов
- Количество правил
- Статистика по типам
- Топ нарушений

---

### 3. API для проверки соответствия

**Endpoint:** `POST /api/normative/validate-field`

```python
@app.post("/api/normative/validate-field")
def validate_field_value(
    field_name: str,
    actual_value: float,
    sheet_name: Optional[str] = None
):
    """Проверить соответствие значения нормативу"""
    return validate_against_normative(actual_value, field_name, sheet_name)
```

---

## ✅ Итог

**Хорошие идеи из плана Bitrix24:**
1. ✅ Дашборд со статистикой
2. ✅ Статусы "Нарушение" / "Соответствует"
3. ✅ Уведомления о превышении
4. ✅ Мониторинг критических полей
5. ✅ Экспорт результатов

**Все это можно реализовать в текущей системе БЕЗ Bitrix24!**

---

**Автор:** Agent-1 (Auto)  
**Дата:** 2025-12-01


