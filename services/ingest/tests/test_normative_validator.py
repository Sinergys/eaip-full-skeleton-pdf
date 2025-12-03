"""
Тесты для модуля normative_validator.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.normative_validator import (
    validate_against_normative,
    check_critical_fields,
    get_top_fields_with_normatives,
    get_normative_statistics,
)


class TestValidateAgainstNormative:
    """Тесты для функции validate_against_normative"""

    @patch("domain.normative_validator.database")
    def test_validate_compliant(self, mock_db):
        """Тест: значение соответствует нормативу"""
        # Мокаем правила из БД
        mock_db.get_normative_rules_for_field.return_value = [
            {
                "id": 1,
                "numeric_value": 0.15,
                "extraction_confidence": 0.95,
                "unit": "кВт·ч/м²",
                "document_title": "PKM690",
            }
        ]

        result = validate_against_normative(
            actual_value=0.14,
            field_name="Удельный расход",
            sheet_name="Динамика ср",
        )

        assert result["status"] == "compliant"
        assert result["actual"] == 0.14
        assert result["normative"] == 0.15
        assert "Соответствует нормативу" in result["message"]

    @patch("domain.normative_validator.database")
    def test_validate_violation(self, mock_db):
        """Тест: значение превышает норматив"""
        mock_db.get_normative_rules_for_field.return_value = [
            {
                "id": 1,
                "numeric_value": 0.15,
                "extraction_confidence": 0.95,
                "unit": "кВт·ч/м²",
                "document_title": "PKM690",
            }
        ]

        result = validate_against_normative(
            actual_value=0.20,  # Превышение на 33%
            field_name="Удельный расход",
            sheet_name="Динамика ср",
            tolerance_percent=10.0,
        )

        assert result["status"] == "violation"
        assert result["actual"] == 0.20
        assert result["normative"] == 0.15
        assert "Превышение норматива" in result["message"]

    @patch("domain.normative_validator.database")
    def test_validate_no_normative(self, mock_db):
        """Тест: норматив не найден"""
        mock_db.get_normative_rules_for_field.return_value = []

        result = validate_against_normative(
            actual_value=0.18,
            field_name="Неизвестное поле",
            sheet_name="Лист",
        )

        assert result["status"] == "unknown"
        assert result["normative"] is None
        assert "Норматив не найден" in result["message"]

    @patch("domain.normative_validator.database")
    def test_validate_no_numeric_value(self, mock_db):
        """Тест: норматив не имеет числового значения"""
        mock_db.get_normative_rules_for_field.return_value = [
            {
                "id": 1,
                "numeric_value": None,
                "extraction_confidence": 0.95,
                "unit": "кВт·ч/м²",
            }
        ]

        result = validate_against_normative(
            actual_value=0.18,
            field_name="Удельный расход",
        )

        assert result["status"] == "unknown"
        assert result["normative"] is None
        assert "не имеет числового значения" in result["message"]

    @patch("domain.normative_validator.database")
    def test_validate_below_norm(self, mock_db):
        """Тест: значение ниже норматива"""
        mock_db.get_normative_rules_for_field.return_value = [
            {
                "id": 1,
                "numeric_value": 0.15,
                "extraction_confidence": 0.95,
                "unit": "кВт·ч/м²",
            }
        ]

        result = validate_against_normative(
            actual_value=0.10,  # Ниже на 33%
            field_name="Удельный расход",
            tolerance_percent=10.0,
        )

        assert result["status"] == "below_norm"
        assert "ниже норматива" in result["message"]


class TestCheckCriticalFields:
    """Тесты для функции check_critical_fields"""

    @patch("domain.normative_validator.database")
    def test_check_critical_fields(self, mock_db):
        """Тест: проверка критических полей"""
        # Мокаем правила для разных полей
        def mock_get_rules(field_name, sheet_name=None):
            if field_name == "Удельный расход":
                return [{"id": 1, "numeric_value": 0.15}]
            return []

        mock_db.get_normative_rules_for_field.side_effect = mock_get_rules

        result = check_critical_fields(enterprise_id=1)

        assert result["enterprise_id"] == 1
        assert result["total_critical_fields"] > 0
        assert "compliant" in result or "has_violations" in result["status"]


class TestGetTopFields:
    """Тесты для функции get_top_fields_with_normatives"""

    @patch("domain.normative_validator.database")
    def test_get_top_fields(self, mock_db):
        """Тест: получение топ полей"""
        # Создаем мок-строки, которые ведут себя как sqlite3.Row
        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_row1 = MockRow({
            "field_name": "Удельный расход",
            "sheet_name": "Динамика ср",
            "rules_count": 5,
        })
        mock_row2 = MockRow({
            "field_name": "Потери",
            "sheet_name": "08_Потери",
            "rules_count": 3,
        })

        mock_conn = MagicMock()
        mock_conn.row_factory = None
        mock_conn.execute.return_value.fetchall.return_value = [mock_row1, mock_row2]
        mock_db.get_connection.return_value.__enter__.return_value = mock_conn

        result = get_top_fields_with_normatives(limit=10)

        # Проверяем, что функция возвращает список
        assert isinstance(result, list)
        # Проверяем, что get_connection был вызван
        mock_db.get_connection.assert_called_once()


class TestGetNormativeStatistics:
    """Тесты для функции get_normative_statistics"""

    @patch("domain.normative_validator.database")
    @patch("domain.normative_validator.get_top_fields_with_normatives")
    def test_get_statistics(self, mock_top_fields, mock_db):
        """Тест: получение статистики"""
        mock_db.list_normative_documents.return_value = [
            {
                "id": 1,
                "title": "PKM690",
                "document_type": "PKM690",
                "rules_count": 10,
                "ai_processed": True,
            },
            {
                "id": 2,
                "title": "GOST",
                "document_type": "GOST",
                "rules_count": 5,
                "ai_processed": False,
            },
        ]

        mock_top_fields.return_value = [
            {"field_name": "Удельный расход", "rules_count": 5}
        ]

        result = get_normative_statistics()

        assert result["total_documents"] == 2
        assert result["total_rules"] == 15
        assert "PKM690" in result["by_type"]
        assert "GOST" in result["by_type"]
        assert len(result["top_fields"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

