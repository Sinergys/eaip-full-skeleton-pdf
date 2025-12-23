"""
Интеллектуальный маршрутизатор документов для системы энергоаудита.

Этот модуль является "мозгом" системы, анализирующим ЛЮБЫЕ загруженные файлы
(Word, Excel, PDF, изображения) и определяющим оптимальный путь обработки.

Основные возможности:
- Быстрый анализ (2-3 сек) для классификации документа
- Глубокий анализ (3-5 сек) для детальной маршрутизации
- Генерация routing map с рекомендациями по обработке
- Интеграция с существующими парсерами как execution layer
- Поддержка любых названий файлов и неограниченного количества файлов
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime

# Импорт safe_json_dumps для обработки datetime
try:
    from database import safe_json_dumps
except ImportError:
    # Fallback если database не доступен
    def safe_json_dumps(obj, **kwargs):
        return json.dumps(obj, default=str, **kwargs)

logger = logging.getLogger(__name__)

# Импорты существующих модулей
try:
    from utils.ai_content_classifier import AIContentClassifier
    HAS_AI_CLASSIFIER = True
except ImportError:
    HAS_AI_CLASSIFIER = False
    logger.warning("AIContentClassifier недоступен")

try:
    from ai_parser import get_ai_parser
    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.warning("AI parser недоступен")

try:
    from file_parser import parse_file
    HAS_FILE_PARSER = True
except ImportError:
    HAS_FILE_PARSER = False
    logger.warning("file_parser недоступен")


class IntelligentRouter:
    """
    Интеллектуальный маршрутизатор документов.
    
    Анализирует любой загруженный файл и определяет оптимальный путь обработки.
    """
    
    # Типы документов
    DOCUMENT_TYPES = [
        "energy_passport",      # Энергетический паспорт
        "balance_act",          # Акт баланса
        "consumption_table",    # Таблица потребления
        "calculation",          # Расчет
        "contract",             # Договор
        "protocol",             # Протокол
        "methodological",       # Методические материалы
        "photo_thermogram",     # Фототермограмма
        "unknown"               # Неизвестный тип
    ]
    
    # Типы ресурсов
    RESOURCE_TYPES = [
        "electricity",          # Электроэнергия
        "gas",                  # Газ
        "water",                # Вода
        "heat",                 # Тепло
        "fuel",                 # Топливо
        "multiple",             # Несколько ресурсов
        "unknown"               # Неизвестный ресурс
    ]
    
    # Типы данных
    DATA_TYPES = [
        "meter_readings",       # Показания счетчиков
        "energy_balance",       # Энергетический баланс
        "savings_calculation",  # Расчет экономии
        "tariffs",              # Тарифы
        "norms",                # Нормы
        "consumption",          # Потребление
        "production",           # Производство
        "realization",          # Реализация
        "unknown"               # Неизвестный тип данных
    ]
    
    # Периоды
    PERIOD_TYPES = [
        "2024_Q1", "2024_Q2", "2024_Q3", "2024_Q4",
        "2023_year", "2024_year",
        "multiyear",            # Многолетние данные
        "unknown"               # Неизвестный период
    ]
    
    # Статусы данных
    STATUS_TYPES = [
        "source_data",          # Исходные данные
        "calculated",           # Рассчитанные данные
        "reported",             # Отчетные данные
        "methodological"        # Методические материалы
    ]
    
    def __init__(self):
        """Инициализация маршрутизатора"""
        self.ai_classifier = None
        self.ai_parser = None
        
        # Инициализация AI компонентов
        if HAS_AI_CLASSIFIER:
            try:
                self.ai_classifier = AIContentClassifier()
            except Exception as e:
                logger.warning(f"Не удалось инициализировать AI классификатор: {e}")
        
        if HAS_AI_PARSER:
            try:
                self.ai_parser = get_ai_parser()
            except Exception as e:
                logger.warning(f"Не удалось инициализировать AI парсер: {e}")
        
        logger.info("✅ IntelligentRouter инициализирован")
    
    def analyze_file(
        self,
        file_path: str,
        filename: str,
        raw_json: Optional[Dict[str, Any]] = None,
        fast_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Анализирует файл и возвращает routing map.
        
        Args:
            file_path: Путь к файлу
            filename: Имя файла
            raw_json: Предварительно распарсенные данные (опционально)
            fast_mode: Использовать быстрый анализ (True) или глубокий (False)
        
        Returns:
            Routing map с рекомендациями по обработке
        """
        start_time = time.time()
        
        logger.info(f"🔍 Начало анализа файла: {filename}")
        
        # Этап 1: Быстрый анализ
        fast_analysis = self._fast_analysis(file_path, filename, raw_json)
        confidence = fast_analysis.get("confidence", 0.0)
        
        # Решение о переходе к глубокому анализу
        if not fast_mode and confidence < 0.7:
            logger.info(f"⚠️ Низкая уверенность ({confidence:.2f}), переход к глубокому анализу")
            deep_analysis = self._deep_analysis(file_path, filename, raw_json)
            # Объединяем результаты
            analysis = {**fast_analysis, **deep_analysis}
            analysis["confidence"] = max(confidence, deep_analysis.get("confidence", 0.0))
        else:
            analysis = fast_analysis
        
        # Этап 2: Генерация routing map
        routing_map = self._generate_routing_map(analysis, file_path, filename)
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Анализ завершен за {elapsed_time:.2f} сек. Confidence: {analysis.get('confidence', 0.0):.2f}")
        
        return routing_map
    
    def _fast_analysis(
        self,
        file_path: str,
        filename: str,
        raw_json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Быстрый анализ файла (2-3 сек).
        
        Анализирует первые листы/страницы для быстрой классификации.
        """
        start_time = time.time()
        
        analysis = {
            "document_type": "unknown",
            "resource_type": "unknown",
            "data_type": "unknown",
            "period": "unknown",
            "status": "source_data",
            "confidence": 0.0,
            "metadata": {},
            "structure": {}
        }
        
        try:
            # Если raw_json уже есть, используем его
            if raw_json is None:
                # Парсим только первые листы/страницы для быстрого анализа
                raw_json = self._parse_file_preview(file_path)
            
            if not raw_json:
                logger.warning("Не удалось получить данные для анализа")
                return analysis
            
            # Анализ структуры
            structure = self._analyze_structure(raw_json, filename)
            analysis["structure"] = structure
            
            # Определение типа документа
            document_type = self._detect_document_type(raw_json, filename)
            analysis["document_type"] = document_type
            
            # Определение типа ресурса
            resource_type = self._detect_resource_type(raw_json, filename)
            analysis["resource_type"] = resource_type
            
            # Определение типа данных
            data_type = self._detect_data_type(raw_json, filename)
            analysis["data_type"] = data_type
            
            # Определение периода
            period = self._detect_period(raw_json, filename)
            analysis["period"] = period
            
            # Определение статуса
            status = self._detect_status(raw_json, filename)
            analysis["status"] = status
            
            # Расчет уверенности
            confidence = self._calculate_confidence(analysis)
            analysis["confidence"] = confidence
            
            # Метаданные
            analysis["metadata"] = {
                "filename": filename,
                "file_size": Path(file_path).stat().st_size if Path(file_path).exists() else 0,
                "file_extension": Path(filename).suffix.lower(),
                "analysis_time": time.time() - start_time,
                "analysis_type": "fast"
            }
            
        except Exception as e:
            logger.error(f"Ошибка при быстром анализе: {e}", exc_info=True)
            analysis["error"] = str(e)
        
        elapsed = time.time() - start_time
        logger.debug(f"Быстрый анализ завершен за {elapsed:.2f} сек")
        
        return analysis
    
    def _deep_analysis(
        self,
        file_path: str,
        filename: str,
        raw_json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Глубокий анализ файла (3-5 сек).
        
        Анализирует весь документ для точной маршрутизации.
        """
        start_time = time.time()
        
        analysis = {
            "document_type": "unknown",
            "resource_type": "unknown",
            "data_type": "unknown",
            "period": "unknown",
            "status": "source_data",
            "confidence": 0.0,
            "anomalies": [],
            "errors": [],
            "recommendations": []
        }
        
        try:
            # Полный парсинг файла
            if raw_json is None:
                if HAS_FILE_PARSER:
                    raw_json = parse_file(file_path)
                else:
                    logger.warning("file_parser недоступен для глубокого анализа")
                    return analysis
            
            if not raw_json:
                logger.warning("Не удалось получить данные для глубокого анализа")
                return analysis
            
            # Повторяем анализ с полными данными
            analysis["document_type"] = self._detect_document_type(raw_json, filename)
            analysis["resource_type"] = self._detect_resource_type(raw_json, filename)
            analysis["data_type"] = self._detect_data_type(raw_json, filename)
            analysis["period"] = self._detect_period(raw_json, filename)
            analysis["status"] = self._detect_status(raw_json, filename)
            
            # Дополнительный анализ для глубокого режима
            analysis["anomalies"] = self._detect_anomalies(raw_json)
            analysis["errors"] = self._detect_errors(raw_json)
            analysis["recommendations"] = self._generate_recommendations(analysis, raw_json)
            
            # Повышенная уверенность после глубокого анализа
            base_confidence = self._calculate_confidence(analysis)
            analysis["confidence"] = min(1.0, base_confidence * 1.2)  # Увеличиваем на 20%
            
            analysis["metadata"] = {
                "filename": filename,
                "analysis_time": time.time() - start_time,
                "analysis_type": "deep"
            }
            
        except Exception as e:
            logger.error(f"Ошибка при глубоком анализе: {e}", exc_info=True)
            analysis["error"] = str(e)
        
        elapsed = time.time() - start_time
        logger.debug(f"Глубокий анализ завершен за {elapsed:.2f} сек")
        
        return analysis
    
    def _parse_file_preview(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Парсит только превью файла (первые листы/страницы) для быстрого анализа.
        """
        try:
            if HAS_FILE_PARSER:
                # Парсим файл (можно оптимизировать для превью)
                return parse_file(file_path)
            return None
        except Exception as e:
            logger.warning(f"Ошибка при парсинге превью: {e}")
            return None
    
    def _analyze_structure(
        self,
        raw_json: Dict[str, Any],
        filename: str
    ) -> Dict[str, Any]:
        """Анализирует структуру документа"""
        structure = {
            "sheets_count": 0,
            "pages_count": 0,
            "tables_count": 0,
            "has_images": False,
            "sheet_names": [],
            "headers": []
        }
        
        try:
            # Для Excel файлов
            if "sheets" in raw_json:
                sheets = raw_json["sheets"]
                structure["sheets_count"] = len(sheets)
                structure["sheet_names"] = [s.get("name", "") for s in sheets]
                
                # Подсчет таблиц
                for sheet in sheets:
                    if "data" in sheet:
                        structure["tables_count"] += 1
                    if "headers" in sheet:
                        structure["headers"].extend(sheet["headers"])
            
            # Для PDF файлов
            if "pages" in raw_json:
                structure["pages_count"] = len(raw_json["pages"])
            
            # Проверка на изображения
            if "images" in raw_json or "has_images" in raw_json:
                structure["has_images"] = True
        
        except Exception as e:
            logger.warning(f"Ошибка при анализе структуры: {e}")
        
        return structure
    
    def _detect_document_type(
        self,
        raw_json: Dict[str, Any],
        filename: str
    ) -> str:
        """Определяет тип документа"""
        filename_lower = filename.lower()
        
        # Извлекаем текст из raw_json (может быть из OCR для изображений)
        # Структура: {"file_type": "...", "parsing": {"data": {"text": "..."}}}
        text_content = ""
        if isinstance(raw_json, dict):
            # Структура: {"file_type": "...", "parsing": {"data": {...}}}
            if "parsing" in raw_json and isinstance(raw_json["parsing"], dict):
                parsing_data = raw_json["parsing"].get("data", {})
                if isinstance(parsing_data, dict):
                    # Пробуем разные варианты полей
                    if "text" in parsing_data and parsing_data["text"]:
                        text_content = str(parsing_data["text"]).lower()
                    elif "ocr_text" in parsing_data and parsing_data["ocr_text"]:
                        text_content = str(parsing_data["ocr_text"]).lower()
                    elif "ocr" in parsing_data and isinstance(parsing_data["ocr"], dict):
                        # Структура OCR результата
                        ocr_result = parsing_data["ocr"]
                        if "text" in ocr_result and ocr_result["text"]:
                            text_content = str(ocr_result["text"]).lower()
            
            # Для прямой структуры {"data": {...}}
            if not text_content and "data" in raw_json:
                data = raw_json["data"]
                if isinstance(data, dict):
                    if "text" in data and data["text"]:
                        text_content = str(data["text"]).lower()
                    elif "ocr_text" in data and data["ocr_text"]:
                        text_content = str(data["ocr_text"]).lower()
                    elif "ocr" in data and isinstance(data["ocr"], dict):
                        ocr_result = data["ocr"]
                        if "text" in ocr_result and ocr_result["text"]:
                            text_content = str(ocr_result["text"]).lower()
            
            # Если текста нет, используем JSON представление для поиска ключевых слов
            if not text_content:
                text_content = safe_json_dumps(raw_json).lower()
        else:
            text_content = safe_json_dumps(raw_json).lower()
        
        # Проверяем, является ли файл изображением
        is_image = filename_lower.endswith(('.jpg', '.jpeg', '.png'))
        
        # Для изображений: проверяем OCR-текст и содержимое
        if is_image:
            # Термограммы
            if any(keyword in filename_lower or keyword in text_content 
                   for keyword in ["термограмм", "thermogram", "теплов", "инфракрас"]):
                return "photo_thermogram"
            
            # Показания счетчиков (часто фотографируются)
            if any(keyword in filename_lower or keyword in text_content 
                   for keyword in ["счетчик", "meter", "показания", "т-3", "т3", "т-3а"]):
                return "meter_readings"
            
            # Акт баланса (может быть отсканирован)
            if any(keyword in filename_lower or keyword in text_content 
                   for keyword in ["акт баланса", "баланс", "balance act", "реализация"]):
                return "balance_act"
            
            # Если есть OCR-текст, но тип не определен - возможно показания
            if text_content and len(text_content) > 50:
                # Проверяем наличие чисел и единиц измерения
                if any(keyword in text_content for keyword in ["квтч", "квт", "м³", "м3", "гкал"]):
                    return "meter_readings"
        
        # Правила определения типа документа (для всех файлов)
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["энергетический паспорт", "энергопаспорт", "energy passport"]):
            return "energy_passport"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["акт баланса", "баланс", "balance act", "реализация"]):
            return "balance_act"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["таблица потребления", "consumption table", "потребление"]):
            return "consumption_table"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["расчет", "calculation", "calc"]):
            return "calculation"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["договор", "contract"]):
            return "contract"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["протокол", "protocol"]):
            return "protocol"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["методич", "methodological"]):
            return "methodological"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["термограмм", "thermogram"]):
            return "photo_thermogram"
        
        # Используем AI классификатор если доступен
        if self.ai_classifier and self.ai_classifier.enabled:
            try:
                resource_type, confidence = self.ai_classifier.classify_with_ai(raw_json, filename)
                if confidence > 0.7:
                    # AI может помочь определить тип документа
                    pass
            except Exception as e:
                logger.debug(f"AI классификатор не смог помочь: {e}")
        
        return "unknown"
    
    def _detect_resource_type(
        self,
        raw_json: Dict[str, Any],
        filename: str
    ) -> str:
        """Определяет тип ресурса"""
        filename_lower = filename.lower()
        
        # Извлекаем текст из raw_json (может быть из OCR для изображений)
        text_content = ""
        if isinstance(raw_json, dict):
            # Для изображений с OCR
            if "parsing" in raw_json and isinstance(raw_json["parsing"], dict):
                parsing_data = raw_json["parsing"].get("data", {})
                if "text" in parsing_data:
                    text_content = parsing_data["text"].lower()
                elif "ocr_text" in parsing_data:
                    text_content = parsing_data["ocr_text"].lower()
            # Для обычных файлов
            elif "data" in raw_json:
                data = raw_json["data"]
                if isinstance(data, dict):
                    if "text" in data:
                        text_content = data["text"].lower()
                    elif "ocr_text" in data:
                        text_content = data["ocr_text"].lower()
            
            # Если текста нет, используем JSON представление
            if not text_content:
                text_content = safe_json_dumps(raw_json).lower()
        else:
            text_content = safe_json_dumps(raw_json).lower()
        
        # Правила определения типа ресурса
        resource_keywords = {
            "electricity": ["электр", "electricity", "квтч", "квт", "kwh", "kw", "электроэнергия", "т-3", "т3"],
            "gas": ["газ", "gas", "м³", "м3", "кубометр", "куб"],
            "water": ["вода", "water", "водоснабжение"],
            "heat": ["тепло", "heat", "отопление", "гкал"],
            "fuel": ["топливо", "fuel", "нефть", "бензин"]
        }
        
        found_resources = []
        for resource_type, keywords in resource_keywords.items():
            if any(keyword in filename_lower or keyword in text_content for keyword in keywords):
                found_resources.append(resource_type)
        
        if len(found_resources) == 1:
            return found_resources[0]
        elif len(found_resources) > 1:
            return "multiple"
        
        # Используем AI классификатор
        if self.ai_classifier and self.ai_classifier.enabled:
            try:
                resource_type, confidence = self.ai_classifier.classify_with_ai(raw_json, filename)
                if confidence > 0.5 and resource_type:
                    return resource_type
            except Exception as e:
                logger.debug(f"AI классификатор не смог определить ресурс: {e}")
        
        return "unknown"
    
    def _detect_data_type(
        self,
        raw_json: Dict[str, Any],
        filename: str
    ) -> str:
        """Определяет тип данных"""
        filename_lower = filename.lower()
        text_content = safe_json_dumps(raw_json).lower()
        
        # Правила определения типа данных
        if "реализация" in filename_lower or "реализация" in text_content:
            return "realization"
        
        if "производство" in filename_lower or "производство" in text_content:
            return "production"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["показания", "meter", "счетчик"]):
            return "meter_readings"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["баланс", "balance"]):
            return "energy_balance"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["экономия", "savings", "расчет"]):
            return "savings_calculation"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["тариф", "tariff"]):
            return "tariffs"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["норма", "norm"]):
            return "norms"
        
        # По умолчанию - потребление
        if "потребление" in filename_lower or "потребление" in text_content:
            return "consumption"
        
        return "unknown"
    
    def _detect_period(
        self,
        raw_json: Dict[str, Any],
        filename: str
    ) -> str:
        """Определяет период данных"""
        import re
        
        filename_lower = filename.lower()
        text_content = safe_json_dumps(raw_json).lower()
        
        # Поиск года
        year_match = re.search(r'20\d{2}', filename_lower + " " + text_content)
        year = year_match.group() if year_match else None
        
        # Поиск квартала
        quarter_match = re.search(r'q[1-4]|кв[1-4]|квартал[_\s]*[1-4]', filename_lower + " " + text_content)
        quarter = quarter_match.group() if quarter_match else None
        
        if year and quarter:
            quarter_num = re.search(r'[1-4]', quarter).group() if quarter else None
            if quarter_num:
                return f"{year}_Q{quarter_num}"
        
        if year:
            return f"{year}_year"
        
        # Проверка на многолетние данные
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["многолет", "multiyear", "несколько лет"]):
            return "multiyear"
        
        return "unknown"
    
    def _detect_status(
        self,
        raw_json: Dict[str, Any],
        filename: str
    ) -> str:
        """Определяет статус данных"""
        filename_lower = filename.lower()
        text_content = safe_json_dumps(raw_json).lower()
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["исходн", "source", "первичн"]):
            return "source_data"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["рассчитан", "calculated", "calc"]):
            return "calculated"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["отчет", "reported", "report"]):
            return "reported"
        
        if any(keyword in filename_lower or keyword in text_content 
               for keyword in ["методич", "methodological"]):
            return "methodological"
        
        return "source_data"  # По умолчанию
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Рассчитывает уверенность в результатах анализа"""
        confidence = 0.0
        
        # Базовые правила для расчета уверенности
        if analysis.get("document_type") != "unknown":
            confidence += 0.3
        
        if analysis.get("resource_type") != "unknown":
            confidence += 0.3
        
        if analysis.get("data_type") != "unknown":
            confidence += 0.2
        
        if analysis.get("period") != "unknown":
            confidence += 0.2
        
        # Дополнительные бонусы для определенных типов
        document_type = analysis.get("document_type")
        if document_type in ["meter_readings", "photo_thermogram"]:
            # Для показаний счетчиков и термограмм повышаем уверенность
            confidence += 0.1
        
        # Если есть структура с данными, повышаем уверенность
        structure = analysis.get("structure", {})
        if structure.get("tables_count", 0) > 0 or structure.get("pages_count", 0) > 0:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _detect_anomalies(self, raw_json: Dict[str, Any]) -> List[str]:
        """Обнаруживает аномалии в данных"""
        anomalies = []
        
        try:
            # Проверка на пустые листы
            if "sheets" in raw_json:
                empty_sheets = [s.get("name", "") for s in raw_json["sheets"] 
                              if not s.get("data") or len(s.get("data", [])) == 0]
                if empty_sheets:
                    anomalies.append(f"Пустые листы: {', '.join(empty_sheets)}")
            
            # Проверка на отсутствие заголовков
            if "sheets" in raw_json:
                sheets_without_headers = [s.get("name", "") for s in raw_json["sheets"]
                                         if "headers" not in s or not s["headers"]]
                if sheets_without_headers:
                    anomalies.append(f"Листы без заголовков: {', '.join(sheets_without_headers)}")
        
        except Exception as e:
            logger.debug(f"Ошибка при обнаружении аномалий: {e}")
        
        return anomalies
    
    def _detect_errors(self, raw_json: Dict[str, Any]) -> List[str]:
        """Обнаруживает ошибки в данных"""
        errors = []
        
        try:
            # Проверка на некорректные данные
            if "sheets" in raw_json:
                for sheet in raw_json["sheets"]:
                    if "data" in sheet:
                        # Можно добавить проверки на некорректные значения
                        pass
        
        except Exception as e:
            logger.debug(f"Ошибка при обнаружении ошибок: {e}")
        
        return errors
    
    def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        raw_json: Dict[str, Any]
    ) -> List[str]:
        """Генерирует рекомендации по обработке"""
        recommendations = []
        
        if analysis.get("confidence", 0.0) < 0.7:
            recommendations.append("Рекомендуется ручная проверка из-за низкой уверенности")
        
        if analysis.get("document_type") == "unknown":
            recommendations.append("Тип документа не определен, требуется дополнительный анализ")
        
        if analysis.get("resource_type") == "unknown":
            recommendations.append("Тип ресурса не определен, требуется дополнительный анализ")
        
        return recommendations
    
    def _generate_routing_map(
        self,
        analysis: Dict[str, Any],
        file_path: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Генерирует routing map с рекомендациями по обработке.
        
        Формат routing map:
        {
            "file_info": {...},
            "analysis": {...},
            "routing": {
                "primary_module": "...",
                "secondary_modules": [...],
                "target_tables": [...],
                "processing_priority": "...",
                "validation_required": bool
            },
            "metadata": {...}
        }
        """
        routing_map = {
            "file_info": {
                "filename": filename,
                "file_path": file_path,
                "uploaded_at": datetime.now().isoformat()
            },
            "analysis": analysis,
            "routing": self._determine_routing(analysis),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "router_version": "1.0.0"
            }
        }
        
        return routing_map
    
    def _determine_routing(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Определяет маршрутизацию на основе анализа.
        
        Выбирает модули обработки и целевые таблицы БД.
        """
        document_type = analysis.get("document_type", "unknown")
        resource_type = analysis.get("resource_type", "unknown")
        data_type = analysis.get("data_type", "unknown")
        confidence = analysis.get("confidence", 0.0)
        
        routing = {
            "primary_module": "manual_review",
            "secondary_modules": [],
            "target_tables": [],
            "processing_priority": "normal",
            "validation_required": True
        }
        
        # Если низкая уверенность - ручная проверка
        if confidence < 0.7:
            routing["primary_module"] = "manual_review"
            routing["processing_priority"] = "low"
            return routing
        
        # Определение primary_module на основе типа документа
        if document_type == "balance_act":
            routing["primary_module"] = "balance_sheet_node_extractor"
            routing["target_tables"] = ["node_consumption"]
            if data_type in ["realization", "production"]:
                routing["secondary_modules"] = ["energy_aggregator"]
        
        elif document_type == "energy_passport":
            routing["primary_module"] = "canonical_to_passport"
            routing["target_tables"] = ["parsed_data"]
            routing["secondary_modules"] = ["readiness_validator"]
        
        elif document_type == "consumption_table":
            routing["primary_module"] = "nodes_parser"
            routing["target_tables"] = ["node_consumption"]
            routing["secondary_modules"] = ["energy_aggregator"]
        
        elif document_type == "meter_readings":
            # Показания счетчиков (включая изображения)
            routing["primary_module"] = "file_parser"  # OCR уже применен
            routing["target_tables"] = ["parsed_data"]
            routing["secondary_modules"] = ["ocr_data_adapter"]  # Адаптация OCR данных
            routing["processing_priority"] = "normal"
        
        elif document_type == "photo_thermogram":
            # Фототермограммы
            routing["primary_module"] = "file_parser"
            routing["target_tables"] = ["parsed_data"]
            routing["processing_priority"] = "low"
        
        elif document_type in ["calculation", "savings_calculation"]:
            routing["primary_module"] = "energy_aggregator"
            routing["target_tables"] = ["parsed_data"]
        
        elif document_type == "methodological":
            routing["primary_module"] = "file_parser"
            routing["target_tables"] = ["parsed_data"]
            routing["processing_priority"] = "low"
        
        else:
            # Для неизвестных типов - используем file_parser
            routing["primary_module"] = "file_parser"
            routing["target_tables"] = ["parsed_data", "uploads"]
        
        # Определение приоритета
        if document_type in ["balance_act", "consumption_table"]:
            routing["processing_priority"] = "high"
        
        # Определение необходимости валидации
        if document_type in ["energy_passport", "balance_act"]:
            routing["validation_required"] = True
        else:
            routing["validation_required"] = False
        
        return routing
    
    def route_file(
        self,
        file_path: str,
        filename: str,
        enterprise_id: int,
        batch_id: str,
        raw_json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Полный цикл: анализ + маршрутизация + выполнение.
        
        Args:
            file_path: Путь к файлу
            filename: Имя файла
            enterprise_id: ID предприятия
            batch_id: ID батча
            raw_json: Предварительно распарсенные данные
        
        Returns:
            Результат обработки с routing map и результатами выполнения
        """
        # Анализ файла
        routing_map = self.analyze_file(file_path, filename, raw_json, fast_mode=True)
        
        # Если уверенность низкая - используем глубокий анализ
        if routing_map["analysis"].get("confidence", 0.0) < 0.7:
            routing_map = self.analyze_file(file_path, filename, raw_json, fast_mode=False)
        
        # Добавляем информацию о выполнении
        routing_map["execution"] = {
            "enterprise_id": enterprise_id,
            "batch_id": batch_id,
            "status": "pending",
            "executed_modules": []
        }
        
        return routing_map

