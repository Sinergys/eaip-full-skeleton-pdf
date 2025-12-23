# 🚀 УЛУЧШЕННЫЙ ПРОМПТ: Интеллектуальный маршрутизатор документов

## **🎯 ЗАДАЧА: ИНТЕЛЛЕКТУАЛЬНЫЙ ДИСПЕТЧЕР ДОКУМЕНТОВ ДЛЯ СИСТЕМЫ ЭНЕРГОАУДИТА**

**Контекст:** 
Существующая система парсинга энергоаудита (`file_parser.py`, `nodes_parser.py`, `equipment_parser.py`) требует интеллектуальной маршрутизации. ИИ должен стать "мозгом", анализирующим ЛЮБЫЕ файлы (без ограничений по названиям/количеству) и определяющим оптимальную обработку.

### **🚀 ОСНОВНАЯ ЦЕЛЬ**
Создать `intelligent_router.py`, который при импорте ЛЮБОГО файла (Word, Excel, PDF, изображения) автоматически:
1. **Определяет тип и содержание документа**
2. **Анализирует представленные данные** 
3. **Генерирует маршрутизационную карту** для системы
4. **Рекомендует модули обработки и таблицы БД**

---

## **🔍 КРИТИЧЕСКИЕ ТРЕБОВАНИЯ**

### **✅ БЕЗ ОГРАНИЧЕНИЙ:**
- Поддержка ЛЮБЫХ названий файлов
- Обработка НЕОГРАНИЧЕННОГО количества файлов
- Анализ ЛЮБЫХ типов данных энергоаудита
- Адаптация к НЕИЗВЕСТНЫМ форматам

### **✅ ИНТЕЛЛЕКТУАЛЬНЫЙ АНАЛИЗ:**
```python
# Что должен определить ИИ для каждого файла:
1. ДОКУМЕНТ: energy_passport | balance_act | consumption_table | calculation | contract | protocol
2. РЕСУРС: electricity | gas | water | heat | fuel | multiple
3. ДАННЫЕ: meter_readings | energy_balance | savings_calculation | tariffs | norms
4. ПЕРИОД: 2024_Q1 | 2023_year | multiyear | unknown
5. СТАТУС: source_data | calculated | reported | methodological
```

---

## **🔄 АЛГОРИТМ РАБОТЫ**

### **Этап 1: Быстрый анализ (2-3 сек)**

**Цель:** Быстрая классификация документа для принятия решения о дальнейшей обработке.

**Процесс:**
1. Загрузка первых 3-5 листов Excel / первых 2-3 страниц PDF
2. Извлечение названий листов, заголовков таблиц
3. Анализ структуры документа
4. Определение базовых метаданных:
   - Тип документа
   - Тип ресурса
   - Период данных
   - Предприятие

**Критерии перехода:**
- Если confidence > 0.7 → переход к маршрутизации
- Если confidence < 0.7 → переход к глубокому анализу

### **Этап 2: Глубокий анализ (3-5 сек, опционально)**

**Цель:** Полный анализ документа для точной маршрутизации.

**Процесс:**
1. Анализ всех листов/страниц
2. Извлечение полной структуры данных
3. Выявление аномалий и ошибок
4. Определение детальных метаданных
5. Генерация полного routing map

### **Этап 3: Маршрутизация**

**Цель:** Выбор оптимальных модулей обработки и таблиц БД.

**Процесс:**
1. Генерация routing map на основе анализа
2. Выбор модулей обработки
3. Вызов специализированных парсеров
4. Сохранение результатов в соответствующие таблицы БД

---

## **🎪 СИСТЕМА МАРШРУТИЗАЦИИ**

**ИИ анализирует → Система выполняет:**

| Обнаружено в файле | Решение системы |
|---------------------|-----------------|
| `balance_act` + `electricity` + `meter_readings` | → `balance_processor` → таблицы `node_consumption`, `energy_balance` |
| `energy_passport` + `multiple` + `savings_calculation` | → `passport_assembler` → таблицы `enterprise_data`, `energy_savings` |
| `consumption_table` + `gas` + `monthly_data` | → `resource_calculator` → таблица `consumption_data` |
| `calculation` + `water` + `norms` | → `normative_validator` → таблица `calculation_results` |
| `contract` + `tariffs` + `limits` | → `documents_repository` → таблица `contracts` |

---

## **📦 ВЫХОДНОЙ ФОРМАТ (ROUTING MAP)**

```json
{
  "file_analysis": {
    "document_type": "balance_act",
    "document_subtype": "electricity", 
    "content_types": ["meter_readings", "energy_balance"],
    "resources": ["active_energy", "reactive_energy"],
    "period": "2024_Q1",
    "enterprise": "Навоийский ГМК",
    "confidence": 0.94
  },
  "routing_decisions": {
    "primary_module": "balance_processor",
    "secondary_modules": ["data_validator", "anomaly_detector"],
    "target_tables": ["node_consumption", "energy_balance"],
    "processing_priority": "high",
    "validation_required": true
  },
  "system_instructions": {
    "next_action": "parse_with_balance_processor",
    "parameters": {"extract_nodes": true, "validate_balance": true},
    "fallback_strategy": "manual_review"
  },
  "data_extraction_hints": {
    "expected_tables": ["node_consumption", "energy_balance"],
    "expected_columns": ["node_name", "active_energy", "period"],
    "validation_rules": ["sum_check", "period_consistency"]
  },
  "quality_metrics": {
    "completeness": 0.95,
    "accuracy_estimate": 0.92,
    "requires_manual_review": false
  }
}
```

---

## **🔧 ТЕХНИЧЕСКАЯ АРХИТЕКТУРА**

### **Модуль:** `intelligent_router.py`

### **Интеграция с существующей системой:**
```python
# СУЩЕСТВУЮЩАЯ АРХИТЕКТУРА (адаптировать):
file_parser.py           # Базовый парсинг
nodes_parser.py          # Узлы учета  
equipment_parser.py      # Оборудование
balance_sheet_node_extractor.py  # Акты балансов
energy_aggregator.py     # Агрегация данных

# НОВЫЙ ИНТЕЛЛЕКТУАЛЬНЫЙ СЛОЙ:
intelligent_router.py    # Мозг системы - определяет КАК обрабатывать
```

### **Структура модуля:**
```python
class IntelligentRouter:
    """
    Интеллектуальный маршрутизатор документов для системы энергоаудита.
    """
    
    def __init__(self):
        self.ai_analyzer = AIFileAnalyzer()
        self.routing_rules = RoutingRules()
        self.fallback_handler = FallbackHandler()
    
    def route_file(self, file_path: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Главная функция маршрутизации файла.
        
        Args:
            file_path: Путь к файлу
            parsed_data: Результаты базового парсинга
            
        Returns:
            Routing map с инструкциями для обработки
        """
        # 1. Быстрый анализ
        quick_analysis = self.ai_analyzer.quick_analyze(file_path, parsed_data)
        
        # 2. Глубокий анализ (если нужно)
        if quick_analysis["confidence"] < 0.7:
            deep_analysis = self.ai_analyzer.deep_analyze(file_path, parsed_data)
        else:
            deep_analysis = quick_analysis
        
        # 3. Генерация routing map
        routing_map = self.routing_rules.generate_routing_map(deep_analysis)
        
        # 4. Валидация routing map
        if routing_map["quality_metrics"]["requires_manual_review"]:
            return self.fallback_handler.handle_low_confidence(routing_map)
        
        return routing_map
    
    def execute_routing(self, routing_map: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """
        Выполнение маршрутизации - вызов соответствующих модулей.
        """
        primary_module = routing_map["routing_decisions"]["primary_module"]
        
        # Вызов соответствующего модуля обработки
        if primary_module == "balance_processor":
            from utils.balance_sheet_node_extractor import extract_node_consumption_from_balance_sheet
            return extract_node_consumption_from_balance_sheet(file_path, ...)
        elif primary_module == "nodes_parser":
            from utils.nodes_parser import parse_nodes_workbook
            return parse_nodes_workbook(file_path)
        # ... другие модули
        
        return {"status": "routed", "module": primary_module}
```

---

## **⚠️ ОБРАБОТКА ОШИБОК**

### **Сценарии ошибок:**

1. **ИИ недоступен:**
   - Fallback на существующую логику (правила из `resource_classifier.py`)
   - Логирование ошибки
   - Продолжение обработки без ИИ

2. **Confidence < 70%:**
   - Запрос подтверждения у пользователя
   - Предложение вариантов маршрутизации
   - Сохранение для обучения

3. **Маршрутизация неверна:**
   - Возможность исправления пользователем
   - Сохранение исправления для обучения
   - Обновление правил маршрутизации

4. **Ошибка парсинга:**
   - Логирование ошибки
   - Уведомление пользователя
   - Предложение альтернативных вариантов

---

## **💾 ИНТЕГРАЦИЯ С БД**

### **Новые таблицы:**

1. **Таблица `routing_history`:**
   ```sql
   CREATE TABLE routing_history (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       batch_id TEXT NOT NULL,
       filename TEXT NOT NULL,
       routing_map TEXT NOT NULL,  -- JSON
       confidence REAL,
       executed_module TEXT,
       success BOOLEAN,
       created_at TEXT NOT NULL
   )
   ```

2. **Таблица `routing_feedback`:**
   ```sql
   CREATE TABLE routing_feedback (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       routing_history_id INTEGER,
       user_correction TEXT,  -- JSON с исправлениями
       feedback_type TEXT,  -- 'correct', 'incorrect', 'partial'
       created_at TEXT NOT NULL,
       FOREIGN KEY (routing_history_id) REFERENCES routing_history(id)
   )
   ```

### **Использование истории:**
- Анализ успешности маршрутизации
- Обучение ИИ на исторических данных
- Улучшение accuracy со временем

---

## **🎯 КРИТЕРИИ УСПЕХА MVP**

- [ ] Обрабатывает ЛЮБЫЕ файлы энергоаудита (независимо от названия)
- [ ] Автоматически выбирает правильный модуль обработки в 90% случаев
- [ ] Данные попадают в корректные таблицы БД
- [ ] Снижение ручного вмешательства на 80%
- [ ] Система масштабируется для новых типов документов
- [ ] Время обработки < 10 секунд (быстрый анализ + маршрутизация)
- [ ] Fallback работает корректно при недоступности ИИ

---

## **⚠️ ИНТЕГРАЦИОННЫЕ ТРЕБОВАНИЯ**

### **СОВМЕСТИМОСТЬ С ТЗ:**
- ✅ Соответствие разделу 4.2 ТЗ (обработка файлов до 50 МБ)
- ✅ Интеграция с существующей БД (`uploads`, `parsed_data`, `node_consumption`)
- ✅ Поддержка эталонных шаблонов ПКМ-690
- ✅ Использование существующих парсеров как execution layer

### **ОБРАБОТКА НЕИЗВЕСТНЫХ ФАЙЛОВ:**
- При низком confidence (<70%) → маршрут `manual_review`
- Возможность обучения на новых типах документов
- Расширяемая база правил классификации

---

## **📊 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ**

### **Целевые показатели:**

- **Время обработки:**
  - Быстрый анализ: < 3 сек
  - Глубокий анализ: < 5 сек
  - Маршрутизация: < 2 сек
  - **Общее время: < 10 сек**

- **Точность:**
  - Accuracy: > 90%
  - Precision: > 85%
  - Recall: > 80%

- **Производительность:**
  - Обработка файлов до 50 МБ: < 30 сек (включая парсинг)
  - Batch обработка: параллельная обработка нескольких файлов

---

## **🚀 ПЛАН РЕАЛИЗАЦИИ**

### **Фаза 1: MVP (2-3 недели)**

1. ✅ Создать `intelligent_router.py` с базовой функциональностью
2. ✅ Реализовать быстрый анализ (2-3 сек)
3. ✅ Реализовать генерацию routing map
4. ✅ Интегрировать с существующими парсерами
5. ✅ Добавить fallback механизм
6. ✅ Тестирование на реальных файлах

### **Фаза 2: Расширение (2-3 недели)**

1. ✅ Реализовать глубокий анализ (3-5 сек)
2. ✅ Добавить обучение на ошибках
3. ✅ Создать таблицы БД для истории маршрутизации
4. ✅ Добавить метрики производительности
5. ✅ Оптимизация промптов

### **Фаза 3: Оптимизация (1-2 недели)**

1. ✅ Кэширование результатов
2. ✅ Batch обработка
3. ✅ Мониторинг производительности
4. ✅ Улучшение accuracy на основе обратной связи

---

**Готов к реализации!** 🚀


