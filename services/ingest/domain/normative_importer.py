"""
Модуль импорта нормативных документов с AI-анализом
Извлекает формулы, нормативы и требования из документов (PDF, Word, Excel)
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Импорт AI-модулей
try:
    from ai_parser import get_ai_parser

    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.warning("ai_parser модуль не найден. AI-анализ недоступен.")

try:
    from ai_table_parser import get_ai_table_parser

    HAS_AI_TABLE_PARSER = True
except ImportError:
    HAS_AI_TABLE_PARSER = False
    logger.debug("ai_table_parser модуль не найден.")

try:
    from file_parser import parse_file

    HAS_FILE_PARSER = True
except ImportError:
    HAS_FILE_PARSER = False
    logger.warning("file_parser модуль не найден.")

# Импорт database функций
try:
    import database

    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logger.error("database модуль не найден.")


class NormativeImporter:
    """
    Класс для импорта и анализа нормативных документов
    """

    def __init__(self):
        self.ai_parser = None
        self.ai_table_parser = None

        if HAS_AI_PARSER:
            try:
                self.ai_parser = get_ai_parser()
                if self.ai_parser and not self.ai_parser.enabled:
                    logger.warning("AI парсер доступен, но отключен (AI_ENABLED=false)")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать AI парсер: {e}")

        if HAS_AI_TABLE_PARSER:
            try:
                self.ai_table_parser = get_ai_table_parser()
            except Exception as e:
                logger.debug(f"Не удалось инициализировать AI table parser: {e}")

    def import_normative_document(
        self,
        file_path: str,
        title: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Импортировать нормативный документ с AI-анализом

        Args:
            file_path: Путь к файлу документа
            title: Название документа (если None, берется из имени файла)
            document_type: Тип документа (PKM690, GOST, SNiP и т.д.)

        Returns:
            Словарь с результатами импорта
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        # Определяем тип документа если не указан
        if not document_type:
            document_type = self._detect_document_type(file_path)

        # Определяем название если не указано
        if not title:
            title = path.stem

        # Вычисляем хеш файла
        file_hash = self._calculate_file_hash(file_path)
        file_size = path.stat().st_size

        # Проверка на дубликаты (дедупликация)
        if not HAS_DATABASE:
            raise RuntimeError("database модуль недоступен")

        existing_doc = database.find_normative_document_by_hash(file_hash)
        if existing_doc:
            rules_count = database.count_rules_for_document(existing_doc["id"])
            logger.info(
                f"⚠️ Документ уже импортирован ранее: ID={existing_doc['id']}, "
                f"правил={rules_count}, загружен={existing_doc.get('uploaded_at')}"
            )
            return {
                "document_id": existing_doc["id"],
                "title": existing_doc["title"],
                "document_type": existing_doc["document_type"],
                "rules_extracted": rules_count,
                "references_created": 0,  # Не пересчитываем
                "status": "duplicate",
                "message": f"Документ уже был импортирован ранее (ID={existing_doc['id']})",
                "existing_document": {
                    "id": existing_doc["id"],
                    "uploaded_at": existing_doc.get("uploaded_at"),
                    "rules_count": rules_count,
                },
            }

        # Парсим файл
        try:
            parsed_result = self._parse_document(file_path)
        except Exception as e:
            logger.error(f"Ошибка парсинга документа: {e}")
            # Создаем запись даже при ошибке парсинга (для отслеживания)
            doc_record = database.create_normative_document(
                title=title,
                document_type=document_type,
                file_path=str(path.absolute()),
                file_hash=file_hash,
                file_size=file_size,
                full_text=None,
                parsed_data_json=None,
            )
            doc_id = doc_record["id"]
            database.update_normative_document_status(
                doc_id, ai_processed=False, processing_status="error"
            )
            raise

        # Извлекаем полный текст
        full_text = self._extract_text_content(parsed_result)
        parsed_data_json = json.dumps(parsed_result, ensure_ascii=False) if parsed_result else None

        # Создаем запись в БД с полным текстом
        doc_record = database.create_normative_document(
            title=title,
            document_type=document_type,
            file_path=str(path.absolute()),
            file_hash=file_hash,
            file_size=file_size,
            full_text=full_text,
            parsed_data_json=parsed_data_json,
        )

        doc_id = doc_record["id"]
        logger.info(f"Создана запись нормативного документа ID={doc_id}: {title}")

        # AI-анализ для извлечения формул и нормативов
        try:
            extracted_rules = self._extract_rules_with_ai(
                parsed_result, doc_id, document_type
            )

            # Сохраняем извлеченные правила в БД
            rules_count = 0
            references_count = 0

            for rule_data in extracted_rules:
                rule_record = database.create_normative_rule(
                    document_id=doc_id,
                    rule_type=rule_data.get("rule_type", "unknown"),
                    description=rule_data.get("description"),
                    formula=rule_data.get("formula"),
                    parameters=rule_data.get("parameters"),
                    numeric_value=rule_data.get("numeric_value"),
                    unit=rule_data.get("unit"),
                    ai_extracted=rule_data.get("ai_extracted", True),
                    extraction_confidence=rule_data.get("confidence", 0.5),
                )
                rules_count += 1

                # Создаем связи с полями паспорта
                references = rule_data.get("references", [])
                for ref in references:
                    database.create_normative_reference(
                        rule_id=rule_record["id"],
                        field_name=ref.get("field_name"),
                        sheet_name=ref.get("sheet_name"),
                        cell_reference=ref.get("cell_reference"),
                        passport_field_path=ref.get("passport_field_path"),
                    )
                    references_count += 1

            # Обновляем статус (текст уже сохранен при создании)
            database.update_normative_document_status(
                doc_id, ai_processed=True, processing_status="processed"
            )

            logger.info(
                f"✅ Нормативный документ обработан: "
                f"ID={doc_id}, правил={rules_count}, связей={references_count}"
            )

            return {
                "document_id": doc_id,
                "title": title,
                "document_type": document_type,
                "rules_extracted": rules_count,
                "references_created": references_count,
                "status": "processed",
            }

        except Exception as e:
            logger.error(f"Ошибка AI-анализа документа: {e}")
            database.update_normative_document_status(
                doc_id, ai_processed=False, processing_status="partial"
            )
            return {
                "document_id": doc_id,
                "title": title,
                "document_type": document_type,
                "status": "partial",
                "error": str(e),
            }

    def _detect_document_type(self, file_path: str) -> str:
        """Определить тип документа по имени файла"""
        path_lower = Path(file_path).name.lower()

        if "pkm" in path_lower or "690" in path_lower:
            return "PKM690"
        elif "gost" in path_lower or "гост" in path_lower:
            return "GOST"
        elif "snip" in path_lower or "снип" in path_lower:
            return "SNiP"
        elif "sanpin" in path_lower or "санпин" in path_lower:
            return "SanPiN"
        elif "pue" in path_lower or "пуэ" in path_lower:
            return "PUE"
        elif "ptee" in path_lower or "птээп" in path_lower:
            return "PTEEP"
        else:
            return "normative"

    def _calculate_file_hash(self, file_path: str) -> str:
        """Вычислить SHA1 хеш файла"""
        sha1 = hashlib.sha1()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()

    def _parse_document(self, file_path: str) -> Dict[str, Any]:
        """Парсить документ используя file_parser"""
        if not HAS_FILE_PARSER:
            raise RuntimeError("file_parser модуль недоступен")

        logger.info(f"Парсинг документа: {file_path}")
        return parse_file(file_path)

    def _extract_rules_with_ai(
        self,
        parsed_result: Dict[str, Any],
        document_id: int,
        document_type: str,
    ) -> List[Dict[str, Any]]:
        """
        Извлечь правила, формулы и нормативы из распарсенного документа с помощью AI

        Args:
            parsed_result: Результат парсинга документа
            document_id: ID документа в БД
            document_type: Тип документа

        Returns:
            Список извлеченных правил
        """
        if not self.ai_parser or not self.ai_parser.enabled:
            logger.warning("AI парсер недоступен, пропускаем AI-анализ")
            return []

        # Получаем текст из распарсенного документа
        text_content = self._extract_text_content(parsed_result)

        if not text_content:
            logger.warning("Не удалось извлечь текст из документа для AI-анализа")
            return []

        logger.info(
            f"Начинаю AI-анализ нормативного документа (тип: {document_type})..."
        )

        # Формируем промпт для AI
        prompt = self._build_extraction_prompt(text_content, document_type)

        try:
            # Вызываем AI для извлечения правил
            ai_response = self._call_ai_extraction(prompt)

            # Парсим ответ AI
            extracted_rules = self._parse_ai_extraction_result(
                ai_response, document_type
            )

            logger.info(f"AI извлек {len(extracted_rules)} правил из документа")
            return extracted_rules

        except Exception as e:
            logger.error(f"Ошибка AI-извлечения правил: {e}")
            return []

    def _extract_text_content(self, parsed_result: Dict[str, Any]) -> str:
        """Извлечь текстовое содержимое из результата парсинга"""
        # Пробуем разные источники текста
        text_parts = []

        # Из parsing.data.text (для PDF)
        parsing_data = parsed_result.get("parsing", {})
        if isinstance(parsing_data, dict):
            data = parsing_data.get("data", {})
            if isinstance(data, dict):
                text = data.get("text")
                if text and isinstance(text, str):
                    text_parts.append(text)

        # Из parsing.data.paragraphs (для Word)
        if isinstance(parsing_data, dict):
            data = parsing_data.get("data", {})
            if isinstance(data, dict):
                paragraphs = data.get("paragraphs", [])
                if paragraphs:
                    para_texts = [
                        p.get("text", "")
                        for p in paragraphs
                        if isinstance(p, dict) and p.get("text")
                    ]
                    text_parts.append("\n".join(para_texts))

        # Из parsing.data.sheets (для Excel) - извлекаем текст из ячеек
        if isinstance(parsing_data, dict):
            data = parsing_data.get("data", {})
            if isinstance(data, dict):
                sheets = data.get("sheets", [])
                for sheet in sheets:
                    if isinstance(sheet, dict):
                        rows = sheet.get("rows", [])
                        for row in rows:
                            if isinstance(row, list):
                                row_text = "\t".join(
                                    str(cell) if cell is not None else ""
                                    for cell in row
                                )
                                text_parts.append(row_text)

        return "\n\n".join(text_parts)

    def _build_extraction_prompt(self, text_content: str, document_type: str) -> str:
        """Построить промпт для AI-извлечения правил"""
        # Ограничиваем размер текста для экономии токенов
        max_chars = 15000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "\n... [текст обрезан]"

        prompt = f"""Проанализируй нормативный документ типа "{document_type}" и извлеки все формулы, нормативы и правила.

Текст документа:
{text_content}

Извлеки следующую информацию и верни в формате JSON:

1. **Формулы расчета** - математические формулы с описанием переменных
2. **Числовые нормативы** - конкретные значения (кВт·ч/м², коэффициенты и т.д.)
3. **Требования** - текстовые требования к расчетам
4. **Связи с полями энергопаспорта** - укажи, к каким полям паспорта относятся правила

Формат ответа:
{{
    "rules": [
        {{
            "rule_type": "formula|normative|requirement",
            "description": "Описание правила",
            "formula": "формула если есть (например, Q = A * ΔT / R)",
            "parameters": {{"A": "площадь, м²", "ΔT": "разница температур, °C", "R": "сопротивление, м²·°C/Вт"}},
            "numeric_value": 0.15,  // если есть конкретное числовое значение
            "unit": "кВт·ч/м²·год",  // единица измерения
            "confidence": 0.9,  // уверенность в извлечении (0-1)
            "references": [  // связь с полями энергопаспорта
                {{
                    "field_name": "Удельный расход электроэнергии",
                    "sheet_name": "Динамика ср",
                    "cell_reference": "C5",
                    "passport_field_path": "resources.electricity.specific_consumption"
                }}
            ]
        }}
    ]
}}

Важно:
- Для формул укажи все параметры с их единицами измерения
- Для нормативов укажи конкретные числовые значения и единицы
- Попытайся связать каждое правило с соответствующим полем энергопаспорта
- Если не уверен в связи, оставь references пустым
"""
        return prompt

    def _call_ai_extraction(self, prompt: str) -> str:
        """Вызвать AI для извлечения правил"""
        if not self.ai_parser:
            raise RuntimeError("AI парсер недоступен")

        try:
            # Используем text-модель для анализа структурированного текста
            if hasattr(self.ai_parser, "client") and self.ai_parser.client:
                if hasattr(self.ai_parser, "model_text"):
                    model = self.ai_parser.model_text
                else:
                    model = "deepseek-chat"

                response = self.ai_parser.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты эксперт по нормативным документам энергетики. Извлекай формулы, нормативы и требования с максимальной точностью.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,  # Низкая температура для точности
                    max_tokens=4000,
                )

                return response.choices[0].message.content
            else:
                raise RuntimeError("AI клиент не настроен")

        except Exception as e:
            logger.error(f"Ошибка вызова AI: {e}")
            raise

    def _parse_ai_extraction_result(
        self, ai_response: str, document_type: str
    ) -> List[Dict[str, Any]]:
        """Распарсить результат AI-извлечения"""
        try:
            # Извлекаем JSON из ответа
            json_text = ai_response
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()

            result = json.loads(json_text)
            rules = result.get("rules", [])

            # Валидируем и нормализуем правила
            normalized_rules = []
            for rule in rules:
                if not isinstance(rule, dict):
                    continue

                # Убеждаемся что есть минимум rule_type
                if "rule_type" not in rule:
                    rule["rule_type"] = "unknown"

                normalized_rules.append(rule)

            return normalized_rules

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON ответа AI: {e}")
            logger.debug(f"Ответ AI: {ai_response[:500]}")
            return []
        except Exception as e:
            logger.error(f"Ошибка обработки результата AI: {e}")
            return []


def get_normative_importer() -> Optional[NormativeImporter]:
    """Получить экземпляр импортера нормативных документов"""
    try:
        return NormativeImporter()
    except Exception as e:
        logger.error(f"Не удалось создать NormativeImporter: {e}")
        return None
