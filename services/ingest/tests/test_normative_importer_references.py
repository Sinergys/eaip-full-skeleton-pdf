"""
Тесты для связей нормативных правил с полями энергопаспорта
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


class TestNormativeReferences:
    """Тесты для связей нормативных правил с полями"""

    @patch("database.get_connection")
    def test_create_normative_reference(self, mock_get_conn):
        """Тест создания связи правила с полем"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        result = database.create_normative_reference(
            rule_id=1,
            field_name="Удельный расход",
            sheet_name="Динамика ср",
            cell_reference="C5",
            passport_field_path="resources.electricity.specific_consumption",
        )

        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["field_name"] == "Удельный расход"
        mock_conn.execute.assert_called_once()
        call_args = mock_conn.execute.call_args
        assert "INSERT INTO normative_references" in call_args[0][0]

    @patch("database.get_connection")
    def test_get_normative_rules_for_field(self, mock_get_conn):
        """Тест получения правил для конкретного поля"""
        # Мокаем строки из БД
        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data[key]

            def keys(self):
                return self._data.keys()

        mock_row = MockRow({
            "id": 1,
            "document_id": 1,
            "rule_type": "limit",
            "numeric_value": 0.15,
            "unit": "кВт·ч/м²",
            "extraction_confidence": 0.95,
            "document_title": "PKM690",
            "document_type": "PKM690",
            "cell_reference": "C5",
            "parameters": "{}",
        })

        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [mock_row]
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        rules = database.get_normative_rules_for_field(
            field_name="Удельный расход",
            sheet_name="Динамика ср",
        )

        assert len(rules) == 1
        assert rules[0]["numeric_value"] == 0.15
        # field_name не возвращается в правилах, только в references
        assert "document_title" in rules[0]

    @patch("database.get_connection")
    def test_get_normative_rules_for_field_no_sheet(self, mock_get_conn):
        """Тест получения правил без указания листа"""
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = []
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        rules = database.get_normative_rules_for_field(
            field_name="Удельный расход",
            sheet_name=None,
        )

        assert isinstance(rules, list)
        # Проверяем, что запрос выполнен без sheet_name
        mock_conn.execute.assert_called()
        call_args = mock_conn.execute.call_args
        # В WHERE должно быть только field_name
        assert "nref.field_name = ?" in call_args[0][0]

    @patch("domain.normative_importer.database")
    def test_importer_creates_references(self, mock_db):
        """Тест: импортер создает связи с полями"""
        from domain.normative_importer import NormativeImporter

        # Мокаем AI-ответ - _extract_rules_with_ai возвращает список правил
        mock_ai_response = [
            {
                "rule_type": "limit",
                "description": "Удельный расход электроэнергии",
                "numeric_value": 0.15,
                "unit": "кВт·ч/м²",
                "confidence": 0.95,
                "references": [  # Используем "references", а не "field_references"
                    {
                        "field_name": "Удельный расход",
                        "sheet_name": "Динамика ср",
                        "cell_reference": "C5",
                    }
                ],
            }
        ]

        mock_db.find_normative_document_by_hash.return_value = None
        mock_db.create_normative_document.return_value = {"id": 1}
        mock_db.create_normative_rule.return_value = {"id": 1}
        mock_db.create_normative_reference.return_value = {"id": 1}

        # Мокаем парсинг файла
        with patch("domain.normative_importer.parse_file") as mock_parse:
            mock_parse.return_value = {
                "text": "Удельный расход электроэнергии не должен превышать 0.15 кВт·ч/м²",
                "file_type": "pdf",
            }

            # Мокаем AI-анализ
            with patch.object(
                NormativeImporter, "_extract_rules_with_ai", return_value=mock_ai_response
            ):
                importer = NormativeImporter()
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(b"fake pdf content")
                    tmp_path = tmp.name

                try:
                    result = importer.import_normative_document(tmp_path)
                    # Проверяем, что создана связь
                    mock_db.create_normative_reference.assert_called()
                finally:
                    Path(tmp_path).unlink(missing_ok=True)

    @patch("database.get_connection")
    def test_multiple_references_for_one_rule(self, mock_get_conn):
        """Тест: одно правило может быть связано с несколькими полями"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        mock_get_conn.return_value.__enter__.return_value = mock_conn

        # Создаем несколько связей для одного правила
        ref1 = database.create_normative_reference(
            rule_id=1,
            field_name="Удельный расход",
            sheet_name="Динамика ср",
        )
        ref2 = database.create_normative_reference(
            rule_id=1,
            field_name="Удельный расход электроэнергии",
            sheet_name="Расход на ед.п",
        )

        assert isinstance(ref1, dict)
        assert isinstance(ref2, dict)
        assert ref1["id"] == 1
        assert ref2["id"] == 1
        # Проверяем, что было два вызова
        assert mock_conn.execute.call_count == 2


class TestFieldReferenceMatching:
    """Тесты для сопоставления полей с правилами"""

    def test_field_name_matching(self):
        """Тест: сопоставление по точному имени поля"""
        # Симуляция поиска правил
        field_name = "Удельный расход"
        rules = database.get_normative_rules_for_field(field_name, "Динамика ср")

        # Проверяем, что поиск работает
        assert isinstance(rules, list)

    def test_field_name_partial_matching(self):
        """Тест: частичное совпадение имен полей"""
        # В реальной системе может быть нечеткое сопоставление
        # Пока проверяем базовую функциональность
        field_name = "Удельный расход электроэнергии"
        rules = database.get_normative_rules_for_field(field_name, None)

        assert isinstance(rules, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

