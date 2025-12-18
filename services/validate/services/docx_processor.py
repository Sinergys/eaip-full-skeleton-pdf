"""
DocxProcessor - Извлечение текста и объектов из DOCX документов.
Соответствует разделу 3.1.3 ТЗ.

Основные задачи:
- Извлечение текста с сохранением структуры
- Извлечение объектов (изображения, таблицы, графики)
- Замена объектов маркерами [[OBJ_XXX]]
- Корректная обработка merged cells в таблицах
"""
import io
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from docx import Document
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl

from core.models import ExtractedObject
from utils.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class DocxProcessor:
    """
    Обработка DOCX документов: извлечение текста и объектов.
    Соответствует разделу 3.1.3 ТЗ.
    """

    def __init__(self):
        """Инициализация процессора."""
        self.obj_counter = 0

    async def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Извлечь весь контент из DOCX файла.

        Args:
            file_path: Путь к DOCX файлу

        Returns:
            {
                'text': str,  # Текст с маркерами вместо объектов
                'objects': Dict[str, ExtractedObject]  # {obj_id: object}
            }

        Raises:
            ProcessingError: При ошибках обработки
        """
        try:
            logger.info(f"Starting extraction from: {file_path}")
            path = Path(file_path)

            if not path.exists():
                raise ProcessingError(f"File not found: {file_path}")

            if not path.suffix.lower() in ['.docx', '.doc']:
                raise ProcessingError(f"Invalid file format: {path.suffix}")

            # Открыть документ
            try:
                document = Document(str(path))
            except Exception as e:
                raise ProcessingError(f"Failed to open DOCX file: {str(e)}")

            # Reset counter для новой обработки
            self.obj_counter = 0

            # Извлечь все объекты из документа
            all_objects: Dict[str, ExtractedObject] = {}

            # 1. Извлечь изображения
            images = self._extract_images(document)
            all_objects.update(images)

            # 2. Извлечь таблицы
            tables = self._extract_tables(document)
            all_objects.update(tables)

            # 3. Извлечь графики (если есть)
            charts = self._extract_charts(document)
            all_objects.update(charts)

            # 4. Извлечь текст с заменой объектов на маркеры
            text_with_markers = self._extract_text_with_markers(document, all_objects)

            logger.info(f"Extraction complete: {len(all_objects)} objects, {len(text_with_markers)} chars")

            return {
                'text': text_with_markers,
                'objects': all_objects
            }

        except ProcessingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {str(e)}", exc_info=True)
            raise ProcessingError(f"Document extraction failed: {str(e)}")

    def _extract_images(self, document: Document) -> Dict[str, ExtractedObject]:
        """
        Извлечь все изображения из документа.

        Args:
            document: python-docx Document объект

        Returns:
            Dict[str, ExtractedObject]: {obj_id: ExtractedObject}
        """
        images = {}

        try:
            # ИЗМЕНЕНО: Последовательное извлечение изображений по XML порядку
            # Получаем упорядоченный список relationships
            image_rels = []
            for rel_id, rel in document.part.rels.items():
                if "image" in rel.target_ref:
                    image_rels.append((rel_id, rel))
            
            # Обрабатываем изображения в порядке их появления в XML
            for rel_id, rel in image_rels:
                    self.obj_counter += 1
                    obj_id = f"OBJ_{self.obj_counter:03d}"

                    # Извлечь binary data изображения
                    image_part = rel.target_part
                    image_bytes = image_part.blob

                    # Определить тип изображения
                    content_type = image_part.content_type

                    images[obj_id] = ExtractedObject(
                        id=obj_id,
                        object_type="image",
                        binary_data=image_bytes,
                        caption=None,  # Caption извлечём при обработке параграфов
                        metadata={
                            'content_type': content_type,
                            'size_bytes': len(image_bytes),
                            'rel_id': rel_id
                        }
                    )

            logger.info(f"Extracted {len(images)} images")
            return images

        except Exception as e:
            logger.warning(f"Error extracting images: {str(e)}")
            return images

    def _extract_tables(self, document: Document) -> Dict[str, ExtractedObject]:
        """
        Извлечь все таблицы из документа.

        ВАЖНО: Обрабатывать merged cells корректно!

        Args:
            document: python-docx Document объект

        Returns:
            Dict[str, ExtractedObject]: {obj_id: ExtractedObject}
        """
        tables = {}

        try:
            for table_idx, table in enumerate(document.tables):
                self.obj_counter += 1
                obj_id = f"OBJ_{self.obj_counter:03d}"

                # Извлечь данные таблицы
                table_data = self._extract_table_data(table)

                # Сохранить как JSON для последующей вставки
                tables[obj_id] = ExtractedObject(
                    id=obj_id,
                    object_type="table",
                    binary_data=None,  # Таблицы сохраняем как структурированные данные
                    caption=None,  # Caption извлечём при обработке параграфов
                    metadata={
                        'table_index': table_idx,
                        'rows': len(table.rows),
                        'columns': len(table.columns) if table.rows else 0,
                        'data': table_data
                    }
                )

            logger.info(f"Extracted {len(tables)} tables")
            return tables

        except Exception as e:
            logger.warning(f"Error extracting tables: {str(e)}")
            return tables

    def _extract_table_data(self, table: Table) -> List[List[str]]:
        """
        Извлечь данные из таблицы с обработкой merged cells.

        Args:
            table: python-docx Table объект

        Returns:
            List[List[str]]: 2D массив с данными таблицы
        """
        table_data = []

        try:
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    # Обработка merged cells
                    cell_text = self._get_merged_cell_value(cell)
                    row_data.append(cell_text)
                table_data.append(row_data)

            return table_data

        except Exception as e:
            logger.warning(f"Error extracting table data: {str(e)}")
            return table_data

    def _get_merged_cell_value(self, cell: _Cell) -> str:
        """
        Корректно обработать merged cells.

        python-docx плохо работает с merged cells, поэтому нужна специальная обработка.

        Args:
            cell: python-docx _Cell объект

        Returns:
            str: Текст ячейки
        """
        try:
            # Проверить на merged cell через XML properties
            tc = cell._tc
            tcPr = tc.tcPr

            if tcPr is not None:
                # Проверить gridSpan (horizontal merge)
                gridSpan = tcPr.gridSpan
                if gridSpan is not None:
                    # Это merged cell
                    pass

                # Проверить vMerge (vertical merge)
                vMerge = tcPr.vMerge
                if vMerge is not None:
                    # Если vMerge без val атрибута, это continuation cell
                    if vMerge.val is None:
                        # Пустая ячейка (continuation of merge)
                        return ""

            # Вернуть текст ячейки
            return cell.text.strip()

        except Exception as e:
            logger.debug(f"Error processing merged cell: {str(e)}")
            return cell.text.strip() if hasattr(cell, 'text') else ""

    def _extract_charts(self, document: Document) -> Dict[str, ExtractedObject]:
        """
        Извлечь графики/диаграммы.

        Опциональная функция, так как графики редко встречаются в энергоаудите.

        Args:
            document: python-docx Document объект

        Returns:
            Dict[str, ExtractedObject]: {obj_id: ExtractedObject}
        """
        charts = {}

        try:
            # ИЗМЕНЕНО: Последовательное извлечение графиков по XML порядку
            # Получаем упорядоченный список relationships для графиков
            chart_rels = []
            for rel_id, rel in document.part.rels.items():
                if "chart" in rel.target_ref.lower() or "oleObject" in rel.target_ref:
                    chart_rels.append((rel_id, rel))
            
            # Обрабатываем графики в порядке их появления в XML
            for rel_id, rel in chart_rels:
                    self.obj_counter += 1
                    obj_id = f"OBJ_{self.obj_counter:03d}"

                    charts[obj_id] = ExtractedObject(
                        id=obj_id,
                        object_type="chart",
                        binary_data=None,  # Charts сложнее извлекать в binary
                        caption=None,
                        metadata={
                            'rel_id': rel_id,
                            'target_ref': rel.target_ref
                        }
                    )

            logger.info(f"Extracted {len(charts)} charts")
            return charts

        except Exception as e:
            logger.warning(f"Error extracting charts: {str(e)}")
            return charts

    def _extract_text_with_markers(
        self,
        document: Document,
        objects: Dict[str, ExtractedObject]
    ) -> str:
        """
        Извлечь текст документа с заменой объектов на маркеры.

        Args:
            document: python-docx Document объект
            objects: Словарь извлечённых объектов

        Returns:
            str: Текст с маркерами [[OBJ_XXX]]
        """
        text_parts = []

        # Создать mapping для быстрого поиска объектов
        table_obj_map = {}
        image_obj_list = []
        
        # Подготовить mapping для таблиц и список изображений
        for obj_id, obj in objects.items():
            if obj.object_type == "table":
                table_idx = obj.metadata.get('table_index')
                if table_idx is not None:
                    table_obj_map[table_idx] = obj_id
            elif obj.object_type == "image":
                image_obj_list.append(obj_id)

        # ИЗМЕНЕНО: Унифицированный подход к отслеживанию позиций объектов
        # Создаем сортированный список всех объектов по ID для обеспечения последовательности
        all_objects_sorted = sorted(objects.items(), key=lambda x: x[0])
        
        # Iterate через все элементы документа в порядке появления
        element_index = 0
        for element in document.element.body:
            if isinstance(element, CT_P):
                # Параграф - передаем список доступных image IDs
                paragraph = Paragraph(element, document)
                para_text = self._process_paragraph_with_markers(paragraph, image_obj_list, element_index)
                if para_text:
                    text_parts.append(para_text)

            elif isinstance(element, CT_Tbl):
                # Таблица - заменить на маркер
                table_idx = len([e for e in document.element.body[:element_index] if isinstance(e, CT_Tbl)])
                if table_idx in table_obj_map:
                    obj_id = table_obj_map[table_idx]
                    marker = f"[[{obj_id}]]"
                    text_parts.append(marker)
                    logger.debug(f"Inserted table marker: {marker}")
            
            element_index += 1

        return '\n\n'.join(text_parts)

    def _process_paragraph_with_markers(self, paragraph: Paragraph, image_obj_list: List[str], start_image_counter: int) -> str:
        """
        Обработать параграф и заменить inline изображения на маркеры.

        Args:
            paragraph: python-docx Paragraph объект
            image_obj_list: Список доступных image IDs
            start_image_counter: Начальный счетчик для image IDs

        Returns:
            str: Текст параграфа с маркерами
        """
        # Проверить на inline изображения
        image_count = 0
        image_markers = []

        for run in paragraph.runs:
            # Проверить на inline shapes (drawing elements)
            if hasattr(run, '_element'):
                drawings = run._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing')
                if drawings:
                    # Найдено изображение - получить obj_id из списка
                    if start_image_counter + image_count < len(image_obj_list):
                        obj_id = image_obj_list[start_image_counter + image_count]
                        image_markers.append(obj_id)
                        
                        # ИЗМЕНЕНО: Безопасная замена содержимого run без clear()
                        # Сохранить исходный текст run
                        original_text = run.text
                        # Заменить на маркер, сохраняя форматирование
                        run.text = f"[[{obj_id}]]"
                        
                        logger.debug(f"Replaced inline image with marker: {obj_id}")
                    else:
                        logger.warning(f"Image index {start_image_counter + image_count} out of range for available images")

                    image_count += 1

        # Если в параграфе были изображения, логируем
        if image_count > 0:
            logger.info(f"Found {image_count} inline images in paragraph, replaced with markers: {image_markers}")

        # Возвращаем обработанный текст
        return paragraph.text.strip()
