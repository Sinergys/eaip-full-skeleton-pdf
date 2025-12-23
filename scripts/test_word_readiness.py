"""Тестовый скрипт для проверки readiness-валидации Word-отчёта."""
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

from domain.report_data import ReportData
from utils.word_readiness_validator import validate_word_report_readiness, get_missing_data_summary

# Тестовые данные
test_data = {
    'resources': {
        'electricity': {
            '2022-Q1': {
                'quarter_totals': {
                    'active_kwh': 1000,
                    'cost_sum': 150000
                }
            }
        },
        'gas': {
            '2022-Q1': {
                'quarter_totals': {
                    'volume_m3': 500,
                    'cost_sum': 75000
                }
            }
        },
        'water': {
            '2022-Q1': {
                'quarter_totals': {
                    'volume_m3': 200,
                    'cost_sum': 30000
                }
            }
        }
    }
}

# Создаем ReportData
rd = ReportData.from_raw_data(
    aggregated_data=test_data,
    enterprise_data={'name': 'Тест', 'address': 'Адрес'}
)

# Проверяем готовность
result = validate_word_report_readiness(rd)

print('✅ Проверка готовности выполнена')
print(f'Готовность: {result["ready"]}')
print(f'Оценка: {result["completeness_score"]*100:.0f}%')
print(f'Готовых разделов: {result["ready_sections_count"]}/{result["total_sections_count"]}')
print()
print('Сводка:')
print(get_missing_data_summary(result))

