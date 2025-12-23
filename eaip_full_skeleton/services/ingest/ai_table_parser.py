"""
Модуль для структурирования таблиц через AI
Помогает восстановить структуру таблиц после OCR
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Импорт AI парсера
try:
    from ai_parser import get_ai_parser

    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.warning("ai_parser модуль не найден. AI-структурирование таблиц недоступно.")


class AITableParser:
    """
    Класс для структурирования таблиц через AI
    """

    def __init__(self):
        self.ai_parser = None
        self.enabled = False

        # Проверяем доступность AI
        if HAS_AI_PARSER:
            try:
                self.ai_parser = get_ai_parser()
                if self.ai_parser and self.ai_parser.enabled:
                    self.enabled = True
                    logger.info("AI-структурирование таблиц включено")
                else:
                    logger.debug(
                        "AI парсер недоступен, AI-структурирование таблиц отключено"
                    )
            except Exception as e:
                logger.warning(f"Не удалось инициализировать AI парсер для таблиц: {e}")

    def ai_table_structure(
        self, messy_table_data: str, page_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        AI помогает восстановить структуру таблицы из сырых данных OCR

        Args:
            messy_table_data: Сырые данные таблицы из OCR
            page_number: Номер страницы (опционально)

        Returns:
            Словарь со структурированной таблицей
        """
        if not self.enabled or not self.ai_parser:
            return {"table": [], "headers": [], "rows": [], "ai_used": False}

        try:
            logger.info(
                f"Начинаю AI-структурирование таблицы (страница {page_number or 'N/A'})..."
            )

            # Формируем промпт для структурирования
            prompt = self._build_table_structure_prompt(messy_table_data)

            # Отправляем запрос в AI
            structured_table = self._call_ai_table_structure(prompt)

            # Парсим результат
            parsed_result = self._parse_table_result(structured_table)

            logger.info(
                f"AI-структурирование таблицы завершено: "
                f"строк: {len(parsed_result.get('rows', []))}, "
                f"столбцов: {len(parsed_result.get('headers', []))}"
            )

            return parsed_result

        except Exception as e:
            logger.error(f"Ошибка при AI-структурировании таблицы: {e}")
            return {
                "table": [],
                "headers": [],
                "rows": [],
                "ai_used": False,
                "error": str(e),
            }

    def _build_table_structure_prompt(self, messy_data: str) -> str:
        """
        Формирует промпт для AI-структурирования таблицы
        """
        prompt = f"""Восстанови структуру таблицы из сырых данных OCR.

Сырые данные OCR:
{messy_data[:3000]}  # Ограничиваем размер

Определи:
1. Заголовки столбцов (если есть)
2. Строки данных
3. Числовые и текстовые ячейки
4. Единицы измерения в столбцах (если есть)
5. Тип данных в каждом столбце

Верни результат в формате JSON:
{{
    "headers": ["столбец1", "столбец2", "столбец3"],
    "rows": [
        ["значение1", "значение2", "значение3"],
        ["значение4", "значение5", "значение6"]
    ],
    "column_types": ["text", "number", "number"],
    "units": ["", "кВт·ч", "Гкал"],
    "confidence": 0.95
}}
"""
        return prompt

    def _call_ai_table_structure(self, prompt: str) -> str:
        """
        Вызывает AI для структурирования таблицы
        """
        if not self.ai_parser or not self.ai_parser.enabled:
            raise ValueError("AI парсер недоступен")

        provider = self.ai_parser.provider

        try:
            if provider in ["deepseek", "openai"]:
                response = self.ai_parser.client.chat.completions.create(
                    model=self.ai_parser.model_text,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты эксперт по структурированию табличных данных из OCR. Твоя задача - восстановить структуру таблицы из сырых данных OCR. Всегда возвращай валидный JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"}
                    if provider == "openai"
                    else None,
                    max_tokens=3000,
                    temperature=0.2,  # Низкая температура для более точного структурирования
                )
                return response.choices[0].message.content.strip()

            elif provider == "anthropic":
                response = self.ai_parser.client.messages.create(
                    model=self.ai_parser.model_text,
                    max_tokens=3000,
                    temperature=0.2,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()

            else:
                raise ValueError(f"Неподдерживаемый провайдер: {provider}")

        except Exception as e:
            logger.error(f"Ошибка при вызове AI для структурирования таблицы: {e}")
            raise

    def _parse_table_result(self, ai_response: str) -> Dict[str, Any]:
        """
        Парсит результат структурирования таблицы от AI
        """
        import json

        try:
            # Извлекаем JSON из ответа (может быть обернут в markdown)
            if "```json" in ai_response:
                json_text = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_text = ai_response.split("```")[1].split("```")[0].strip()
            else:
                json_text = ai_response.strip()

            result = json.loads(json_text)

            # Нормализуем структуру
            headers = result.get("headers", [])
            rows = result.get("rows", [])

            # Формируем полную таблицу
            table = []
            if headers:
                table.append(headers)
            table.extend(rows)

            return {
                "table": table,
                "headers": headers,
                "rows": rows,
                "column_types": result.get("column_types", []),
                "units": result.get("units", []),
                "confidence": result.get("confidence", 0.8),
                "ai_used": True,
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Не удалось распарсить JSON ответ AI: {e}")
            logger.debug(f"Ответ AI: {ai_response[:500]}")

            return {
                "table": [],
                "headers": [],
                "rows": [],
                "ai_used": True,
                "error": "Не удалось распарсить структурированный ответ AI",
                "raw_response": ai_response,
            }

    def structure_multiple_tables(
        self, tables_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Структурирует несколько таблиц

        Args:
            tables_data: Список словарей с данными таблиц

        Returns:
            Список структурированных таблиц
        """
        structured_tables = []

        for table_data in tables_data:
            messy_text = table_data.get("text", "")
            page_num = table_data.get("page", None)

            if messy_text:
                structured = self.ai_table_structure(messy_text, page_number=page_num)
                structured_tables.append({**table_data, **structured})
            else:
                structured_tables.append(table_data)

        return structured_tables


def get_ai_table_parser() -> Optional[AITableParser]:
    """
    Получить экземпляр AI-парсера таблиц

    Returns:
        AITableParser или None если AI недоступен
    """
    try:
        parser = AITableParser()
        if parser.enabled:
            return parser
        return None
    except Exception as e:
        logger.warning(f"Не удалось инициализировать AI-парсер таблиц: {e}")
        return None
