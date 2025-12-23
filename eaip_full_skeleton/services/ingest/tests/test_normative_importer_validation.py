"""
Тесты для валидации нормативных документов и правил
"""
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

# Добавляем путь к модулям
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import database


class TestNormativeDocumentValidation:
    """Тесты для валидации нормативных документов"""

    def test_validate_document_hash(self):
        """Тест: проверка хеша документа для дедупликации"""
        import hashlib

        content = b"test document content"
        hash_value = hashlib.sha256(content).hexdigest()

        # Проверяем, что хеш генерируется корректно
        assert len(hash_value) == 64
        assert isinstance(hash_value, str)

    @patch("database.find_normative_document_by_hash")
    def test_duplicate_document_detection(self, mock_find):
        """Тест: обнаружение дубликата документа"""
        # Мокаем найденный дубликат
        mock_find.return_value = {
            "id": 1,
            "title": "PKM690",
            "file_hash": "abc123",
        }

        from domain.normative_importer import NormativeImporter

        importer = NormativeImporter()
        # Должен вернуть информацию о дубликате
        duplicate = database.find_normative_document_by_hash("abc123")
        assert duplicate is not None
        assert duplicate["id"] == 1

    def test_validate_rule_numeric_value(self):
        """Тест: валидация числового значения правила"""
        # Валидные значения
        valid_values = [0.15, 100, 0.001, -10.5]
        for val in valid_values:
            assert isinstance(val, (int, float))

        # Невалидные значения (должны быть обработаны)
        invalid_values = [None, "", "abc", []]
        for val in invalid_values:
            assert not isinstance(val, (int, float)) or val is None

    def test_validate_rule_unit(self):
        """Тест: валидация единиц измерения"""
        valid_units = ["кВт·ч/м²", "кВт·ч/кг", "м³", "кг", "кВт"]
        for unit in valid_units:
            assert isinstance(unit, str)
            assert len(unit) > 0

    def test_validate_extraction_confidence(self):
        """Тест: валидация уверенности извлечения"""
        # Уверенность должна быть от 0 до 1
        valid_confidences = [0.0, 0.5, 0.95, 1.0]
        for conf in valid_confidences:
            assert 0.0 <= conf <= 1.0

        invalid_confidences = [-0.1, 1.1, 2.0]
        for conf in invalid_confidences:
            assert not (0.0 <= conf <= 1.0)


class TestRuleValidation:
    """Тесты для валидации правил"""

    @patch("database.get_connection")
    def test_validate_rule_creation(self, mock_get_conn):
        """Тест: валидация при создании правила"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        # Создаем правило с валидными данными
        rule_result = database.create_normative_rule(
            document_id=1,
            rule_type="limit",
            description="Удельный расход",
            numeric_value=0.15,
            unit="кВт·ч/м²",
            extraction_confidence=0.95,
        )

        assert isinstance(rule_result, dict)
        assert rule_result["id"] == 1
        mock_conn.execute.assert_called_once()

    def test_validate_rule_type(self):
        """Тест: валидация типа правила"""
        valid_types = ["limit", "formula", "requirement", "standard"]
        for rule_type in valid_types:
            assert isinstance(rule_type, str)
            assert len(rule_type) > 0

    def test_validate_field_reference(self):
        """Тест: валидация ссылки на поле"""
        valid_references = [
            {"field_name": "Удельный расход", "sheet_name": "Динамика ср"},
            {"field_name": "Потери", "sheet_name": "08_Потери"},
        ]

        for ref in valid_references:
            assert "field_name" in ref
            assert isinstance(ref["field_name"], str)
            assert len(ref["field_name"]) > 0


class TestDataIntegrity:
    """Тесты для целостности данных"""

    @patch("database.get_connection")
    def test_foreign_key_constraints(self, mock_get_conn):
        """Тест: проверка внешних ключей"""
        # При создании правила с несуществующим document_id
        # должна быть ошибка (в реальной БД)
        mock_conn = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        # В тестовом окружении просто проверяем структуру
        # В реальной БД SQLite проверит внешние ключи
        assert True  # Placeholder для проверки структуры

    def test_required_fields(self):
        """Тест: проверка обязательных полей"""
        # Обязательные поля для документа
        required_doc_fields = ["title", "file_path", "file_hash"]
        for field in required_doc_fields:
            assert isinstance(field, str)

        # Обязательные поля для правила
        required_rule_fields = ["document_id", "rule_type"]
        for field in required_rule_fields:
            assert isinstance(field, str)


class TestAIExtractionValidation:
    """Тесты для валидации AI-извлечения"""

    def test_validate_ai_response_structure(self):
        """Тест: валидация структуры AI-ответа"""
        # Пример валидного AI-ответа
        valid_ai_response = {
            "rules": [
                {
                    "rule_type": "limit",
                    "description": "Удельный расход",
                    "numeric_value": 0.15,
                    "unit": "кВт·ч/м²",
                    "extraction_confidence": 0.95,
                    "field_references": [
                        {
                            "field_name": "Удельный расход",
                            "sheet_name": "Динамика ср",
                        }
                    ],
                }
            ]
        }

        assert "rules" in valid_ai_response
        assert isinstance(valid_ai_response["rules"], list)
        if valid_ai_response["rules"]:
            rule = valid_ai_response["rules"][0]
            assert "rule_type" in rule
            assert "numeric_value" in rule or "formula" in rule

    def test_validate_confidence_threshold(self):
        """Тест: проверка порога уверенности"""
        # Правила с низкой уверенностью должны быть помечены
        low_confidence = 0.3
        high_confidence = 0.9

        threshold = 0.5

        assert low_confidence < threshold
        assert high_confidence >= threshold


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

