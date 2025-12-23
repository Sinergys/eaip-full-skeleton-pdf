"""
ИИ-классификатор содержимого файлов для определения типа энергоресурса.

Использует LLM для анализа структуры данных и определения типа ресурса
на основе содержимого файла, а не только имени файла.
"""

import logging
import json
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Попытка импорта AI парсера
try:
    from ai_parser import get_ai_parser

    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.debug("ai_parser модуль не найден. AI-классификация недоступна.")

# Попытка импорта настроек AI
try:
    from settings.ai_settings import has_ai_config

    HAS_AI_SETTINGS = True
except ImportError:
    HAS_AI_SETTINGS = False
    logger.debug("settings.ai_settings модуль не найден. AI-классификация недоступна.")


class AIContentClassifier:
    """
    ИИ-классификатор содержимого файлов для определения типа энергоресурса.

    Использует LLM для анализа структуры данных и определения типа ресурса
    на основе содержимого файла, когда правила не уверены.
    """

    def __init__(self):
        """Инициализация AI классификатора"""
        self.ai_parser = None
        self.enabled = False

        # Проверяем доступность AI
        if HAS_AI_PARSER and HAS_AI_SETTINGS:
            try:
                if has_ai_config():
                    self.ai_parser = get_ai_parser()
                    if self.ai_parser and self.ai_parser.enabled:
                        self.enabled = True
                        logger.info("AI классификатор инициализирован и готов к работе")
                    else:
                        logger.debug("AI парсер недоступен или отключен")
                else:
                    logger.debug("AI не настроен (нет валидной конфигурации)")
            except Exception as e:
                logger.warning(f"Ошибка инициализации AI классификатора: {e}")
                self.enabled = False
        else:
            logger.debug("AI классификатор недоступен (модули не найдены)")

    def classify_with_ai(
        self, raw_json: Dict[str, Any], filename: str
    ) -> Tuple[Optional[str], float]:
        """
        Классификация типа ресурса с помощью ИИ.

        Args:
            raw_json: Распарсенные данные файла
            filename: Имя файла

        Returns:
            Кортеж (тип_ресурса, уверенность_0.0-1.0) или (None, 0.0) при ошибке
        """
        if not self.enabled or not self.ai_parser:
            return (None, 0.0)

        if not raw_json:
            return (None, 0.0)

        try:
            # Подготавливаем данные для анализа
            analysis_data = self._prepare_analysis_data(raw_json, filename)

            # Формируем промпт для AI
            prompt = self._build_classification_prompt(analysis_data)

            # Вызываем AI для классификации
            result = self._call_ai_classification(prompt)

            if result:
                resource_type = result.get("resource_type")
                confidence = result.get("confidence", 0.0)

                if resource_type and confidence > 0.5:
                    logger.info(
                        f"AI определил тип ресурса: {resource_type} "
                        f"(уверенность: {confidence:.2f}) для файла {filename}"
                    )
                    return (resource_type, confidence)
                else:
                    logger.debug(
                        f"AI не смог определить тип ресурса с достаточной уверенностью "
                        f"(уверенность: {confidence:.2f}) для файла {filename}"
                    )

            return (None, 0.0)

        except Exception as e:
            logger.warning(f"Ошибка при AI классификации файла {filename}: {e}")
            return (None, 0.0)

    def _prepare_analysis_data(
        self, raw_json: Dict[str, Any], filename: str
    ) -> Dict[str, Any]:
        """
        Подготавливает данные для анализа AI.

        Извлекает ключевую информацию из raw_json для отправки в AI.
        """
        file_type = raw_json.get("file_type", "").lower()
        parsing_data = raw_json.get("parsing", {}).get("data", {})

        analysis_data = {"filename": filename, "file_type": file_type, "summary": {}}

        if file_type in ("excel", "xlsx"):
            # Для Excel извлекаем названия листов и заголовки
            sheets = parsing_data.get("sheets", [])
            sheet_names = [
                sheet.get("name", "") for sheet in sheets[:5]
            ]  # Первые 5 листов

            # Извлекаем заголовки из первых строк каждого листа
            headers = []
            for sheet in sheets[:3]:  # Первые 3 листа
                rows = sheet.get("rows", [])
                for row in rows[:3]:  # Первые 3 строки
                    if isinstance(row, list):
                        row_text = " ".join(
                            str(cell) for cell in row[:10] if cell
                        )  # Первые 10 колонок
                        if row_text.strip():
                            headers.append(row_text[:200])  # Ограничиваем длину

            analysis_data["summary"] = {
                "sheet_names": sheet_names,
                "headers": headers[:10],  # Первые 10 заголовков
                "total_sheets": len(sheets),
            }

        elif file_type == "pdf":
            # Для PDF извлекаем текст
            text = parsing_data.get("text", "")
            # Берем первые 2000 символов для анализа
            analysis_data["summary"] = {
                "text_preview": text[:2000] if text else "",
                "total_characters": len(text) if text else 0,
            }

        return analysis_data

    def _build_classification_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """
        Формирует промпт для AI классификации.

        Args:
            analysis_data: Подготовленные данные для анализа

        Returns:
            Промпт для отправки в AI
        """
        filename = analysis_data.get("filename", "unknown")
        file_type = analysis_data.get("file_type", "unknown")
        summary = analysis_data.get("summary", {})

        prompt = f"""Проанализируй содержимое файла и определи тип энергоресурса.

Имя файла: {filename}
Тип файла: {file_type}

"""

        if file_type in ("excel", "xlsx"):
            sheet_names = summary.get("sheet_names", [])
            headers = summary.get("headers", [])

            prompt += f"""Структура файла:
- Названия листов: {", ".join(sheet_names) if sheet_names else "не указаны"}
- Заголовки таблиц:
"""
            for i, header in enumerate(headers[:5], 1):
                prompt += f"  {i}. {header}\n"

        elif file_type == "pdf":
            text_preview = summary.get("text_preview", "")
            prompt += f"""Текст документа (первые 2000 символов):
{text_preview}
"""

        prompt += """
Определи тип энергоресурса на основе содержимого файла.

Доступные типы ресурсов:
- electricity: Электроэнергия (кВт·ч, кВт, кВтч)
- gas: Газ (м³, м3, кубометры)
- water: Вода (м³, м3, литры, СУВ, ХВС, ГВС)
- heat: Тепловая энергия (Гкал, ккал, отопление, котел)
- fuel: Топливо и ГСМ (мазут, дизельное топливо, тонны, литры)
- coal: Уголь (тонны, кг)
- equipment: Оборудование (списки оборудования, техники)
- envelope: Ограждающие конструкции (расчет теплопотерь, стены, окна)
- nodes: Узлы учета (счетчики, приборы учета)
- other: Прочее (если не подходит ни один тип)

Верни результат в формате JSON:
{
    "resource_type": "тип_ресурса",
    "confidence": 0.0-1.0,
    "reasoning": "краткое объяснение почему выбран этот тип"
}

Важно:
- Анализируй содержимое файла, а не только имя файла
- Обращай внимание на единицы измерения (кВт·ч, м³, Гкал и т.д.)
- Обращай внимание на названия листов и заголовки таблиц
- Если уверенность низкая (< 0.7), верни "other" с низкой уверенностью
"""

        return prompt

    def _call_ai_classification(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Вызывает AI для классификации.

        Args:
            prompt: Промпт для AI

        Returns:
            Результат классификации или None при ошибке
        """
        if not self.ai_parser or not self.ai_parser.enabled:
            return None

        try:
            # Используем text модель для классификации
            provider = self.ai_parser.provider
            model = self.ai_parser.model_text

            if provider in ("deepseek", "openai"):
                # OpenAI-совместимый API
                response = self.ai_parser.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты помощник для классификации энергетических документов. Всегда возвращай валидный JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"}
                    if provider == "openai"
                    else None,
                    max_tokens=500,
                    temperature=0.3,  # Низкая температура для более детерминированных результатов
                )
                result_text = response.choices[0].message.content

            elif provider == "anthropic":
                # Anthropic Claude API
                response = self.ai_parser.client.messages.create(
                    model=model,
                    max_tokens=500,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}],
                )
                result_text = response.content[0].text
            else:
                logger.warning(f"Неподдерживаемый провайдер AI: {provider}")
                return None

            # Парсим JSON ответ
            try:
                # Извлекаем JSON из ответа (может быть обернут в markdown)
                if "```json" in result_text:
                    result_text = (
                        result_text.split("```json")[1].split("```")[0].strip()
                    )
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                result = json.loads(result_text)

                # Валидация результата
                if "resource_type" in result:
                    # Нормализуем тип ресурса
                    resource_type = result["resource_type"].lower().strip()

                    # Проверяем, что тип валиден
                    valid_types = [
                        "electricity",
                        "gas",
                        "water",
                        "heat",
                        "fuel",
                        "coal",
                        "equipment",
                        "envelope",
                        "nodes",
                        "other",
                    ]

                    if resource_type not in valid_types:
                        logger.warning(
                            f"AI вернул невалидный тип ресурса: {resource_type}"
                        )
                        return None

                    result["resource_type"] = resource_type
                    result["confidence"] = float(result.get("confidence", 0.0))

                    return result
                else:
                    logger.warning("AI не вернул resource_type в ответе")
                    return None

            except json.JSONDecodeError as e:
                logger.warning(f"Ошибка парсинга JSON ответа AI: {e}")
                logger.debug(f"Ответ AI: {result_text[:500]}")
                return None

        except Exception as e:
            logger.error(f"Ошибка при вызове AI для классификации: {e}")
            return None


# Глобальный экземпляр классификатора (singleton)
_ai_classifier_instance: Optional[AIContentClassifier] = None


def get_ai_content_classifier() -> Optional[AIContentClassifier]:
    """
    Получить экземпляр AI классификатора (singleton).

    Returns:
        AIContentClassifier или None если AI недоступен
    """
    global _ai_classifier_instance
    if _ai_classifier_instance is None:
        _ai_classifier_instance = AIContentClassifier()

    if _ai_classifier_instance.enabled:
        return _ai_classifier_instance
    return None
