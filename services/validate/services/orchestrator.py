"""
Orchestrator Service - Main coordinator for Word document validation.
Manages the entire validation pipeline from file upload to final document.

Соответствует разделу 3.1.1 ТЗ.
PHASE 2 - ПОЛНАЯ РЕАЛИЗАЦИЯ
"""
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from core.config import Settings
from core.models import (
    ExtractedObject,
    TextChunk,
    OllamaAnalysisResult,
    DeepSeekCorrectionResult,
    ProcessingSummary
)
from core.constants import (
    DEFAULT_CHUNK_SIZE_TOKENS,
    SECTION_INTERRUPTED_PREFIX,
    SECTION_INTERRUPTED_SUFFIX,
    CONTINUATION_PREFIX,
    CONTINUATION_SUFFIX
)
from utils.exceptions import ProcessingError, PKMRequirementsError
from utils.helpers import count_tokens

from .docx_processor import DocxProcessor
from .ai_processor import AIProcessor
from .document_assembler import DocumentAssembler

logger = logging.getLogger(__name__)


class OrchestratorService:
    """
    Центральный управляющий компонент (3.1.1 ТЗ).
    Координирует все этапы обработки отчёта.

    PHASE 2 - ПОЛНАЯ РЕАЛИЗАЦИЯ всех методов.
    """

    def __init__(self, settings: Settings):
        """
        Инициализация оркестратора.

        Args:
            settings: Конфигурация приложения
        """
        self.settings = settings

        # Инициализация сервисов
        self.docx_processor = DocxProcessor()

        self.ai_processor = AIProcessor(
            ollama_url=settings.OLLAMA_URL,
            deepseek_api_key=settings.DEEPSEEK_API_KEY,
            deepseek_url=settings.DEEPSEEK_API_URL,
            ollama_model=settings.OLLAMA_MODEL,
            deepseek_model=settings.DEEPSEEK_MODEL,
            deepseek_max_tokens=settings.DEEPSEEK_MAX_TOKENS,
            ollama_timeout=settings.OLLAMA_TIMEOUT,
            deepseek_timeout=settings.DEEPSEEK_TIMEOUT
        )

        self.assembler = DocumentAssembler(
            template_path=settings.GOST_TEMPLATE_PATH
        )

        logger.info("OrchestratorService полностью инициализирован (Phase 2)")

    async def process_report(
        self,
        file_path: str,
        file_hash: str,
        original_filename: str
    ) -> str:
        """
        Главный pipeline обработки отчёта (3.1.2 - 3.1.8 ТЗ).

        ПОЛНАЯ РЕАЛИЗАЦИЯ всех шагов из ТЗ раздел 3.1:

        1. Извлечение контента (3.1.3)
        2. Разбивка на чанки (3.1.4)
        3. Обработка каждого чанка:
           - Ollama анализ
           - DeepSeek корректировка
        4. Агрегация результатов (3.1.6)
        5. Сборка финального документа (3.1.7)
        6. Возврат пути к файлу

        Args:
            file_path: Путь к загруженному файлу
            file_hash: SHA-256 хеш файла
            original_filename: Оригинальное имя файла

        Returns:
            Путь к финальному файлу [Original]_Проверенный.docx

        Raises:
            ProcessingError: При ошибках обработки
        """
        start_time = time.time()

        logger.info(
            f"Начинаю обработку: file={original_filename}, "
            f"hash={file_hash[:16]}..."
        )

        try:
            # 1. Извлечение контента (3.1.3)
            logger.info("Step 1/5: Извлечение контента из DOCX")
            content = await self._extract_content(file_path)
            text = content['text']
            objects = content['objects']

            logger.info(f"Извлечено: {len(text)} символов, {len(objects)} объектов")

            # 2. Загрузка требований ПКМ 690
            logger.info("Step 2/5: Загрузка требований ПКМ 690")
            pkm_requirements = await self._load_pkm_requirements()

            # 3. Разбивка на чанки (3.1.4)
            logger.info("Step 3/5: Разбивка текста на чанки")
            chunks = self._create_chunks(text, max_tokens=DEFAULT_CHUNK_SIZE_TOKENS)

            logger.info(f"Создано {len(chunks)} чанков")

            # 4. Циклическая обработка чанков (3.1.5)
            logger.info("Step 4/5: Обработка чанков через AI")
            corrected_chunks = []
            all_recommendations = []
            total_issues = 0

            for idx, chunk in enumerate(chunks):
                logger.info(f"Обработка чанка {idx + 1}/{len(chunks)}")

                # Обработка чанка через Ollama + DeepSeek
                result = await self._process_chunk(chunk, pkm_requirements)

                corrected_chunks.append(result.corrected_text)
                all_recommendations.extend(result.recommendations)

                logger.info(f"Чанк {idx + 1} обработан: {len(result.recommendations)} рекомендаций")

            # 5. Агрегация результатов (3.1.6)
            logger.info("Step 5/5: Агрегация результатов и сборка документа")

            # Объединение чанков
            merged_text = self._merge_chunks(corrected_chunks)

            # Создание summary
            processing_time = time.time() - start_time
            summary = self._create_summary(
                all_recommendations,
                len(chunks),
                total_issues,
                processing_time
            )

            # 6. Сборка финального документа (3.1.7)
            output_path = await self.assembler.assemble_document(
                corrected_text=merged_text,
                objects=objects,
                recommendations=all_recommendations,
                summary=summary,
                original_filename=original_filename,
                output_dir=self.settings.TEMP_DIR
            )

            logger.info(
                f"Обработка завершена успешно: {output_path} "
                f"(время: {processing_time:.1f}s)"
            )

            return output_path

        except Exception as e:
            logger.error(f"Ошибка обработки отчёта: {e}", exc_info=True)
            raise ProcessingError(f"Ошибка обработки отчёта: {str(e)}")

    async def _extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Извлечение контента из DOCX (3.1.3 ТЗ).

        Args:
            file_path: Путь к DOCX файлу

        Returns:
            {
                'text': str,
                'objects': Dict[str, ExtractedObject]
            }

        Raises:
            ProcessingError: При ошибках извлечения
        """
        try:
            content = await self.docx_processor.extract_content(file_path)
            return content

        except Exception as e:
            raise ProcessingError(f"Ошибка извлечения контента: {str(e)}")

    def _create_chunks(
        self,
        text: str,
        max_tokens: int = 20000
    ) -> List[TextChunk]:
        """
        Разбивка текста на чанки с учётом маркеров разрыва секций (3.1.4 ТЗ).

        Логика:
        1. Использовать tiktoken для подсчёта токенов
        2. Искать границы секций/глав
        3. Если разрыв внутри секции:
           - В конец чанка: [[SECTION_INTERRUPTED_AT_CHAPTER_X]]
           - В начало следующего: [[CONTINUATION_OF_CHAPTER_X]]

        Args:
            text: Текст для разбивки
            max_tokens: Максимальный размер чанка в токенах

        Returns:
            List[TextChunk]: Список чанков
        """
        try:
            chunks = []

            # Разбить текст на параграфы
            paragraphs = text.split('\n\n')

            current_chunk_text = ""
            current_chunk_tokens = 0
            chunk_index = 0
            current_section = None

            for para_idx, para in enumerate(paragraphs):
                para = para.strip()
                if not para:
                    continue

                # Подсчёт токенов параграфа
                para_tokens = count_tokens(para)

                # Проверить, является ли это заголовком секции
                # Простая эвристика: короткий параграф заглавными буквами
                is_section_header = (
                    len(para) < 100 and
                    para.isupper() and
                    not para.startswith('[[OBJ_')
                )

                if is_section_header:
                    current_section = para

                # Проверить, поместится ли параграф в текущий чанк
                if current_chunk_tokens + para_tokens > max_tokens:
                    # Сохранить текущий чанк
                    if current_chunk_text:
                        # Если разрыв внутри секции, добавить маркер
                        is_interrupted = current_section is not None

                        if is_interrupted:
                            section_marker = f"{SECTION_INTERRUPTED_PREFIX}{current_section}{SECTION_INTERRUPTED_SUFFIX}"
                            current_chunk_text += f"\n\n{section_marker}"

                        chunks.append(TextChunk(
                            index=chunk_index,
                            text=current_chunk_text,
                            token_count=current_chunk_tokens,
                            is_section_interrupted=is_interrupted,
                            chapter_name=current_section if is_interrupted else None
                        ))

                        chunk_index += 1

                    # Начать новый чанк
                    current_chunk_text = ""
                    current_chunk_tokens = 0

                    # Если была прервана секция, добавить маркер продолжения
                    if current_section and not is_section_header:
                        continuation_marker = f"{CONTINUATION_PREFIX}{current_section}{CONTINUATION_SUFFIX}"
                        current_chunk_text = continuation_marker + "\n\n"
                        current_chunk_tokens = count_tokens(continuation_marker)

                # Добавить параграф к текущему чанку
                if current_chunk_text:
                    current_chunk_text += "\n\n"

                current_chunk_text += para
                current_chunk_tokens += para_tokens

            # Сохранить последний чанк
            if current_chunk_text:
                chunks.append(TextChunk(
                    index=chunk_index,
                    text=current_chunk_text,
                    token_count=current_chunk_tokens,
                    is_section_interrupted=False,
                    chapter_name=None
                ))

            logger.info(f"Создано {len(chunks)} чанков (макс {max_tokens} токенов)")

            return chunks

        except Exception as e:
            raise ProcessingError(f"Ошибка разбивки на чанки: {str(e)}")

    async def _process_chunk(
        self,
        chunk: TextChunk,
        pkm_requirements: str
    ) -> DeepSeekCorrectionResult:
        """
        Обработка одного чанка через Ollama + DeepSeek (3.1.5 ТЗ).

        Args:
            chunk: TextChunk для обработки
            pkm_requirements: Требования ПКМ 690

        Returns:
            DeepSeekCorrectionResult: Результат корректировки

        Raises:
            ProcessingError: При ошибках обработки
        """
        try:
            # 1. Предварительный анализ через Ollama (если включен)
            if self.settings.USE_OLLAMA:
                logger.info(f"Ollama анализ чанка {chunk.index}")
                ollama_result = await self.ai_processor.analyze_with_ollama(chunk.text)
            else:
                # Пропускаем Ollama, используем пустой результат
                ollama_result = OllamaAnalysisResult(issues=[], fixes=[])
                logger.debug(f"[Ollama DISABLED] Чанк {chunk.index} -> DeepSeek")

            # 2. Корректировка через DeepSeek
            logger.info(f"DeepSeek корректировка чанка {chunk.index}")
            deepseek_result = await self.ai_processor.analyze_with_deepseek(
                chunk=chunk.text,
                ollama_report=ollama_result,
                pkm_requirements=pkm_requirements,
                chunk_index=chunk.index
            )

            return deepseek_result

        except Exception as e:
            raise ProcessingError(f"Ошибка обработки чанка {chunk.index}: {str(e)}")

    async def _load_pkm_requirements(self) -> str:
        """
        Загрузка требований ПКМ 690 из существующего модуля.

        ИНТЕГРАЦИЯ с existing code:
        from eaip_full_skeleton.services.ingest.domain.pkm690_sections import (
            PKM690_SECTIONS
        )

        Returns:
            str: Текстовое описание требований ПКМ 690

        Raises:
            PKMRequirementsError: При ошибке загрузки
        """
        try:
            # Попытка импорта из существующего модуля ingest
            import sys
            from pathlib import Path

            # Добавить путь к ingest модулю
            ingest_path = Path(__file__).parent.parent.parent.parent / "ingest"

            if ingest_path.exists():
                sys.path.insert(0, str(ingest_path))

                try:
                    from domain.pkm690_sections import PKM690_SECTIONS

                    # Собрать требования в текст
                    sections_text = []
                    for section in PKM690_SECTIONS:
                        section_content = f"{section.pkm690_number}. {section.pkm690_title}\n"

                        if hasattr(section, 'template') and section.template:
                            section_content += f"\nШаблон:\n{section.template}\n"

                        if hasattr(section, 'requirements') and section.requirements:
                            section_content += f"\nТребования:\n{section.requirements}\n"

                        sections_text.append(section_content)

                    result = "\n\n---\n\n".join(sections_text)

                    logger.info(f"Загружено {len(PKM690_SECTIONS)} секций ПКМ 690")
                    return result

                except ImportError as e:
                    logger.warning(f"Не удалось импортировать PKM690_SECTIONS: {e}")

            # Fallback: использовать базовые требования
            logger.warning("Используются базовые требования ПКМ 690 (fallback)")
            return self._get_fallback_pkm_requirements()

        except Exception as e:
            logger.error(f"Ошибка загрузки требований ПКМ 690: {str(e)}")
            raise PKMRequirementsError(f"Не удалось загрузить требования ПКМ 690: {str(e)}")

    def _get_fallback_pkm_requirements(self) -> str:
        """
        Получить базовые требования ПКМ 690 (fallback).

        Returns:
            str: Базовые требования
        """
        return """
ТРЕБОВАНИЯ ПКМ №690 (БАЗОВЫЕ)

1. ВВЕДЕНИЕ
- Цель и задачи энергоаудита
- Объект обследования
- Нормативные документы

2. ОБЩИЕ СВЕДЕНИЯ О ПРЕДПРИЯТИИ
- Наименование и адрес
- Вид деятельности
- Основные производственные показатели

3. АНАЛИЗ ЭНЕРГОПОТРЕБЛЕНИЯ
- Структура энергопотребления
- Анализ энергоносителей
- Удельные показатели

4. АНАЛИЗ ОБОРУДОВАНИЯ
- Перечень энергопотребляющего оборудования
- Технические характеристики
- Состояние оборудования

5. МЕРОПРИЯТИЯ ПО ЭНЕРГОСБЕРЕЖЕНИЮ
- Организационные мероприятия
- Технические мероприятия
- Экономическое обоснование

6. ЭКОНОМИЧЕСКИЙ АНАЛИЗ
- Расчёт экономии
- Срок окупаемости
- Финансовые показатели

7. ЗАКЛЮЧЕНИЕ
- Выводы и рекомендации

8. ПРИЛОЖЕНИЯ
- Таблицы и графики
- Дополнительные материалы
"""

    def _merge_chunks(self, corrected_chunks: List[str]) -> str:
        """
        Объединение чанков с обработкой маркеров (3.1.6 ТЗ).

        Удаляет маркеры разрыва секций:
        - [[SECTION_INTERRUPTED_AT_CHAPTER_X]]
        - [[CONTINUATION_OF_CHAPTER_X]]

        Args:
            corrected_chunks: Список исправленных чанков

        Returns:
            str: Объединённый текст
        """
        try:
            merged_text = []

            for chunk_text in corrected_chunks:
                # Удалить маркеры разрыва секций
                import re

                # Удалить маркеры SECTION_INTERRUPTED
                chunk_text = re.sub(
                    r'\[\[SECTION_INTERRUPTED_AT_CHAPTER_.*?\]\]',
                    '',
                    chunk_text
                )

                # Удалить маркеры CONTINUATION
                chunk_text = re.sub(
                    r'\[\[CONTINUATION_OF_CHAPTER_.*?\]\]',
                    '',
                    chunk_text
                )

                chunk_text = chunk_text.strip()
                if chunk_text:
                    merged_text.append(chunk_text)

            result = '\n\n'.join(merged_text)

            logger.info(f"Объединено {len(corrected_chunks)} чанков в {len(result)} символов")

            return result

        except Exception as e:
            raise ProcessingError(f"Ошибка объединения чанков: {str(e)}")

    def _create_summary(
        self,
        recommendations: List[str],
        total_chunks: int,
        total_issues: int,
        processing_time: float
    ) -> ProcessingSummary:
        """
        Создание финального summary на основе рекомендаций (3.1.6 ТЗ).

        Args:
            recommendations: Список всех рекомендаций
            total_chunks: Количество обработанных чанков
            total_issues: Количество найденных проблем
            processing_time: Время обработки (секунды)

        Returns:
            ProcessingSummary: Итоговая сводка
        """
        try:
            # Подсчёт рекомендаций по категориям (простая группировка по ключевым словам)
            categories = {
                'ПКМ 690': 0,
                'Форматирование': 0,
                'Орфография': 0,
                'Стиль': 0,
                'Прочее': 0
            }

            for rec in recommendations:
                rec_lower = rec.lower()

                if 'пкм' in rec_lower or '690' in rec_lower:
                    categories['ПКМ 690'] += 1
                elif 'формат' in rec_lower or 'стиль оформления' in rec_lower:
                    categories['Форматирование'] += 1
                elif 'орфограф' in rec_lower or 'ошибка' in rec_lower:
                    categories['Орфография'] += 1
                elif 'стиль' in rec_lower or 'стилист' in rec_lower:
                    categories['Стиль'] += 1
                else:
                    categories['Прочее'] += 1

            summary = ProcessingSummary(
                total_chunks=total_chunks,
                total_recommendations=len(recommendations),
                total_issues_found=total_issues,
                processing_time_seconds=processing_time,
                recommendations_by_category=categories
            )

            logger.info(f"Summary создан: {len(recommendations)} рекомендаций")

            return summary

        except Exception as e:
            raise ProcessingError(f"Ошибка создания summary: {str(e)}")

    async def close(self):
        """Закрыть все сервисы и освободить ресурсы."""
        try:
            await self.ai_processor.close()
            logger.info("OrchestratorService закрыт")
        except Exception as e:
            logger.error(f"Ошибка при закрытии OrchestratorService: {str(e)}")
