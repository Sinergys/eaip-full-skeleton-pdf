# AI-Верификация и Анализ Энергетических Данных

## Обзор

Система использует AI для комплексной верификации и анализа энергетических данных согласно ПКМ №690. Это критически важная функция, которая обеспечивает качество и достоверность данных для всего энергоаудита.

## Архитектура

### Модули

1. **`ai_energy_verifier.py`** - Верификация энергопоказателей
   - Проверяет корректность данных согласно ПКМ №690
   - Валидирует единицы измерения ГОСТ
   - Проверяет логику баланса энергопотребления
   - Выявляет статистические аномалии

2. **`ai_anomaly_detector.py`** - Детекция аномалий
   - Выявляет резкие скачки потребления
   - Обнаруживает несоответствия между связанными показателями
   - Находит данные вне типичных диапазонов
   - Выявляет признаки ошибок ввода или измерений

3. **`ai_efficiency_analyzer.py`** - Анализ энергоэффективности
   - Рассчитывает удельное энергопотребление на единицу продукции
   - Вычисляет энергоемкость производства
   - Сравнивает с отраслевыми нормативами
   - Оценивает потенциал энергосбережения

4. **`ai_compliance_checker.py`** - Проверка соответствия ПКМ №690
   - Проверяет полноту данных по требуемым разделам
   - Валидирует баланс энергопотребления
   - Проверяет корректность коэффициентов трансформации
   - Валидирует форматы и единицы измерения

5. **`ai_energy_analysis.py`** - Объединяющий модуль
   - Выполняет полный AI-анализ энергетических данных
   - Объединяет результаты всех проверок
   - Вычисляет общую уверенность в данных

## Использование

### Настройка

AI-анализ автоматически включается, если:
1. AI провайдер настроен (см. `AI_SETUP.md`)
2. Переменная окружения `AI_ENABLED=true`

```env
AI_ENABLED=true
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-ваш-ключ
```

### Пример использования

```python
from ai_energy_analysis import enhanced_energy_analysis

# Извлеченные энергетические данные
extracted_data = {
    "enterprise_info": {...},
    "electricity": {...},
    "gas": {...},
    "water": {...},
    # ... другие разделы
}

# Полный AI-анализ
analysis_result = enhanced_energy_analysis(extracted_data)

# Результаты анализа
print(f"Валидно: {analysis_result['summary']['is_valid']}")
print(f"Аномалий: {analysis_result['anomalies']['anomaly_count']}")
print(f"Соответствует ПКМ №690: {analysis_result['summary']['is_compliant']}")
print(f"Класс энергоэффективности: {analysis_result['summary']['efficiency_class']}")
print(f"Уверенность: {analysis_result['confidence_score']:.2f}")
```

### Использование отдельных модулей

#### Верификация энергопоказателей

```python
from ai_energy_verifier import get_energy_data_verifier

verifier = get_energy_data_verifier()
if verifier:
    result = verifier.verify_energy_metrics(extracted_data, enterprise_type="промышленное")
    print(f"Валидно: {result['is_valid']}")
    print(f"Проблем: {len(result['issues'])}")
```

#### Детекция аномалий

```python
from ai_anomaly_detector import get_anomaly_detector

detector = get_anomaly_detector()
if detector:
    result = detector.detect_data_anomalies(extracted_data, historical_data)
    print(f"Найдено аномалий: {result['anomaly_count']}")
    print(f"Критических: {result['critical_count']}")
```

#### Анализ энергоэффективности

```python
from ai_efficiency_analyzer import get_efficiency_analyzer

analyzer = get_efficiency_analyzer()
if analyzer:
    result = analyzer.calculate_efficiency_metrics(extracted_data, production_data)
    print(f"Класс энергоэффективности: {result['comparison_with_normatives']['energy_class']}")
    print(f"Потенциал экономии: {result['potential_savings']['percent']}%")
```

#### Проверка соответствия ПКМ №690

```python
from ai_compliance_checker import get_compliance_checker

checker = get_compliance_checker()
if checker:
    result = checker.check_compliance(extracted_data)
    print(f"Соответствует: {result['is_compliant']}")
    print(f"Оценка соответствия: {result['compliance_score']:.2f}")
    print(f"Отсутствует разделов: {len(result['missing_sections'])}")
```

## Результаты анализа

### Структура результата

```json
{
  "verification": {
    "is_valid": true,
    "confidence": 0.95,
    "verified_sections": ["электроэнергия", "газ", "вода"],
    "issues": [],
    "warnings": [],
    "balance_check": {
      "is_balanced": true,
      "discrepancies": []
    },
    "compliance_score": 0.95
  },
  "anomalies": {
    "anomalies": [],
    "anomaly_count": 0,
    "severity_distribution": {
      "critical": 0,
      "warning": 0,
      "info": 0
    },
    "critical_count": 0,
    "warning_count": 0,
    "info_count": 0
  },
  "efficiency": {
    "efficiency_metrics": {
      "specific_consumption": {
        "electricity_per_unit": 123.45,
        "heat_per_unit": 67.89,
        "gas_per_unit": 12.34
      },
      "energy_intensity": {
        "total": 1.23,
        "by_resource": {
          "electricity": 0.5,
          "gas": 0.4,
          "heat": 0.3
        }
      },
      "trend": "stable"
    },
    "comparison_with_normatives": {
      "deviation_percent": 15.5,
      "energy_class": "C",
      "industry_average": 1.0,
      "enterprise_value": 1.15
    },
    "potential_savings": {
      "percent": 20.0,
      "priority_areas": ["освещение", "отопление"],
      "estimated_annual_savings": 5000000
    }
  },
  "compliance": {
    "is_compliant": true,
    "compliance_score": 0.95,
    "missing_sections": [],
    "present_sections": ["enterprise_info", "electricity", "gas", ...],
    "issues": [],
    "warnings": [],
    "balance_check": {
      "is_balanced": true,
      "discrepancies": []
    },
    "format_check": {
      "units_compliant": true,
      "formats_compliant": true,
      "issues": []
    }
  },
  "confidence_score": 0.90,
  "summary": {
    "is_valid": true,
    "has_anomalies": false,
    "is_compliant": true,
    "efficiency_class": "C"
  }
}
```

## Ожидаемые результаты

### Автоматическая верификация
- **95%+** загружаемых энергопаспортов проходят автоматическую верификацию
- Выявление проблем до сохранения в систему
- Рекомендации по исправлению ошибок

### Выявление аномалий
- **90%+** аномалий и ошибок в данных обнаруживаются автоматически
- Статистический анализ + AI-анализ
- Классификация по серьезности (critical/warning/info)

### Расчет показателей энергоэффективности
- Расчет в реальном времени
- Сравнение с отраслевыми нормативами
- Оценка потенциала энергосбережения

### Гарантия соответствия ПКМ №690
- Проверка полноты всех обязательных разделов
- Валидация балансов и коэффициентов
- Проверка форматов и единиц измерения

## Логирование

Система логирует все этапы AI-анализа:

```
INFO: Начинаю полный AI-анализ энергетических данных...
INFO: Начинаю AI-верификацию энергетических показателей...
INFO: AI-верификация завершена: валидно: true, проблем: 0, уверенность: 0.95
INFO: Начинаю AI-детекцию аномалий в энергетических данных...
INFO: AI-детекция аномалий завершена: найдено 0 аномалий (критических: 0)
INFO: Начинаю AI-анализ энергоэффективности...
INFO: AI-анализ энергоэффективности завершен
INFO: Начинаю AI-проверку соответствия ПКМ №690...
INFO: AI-проверка соответствия завершена: соответствует: true, оценка: 0.95, отсутствует разделов: 0
INFO: Полный AI-анализ завершен: валидно: true, аномалий: 0, соответствует: true, уверенность: 0.90
```

## Обработка ошибок

Система gracefully обрабатывает ошибки AI:
- Если AI недоступен, возвращаются базовые результаты
- Ошибки логируются, но не прерывают обработку
- Fallback на стандартные методы при сбоях

## Производительность

- AI-верификация: ~2-5 секунд на документ
- AI-детекция аномалий: ~2-4 секунды на документ
- AI-анализ энергоэффективности: ~3-6 секунд на документ
- AI-проверка соответствия: ~2-5 секунд на документ

**Общее время полного анализа:** ~10-20 секунд на документ

## Требования

- AI провайдер настроен (DeepSeek, OpenAI, Anthropic)
- `AI_ENABLED=true` в переменных окружения
- Доступ к AI API (интернет-соединение)

## Интеграция в пайплайн

AI-анализ можно интегрировать в пайплайн обработки данных:

```python
# После парсинга файла
parsing_result = parse_file(file_path)

# Если это энергетический паспорт
if is_energy_passport(parsing_result):
    # Полный AI-анализ
    analysis = enhanced_energy_analysis(parsing_result.get("data", {}))
    
    # Добавляем результаты анализа в результат парсинга
    parsing_result["ai_analysis"] = analysis
    
    # Проверяем, прошли ли данные верификацию
    if not analysis["summary"]["is_valid"]:
        logger.warning("Данные не прошли AI-верификацию")
    
    # Проверяем наличие аномалий
    if analysis["summary"]["has_anomalies"]:
        logger.warning(f"Обнаружено {analysis['anomalies']['anomaly_count']} аномалий")
```

## Отключение AI-анализа

Если нужно отключить AI-анализ:

```env
AI_ENABLED=false
```

Или просто не настраивать AI провайдер - система автоматически пропустит AI-анализ.

