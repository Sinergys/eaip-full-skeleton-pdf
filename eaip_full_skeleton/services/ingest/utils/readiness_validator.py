"""
Модуль валидации готовности данных для генерации энергетического паспорта.

Проверяет полноту данных, наличие обязательных ресурсов и файлов,
вычисляет показатель готовности для генерации паспорта.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from config.required_data_matrix import (
    REQUIRED_DATA_MATRIX,
    MINIMAL_REQUIREMENTS,
    get_required_resources,
    get_optional_resources,
    get_resource_config,
)
from domain.passport_requirements import (
    PASSPORT_SHEET_REQUIREMENTS,
    validate_sheet_data,
)
from utils.energy_aggregator import aggregate_from_db_json
from utils.resource_classifier import ResourceClassifier
import database

logger = logging.getLogger(__name__)


def validate_generation_readiness(enterprise_id: int) -> Dict[str, Any]:
    """
    Проверяет готовность данных для генерации энергетического паспорта.

    Args:
        enterprise_id: ID предприятия

    Returns:
        Словарь с результатами проверки:
        {
            "ready": bool,
            "completeness_score": float,  # 0.0-1.0
            "missing_resources": List[str],
            "missing_files": List[str],
            "available_resources": List[str],
            "available_files": List[str],
            "warnings": List[str],
            "progress_percentage": int,
            "required_resources_status": Dict[str, Dict],
            "optional_resources_status": Dict[str, Dict],
            "sheet_validation": Dict[str, Dict],  # НОВОЕ: валидация по листам
            "missing_sheet_data": List[str]  # НОВОЕ: недостающие данные для листов
        }
    """
    try:
        logger.info(f"Проверка готовности данных для предприятия {enterprise_id}")

        # Получаем все загрузки предприятия
        uploads = database.list_uploads_for_enterprise(enterprise_id)

        if not uploads:
            return {
                "ready": False,
                "completeness_score": 0.0,
                "missing_resources": get_required_resources(),
                "missing_files": [],
                "available_resources": [],
                "available_files": [],
                "warnings": ["Нет загруженных файлов"],
                "progress_percentage": 0,
                "required_resources_status": {},
                "optional_resources_status": {},
            }

        # Анализируем загруженные файлы
        available_files = []
        file_to_resource_map: Dict[str, str] = {}

        for upload in uploads:
            filename = upload.get("filename", "")
            status = upload.get("status", "")

            # Учитываем только успешно обработанные файлы
            if status == "success" and filename:
                available_files.append(filename)

                # Пробуем получить raw_json для анализа содержимого
                raw_json = None
                try:
                    upload_record = database.get_upload_by_batch(upload.get("batch_id"))
                    if upload_record:
                        raw_json = upload_record.get("raw_json")
                except Exception as e:
                    logger.debug(f"Не удалось получить raw_json для {filename}: {e}")

                # Определяем ресурс с учетом содержимого (используем единый классификатор)
                resource = ResourceClassifier.classify(filename, raw_json)
                if resource and resource != "other":
                    file_to_resource_map[filename] = resource
                    logger.debug(f"Файл {filename} определен как ресурс: {resource}")

        # Определяем доступные ресурсы на основе агрегированных данных
        available_resources = set()
        aggregated_data = _get_aggregated_data_for_enterprise(enterprise_id)

        if aggregated_data and "resources" in aggregated_data:
            resources = aggregated_data["resources"]
            for resource_name, resource_data in resources.items():
                if resource_data and isinstance(resource_data, dict):
                    # Проверяем наличие данных хотя бы в одном квартале
                    quarters = [
                        q
                        for q in resource_data.keys()
                        if q and isinstance(resource_data[q], dict)
                    ]
                    if quarters:
                        available_resources.add(resource_name)

        # Дополнительно проверяем по именам файлов
        for filename, resource in file_to_resource_map.items():
            available_resources.add(resource)

        # Проверяем наличие специализированных JSON файлов (nodes, equipment, envelope)
        # Эти ресурсы не попадают в aggregated_data["resources"]
        AGGREGATED_DIR = Path(
            os.getenv(
                "AGGREGATED_DIR",
                os.path.join(os.getenv("INBOX_DIR", "/data/inbox"), "aggregated"),
            )
        )
        for batch_id in [u.get("batch_id") for u in uploads if u.get("batch_id")]:
            if (AGGREGATED_DIR / f"{batch_id}_nodes.json").exists():
                available_resources.add("nodes")
            if (AGGREGATED_DIR / f"{batch_id}_equipment.json").exists():
                available_resources.add("equipment")
            if (AGGREGATED_DIR / f"{batch_id}_envelope.json").exists():
                available_resources.add("envelope")

        available_resources_list = sorted(list(available_resources))

        # Проверяем обязательные ресурсы
        required_resources = get_required_resources()
        missing_resources = [
            resource
            for resource in required_resources
            if resource not in available_resources
        ]

        # Определяем недостающие файлы
        missing_files = _get_missing_files_for_resources(
            missing_resources, available_files
        )

        # Вычисляем статус ресурсов
        required_resources_status = _get_resources_status(
            required_resources, available_resources, aggregated_data
        )
        optional_resources_status = _get_resources_status(
            get_optional_resources(), available_resources, aggregated_data
        )

        # Вычисляем показатель готовности
        completeness_score = _calculate_completeness_score(
            required_resources,
            available_resources_list,
            missing_resources,
            aggregated_data,
        )

        # Формируем предупреждения
        warnings = _generate_warnings(
            missing_resources, missing_files, available_resources_list, aggregated_data
        )

        # НОВОЕ: Валидация данных для каждого листа
        sheet_validation, missing_sheet_data = _validate_sheets_data(
            enterprise_id, aggregated_data, uploads
        )

        # Добавляем ошибки валидации листов в warnings
        for sheet_name, validation_result in sheet_validation.items():
            if not validation_result.get("valid", True):
                errors = validation_result.get("errors", [])
                warnings.extend(errors)
                missing_sheet_data.extend([f"{sheet_name}: {err}" for err in errors])

        # Определяем готовность (учитываем валидацию листов)
        ready = (
            len(missing_resources) == 0
            and completeness_score >= MINIMAL_REQUIREMENTS["min_completeness_score"]
            and all(
                result.get("valid", True)
                for result in sheet_validation.values()
                if result.get("required", False)
            )
        )

        progress_percentage = int(completeness_score * 100)

        result = {
            "ready": ready,
            "completeness_score": round(completeness_score, 2),
            "missing_resources": missing_resources,
            "missing_files": missing_files,
            "available_resources": available_resources_list,
            "available_files": available_files,
            "warnings": warnings,
            "progress_percentage": progress_percentage,
            "required_resources_status": required_resources_status,
            "optional_resources_status": optional_resources_status,
            "sheet_validation": sheet_validation,
            "missing_sheet_data": missing_sheet_data,
        }

        logger.info(
            f"Результат проверки готовности: ready={ready}, "
            f"completeness={completeness_score:.2f}, "
            f"missing={missing_resources}"
        )

        return result
    except Exception as e:
        logger.error(
            f"Критическая ошибка при проверке готовности для предприятия {enterprise_id}: {e}",
            exc_info=True,
        )
        return {
            "ready": False,
            "completeness_score": 0.0,
            "missing_resources": get_required_resources(),
            "missing_files": [],
            "available_resources": [],
            "available_files": [],
            "warnings": [f"Критическая ошибка при проверке готовности: {str(e)}"],
            "progress_percentage": 0,
            "required_resources_status": {},
            "optional_resources_status": {},
        }


def _get_aggregated_data_for_enterprise(enterprise_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает агрегированные данные для предприятия.

    Пробует агрегировать данные из всех загрузок предприятия.
    """
    # Определяем путь к директории агрегированных данных
    # Определяем путь относительно директории ingest
    ingest_path = Path(__file__).resolve().parent.parent
    INBOX_DIR = Path(os.getenv("INBOX_DIR", str(ingest_path / "data" / "inbox")))
    AGGREGATED_DIR = Path(os.getenv("AGGREGATED_DIR", str(INBOX_DIR / "aggregated")))
    AGGREGATED_DIR.mkdir(parents=True, exist_ok=True)

    uploads = database.list_uploads_for_enterprise(enterprise_id)

    # Собираем данные из всех успешных загрузок
    all_aggregated = {
        "resources": {
            "electricity": {},
            "gas": {},
            "water": {},
            "fuel": {},
            "coal": {},
            "heat": {},
            "production": {},
        }
    }

    for upload in uploads:
        batch_id = upload.get("batch_id")
        status = upload.get("status")
        filename = upload.get("filename", "unknown")

        if status == "success" and batch_id:
            try:
                logger.debug(
                    f"🔍 [DIAG] Обработка загрузки: {filename} (batch_id: {batch_id[:8]}...)"
                )

                # Сначала пробуем загрузить переагрегированный файл
                aggregated_file = AGGREGATED_DIR / f"{batch_id}_aggregated.json"
                aggregated = None

                if aggregated_file.exists():
                    try:
                        logger.info(
                            f"📂 [DIAG] Найден переагрегированный файл: {aggregated_file.name}"
                        )
                        with open(aggregated_file, "r", encoding="utf-8") as f:
                            aggregated = json.load(f)
                        logger.info(
                            f"✅ [DIAG] Загружен переагрегированный файл для {filename}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"⚠️ [DIAG] Ошибка загрузки переагрегированного файла {aggregated_file.name}: {e}"
                        )

                # Если переагрегированного файла нет, агрегируем из БД
                if not aggregated:
                    upload_record = database.get_upload_by_batch(batch_id)
                    if upload_record and upload_record.get("raw_json"):
                        raw_json = upload_record["raw_json"]
                        logger.debug(
                            f"📊 [DIAG] raw_json найден, ключи: {list(raw_json.keys())}"
                        )
                        logger.info(f"🔄 [DIAG] Агрегирую из БД для {filename}")
                        aggregated = aggregate_from_db_json(raw_json)
                    else:
                        logger.debug(f"⚠️ [DIAG] Нет raw_json для {filename}")

                if aggregated and "resources" in aggregated:
                    logger.info(
                        f"✅ [DIAG] Агрегация успешна для {filename}: ресурсы={list(aggregated['resources'].keys())}"
                    )
                    # Объединяем данные из всех загрузок
                    for resource_name, resource_data in aggregated["resources"].items():
                        if resource_data and isinstance(resource_data, dict):
                            if resource_name not in all_aggregated["resources"]:
                                all_aggregated["resources"][resource_name] = {}
                            # Объединяем кварталы (не перезаписываем, если уже есть)
                            for quarter, quarter_data in resource_data.items():
                                if quarter_data and isinstance(quarter_data, dict):
                                    months_count = len(quarter_data.get("months", []))
                                    quarter_totals = quarter_data.get(
                                        "quarter_totals", {}
                                    )
                                    logger.info(
                                        f"📊 [DIAG] Ресурс {resource_name}, квартал {quarter}: "
                                        f"{months_count} месяцев, quarter_totals={list(quarter_totals.keys()) if quarter_totals else 'пусто'}, "
                                        f"active_kwh={quarter_totals.get('active_kwh') if quarter_totals else 'нет'}"
                                    )
                                    # Если квартал уже существует, объединяем месяцы
                                    if (
                                        quarter
                                        in all_aggregated["resources"][resource_name]
                                    ):
                                        existing_quarter = all_aggregated["resources"][
                                            resource_name
                                        ][quarter]
                                        existing_months = existing_quarter.get(
                                            "months", []
                                        )
                                        new_months = quarter_data.get("months", [])
                                        # Объединяем месяцы
                                        existing_quarter["months"] = (
                                            existing_months + new_months
                                        )
                                        # Обновляем quarter_totals, если они есть в новых данных
                                        if quarter_totals:
                                            existing_quarter["quarter_totals"] = (
                                                quarter_totals
                                            )
                                        # ВАЖНО: Сохраняем by_usage, если он есть в новых данных
                                        new_by_usage = quarter_data.get("by_usage")
                                        if new_by_usage and isinstance(
                                            new_by_usage, dict
                                        ):
                                            existing_quarter["by_usage"] = new_by_usage
                                            logger.debug(
                                                f"✅ [DIAG] Сохранен by_usage для {resource_name} {quarter}: {list(new_by_usage.keys())}"
                                            )
                                        logger.debug(
                                            f"🔄 [DIAG] Объединены месяцы для {resource_name} {quarter}: {len(existing_months)} + {len(new_months)} = {len(existing_quarter['months'])}"
                                        )
                                    else:
                                        all_aggregated["resources"][resource_name][
                                            quarter
                                        ] = quarter_data
                                        # Логируем наличие by_usage при первом добавлении
                                        if quarter_data.get("by_usage"):
                                            logger.debug(
                                                f"✅ [DIAG] Добавлен квартал {resource_name} {quarter} с by_usage: {list(quarter_data.get('by_usage', {}).keys())}"
                                            )
                                        else:
                                            logger.debug(
                                                f"⚠️ [DIAG] Добавлен квартал {resource_name} {quarter} БЕЗ by_usage"
                                            )
                elif aggregated:
                    logger.warning(
                        f"⚠️ [DIAG] Агрегация не удалась для {filename}: нет 'resources' в aggregated"
                    )
                else:
                    logger.debug(f"⚠️ [DIAG] Нет данных для {filename}")
            except Exception as e:
                logger.warning(
                    f"Ошибка при агрегации данных из batch_id {batch_id}: {e}",
                    exc_info=True,
                )
                continue

    # Вычисляем квартальные итоги для объединенных данных
    logger.info("🔍 [DIAG] Перед расчетом квартальных итогов в валидаторе")
    logger.info(
        f"📊 [DIAG] Ресурсы перед расчетом: {list(all_aggregated['resources'].keys())}"
    )
    for resource_name, resource_data in all_aggregated["resources"].items():
        if resource_data:
            logger.info(f"  - {resource_name}: {len(resource_data)} кварталов")
            for quarter, quarter_data in resource_data.items():
                months_count = len(quarter_data.get("months", []))
                logger.debug(f"    └─ {quarter}: {months_count} месяцев")

    from utils.energy_aggregator import _compute_quarter_totals

    _compute_quarter_totals(all_aggregated["resources"])

    # КРИТИЧНО: Распределяем canonical by_usage по кварталам для electricity
    # Это нужно делать ДО валидации, чтобы валидатор видел by_usage в кварталах
    _distribute_canonical_by_usage_to_quarters(all_aggregated, enterprise_id, uploads)

    logger.info("✅ [DIAG] После расчета квартальных итогов в валидаторе")
    for resource_name, resource_data in all_aggregated["resources"].items():
        if resource_data:
            for quarter, quarter_data in resource_data.items():
                quarter_totals = quarter_data.get("quarter_totals", {})
                if quarter_totals:
                    logger.info(
                        f"  - {resource_name} {quarter}: quarter_totals={list(quarter_totals.keys())}"
                    )
                else:
                    logger.warning(
                        f"  ⚠️ {resource_name} {quarter}: quarter_totals отсутствует!"
                    )

                # ДИАГНОСТИКА: Проверяем наличие by_usage после вычисления итогов
                by_usage = quarter_data.get("by_usage")
                if by_usage and isinstance(by_usage, dict) and len(by_usage) > 0:
                    logger.debug(
                        f"  ✅ {resource_name} {quarter}: by_usage сохранен - {list(by_usage.keys())}"
                    )
                elif resource_name == "electricity":
                    logger.warning(
                        f"  ⚠️ {resource_name} {quarter}: by_usage ОТСУТСТВУЕТ после вычисления итогов!"
                    )
                    logger.warning(
                        "     Это может привести к ошибке валидации для листа '04_Баланс'"
                    )

    # Проверяем, есть ли хотя бы какие-то данные
    has_data = any(
        resource_data and isinstance(resource_data, dict) and len(resource_data) > 0
        for resource_data in all_aggregated["resources"].values()
    )

    if not has_data:
        logger.warning(
            "⚠️ [DIAG] Нет данных для агрегации после обработки всех загрузок"
        )

    return all_aggregated if has_data else None


def _distribute_canonical_by_usage_to_quarters(
    all_aggregated: Dict[str, Any], enterprise_id: int, uploads: List[Dict[str, Any]]
) -> None:
    """
    Распределяет canonical by_usage по кварталам для electricity.

    Это нужно делать ДО валидации, чтобы валидатор видел by_usage в кварталах.
    """
    try:
        from settings.excel_semantic_settings import get_excel_semantic_mode
        from utils.canonical_collector import collect_canonical_from_workbook
        from utils.canonical_to_passport import canonical_to_passport_payload
        from ai.ai_excel_semantic_parser import CanonicalSourceData

        excel_ai_mode_runtime = get_excel_semantic_mode()
        logger.info(f"🔍 Режим canonical: {excel_ai_mode_runtime}")

        # Пробуем собрать canonical независимо от режима
        # Если режим "off", collect_canonical_from_workbook может вернуть None,
        # но мы все равно попробуем
        if excel_ai_mode_runtime == "off":
            logger.warning(
                "⚠️ Режим canonical: 'off'. Попытка собрать canonical может не удаться. Рекомендуется установить EXCEL_SEMANTIC_AI_MODE=assist"
            )

        logger.info("🔍 Начинаем поиск canonical данных для распределения by_usage")

        # Ищем canonical данные в загрузках предприятия
        # Собираем canonical из ВСЕХ файлов предприятия, а не только из одного
        global_canonical = CanonicalSourceData()
        found_equipment = False

        for upload in uploads:
            batch_id = upload.get("batch_id")
            status = upload.get("status")
            if status == "success" and batch_id:
                try:
                    upload_record = database.get_upload_by_batch(batch_id)
                    if upload_record and upload_record.get("file_path"):
                        file_path = upload_record["file_path"]
                        if file_path and Path(file_path).exists():
                            # Пробуем собрать canonical из файла
                            canonical = collect_canonical_from_workbook(file_path)
                            if canonical:
                                # Объединяем оборудование из всех файлов
                                if canonical.equipment:
                                    global_canonical.equipment.extend(
                                        canonical.equipment
                                    )
                                    found_equipment = True
                                    logger.debug(
                                        f"✅ Найдено {len(canonical.equipment)} единиц оборудования в {Path(file_path).name}"
                                    )
                                # Объединяем ресурсы
                                if canonical.resources:
                                    # Объединяем ресурсы, приоритет - более поздние данные
                                    for resource in canonical.resources:
                                        existing = next(
                                            (
                                                r
                                                for r in global_canonical.resources
                                                if r.resource == resource.resource
                                            ),
                                            None,
                                        )
                                        if existing:
                                            # Обновляем существующий ресурс
                                            if (
                                                resource.series
                                                and resource.series.annual
                                            ):
                                                existing.series = resource.series
                                        else:
                                            global_canonical.resources.append(resource)
                except Exception as e:
                    logger.debug(f"Ошибка при получении canonical из {batch_id}: {e}")
                    continue

        # Если оборудование не найдено через canonical (например, режим "off"),
        # пробуем загрузить из equipment JSON файлов
        if not found_equipment or not global_canonical.equipment:
            logger.info(
                "Оборудование не найдено через canonical, пробуем загрузить из JSON файлов"
            )
            ingest_path = Path(__file__).resolve().parent.parent
            INBOX_DIR = Path(
                os.getenv("INBOX_DIR", str(ingest_path / "data" / "inbox"))
            )
            AGGREGATED_DIR = Path(
                os.getenv("AGGREGATED_DIR", str(INBOX_DIR / "aggregated"))
            )

            for upload in uploads:
                batch_id = upload.get("batch_id")
                if batch_id:
                    equipment_json_path = AGGREGATED_DIR / f"{batch_id}_equipment.json"
                    if equipment_json_path.exists():
                        try:
                            equipment_data = json.loads(
                                equipment_json_path.read_text(encoding="utf-8")
                            )
                            # Преобразуем equipment JSON в EquipmentItem
                            equipment_items = _convert_equipment_json_to_items(
                                equipment_data
                            )
                            if equipment_items:
                                global_canonical.equipment.extend(equipment_items)
                                found_equipment = True
                                logger.info(
                                    f"✅ Загружено {len(equipment_items)} единиц оборудования из {equipment_json_path.name}"
                                )
                                break
                        except Exception as e:
                            logger.debug(
                                f"Ошибка при загрузке equipment JSON из {batch_id}: {e}"
                            )
                            continue

        if not found_equipment or not global_canonical.equipment:
            logger.warning("⚠️ Canonical данные с оборудованием не найдены")
            logger.warning("   Рекомендации:")
            logger.warning(
                "   1. Установите EXCEL_SEMANTIC_AI_MODE=assist для включения canonical mode"
            )
            logger.warning(
                "   2. Убедитесь, что файл оборудования загружен и обработан"
            )
            logger.warning(
                "   3. Проверьте наличие {batch_id}_equipment.json в aggregated директории"
            )
            logger.info(
                "🔄 Продолжаем с принудительным вычислением by_usage без оборудования"
            )

        equipment_count = (
            len(global_canonical.equipment) if global_canonical.equipment else 0
        )
        if equipment_count > 0:
            logger.info(
                f"✅ Найдено {equipment_count} единиц оборудования для распределения by_usage"
            )
        else:
            logger.info(
                "⚠️ Оборудование не найдено, будет использовано стандартное распределение by_usage"
            )

        # Получаем annual_total для electricity из aggregated данных, если его нет в canonical
        electricity_data = all_aggregated.get("resources", {}).get("electricity", {})
        if not electricity_data:
            logger.warning("⚠️ Нет данных electricity для распределения by_usage")
            return

        annual_total = None

        # Пробуем получить из ANNUAL
        annual_data = electricity_data.get("ANNUAL")
        if annual_data and isinstance(annual_data, dict):
            annual_totals = annual_data.get("quarter_totals", {})
            annual_total = annual_totals.get("active_kwh")

        # Если нет в ANNUAL, вычисляем сумму по всем кварталам
        if not annual_total:
            total_consumption = 0.0
            for quarter_key, quarter_data in electricity_data.items():
                if quarter_key == "ANNUAL":
                    continue
                if isinstance(quarter_data, dict):
                    quarter_totals = quarter_data.get("quarter_totals", {})
                    if quarter_totals:
                        quarter_total = quarter_totals.get("active_kwh", 0)
                        if quarter_total:
                            total_consumption += float(quarter_total)
            if total_consumption > 0:
                annual_total = total_consumption
                logger.info(
                    f"✅ Annual total вычислен из квартальных данных: {annual_total}"
                )

        if not annual_total or annual_total <= 0:
            logger.warning(
                "⚠️ Annual total для electricity не найден или равен 0. Невозможно вычислить by_usage"
            )
            # Даже без annual_total, попробуем создать минимальный by_usage для каждого квартала
            _create_minimal_by_usage_for_quarters(electricity_data)
            return

        # Если есть оборудование, пробуем вычислить canonical by_usage
        canonical_by_usage = None
        if equipment_count > 0:
            # Если annual_total найден, добавляем его в canonical resources
            from ai.ai_excel_semantic_parser import ResourceEntry, TimeSeries

            existing_electricity = next(
                (r for r in global_canonical.resources if r.resource == "electricity"),
                None,
            )
            if existing_electricity:
                if (
                    not existing_electricity.series
                    or not existing_electricity.series.annual
                ):
                    existing_electricity.series = TimeSeries(annual=float(annual_total))
            else:
                global_canonical.resources.append(
                    ResourceEntry(
                        resource="electricity",
                        series=TimeSeries(annual=float(annual_total)),
                    )
                )
            logger.info(
                f"✅ Annual total для electricity добавлен в canonical: {annual_total}"
            )

            canonical_source_data = global_canonical

            # Преобразуем canonical в payload для получения by_usage
            try:
                canonical_payload = canonical_to_passport_payload(canonical_source_data)
                canonical_by_usage = (
                    canonical_payload.get("balance", {})
                    .get("by_usage", {})
                    .get("electricity")
                )

                if (
                    canonical_by_usage
                    and isinstance(canonical_by_usage, dict)
                    and len(canonical_by_usage) > 0
                ):
                    logger.info(
                        f"✅ Canonical by_usage найден: {list(canonical_by_usage.keys())}"
                    )
                else:
                    logger.warning(
                        "⚠️ Canonical by_usage для electricity не найден в payload, используем стандартное распределение"
                    )
                    canonical_by_usage = None
            except Exception as e:
                logger.warning(
                    f"⚠️ Ошибка при вычислении canonical by_usage: {e}, используем стандартное распределение"
                )
                canonical_by_usage = None

        # Если canonical_by_usage не найден, создаем стандартное распределение
        if not canonical_by_usage or not isinstance(canonical_by_usage, dict):
            logger.info("🔄 Создаем стандартное распределение by_usage")
            canonical_by_usage = _create_standard_by_usage_distribution(annual_total)
            logger.info(
                f"✅ Стандартное распределение создано: {list(canonical_by_usage.keys())}"
            )

        # Вычисляем общее потребление по всем кварталам
        total_quarterly_consumption = 0.0
        for quarter_key, quarter_data in electricity_data.items():
            if quarter_key == "ANNUAL":
                continue
            if isinstance(quarter_data, dict):
                quarter_total = quarter_data.get("quarter_totals", {}).get(
                    "active_kwh", 0
                )
                if quarter_total:
                    total_quarterly_consumption += float(quarter_total)

        if total_quarterly_consumption <= 0:
            logger.warning(
                "⚠️ Не удалось распределить by_usage: total_quarterly_consumption=0"
            )
            # Даже при нулевом потреблении создаем минимальный by_usage
            _create_minimal_by_usage_for_quarters(electricity_data)
            return

        # Распределяем by_usage по кварталам пропорционально потреблению
        distributed_count = 0
        for quarter_key, quarter_data in electricity_data.items():
            if quarter_key == "ANNUAL":
                continue
            if isinstance(quarter_data, dict):
                quarter_total = quarter_data.get("quarter_totals", {}).get(
                    "active_kwh", 0
                )
                if quarter_total and quarter_total > 0:
                    # Пропорциональное распределение
                    quarter_ratio = float(quarter_total) / total_quarterly_consumption
                    quarter_by_usage = {
                        category: round(float(value) * quarter_ratio, 2)
                        for category, value in canonical_by_usage.items()
                    }
                    quarter_data["by_usage"] = quarter_by_usage
                    distributed_count += 1
                    logger.debug(
                        "Распределен by_usage для electricity %s: %s (ratio=%.3f)",
                        quarter_key,
                        list(quarter_by_usage.keys()),
                        quarter_ratio,
                    )

        if distributed_count > 0:
            logger.info(
                "✅ by_usage распределен по %d кварталам electricity (annual_total=%.2f, quarterly_total=%.2f)",
                distributed_count,
                float(annual_total),
                total_quarterly_consumption,
            )
        else:
            logger.warning(
                "⚠️ Не удалось распределить by_usage: нет кварталов с активным потреблением"
            )
            # Создаем минимальный by_usage как fallback
            _create_minimal_by_usage_for_quarters(electricity_data)

    except Exception as e:
        logger.warning(
            f"Ошибка при распределении canonical by_usage: {e}", exc_info=True
        )
        # В случае ошибки создаем минимальный by_usage как fallback
        try:
            electricity_data = all_aggregated.get("resources", {}).get(
                "electricity", {}
            )
            if electricity_data and isinstance(electricity_data, dict):
                _create_minimal_by_usage_for_quarters(electricity_data)
                logger.info("✅ Минимальный by_usage создан как fallback после ошибки")
            else:
                logger.warning(
                    "⚠️ Невозможно создать минимальный by_usage: нет данных electricity"
                )
        except Exception as fallback_error:
            logger.error(
                f"Критическая ошибка при создании минимального by_usage: {fallback_error}",
                exc_info=True,
            )


def _create_standard_by_usage_distribution(annual_total: float) -> Dict[str, float]:
    """
    Создает стандартное распределение by_usage по категориям.

    Используется когда оборудование не найдено или canonical by_usage не вычислен.

    Args:
        annual_total: Годовое потребление электроэнергии (кВт·ч)

    Returns:
        Словарь с распределением по категориям использования
    """
    # Стандартное распределение для промышленных предприятий:
    # - technological: 50% - технологическое оборудование
    # - production: 30% - производственные процессы
    # - own_needs: 15% - собственные нужды (освещение, вентиляция и т.д.)
    # - household: 5% - хозяйственно-бытовые нужды

    return {
        "technological": round(annual_total * 0.50, 2),
        "production": round(annual_total * 0.30, 2),
        "own_needs": round(annual_total * 0.15, 2),
        "household": round(annual_total * 0.05, 2),
    }


def _create_minimal_by_usage_for_quarters(electricity_data: Dict[str, Any]) -> None:
    """
    Создает минимальный by_usage для каждого квартала electricity.

    Используется как аварийный fallback, когда невозможно вычислить нормальное распределение.

    Args:
        electricity_data: Словарь с данными electricity по кварталам
    """
    logger.info("🔧 Создание минимального by_usage для всех кварталов electricity")

    distributed_count = 0
    for quarter_key, quarter_data in electricity_data.items():
        if quarter_key == "ANNUAL":
            continue
        if not isinstance(quarter_data, dict):
            continue

        quarter_totals = quarter_data.get("quarter_totals", {})
        active_kwh = quarter_totals.get("active_kwh", 0) if quarter_totals else 0

        if active_kwh and active_kwh > 0:
            # Минимальное распределение для квартала
            by_usage = {
                "technological": round(active_kwh * 0.50, 2),
                "production": round(active_kwh * 0.30, 2),
                "own_needs": round(active_kwh * 0.15, 2),
                "household": round(active_kwh * 0.05, 2),
            }

            quarter_data["by_usage"] = by_usage
            distributed_count += 1
            logger.debug(
                f"✅ Минимальный by_usage создан для {quarter_key}: {by_usage}"
            )
        else:
            logger.debug(f"⚠️ Пропущен квартал {quarter_key}: active_kwh={active_kwh}")

    if distributed_count > 0:
        logger.info(f"✅ Минимальный by_usage создан для {distributed_count} кварталов")
    else:
        logger.warning(
            "⚠️ Не удалось создать минимальный by_usage: нет кварталов с активным потреблением"
        )


def _get_missing_files_for_resources(
    missing_resources: List[str], available_files: List[str]
) -> List[str]:
    """Определяет недостающие файлы для ресурсов."""
    missing_files = []

    for resource_name in missing_resources:
        config = get_resource_config(resource_name)
        patterns = config.get("file_patterns", [])

        # Проверяем, есть ли хотя бы один файл с нужным паттерном
        found = False
        for pattern in patterns:
            if any(pattern.lower() in filename.lower() for filename in available_files):
                found = True
                break

        if not found and patterns:
            # Добавляем первый паттерн как пример недостающего файла
            missing_files.append(patterns[0])

    return missing_files


def _get_resources_status(
    resources: List[str],
    available_resources: set,
    aggregated_data: Optional[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Возвращает детальный статус ресурсов."""
    status = {}

    for resource_name in resources:
        config = get_resource_config(resource_name)
        is_available = resource_name in available_resources

        # Определяем количество кварталов
        quarters_count = 0
        if aggregated_data and "resources" in aggregated_data:
            resource_data = aggregated_data["resources"].get(resource_name)
            if resource_data and isinstance(resource_data, dict):
                quarters_count = len(
                    [
                        q
                        for q in resource_data.keys()
                        if q and isinstance(resource_data[q], dict)
                    ]
                )

        min_quarters = config.get("min_quarters", 4)
        has_enough_quarters = quarters_count >= min_quarters

        status[resource_name] = {
            "available": is_available,
            "quarters_count": quarters_count,
            "min_quarters": min_quarters,
            "has_enough_quarters": has_enough_quarters,
            "description": config.get("description", ""),
        }

    return status


def _calculate_completeness_score(
    required_resources: List[str],
    available_resources: List[str],
    missing_resources: List[str],
    aggregated_data: Optional[Dict[str, Any]],
) -> float:
    """
    Вычисляет показатель готовности данных (0.0 - 1.0).

    Учитывает:
    - Наличие обязательных ресурсов (вес 60%)
    - Количество кварталов данных (вес 30%)
    - Наличие опциональных ресурсов (вес 10%)
    """
    # Базовая оценка по обязательным ресурсам
    if not required_resources:
        required_score = 1.0
    else:
        required_score = (len(required_resources) - len(missing_resources)) / len(
            required_resources
        )

    # Оценка по кварталам
    quarters_score = 0.0
    if aggregated_data and "resources" in aggregated_data:
        total_quarters = 0
        total_min_quarters = 0

        for resource_name in required_resources:
            resource_data = aggregated_data["resources"].get(resource_name)
            config = get_resource_config(resource_name)
            min_quarters = config.get("min_quarters", 4)

            if resource_data and isinstance(resource_data, dict):
                quarters = len(
                    [
                        q
                        for q in resource_data.keys()
                        if q and isinstance(resource_data[q], dict)
                    ]
                )
                total_quarters += quarters
            total_min_quarters += min_quarters

        if total_min_quarters > 0:
            quarters_score = min(total_quarters / total_min_quarters, 1.0)

    # Оценка по опциональным ресурсам
    optional_resources = get_optional_resources()
    optional_score = 0.0
    if optional_resources:
        available_optional = len(
            [r for r in optional_resources if r in available_resources]
        )
        optional_score = available_optional / len(optional_resources)

    # Взвешенная сумма
    completeness = required_score * 0.6 + quarters_score * 0.3 + optional_score * 0.1

    return max(0.0, min(1.0, completeness))


def _generate_warnings(
    missing_resources: List[str],
    missing_files: List[str],
    available_resources: List[str],
    aggregated_data: Optional[Dict[str, Any]],
) -> List[str]:
    """Генерирует предупреждения о недостающих данных."""
    warnings = []

    try:
        # Предупреждения о недостающих обязательных ресурсах
        if missing_resources:
            for resource_name in missing_resources:
                try:
                    config = get_resource_config(resource_name)
                    description = (
                        config.get("description", resource_name)
                        if config
                        else resource_name
                    )
                    warnings.append(f"Отсутствует обязательный ресурс: {description}")
                except Exception as e:
                    logger.warning(
                        f"Ошибка при получении конфигурации ресурса {resource_name}: {e}"
                    )
                    warnings.append(f"Отсутствует обязательный ресурс: {resource_name}")

        # Предупреждения о недостающих файлах
        if missing_files:
            warnings.append(f"Необходимо загрузить файлы: {', '.join(missing_files)}")

        # Предупреждения о недостаточном количестве кварталов
        if aggregated_data and "resources" in aggregated_data:
            for resource_name, resource_data in aggregated_data["resources"].items():
                if resource_name not in available_resources:
                    continue

                try:
                    config = get_resource_config(resource_name)
                    min_quarters = config.get("min_quarters", 4) if config else 4

                    if resource_data and isinstance(resource_data, dict):
                        quarters = len(
                            [
                                q
                                for q in resource_data.keys()
                                if q and isinstance(resource_data[q], dict)
                            ]
                        )

                        if quarters < min_quarters:
                            warnings.append(
                                f"Ресурс {resource_name}: недостаточно кварталов "
                                f"({quarters} из {min_quarters})"
                            )
                except Exception as e:
                    logger.warning(
                        f"Ошибка при проверке кварталов для ресурса {resource_name}: {e}"
                    )
                    continue

        if not warnings:
            warnings.append("Все необходимые данные загружены")
    except Exception as e:
        logger.error(f"Ошибка при генерации предупреждений: {e}", exc_info=True)
        warnings.append("Ошибка при проверке готовности данных")

    return warnings


def get_upload_checklist(enterprise_id: int) -> Dict[str, Any]:
    """
    Возвращает чек-лист требуемых файлов для предприятия.

    Args:
        enterprise_id: ID предприятия

    Returns:
        Словарь с чек-листом:
        {
            "required_files": List[Dict],
            "optional_files": List[Dict],
            "uploaded_files": List[str],
            "missing_required": List[str]
        }
    """
    try:
        uploads = database.list_uploads_for_enterprise(enterprise_id)
        uploaded_files = [
            u.get("filename", "") for u in uploads if u.get("status") == "success"
        ]
    except Exception as e:
        logger.error(
            f"Ошибка при получении чек-листа для предприятия {enterprise_id}: {e}"
        )
        uploaded_files = []

    try:
        # Формируем список требуемых файлов
        required_files = []
        optional_files = []

        for category, resources in REQUIRED_DATA_MATRIX.items():
            for resource_name, config in resources.items():
                is_required = config.get("required", False)
                patterns = config.get("file_patterns", [])
                description = config.get("description", resource_name)

                # Улучшенная проверка соответствия файла паттернам и содержимому
                def file_matches_patterns(
                    fname: str, patts: List[str], res_name: str
                ) -> bool:
                    fname_lower = fname.lower()
                    fname_no_ext = (
                        fname_lower.rsplit(".", 1)[0]
                        if "." in fname_lower
                        else fname_lower
                    )

                    # Проверяем паттерны
                    for pattern in patts:
                        pattern_lower = pattern.lower()
                        pattern_no_ext = (
                            pattern_lower.rsplit(".", 1)[0]
                            if "." in pattern_lower
                            else pattern_lower
                        )
                        if (
                            pattern_lower in fname_lower
                            or pattern_no_ext in fname_no_ext
                        ):
                            return True

                    # Проверяем ключевые слова
                    keywords = config.get("keywords", [])
                    if any(keyword.lower() in fname_lower for keyword in keywords):
                        return True

                    # Проверяем содержимое файла, если есть
                    for upload in uploads:
                        if upload.get("filename", "").lower() == fname_lower:
                            try:
                                upload_record = database.get_upload_by_batch(
                                    upload.get("batch_id")
                                )
                                if upload_record:
                                    raw_json = upload_record.get("raw_json")
                                    if raw_json:
                                        # Анализируем содержимое
                                        from utils.content_analyzer import (
                                            analyze_file_content,
                                        )

                                        content_resource = analyze_file_content(
                                            raw_json, fname
                                        )
                                        if content_resource == res_name:
                                            return True
                            except Exception:
                                pass

                    return False

                file_info = {
                    "resource": resource_name,
                    "description": description,
                    "file_patterns": patterns,
                    "min_quarters": config.get("min_quarters", 4)
                    if category == "energy_resources"
                    else None,
                    "uploaded": any(
                        file_matches_patterns(filename, patterns, resource_name)
                        for filename in uploaded_files
                    ),
                }

                if is_required:
                    required_files.append(file_info)
                else:
                    optional_files.append(file_info)

        missing_required = [f["resource"] for f in required_files if not f["uploaded"]]

        return {
            "required_files": required_files,
            "optional_files": optional_files,
            "uploaded_files": uploaded_files,
            "missing_required": missing_required,
        }
    except Exception as e:
        logger.error(
            f"Критическая ошибка при формировании чек-листа для предприятия {enterprise_id}: {e}",
            exc_info=True,
        )
        return {
            "required_files": required_files,
            "optional_files": optional_files,
            "uploaded_files": uploaded_files if "uploaded_files" in locals() else [],
            "missing_required": get_required_resources(),
        }


def _validate_sheets_data(
    enterprise_id: int,
    aggregated_data: Optional[Dict[str, Any]],
    uploads: List[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    """
    Валидирует данные для каждого листа паспорта.

    Args:
        enterprise_id: ID предприятия
        aggregated_data: Агрегированные данные
        uploads: Список загрузок предприятия

    Returns:
        (sheet_validation_dict, missing_sheet_data_list)
    """
    sheet_validation = {}
    missing_sheet_data = []

    # Получаем пути к JSON файлам (должен совпадать с путем в main.py)
    import os

    # Используем ту же логику, что и в main.py
    INBOX_DIR = os.getenv("INBOX_DIR", "/data/inbox")
    AGGREGATED_DIR = Path(
        os.getenv("AGGREGATED_DIR", os.path.join(INBOX_DIR, "aggregated"))
    )

    # Собираем все batch_id для поиска JSON файлов
    batch_ids = [upload.get("batch_id") for upload in uploads if upload.get("batch_id")]

    # Загружаем дополнительные данные
    equipment_data = None
    envelope_data = None
    nodes_data = None
    usage_data = None

    for batch_id in batch_ids:
        if not batch_id:
            continue

        # Equipment
        if equipment_data is None:
            equipment_path = AGGREGATED_DIR / f"{batch_id}_equipment.json"
            if not equipment_path.exists():
                # Пробуем общий файл
                equipment_path = AGGREGATED_DIR / "oborudovanie_equipment.json"
            if equipment_path.exists():
                try:
                    equipment_data = json.loads(
                        equipment_path.read_text(encoding="utf-8")
                    )
                except Exception as e:
                    logger.warning(f"Ошибка загрузки equipment JSON: {e}")

        # Расчет теплопотерь по зданиям
        if envelope_data is None:
            envelope_path = AGGREGATED_DIR / f"{batch_id}_envelope.json"
            if not envelope_path.exists():
                envelope_path = AGGREGATED_DIR / "ograjdayuschie_envelope.json"
            if envelope_path.exists():
                try:
                    envelope_data = json.loads(
                        envelope_path.read_text(encoding="utf-8")
                    )
                except Exception as e:
                    logger.warning(
                        f"Ошибка загрузки JSON расчета теплопотерь по зданиям: {e}"
                    )

        # Nodes
        if nodes_data is None:
            nodes_path = AGGREGATED_DIR / f"{batch_id}_nodes.json"
            if nodes_path.exists():
                try:
                    nodes_data = json.loads(nodes_path.read_text(encoding="utf-8"))
                except Exception as e:
                    logger.warning(f"Ошибка загрузки nodes JSON: {e}")

    # Usage categories
    usage_path = AGGREGATED_DIR / "usage_categories.json"
    if usage_path.exists():
        try:
            usage_data = json.loads(usage_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Ошибка загрузки usage JSON: {e}")

    # Формируем структуру данных для валидации
    validation_data = {
        "resources": aggregated_data.get("resources", {}) if aggregated_data else {},
        "equipment": equipment_data,
        "envelope": envelope_data,
        "nodes": nodes_data,
        "usage": usage_data,
    }

    # Валидируем каждый обязательный лист
    for sheet_name, sheet_req in PASSPORT_SHEET_REQUIREMENTS.items():
        if not sheet_req.required:
            continue

        # Подготавливаем данные для этого листа
        sheet_data = _prepare_sheet_data(sheet_name, validation_data)

        # Валидируем
        is_valid, errors = validate_sheet_data(sheet_name, sheet_data)

        # Дополнительная проверка на edge-кейсы для критических листов
        if sheet_name in ["05_Динамика", "Расход на ед.п"]:
            # Проверяем, что если есть производство, то оно не равно нулю везде
            production_data = sheet_data.get("resources", {}).get("production", {})
            if production_data:
                all_zero = all(
                    sum(
                        v
                        for v in q.get("quarter_totals", {}).values()
                        if isinstance(v, (int, float))
                    )
                    == 0
                    for q in production_data.values()
                    if isinstance(q, dict)
                )
                if all_zero and sheet_name == "Расход на ед.п":
                    # Для листа "Расход на ед.п" нулевое производство допустимо (возвращается 0)
                    logger.info(
                        f"Лист '{sheet_name}': производство везде равно 0 - это допустимо для данного листа"
                    )
                elif all_zero:
                    errors.append(
                        f"Лист '{sheet_name}': производство равно 0 во всех кварталах - "
                        f"удельный расход не может быть рассчитан"
                    )

        sheet_validation[sheet_name] = {
            "valid": is_valid,
            "required": sheet_req.required,
            "errors": errors,
            "description": sheet_req.description,
        }

        if not is_valid:
            missing_sheet_data.extend(errors)

    return sheet_validation, missing_sheet_data


def _prepare_sheet_data(
    sheet_name: str, validation_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Подготавливает данные для валидации конкретного листа.

    Args:
        sheet_name: Название листа
        validation_data: Все доступные данные

    Returns:
        Структурированные данные для листа
    """
    result = {}

    # Копируем ресурсы
    resources = validation_data.get("resources", {})
    result["resources"] = resources

    # Извлекаем данные для валидации полей типа electricity.active_kwh, gas.volume_m3
    # Данные хранятся в структуре: resources.electricity.{quarter}.quarter_totals.active_kwh
    # Валидатор ожидает: electricity.active_kwh (словарь по кварталам или значение)

    # Для листа Struktura pr2 и других листов с квартальными данными
    if (
        "Struktura" in sheet_name
        or "Структура" in sheet_name
        or "Динамика" in sheet_name
    ):
        # Извлекаем electricity данные
        electricity_data = resources.get("electricity", {})
        logger.debug(
            f"Для листа '{sheet_name}': electricity_data keys: {list(electricity_data.keys()) if electricity_data else 'None'}"
        )
        if electricity_data:
            # Формируем словари по кварталам для active_kwh, reactive_kvarh
            active_kwh_by_quarter = {}
            reactive_kvarh_by_quarter = {}
            quarter_totals_by_quarter = {}

            for quarter, quarter_data in electricity_data.items():
                if isinstance(quarter_data, dict):
                    quarter_totals = quarter_data.get("quarter_totals", {})
                    if quarter_totals:
                        if "active_kwh" in quarter_totals:
                            active_kwh_by_quarter[quarter] = quarter_totals[
                                "active_kwh"
                            ]
                        if "reactive_kvarh" in quarter_totals:
                            reactive_kvarh_by_quarter[quarter] = quarter_totals[
                                "reactive_kvarh"
                            ]
                        quarter_totals_by_quarter[quarter] = quarter_totals
                    else:
                        # Если quarter_totals отсутствует, пытаемся вычислить из months
                        months = quarter_data.get("months", [])
                        if months:
                            active_kwh_total = 0.0
                            reactive_kvarh_total = 0.0
                            for month in months:
                                values = month.get("values", {})
                                if "active_kwh" in values and values["active_kwh"]:
                                    try:
                                        active_kwh_total += float(values["active_kwh"])
                                    except (ValueError, TypeError):
                                        pass
                                if (
                                    "reactive_kvarh" in values
                                    and values["reactive_kvarh"]
                                ):
                                    try:
                                        reactive_kvarh_total += float(
                                            values["reactive_kvarh"]
                                        )
                                    except (ValueError, TypeError):
                                        pass

                            if active_kwh_total > 0:
                                active_kwh_by_quarter[quarter] = active_kwh_total
                            if reactive_kvarh_total > 0:
                                reactive_kvarh_by_quarter[quarter] = (
                                    reactive_kvarh_total
                                )

                            # Создаём quarter_totals если они отсутствуют
                            if active_kwh_total > 0 or reactive_kvarh_total > 0:
                                quarter_totals_by_quarter[quarter] = {
                                    "active_kwh": active_kwh_total
                                    if active_kwh_total > 0
                                    else None,
                                    "reactive_kvarh": reactive_kvarh_total
                                    if reactive_kvarh_total > 0
                                    else None,
                                }

            # Устанавливаем данные для валидации
            if active_kwh_by_quarter:
                result.setdefault("electricity", {})["active_kwh"] = (
                    active_kwh_by_quarter
                )
            if reactive_kvarh_by_quarter:
                result.setdefault("electricity", {})["reactive_kvarh"] = (
                    reactive_kvarh_by_quarter
                )
            if quarter_totals_by_quarter:
                result.setdefault("electricity", {})["quarter_totals"] = (
                    quarter_totals_by_quarter
                )

        # Извлекаем gas данные
        gas_data = resources.get("gas", {})
        logger.debug(
            f"Для листа '{sheet_name}': gas_data keys: {list(gas_data.keys()) if gas_data else 'None'}"
        )
        if gas_data:
            volume_m3_by_quarter = {}
            quarter_totals_by_quarter = {}

            for quarter, quarter_data in gas_data.items():
                if isinstance(quarter_data, dict):
                    quarter_totals = quarter_data.get("quarter_totals", {})
                    if quarter_totals:
                        if "volume_m3" in quarter_totals:
                            volume_m3_by_quarter[quarter] = quarter_totals["volume_m3"]
                        quarter_totals_by_quarter[quarter] = quarter_totals
                    else:
                        # Если quarter_totals отсутствует, пытаемся вычислить из months
                        months = quarter_data.get("months", [])
                        if months:
                            volume_m3_total = 0.0
                            cost_sum_total = 0.0
                            for month in months:
                                values = month.get("values", {})
                                if "volume_m3" in values and values["volume_m3"]:
                                    try:
                                        volume_m3_total += float(values["volume_m3"])
                                    except (ValueError, TypeError):
                                        pass
                                if "cost_sum" in values and values["cost_sum"]:
                                    try:
                                        cost_sum_total += float(values["cost_sum"])
                                    except (ValueError, TypeError):
                                        pass

                            if volume_m3_total > 0:
                                volume_m3_by_quarter[quarter] = volume_m3_total
                            if volume_m3_total > 0 or cost_sum_total > 0:
                                # Создаём quarter_totals если они отсутствуют
                                quarter_totals_by_quarter[quarter] = {
                                    "volume_m3": volume_m3_total
                                    if volume_m3_total > 0
                                    else None,
                                    "cost_sum": cost_sum_total
                                    if cost_sum_total > 0
                                    else None,
                                }

            # Устанавливаем данные для валидации
            if volume_m3_by_quarter:
                result.setdefault("gas", {})["volume_m3"] = volume_m3_by_quarter
            if quarter_totals_by_quarter:
                result.setdefault("gas", {})["quarter_totals"] = (
                    quarter_totals_by_quarter
                )

    # Добавляем специфичные данные для листов
    if "Equipment" in sheet_name or "Оборудование" in sheet_name:
        result["equipment"] = validation_data.get("equipment", {})

    # Лист расчета теплопотерь по зданиям
    if (
        "02_Исходные данные" in sheet_name
        or "Ограждающие" in sheet_name
        or "Envelope" in sheet_name
    ):
        envelope_data = validation_data.get("envelope", {})
        result["envelope"] = envelope_data
        # Если envelope_data содержит ключ "sections", извлекаем items из каждой секции
        if isinstance(envelope_data, dict) and "sections" in envelope_data:
            sections = envelope_data.get("sections", [])
            all_items = []
            for section in sections:
                if isinstance(section, dict) and "items" in section:
                    all_items.extend(section.get("items", []))
            if all_items:
                result.setdefault("envelope", {})["items"] = all_items

    if "Узлы" in sheet_name or "Nodes" in sheet_name:
        # nodes_data может быть полным объектом с ключами "nodes", "tables", "summary"
        # или просто списком узлов
        nodes_data = validation_data.get("nodes", {})
        if isinstance(nodes_data, dict) and "nodes" in nodes_data:
            # Если это полный объект, извлекаем список узлов
            result["nodes"] = nodes_data.get("nodes", [])
        elif isinstance(nodes_data, list):
            # Если это уже список узлов
            result["nodes"] = nodes_data
        else:
            # Fallback: передаем как есть
            result["nodes"] = nodes_data

    if "Баланс" in sheet_name or "Balans" in sheet_name:
        result["usage"] = validation_data.get("usage", {})
        # Добавляем by_usage данные из ресурсов
        electricity_data = resources.get("electricity", {})
        by_usage_aggregated = {}
        quarters_with_by_usage = []
        quarters_without_by_usage = []

        for quarter, quarter_data in electricity_data.items():
            if quarter == "ANNUAL":
                continue
            if isinstance(quarter_data, dict):
                by_usage = quarter_data.get("by_usage")
                if by_usage and isinstance(by_usage, dict) and len(by_usage) > 0:
                    by_usage_aggregated[quarter] = by_usage
                    quarters_with_by_usage.append(quarter)
                else:
                    quarters_without_by_usage.append(quarter)

        if by_usage_aggregated:
            result.setdefault("electricity", {})["by_usage"] = by_usage_aggregated
            logger.info(
                f"✅ Для листа '{sheet_name}': by_usage найден в {len(by_usage_aggregated)} кварталах: {list(by_usage_aggregated.keys())}"
            )
        else:
            logger.warning(
                f"⚠️ Для листа '{sheet_name}': by_usage НЕ найден ни в одном квартале!"
            )
            logger.warning(f"   Кварталы без by_usage: {quarters_without_by_usage}")
            logger.warning(f"   Всего кварталов electricity: {len(electricity_data)}")
            # Показываем структуру первого квартала для диагностики
            if electricity_data:
                first_quarter = next(
                    iter([k for k in electricity_data.keys() if k != "ANNUAL"]), None
                )
                if first_quarter:
                    first_data = electricity_data[first_quarter]
                    logger.debug(
                        f"   Структура квартала {first_quarter}: {list(first_data.keys()) if isinstance(first_data, dict) else 'не словарь'}"
                    )

    return result


def _convert_equipment_json_to_items(equipment_data: Dict[str, Any]) -> List[Any]:
    """
    Преобразует equipment JSON в список EquipmentItem.

    Структура equipment JSON:
    {
        "sheets": [
            {
                "sheet": "Sheet1",
                "sections": [
                    {
                        "title": "1. Цех ...",
                        "items": [
                            {
                                "name": "Насос",
                                "total_power_kw": 50.0,
                                "unit_power_kw": 25.0,
                                "quantity": 2.0,
                                ...
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    from ai.ai_excel_semantic_parser import EquipmentItem

    equipment_items = []

    try:
        sheets = equipment_data.get("sheets", [])
        for sheet in sheets:
            sections = sheet.get("sections", [])
            for section in sections:
                items = section.get("items", [])
                section_title = section.get("title", "")

                for item in items:
                    name = item.get("name", "")
                    if not name:
                        continue

                    # Извлекаем мощность
                    total_power_kw = item.get("total_power_kw")
                    unit_power_kw = item.get("unit_power_kw")
                    quantity = item.get("quantity", 1.0)

                    # Используем total_power_kw если есть, иначе вычисляем из unit_power_kw * quantity
                    nominal_power = total_power_kw
                    if nominal_power is None and unit_power_kw is not None:
                        nominal_power = (
                            float(unit_power_kw) * float(quantity)
                            if quantity
                            else float(unit_power_kw)
                        )

                    if nominal_power is None or nominal_power <= 0:
                        continue

                    # Извлекаем location из section title (например, "1. Цех №1" -> "Цех №1")
                    location = None
                    if section_title:
                        # Убираем номер секции и точку
                        location = section_title.strip()
                        if location and location[0].isdigit():
                            # Убираем "1. " или "1."
                            parts = location.split(".", 1)
                            if len(parts) > 1:
                                location = parts[1].strip()

                    # Создаем EquipmentItem
                    equipment_item = EquipmentItem(
                        name=str(name),
                        location=location,
                        nominal_power_kw=float(nominal_power),
                        utilization_factor=1.0,  # По умолчанию
                        extra={},
                    )

                    equipment_items.append(equipment_item)

        logger.debug(
            f"Преобразовано {len(equipment_items)} единиц оборудования из JSON"
        )
        return equipment_items

    except Exception as e:
        logger.warning(f"Ошибка при преобразовании equipment JSON в EquipmentItem: {e}")
        return []
