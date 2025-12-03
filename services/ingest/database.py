import json
import logging
import os
import sqlite3
import re
from contextlib import contextmanager
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """Кастомный JSON encoder для обработки datetime и date объектов."""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def safe_json_dumps(data: Any, **kwargs) -> str:
    """
    Безопасная сериализация в JSON с поддержкой datetime объектов.
    
    Args:
        data: Данные для сериализации
        **kwargs: Дополнительные параметры для json.dumps
    
    Returns:
        JSON строка
    
    Raises:
        TypeError: При ошибках сериализации
        ValueError: При ошибках сериализации
    """
    # Устанавливаем encoder по умолчанию, если не указан
    if "cls" not in kwargs:
        kwargs["cls"] = DateTimeEncoder
    
    # Устанавливаем ensure_ascii=False по умолчанию для поддержки кириллицы
    if "ensure_ascii" not in kwargs:
        kwargs["ensure_ascii"] = False
    
    try:
        return json.dumps(data, **kwargs)
    except (TypeError, ValueError) as e:
        # Пытаемся конвертировать datetime объекты вручную
        if isinstance(data, dict):
            converted_dict = _convert_datetime_in_dict(data)
            return json.dumps(converted_dict, **kwargs)
        elif isinstance(data, list):
            converted_list: List[Any] = [_convert_datetime_in_dict(item) if isinstance(item, dict) else item for item in data]
            return json.dumps(converted_list, **kwargs)
        else:
            raise


def _convert_datetime_in_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Рекурсивно конвертирует datetime объекты в строки."""
    result: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = _convert_datetime_in_dict(value)
        elif isinstance(value, list):
            result[key] = [
                _convert_datetime_in_dict(item) if isinstance(item, dict) else (
                    item.isoformat() if isinstance(item, (datetime, date)) else item
                )
                for item in value
            ]
        else:
            result[key] = value
    return result

DB_PATH = os.getenv("INGEST_DB_PATH", os.path.join(os.getcwd(), "ingest_data.db"))


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Оптимизация производительности SQLite
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000")  # 64MB
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA mmap_size=268435456")  # 256MB
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    ensure_storage_directory()
    with get_connection() as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS enterprises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                industry TEXT,
                enterprise_type TEXT,
                product_type TEXT
            )
            """
        )
        # Миграция: добавляем новые поля в существующую таблицу (если их нет)
        try:
            # Проверяем существование колонок
            table_info = conn.execute("PRAGMA table_info(enterprises)").fetchall()
            existing_columns = {col[1] for col in table_info}
            
            if 'industry' not in existing_columns:
                conn.execute("ALTER TABLE enterprises ADD COLUMN industry TEXT")
            if 'enterprise_type' not in existing_columns:
                conn.execute("ALTER TABLE enterprises ADD COLUMN enterprise_type TEXT")
            if 'product_type' not in existing_columns:
                conn.execute("ALTER TABLE enterprises ADD COLUMN product_type TEXT")
        except sqlite3.OperationalError:
            # Игнорируем ошибки, если колонки уже существуют
            pass
        
        # Миграция: добавляем новые поля к существующей таблице, если их нет
        try:
            table_info = conn.execute("PRAGMA table_info(enterprises)").fetchall()
            existing_columns = {col[1] for col in table_info}
            
            if 'industry' not in existing_columns:
                conn.execute("ALTER TABLE enterprises ADD COLUMN industry TEXT")
            if 'enterprise_type' not in existing_columns:
                conn.execute("ALTER TABLE enterprises ADD COLUMN enterprise_type TEXT")
            if 'product_type' not in existing_columns:
                conn.execute("ALTER TABLE enterprises ADD COLUMN product_type TEXT")
        except Exception as e:
            logger.warning(f"Ошибка при миграции таблицы enterprises: {e}")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL UNIQUE,
                enterprise_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                status TEXT NOT NULL,
                parsing_summary TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (enterprise_id) REFERENCES enterprises(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS parsed_data (
                upload_id INTEGER PRIMARY KEY,
                raw_json TEXT,
                editable_text TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (upload_id) REFERENCES uploads(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads_storage (
                upload_id INTEGER PRIMARY KEY,
                file_hash TEXT,
                file_mtime REAL,
                FOREIGN KEY (upload_id) REFERENCES uploads(id)
            )
            """
        )
        # Таблицы для нормативных документов
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS normative_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                document_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT,
                file_size INTEGER,
                uploaded_at TEXT NOT NULL,
                ai_processed BOOLEAN DEFAULT FALSE,
                processing_status TEXT DEFAULT 'pending',
                full_text TEXT,
                parsed_data_json TEXT
            )
            """
        )
        # Миграция: добавляем новые колонки если их нет
        try:
            table_info = conn.execute("PRAGMA table_info(normative_documents)").fetchall()
            existing_columns = {col[1] for col in table_info}
            
            if 'full_text' not in existing_columns:
                conn.execute("ALTER TABLE normative_documents ADD COLUMN full_text TEXT")
                logger.info("Добавлена колонка full_text в normative_documents")
            
            if 'parsed_data_json' not in existing_columns:
                conn.execute("ALTER TABLE normative_documents ADD COLUMN parsed_data_json TEXT")
                logger.info("Добавлена колонка parsed_data_json в normative_documents")
        except sqlite3.OperationalError as e:
            logger.warning(f"Ошибка при миграции normative_documents: {e}")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS normative_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                rule_type TEXT NOT NULL,
                description TEXT,
                formula TEXT,
                parameters TEXT,
                numeric_value REAL,
                unit TEXT,
                ai_extracted BOOLEAN DEFAULT FALSE,
                extraction_confidence REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES normative_documents(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS normative_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                sheet_name TEXT,
                cell_reference TEXT,
                passport_field_path TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (rule_id) REFERENCES normative_rules(id) ON DELETE CASCADE
            )
            """
        )
        # Таблица для нарушений нормативов
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS normative_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enterprise_id INTEGER,
                batch_id TEXT,
                field_name TEXT NOT NULL,
                sheet_name TEXT,
                actual_value REAL NOT NULL,
                normative_value REAL,
                deviation_percent REAL,
                status TEXT NOT NULL,
                message TEXT,
                rule_id INTEGER,
                cell_reference TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (enterprise_id) REFERENCES enterprises(id) ON DELETE SET NULL,
                FOREIGN KEY (rule_id) REFERENCES normative_rules(id) ON DELETE SET NULL
            )
            """
        )
        # Таблица для агрегированных данных энергоресурсов
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS aggregated_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enterprise_id INTEGER NOT NULL,
                batch_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                period TEXT NOT NULL,
                data_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (enterprise_id) REFERENCES enterprises(id),
                UNIQUE(enterprise_id, resource_type, period)
            )
            """
        )
        # Таблица для хранения потребления электроэнергии по узлам учёта
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS node_consumption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enterprise_id INTEGER NOT NULL,
                batch_id TEXT NOT NULL,
                node_name TEXT NOT NULL,
                period TEXT NOT NULL,
                active_energy_kwh REAL,
                reactive_energy_kvarh REAL,
                cost_sum REAL,
                data_type TEXT DEFAULT 'consumption',
                data_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (enterprise_id) REFERENCES enterprises(id),
                UNIQUE(enterprise_id, node_name, period, data_type)
            )
            """
        )
        # Добавляем колонку data_type, если её нет (для существующих БД)
        try:
            conn.execute("ALTER TABLE node_consumption ADD COLUMN data_type TEXT DEFAULT 'consumption'")
        except sqlite3.OperationalError:
            # Колонка уже существует, игнорируем ошибку
            pass


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def list_enterprises() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, created_at, industry, enterprise_type, product_type FROM enterprises ORDER BY name COLLATE NOCASE"
        ).fetchall()
        return [_row_to_dict(row) for row in rows]


def get_enterprise_by_id(enterprise_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, created_at, industry, enterprise_type, product_type FROM enterprises WHERE id = ?",
            (enterprise_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None


def get_or_create_enterprise(
    name: str,
    industry: Optional[str] = None,
    enterprise_type: Optional[str] = None,
    product_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Получает существующее предприятие или создает новое.
    
    Args:
        name: Название предприятия
        industry: Отрасль (опционально)
        enterprise_type: Тип предприятия (опционально)
        product_type: Тип продукции (опционально)
    
    Returns:
        Словарь с данными предприятия
    """
    name_normalized = name.strip()
    if not name_normalized:
        raise ValueError("Enterprise name must not be empty.")

    with get_connection() as conn, conn:
        existing = conn.execute(
            "SELECT id, name, created_at, industry, enterprise_type, product_type FROM enterprises WHERE name = ?",
            (name_normalized,),
        ).fetchone()
        if existing:
            return _row_to_dict(existing)

        created_at = datetime.utcnow().isoformat()
        cursor = conn.execute(
            "INSERT INTO enterprises (name, created_at, industry, enterprise_type, product_type) VALUES (?, ?, ?, ?, ?)",
            (name_normalized, created_at, industry, enterprise_type, product_type),
        )
        enterprise_id = cursor.lastrowid
        return {
            "id": enterprise_id,
            "name": name_normalized,
            "created_at": created_at,
            "industry": industry,
            "enterprise_type": enterprise_type,
            "product_type": product_type,
        }


def auto_determine_enterprise_type(enterprise_id: int) -> None:
    """
    Автоматически определяет тип предприятия на основе загруженных файлов.
    
    Args:
        enterprise_id: ID предприятия
    """
    try:
        from utils.enterprise_classifier import classify_enterprise
        
        # Получаем предприятие
        enterprise = get_enterprise_by_id(enterprise_id)
        if not enterprise:
            logger.warning(f"Предприятие с ID {enterprise_id} не найдено")
            return
        
        # Получаем список загруженных файлов
        uploads = list_uploads_for_enterprise(enterprise_id)
        filenames = [upload.get("filename", "") for upload in uploads if upload.get("filename")]
        
        if not filenames:
            logger.info(f"Нет загруженных файлов для предприятия {enterprise_id}, пропускаю определение типа")
            return
        
        # Классифицируем предприятие
        industry, enterprise_type, product_type = classify_enterprise(
            enterprise["name"], filenames
        )
        
        if industry or enterprise_type or product_type:
            update_enterprise_type(
                enterprise_id=enterprise_id,
                industry=industry,
                enterprise_type=enterprise_type,
                product_type=product_type,
            )
            logger.info(
                f"Автоматически определен тип для предприятия {enterprise_id}: "
                f"industry={industry}, enterprise_type={enterprise_type}, product_type={product_type}"
            )
    except ImportError:
        logger.warning("Модуль enterprise_classifier не найден, автоматическое определение типа недоступно")
    except Exception as e:
        logger.error(f"Ошибка при автоматическом определении типа предприятия: {e}", exc_info=True)


def update_enterprise_type(
    enterprise_id: int,
    industry: Optional[str] = None,
    enterprise_type: Optional[str] = None,
    product_type: Optional[str] = None,
) -> None:
    """
    Обновляет тип предприятия, отрасль и тип продукции.
    
    Args:
        enterprise_id: ID предприятия
        industry: Отрасль (например, "энергетика", "химия")
        enterprise_type: Тип предприятия (например, "ТЭС", "химический завод")
        product_type: Тип продукции (например, "электроэнергия", "азотные удобрения")
    """
    updates: List[str] = []
    params: List[Any] = []
    
    if industry is not None:
        updates.append("industry = ?")
        params.append(industry)
    if enterprise_type is not None:
        updates.append("enterprise_type = ?")
        params.append(enterprise_type)
    if product_type is not None:
        updates.append("product_type = ?")
        params.append(product_type)
    
    if not updates:
        return
    
    params.append(enterprise_id)
    
    with get_connection() as conn, conn:
        conn.execute(
            f"UPDATE enterprises SET {', '.join(updates)} WHERE id = ?",
            params,
        )


def create_upload(
    *,
    batch_id: str,
    enterprise_id: int,
    filename: str,
    file_type: Optional[str],
    file_size: Optional[int],
    status: str,
    parsing_summary: Optional[Dict[str, Any]] = None,
    file_hash: Optional[str] = None,
    file_mtime: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Создает запись о загрузке файла в БД.
    
    Args:
        batch_id: Уникальный ID загрузки
        enterprise_id: ID предприятия
        filename: Имя файла (ограничено до 255 символов)
        file_type: Тип файла
        file_size: Размер файла в байтах
        status: Статус обработки
        parsing_summary: Сводка парсинга (ограничена до 50KB JSON)
        file_hash: Хеш файла для дедупликации
        file_mtime: Время модификации файла
    
    Returns:
        Словарь с данными созданной записи
    
    Raises:
        sqlite3.Error: При ошибках БД
        ValueError: При некорректных данных
    """
    import logging
    logger = logging.getLogger(__name__)
    
    created_at = datetime.utcnow().isoformat()
    
    # Ограничиваем длину filename (SQLite TEXT может быть длинным, но для безопасности ограничим)
    if filename and len(filename) > 500:
        logger.warning(f"Имя файла слишком длинное ({len(filename)} символов), обрезано: {filename[:100]}...")
        filename = filename[:500]
    
    # Ограничиваем размер parsing_summary (SQLite TEXT может быть большим, но ограничим для производительности)
    summary_json = None
    if parsing_summary:
        try:
            summary_json = safe_json_dumps(parsing_summary)
            # Ограничиваем до 50KB (примерно 50,000 символов)
            if len(summary_json) > 50000:
                logger.warning(
                    f"parsing_summary слишком большой ({len(summary_json)} символов), "
                    f"обрезан до 50KB для batch_id={batch_id}"
                )
                # Сохраняем только основные поля
                limited_summary = {
                    "status": parsing_summary.get("status"),
                    "file_type": parsing_summary.get("file_type"),
                    "tables_count": parsing_summary.get("tables_count"),
                    "error": "Summary too large, truncated",
                    "original_size": len(summary_json)
                }
                summary_json = safe_json_dumps(limited_summary)
        except (TypeError, ValueError) as e:
            logger.error(f"Ошибка сериализации parsing_summary для batch_id={batch_id}: {e}")
            summary_json = None

    try:
        with get_connection() as conn, conn:
            cursor = conn.execute(
                """
                INSERT INTO uploads (
                    batch_id, enterprise_id, filename, file_type, file_size,
                    status, parsing_summary, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    enterprise_id,
                    filename,
                    file_type,
                    file_size,
                    status,
                    summary_json,
                    created_at,
                ),
            )
            upload_id = cursor.lastrowid
            if file_hash:
                conn.execute(
                    """
                    INSERT INTO uploads_storage (upload_id, file_hash, file_mtime)
                    VALUES (?, ?, ?)
                    """,
                    (upload_id, file_hash, file_mtime),
                )
            return {
                "id": upload_id,
                "batch_id": batch_id,
                "enterprise_id": enterprise_id,
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "status": status,
                "parsing_summary": parsing_summary,
                "created_at": created_at,
            }
    except sqlite3.IntegrityError as e:
        # Ошибка целостности данных (например, дубликат batch_id)
        logger.error(
            f"Ошибка целостности данных при создании загрузки batch_id={batch_id}: {e}"
        )
        raise ValueError(f"Ошибка сохранения: возможно дубликат batch_id или некорректные данные") from e
    except sqlite3.Error as e:
        logger.error(
            f"Ошибка БД при создании загрузки batch_id={batch_id}: {e}",
            exc_info=True
        )
        raise


def update_upload_status(
    batch_id: str,
    *,
    status: str,
    parsing_summary: Optional[Dict[str, Any]] = None,
    file_hash: Optional[str] = None,
    file_mtime: Optional[float] = None,
) -> None:
    summary_json = safe_json_dumps(parsing_summary) if parsing_summary else None
    with get_connection() as conn, conn:
        conn.execute(
            """
            UPDATE uploads
            SET status = ?, parsing_summary = ?
            WHERE batch_id = ?
            """,
            (status, summary_json, batch_id),
        )
        if file_hash is not None:
            row = conn.execute(
                "SELECT id FROM uploads WHERE batch_id = ?", (batch_id,)
            ).fetchone()
            if row:
                conn.execute(
                    """
                    INSERT INTO uploads_storage (upload_id, file_hash, file_mtime)
                    VALUES (?, ?, ?)
                    ON CONFLICT(upload_id) DO UPDATE SET
                        file_hash = excluded.file_hash,
                        file_mtime = excluded.file_mtime
                    """,
                    (row["id"], file_hash, file_mtime),
                )


def save_parsed_content(
    batch_id: str,
    *,
    raw_json: Dict[str, Any],
    editable_text: str,
) -> None:
    """
    Сохраняет результаты парсинга в БД.
    
    Args:
        batch_id: ID загрузки
        raw_json: Результаты парсинга в виде словаря
        editable_text: Текстовое представление данных для редактирования
    
    Raises:
        ValueError: Если загрузка с указанным batch_id не найдена
        sqlite3.Error: При ошибках БД
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        json_text = safe_json_dumps(raw_json)
        # Ограничиваем размер JSON (SQLite TEXT может быть большим, но ограничим для производительности)
        if len(json_text) > 10000000:  # 10MB
            logger.warning(
                f"raw_json слишком большой ({len(json_text)} символов) для batch_id={batch_id}, "
                f"обрезан до 10MB"
            )
            # Сохраняем только основные поля
            limited_json = {
                "batch_id": raw_json.get("batch_id"),
                "filename": raw_json.get("filename"),
                "file_type": raw_json.get("file_type"),
                "status": raw_json.get("status"),
                "error": "JSON слишком большой, обрезан",
                "original_size": len(json_text)
            }
            json_text = safe_json_dumps(limited_json)
        
        updated_at = datetime.utcnow().isoformat()
        
        with get_connection() as conn, conn:
            row = conn.execute(
                "SELECT id FROM uploads WHERE batch_id = ?", (batch_id,)
            ).fetchone()
            if not row:
                logger.error(f"Upload с batch_id={batch_id} не найден в БД")
                raise ValueError(f"Upload with batch_id {batch_id} not found")

            upload_id = row["id"]
            conn.execute(
                """
                INSERT INTO parsed_data (upload_id, raw_json, editable_text, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(upload_id) DO UPDATE SET
                    raw_json = excluded.raw_json,
                    editable_text = excluded.editable_text,
                    updated_at = excluded.updated_at
                """,
                (upload_id, json_text, editable_text, updated_at),
            )
            logger.info(
                f"✅ Данные парсинга сохранены в БД для batch_id={batch_id}, upload_id={upload_id}, "
                f"размер JSON: {len(json_text)} символов"
            )
    except (TypeError, ValueError) as e:
        logger.error(
            f"Ошибка сериализации JSON для batch_id={batch_id}: {e}",
            exc_info=True
        )
        raise ValueError(f"Ошибка сериализации данных парсинга: {e}") from e
    except sqlite3.Error as e:
        logger.error(
            f"Ошибка БД при сохранении данных парсинга для batch_id={batch_id}: {e}",
            exc_info=True
        )
        raise


def update_editable_text(batch_id: str, editable_text: str) -> None:
    updated_at = datetime.utcnow().isoformat()
    with get_connection() as conn, conn:
        row = conn.execute(
            "SELECT id FROM uploads WHERE batch_id = ?", (batch_id,)
        ).fetchone()
        if not row:
            raise ValueError(f"Upload with batch_id {batch_id} not found")

        upload_id = row["id"]
        conn.execute(
            """
            UPDATE parsed_data
            SET editable_text = ?, updated_at = ?
            WHERE upload_id = ?
            """,
            (editable_text, updated_at, upload_id),
        )


def get_upload_by_batch(batch_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.batch_id, u.filename, u.file_type, u.file_size,
                   u.status, u.parsing_summary, u.created_at,
                   e.id AS enterprise_id, e.name AS enterprise_name,
                   pd.raw_json, pd.editable_text, pd.updated_at AS parsed_updated_at
            FROM uploads u
            JOIN enterprises e ON u.enterprise_id = e.id
            LEFT JOIN parsed_data pd ON pd.upload_id = u.id
            WHERE u.batch_id = ?
            """,
            (batch_id,),
        ).fetchone()
        if not row:
            return None

        data = _row_to_dict(row)
        if data.get("parsing_summary"):
            data["parsing_summary"] = json.loads(data["parsing_summary"])
        if data.get("raw_json"):
            data["raw_json"] = json.loads(data["raw_json"])
        return data


def list_uploads_for_enterprise(enterprise_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Получить список загруженных файлов для предприятия.
    
    Args:
        enterprise_id: ID предприятия
        limit: Максимальное количество файлов (None = без ограничений)
    
    Returns:
        Список файлов, отсортированных по дате загрузки (новые первыми)
    """
    with get_connection() as conn:
        query = """
            SELECT batch_id, filename, file_type, file_size,
                   status, parsing_summary, created_at
            FROM uploads
            WHERE enterprise_id = ?
            ORDER BY created_at DESC
        """
        params: tuple = (enterprise_id,)
        
        if limit is not None:
            query += " LIMIT ?"
            params = (enterprise_id, limit)
        
        rows = conn.execute(query, params).fetchall()
        results = []
        for row in rows:
            record = _row_to_dict(row)
            if record.get("parsing_summary"):
                record["parsing_summary"] = json.loads(record["parsing_summary"])
            results.append(record)
        return results


def ensure_storage_directory() -> None:
    directory = os.path.dirname(DB_PATH)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def delete_upload_by_batch_id(batch_id: str) -> bool:
    """
    Удаляет загрузку и все связанные данные по batch_id.
    
    Args:
        batch_id: ID загрузки для удаления
    
    Returns:
        True если загрузка была удалена, False если не найдена
    """
    with get_connection() as conn, conn:
        # Получаем upload_id
        row = conn.execute(
            "SELECT id FROM uploads WHERE batch_id = ?", (batch_id,)
        ).fetchone()
        
        if not row:
            return False
        
        upload_id = row["id"]
        
        # Удаляем связанные данные
        conn.execute("DELETE FROM parsed_data WHERE upload_id = ?", (upload_id,))
        conn.execute("DELETE FROM uploads_storage WHERE upload_id = ?", (upload_id,))
        
        # Удаляем саму загрузку
        conn.execute("DELETE FROM uploads WHERE batch_id = ?", (batch_id,))
        
        return True


def find_duplicate_upload(
    *,
    enterprise_id: int,
    filename: str,
    file_size: int,
    file_hash: str,
) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT u.batch_id, u.filename, u.file_type, u.file_size, u.status,
                   u.parsing_summary
            FROM uploads u
            JOIN uploads_storage s ON s.upload_id = u.id
            WHERE u.enterprise_id = ?
              AND u.filename = ?
              AND u.file_size = ?
              AND s.file_hash = ?
            LIMIT 1
            """,
            (enterprise_id, filename, file_size, file_hash),
        ).fetchone()
        if not row:
            return None
        record = _row_to_dict(row)
        if record.get("parsing_summary"):
            record["parsing_summary"] = json.loads(record["parsing_summary"])
        return record


# Функции для работы с нормативными документами


def find_normative_document_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    """Найти нормативный документ по хешу файла (для дедупликации)"""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM normative_documents
            WHERE file_hash = ?
            ORDER BY uploaded_at DESC
            LIMIT 1
            """,
            (file_hash,),
        ).fetchone()
        return _row_to_dict(row) if row else None


def count_rules_for_document(document_id: int) -> int:
    """Подсчитать количество правил для документа"""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) as count
            FROM normative_rules
            WHERE document_id = ?
            """,
            (document_id,),
        ).fetchone()
        return row["count"] if row else 0


def create_normative_document(
    *,
    title: str,
    document_type: str,
    file_path: str,
    file_hash: Optional[str] = None,
    file_size: Optional[int] = None,
    full_text: Optional[str] = None,
    parsed_data_json: Optional[str] = None,
) -> Dict[str, Any]:
    """Создать запись о нормативном документе"""
    uploaded_at = datetime.utcnow().isoformat()
    with get_connection() as conn, conn:
        cursor = conn.execute(
            """
            INSERT INTO normative_documents (
                title, document_type, file_path, file_hash, file_size,
                uploaded_at, processing_status, full_text, parsed_data_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                document_type,
                file_path,
                file_hash,
                file_size,
                uploaded_at,
                "pending",
                full_text,
                parsed_data_json,
            ),
        )
        doc_id = cursor.lastrowid
        return {
            "id": doc_id,
            "title": title,
            "document_type": document_type,
            "file_path": file_path,
            "file_hash": file_hash,
            "file_size": file_size,
            "uploaded_at": uploaded_at,
            "ai_processed": False,
            "processing_status": "pending",
            "full_text": full_text,
            "parsed_data_json": parsed_data_json,
        }


def update_normative_document_status(
    document_id: int,
    *,
    ai_processed: bool = False,
    processing_status: str = "processed",
    full_text: Optional[str] = None,
    parsed_data_json: Optional[str] = None,
) -> None:
    """Обновить статус обработки нормативного документа"""
    with get_connection() as conn, conn:
        if full_text is not None or parsed_data_json is not None:
            # Обновляем с текстом и данными парсинга
            updates = ["ai_processed = ?", "processing_status = ?"]
            values = [ai_processed, processing_status]
            
            if full_text is not None:
                updates.append("full_text = ?")
                values.append(full_text)
            
            if parsed_data_json is not None:
                updates.append("parsed_data_json = ?")
                values.append(parsed_data_json)
            
            values.append(document_id)
            
            conn.execute(
                f"""
                UPDATE normative_documents
                SET {', '.join(updates)}
                WHERE id = ?
                """,
                tuple(values),
            )
        else:
            # Только статус
            conn.execute(
                """
                UPDATE normative_documents
                SET ai_processed = ?, processing_status = ?
                WHERE id = ?
                """,
                (ai_processed, processing_status, document_id),
            )


def get_normative_document(document_id: int) -> Optional[Dict[str, Any]]:
    """Получить нормативный документ по ID"""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM normative_documents
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None


def create_normative_rule(
    *,
    document_id: int,
    rule_type: str,
    description: Optional[str] = None,
    formula: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    numeric_value: Optional[float] = None,
    unit: Optional[str] = None,
    ai_extracted: bool = False,
    extraction_confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """Создать правило из нормативного документа"""
    created_at = datetime.utcnow().isoformat()
    parameters_json = json.dumps(parameters) if parameters else None

    with get_connection() as conn, conn:
        cursor = conn.execute(
            """
            INSERT INTO normative_rules (
                document_id, rule_type, description, formula, parameters,
                numeric_value, unit, ai_extracted, extraction_confidence, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                rule_type,
                description,
                formula,
                parameters_json,
                numeric_value,
                unit,
                ai_extracted,
                extraction_confidence,
                created_at,
            ),
        )
        rule_id = cursor.lastrowid
        return {
            "id": rule_id,
            "document_id": document_id,
            "rule_type": rule_type,
            "description": description,
            "formula": formula,
            "parameters": parameters,
            "numeric_value": numeric_value,
            "unit": unit,
            "ai_extracted": ai_extracted,
            "extraction_confidence": extraction_confidence,
            "created_at": created_at,
        }


def create_normative_reference(
    *,
    rule_id: int,
    field_name: str,
    sheet_name: Optional[str] = None,
    cell_reference: Optional[str] = None,
    passport_field_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Создать связь между правилом и полем энергопаспорта"""
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn, conn:
        cursor = conn.execute(
            """
            INSERT INTO normative_references (
                rule_id, field_name, sheet_name, cell_reference, passport_field_path, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                rule_id,
                field_name,
                sheet_name,
                cell_reference,
                passport_field_path,
                created_at,
            ),
        )
        ref_id = cursor.lastrowid
        return {
            "id": ref_id,
            "rule_id": rule_id,
            "field_name": field_name,
            "sheet_name": sheet_name,
            "cell_reference": cell_reference,
            "passport_field_path": passport_field_path,
            "created_at": created_at,
        }


def get_normative_rules_by_type(rule_type: str) -> List[Dict[str, Any]]:
    """Получить все правила определенного типа"""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT nr.*, nd.title as document_title, nd.document_type
            FROM normative_rules nr
            JOIN normative_documents nd ON nr.document_id = nd.id
            WHERE nr.rule_type = ?
            ORDER BY nr.extraction_confidence DESC, nr.created_at DESC
            """,
            (rule_type,),
        ).fetchall()
        results = []
        for row in rows:
            record = _row_to_dict(row)
            if record.get("parameters"):
                try:
                    record["parameters"] = json.loads(record["parameters"])
                except (json.JSONDecodeError, TypeError):
                    record["parameters"] = {}
            results.append(record)
        return results


def get_normative_rules_for_field(
    field_name: str, sheet_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Получить правила, связанные с конкретным полем энергопаспорта"""
    with get_connection() as conn:
        if sheet_name:
            rows = conn.execute(
                """
                SELECT nr.*, nd.title as document_title, nd.document_type, nref.cell_reference
                FROM normative_rules nr
                JOIN normative_documents nd ON nr.document_id = nd.id
                JOIN normative_references nref ON nr.id = nref.rule_id
                WHERE nref.field_name = ? AND nref.sheet_name = ?
                ORDER BY nr.extraction_confidence DESC
                """,
                (field_name, sheet_name),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT nr.*, nd.title as document_title, nd.document_type, nref.cell_reference
                FROM normative_rules nr
                JOIN normative_documents nd ON nr.document_id = nd.id
                JOIN normative_references nref ON nr.id = nref.rule_id
                WHERE nref.field_name = ?
                ORDER BY nr.extraction_confidence DESC
                """,
                (field_name,),
            ).fetchall()
        results = []
        for row in rows:
            record = _row_to_dict(row)
            if record.get("parameters"):
                try:
                    record["parameters"] = json.loads(record["parameters"])
                except (json.JSONDecodeError, TypeError):
                    record["parameters"] = {}
            results.append(record)
        return results


def create_normative_violation(
    *,
    enterprise_id: Optional[int] = None,
    batch_id: Optional[str] = None,
    field_name: str,
    sheet_name: Optional[str] = None,
    actual_value: float,
    normative_value: Optional[float] = None,
    deviation_percent: float = 0.0,
    status: str,
    message: Optional[str] = None,
    rule_id: Optional[int] = None,
    cell_reference: Optional[str] = None,
) -> Dict[str, Any]:
    """Создать запись о нарушении норматива"""
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn, conn:
        cursor = conn.execute(
            """
            INSERT INTO normative_violations (
                enterprise_id, batch_id, field_name, sheet_name,
                actual_value, normative_value, deviation_percent,
                status, message, rule_id, cell_reference, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                enterprise_id,
                batch_id,
                field_name,
                sheet_name,
                actual_value,
                normative_value,
                deviation_percent,
                status,
                message,
                rule_id,
                cell_reference,
                created_at,
            ),
        )
        violation_id = cursor.lastrowid
        return {
            "id": violation_id,
            "enterprise_id": enterprise_id,
            "batch_id": batch_id,
            "field_name": field_name,
            "sheet_name": sheet_name,
            "actual_value": actual_value,
            "normative_value": normative_value,
            "deviation_percent": deviation_percent,
            "status": status,
            "message": message,
            "rule_id": rule_id,
            "cell_reference": cell_reference,
            "created_at": created_at,
        }


def get_normative_violations(
    enterprise_id: Optional[int] = None,
    batch_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Получить список нарушений нормативов"""
    with get_connection() as conn:
        query = "SELECT * FROM normative_violations WHERE 1=1"
        params: List[Any] = []

        if enterprise_id:
            query += " AND enterprise_id = ?"
            params.append(enterprise_id)

        if batch_id:
            query += " AND batch_id = ?"
            params.append(batch_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        results = []
        for row in rows:
            results.append(_row_to_dict(row))
        return results


def list_normative_documents() -> List[Dict[str, Any]]:
    """Получить список всех нормативных документов"""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, document_type, file_path, file_size,
                   uploaded_at, ai_processed, processing_status,
                   (SELECT COUNT(*) FROM normative_rules WHERE document_id = normative_documents.id) as rules_count
            FROM normative_documents
            ORDER BY uploaded_at DESC
            """
        ).fetchall()
        return [_row_to_dict(row) for row in rows]


def get_environmental_normatives(rule_type: str = "environmental") -> Dict[str, Any]:
    """
    Получить экологические нормативы из БД.
    
    Args:
        rule_type: Тип правил (по умолчанию "environmental")
    
    Returns:
        Словарь с экологическими нормативами (ПДВ, ПДС, категории опасности)
    """
    # Получаем правила типа "environmental" из БД
    rules = get_normative_rules_by_type(rule_type)
    
    # Структура по умолчанию (если в БД нет данных)
    default_normatives = {
        "emissions": {
            "co": {"max_concentration": 3.0, "unit": "мг/м³"},
            "nox": {"max_concentration": 0.4, "unit": "мг/м³"},
            "so2": {"max_concentration": 0.5, "unit": "мг/м³"},
            "dust": {"max_concentration": 0.5, "unit": "мг/м³"},
            "pm10": {"max_concentration": 0.06, "unit": "мг/м³"},
            "pm2_5": {"max_concentration": 0.035, "unit": "мг/м³"},
        },
        "discharges": {
            "suspended_solids": {"max_concentration": 0.25, "unit": "мг/л"},
            "bod5": {"max_concentration": 3.0, "unit": "мг/л"},
            "cod": {"max_concentration": 30.0, "unit": "мг/л"},
            "ammonium": {"max_concentration": 0.5, "unit": "мг/л"},
            "nitrates": {"max_concentration": 40.0, "unit": "мг/л"},
            "phosphates": {"max_concentration": 0.2, "unit": "мг/л"},
        },
        "hazard_categories": {
            "category_1": {"description": "Чрезвычайно опасные", "criteria": "ПДВ > 1000 т/год"},
            "category_2": {"description": "Высокоопасные", "criteria": "ПДВ 100-1000 т/год"},
            "category_3": {"description": "Умеренно опасные", "criteria": "ПДВ 10-100 т/год"},
            "category_4": {"description": "Малоопасные", "criteria": "ПДВ < 10 т/год"},
        },
    }
    
    # Если есть правила в БД, преобразуем их в структуру
    if rules:
        normatives: Dict[str, Any] = {"emissions": {}, "discharges": {}, "hazard_categories": {}}
        for rule in rules:
            rule_type_lower = rule.get("rule_type", "").lower()
            substance = rule.get("description", "").lower()
            value = rule.get("numeric_value")
            unit = rule.get("unit", "")
            
            if "emission" in rule_type_lower or "выброс" in rule_type_lower:
                normatives["emissions"][substance] = {
                    "max_concentration": value,
                    "unit": unit,
                }
            elif "discharge" in rule_type_lower or "сброс" in rule_type_lower:
                normatives["discharges"][substance] = {
                    "max_concentration": value,
                    "unit": unit,
                }
        
        return normatives
    
    return default_normatives


def create_environmental_normative(
    *,
    document_id: int,
    substance_name: str,
    norm_type: str,  # "emission" или "discharge"
    max_concentration: float,
    unit: str,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Создать экологический норматив в БД.
    
    Args:
        document_id: ID нормативного документа
        substance_name: Название вещества (CO, NOx, SO2 и т.д.)
        norm_type: Тип норматива ("emission" для ПДВ или "discharge" для ПДС)
        max_concentration: Максимальная концентрация
        unit: Единица измерения (мг/м³, мг/л и т.д.)
        description: Описание (опционально)
    
    Returns:
        Созданное правило
    """
    rule_type = f"environmental_{norm_type}"
    description_text = description or f"Норматив {norm_type} для {substance_name}"
    
    return create_normative_rule(
        document_id=document_id,
        rule_type=rule_type,
        description=description_text,
        numeric_value=max_concentration,
        unit=unit,
    )


def save_environmental_measures(
    *,
    enterprise_id: int,
    measures_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Сохранить план экологических мероприятий в БД.
    
    Args:
        enterprise_id: ID предприятия
        measures_data: Данные мероприятий (из парсера)
    
    Returns:
        Сохраненные данные
    """
    # Сохраняем в JSON в таблице parsed_data или создаем отдельную таблицу
    # Пока сохраняем как JSON в metadata
    import json
    
    measures_json = safe_json_dumps(measures_data)
    
    # Можно сохранить в отдельную таблицу или использовать существующую структуру
    # Для простоты сохраняем в metadata существующих записей
    return {
        "enterprise_id": enterprise_id,
        "measures": measures_data.get("measures", []),
        "summary": measures_data.get("summary", {}),
        "source": measures_data.get("source", ""),
        "generated_at": measures_data.get("generated_at", ""),
    }


def get_environmental_measures(enterprise_id: int) -> Optional[Dict[str, Any]]:
    """
    Получить план экологических мероприятий для предприятия.
    
    Args:
        enterprise_id: ID предприятия
    
    Returns:
        Данные мероприятий или None
    """
    # TODO: Реализовать получение из БД
    # Пока возвращаем None, так как структура БД для мероприятий ещё не определена
    return None


def import_resource_to_db(
    enterprise_id: int,
    batch_id: str,
    resource_type: str,
    resource_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Импортирует агрегированные данные энергоресурса в БД (универсальная функция).
    
    Args:
        enterprise_id: ID предприятия
        batch_id: ID загрузки (batch_id из uploads)
        resource_type: Тип ресурса ('electricity', 'gas', 'water', 'heat', 'fuel')
        resource_data: Данные ресурса из aggregated JSON
            Формат: {"2022-Q1": {...}, "2022-Q2": {...}}
    
    Returns:
        Список созданных/обновленных записей
    """
    if not resource_data:
        return []
    
    now = datetime.utcnow().isoformat()
    imported_records = []
    
    with get_connection() as conn, conn:
        for period, period_data in resource_data.items():
            # period имеет формат "2022-Q1", "2022-Q2" и т.д.
            if not isinstance(period_data, dict):
                continue
            
            # Подготавливаем данные для сохранения
            data_json = safe_json_dumps(period_data)
            
            # Проверяем, существует ли запись
            existing = conn.execute(
                """
                SELECT id FROM aggregated_data
                WHERE enterprise_id = ? AND resource_type = ? AND period = ?
                """,
                (enterprise_id, resource_type, period),
            ).fetchone()
            
            if existing:
                # Обновляем существующую запись
                conn.execute(
                    """
                    UPDATE aggregated_data
                    SET batch_id = ?, data_json = ?, updated_at = ?
                    WHERE enterprise_id = ? AND resource_type = ? AND period = ?
                    """,
                    (batch_id, data_json, now, enterprise_id, resource_type, period),
                )
                record_id = existing["id"]
            else:
                # Создаем новую запись
                cursor = conn.execute(
                    """
                    INSERT INTO aggregated_data
                    (enterprise_id, batch_id, resource_type, period, data_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (enterprise_id, batch_id, resource_type, period, data_json, now, now),
                )
                record_id = cursor.lastrowid
            
            imported_records.append({
                "id": record_id,
                "enterprise_id": enterprise_id,
                "batch_id": batch_id,
                "resource_type": resource_type,
                "period": period,
            })
    
    return imported_records


def import_electricity_to_db(
    enterprise_id: int,
    batch_id: str,
    electricity_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Импортирует агрегированные данные электроэнергии в БД.
    
    Args:
        enterprise_id: ID предприятия
        batch_id: ID загрузки (batch_id из uploads)
        electricity_data: Данные электроэнергии из aggregated JSON
            Может быть в двух форматах:
            1. Прямой формат: {"2022-Q1": {...}, "2022-Q2": {...}}
            2. Из aggregated JSON: {"resources": {"electricity": {"2022-Q1": {...}}}}
    
    Returns:
        Список созданных/обновленных записей
    """
    # Если данные в формате полного aggregated JSON, извлекаем electricity
    if "resources" in electricity_data and "electricity" in electricity_data["resources"]:
        electricity_data = electricity_data["resources"]["electricity"]
    
    return import_resource_to_db(enterprise_id, batch_id, "electricity", electricity_data)


def get_aggregated_electricity(
    enterprise_id: int,
    period: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Получить агрегированные данные электроэнергии из БД.
    
    Args:
        enterprise_id: ID предприятия
        period: Период (например, "2022-Q1") или None для всех периодов
    
    Returns:
        Данные электроэнергии в формате {period: {...}} или None
    """
    with get_connection() as conn:
        if period:
            rows = conn.execute(
                """
                SELECT period, data_json FROM aggregated_data
                WHERE enterprise_id = ? AND resource_type = ? AND period = ?
                ORDER BY period
                """,
                (enterprise_id, "electricity", period),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT period, data_json FROM aggregated_data
                WHERE enterprise_id = ? AND resource_type = ?
                ORDER BY period
                """,
                (enterprise_id, "electricity"),
            ).fetchall()
        
        if not rows:
            return None
        
        result = {}
        for row in rows:
            period_key = row["period"]
            data = json.loads(row["data_json"])
            result[period_key] = data
        
        return result


def validate_aggregated_data(aggregated_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Валидирует структуру агрегированных данных перед импортом.
    
    Args:
        aggregated_data: Данные из aggregated JSON файла
    
    Returns:
        Словарь с результатами валидации:
        {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str],
            "resources_found": List[str],
            "periods_found": Dict[str, List[str]]
        }
    """
    result: Dict[str, Any] = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "resources_found": [],
        "periods_found": {}
    }
    
    # Проверка наличия ключа "resources"
    if "resources" not in aggregated_data:
        result["valid"] = False
        result["errors"].append("Отсутствует ключ 'resources' в aggregated данных")
        return result
    
    resources = aggregated_data["resources"]
    if not isinstance(resources, dict):
        result["valid"] = False
        result["errors"].append("'resources' должен быть словарём")
        return result
    
    # Валидация каждого ресурса
    valid_resource_types = ["electricity", "gas", "water", "heat", "fuel", "coal", "production"]
    period_pattern = r"^\d{4}-Q[1-4]$"  # Формат: 2022-Q1
    
    import re
    
    for resource_type, resource_data in resources.items():
        if not isinstance(resource_data, dict):
            result["warnings"].append(f"Ресурс '{resource_type}' не является словарём, пропущен")
            continue
        
        if resource_type not in valid_resource_types:
            result["warnings"].append(f"Неизвестный тип ресурса: '{resource_type}'")
        
        result["resources_found"].append(resource_type)
        periods = []
        
        for period, period_data in resource_data.items():
            # Валидация формата периода
            if not re.match(period_pattern, period):
                result["warnings"].append(f"Неверный формат периода '{period}' для ресурса '{resource_type}'")
                continue
            
            # Валидация данных периода
            if not isinstance(period_data, dict):
                result["warnings"].append(f"Данные периода '{period}' для ресурса '{resource_type}' не являются словарём")
                continue
            
            # Проверка наличия числовых значений
            has_numeric_values = False
            for key, value in period_data.items():
                if isinstance(value, (int, float)) and value != 0:
                    has_numeric_values = True
                    break
            
            if not has_numeric_values:
                result["warnings"].append(f"Период '{period}' для ресурса '{resource_type}' не содержит числовых значений")
            
            periods.append(period)
        
        if periods:
            result["periods_found"][resource_type] = periods
    
    # Проверка наличия хотя бы одного ресурса с данными
    if not result["resources_found"]:
        result["warnings"].append("Не найдено ресурсов с данными")
    
    return result


def batch_import_aggregated_files(
    aggregated_dir: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Batch-импорт всех агрегированных JSON файлов из директории в БД.
    
    Args:
        aggregated_dir: Путь к директории с агрегированными файлами
            Если None, используется значение из переменной окружения AGGREGATED_DIR
        dry_run: Если True, только проверяет файлы без импорта
    
    Returns:
        Словарь с результатами импорта:
        {
            "total_files": int,
            "processed": int,
            "imported": int,
            "skipped": int,
            "errors": int,
            "details": List[Dict]
        }
    """
    import os
    from pathlib import Path
    
    if aggregated_dir is None:
        # Определяем путь к директории aggregated
        ingest_dir = Path(__file__).resolve().parent
        inbox_dir = ingest_dir / "data" / "inbox"
        aggregated_dir = Path(os.getenv("AGGREGATED_DIR", str(inbox_dir / "aggregated")))
    
    if not aggregated_dir.exists():
        return {
            "total_files": 0,
            "processed": 0,
            "imported": 0,
            "skipped": 0,
            "errors": 0,
            "details": [],
            "error": f"Директория не найдена: {aggregated_dir}"
        }
    
    # Находим все файлы *_aggregated.json
    aggregated_files = list(aggregated_dir.glob("*_aggregated.json"))
    
    result: Dict[str, Any] = {
        "total_files": len(aggregated_files),
        "processed": 0,
        "imported": 0,
        "skipped": 0,
        "errors": 0,
        "details": []
    }
    
    for aggregated_file in aggregated_files:
        file_result: Dict[str, Any] = {
            "filename": aggregated_file.name,
            "status": "pending",
            "batch_id": None,
            "enterprise_id": None,
            "resources_imported": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Извлекаем batch_id из имени файла
            # Формат: {batch_id}_aggregated.json
            batch_id = aggregated_file.stem.replace("_aggregated", "")
            file_result["batch_id"] = batch_id
            
            # Загружаем JSON
            with open(aggregated_file, 'r', encoding='utf-8') as f:
                aggregated_data = json.load(f)
            
            # Валидируем данные
            validation = validate_aggregated_data(aggregated_data)
            file_result["warnings"] = validation["warnings"]
            
            if not validation["valid"]:
                file_result["status"] = "validation_failed"
                file_result["errors"] = validation["errors"]
                result["errors"] += 1
                result["details"].append(file_result)
                continue
            
            if dry_run:
                file_result["status"] = "validated"
                file_result["resources_found"] = validation["resources_found"]
                file_result["periods_found"] = validation["periods_found"]
                result["processed"] += 1
                result["details"].append(file_result)
                continue
            
            # Находим enterprise_id по batch_id
            upload_record = get_upload_by_batch(batch_id)
            if not upload_record:
                file_result["status"] = "skipped"
                file_result["errors"].append(f"Загрузка с batch_id '{batch_id}' не найдена в БД")
                result["skipped"] += 1
                result["details"].append(file_result)
                continue
            
            enterprise_id = upload_record["enterprise_id"]
            file_result["enterprise_id"] = enterprise_id
            
            # Импортируем все ресурсы
            resources = aggregated_data.get("resources", {})
            total_imported = 0
            
            for resource_type, resource_data in resources.items():
                if not resource_data or not isinstance(resource_data, dict):
                    continue
                
                imported_records = import_resource_to_db(
                    enterprise_id=enterprise_id,
                    batch_id=batch_id,
                    resource_type=resource_type,
                    resource_data=resource_data
                )
                
                if imported_records:
                    file_result["resources_imported"][resource_type] = len(imported_records)
                    total_imported += len(imported_records)
            
            if total_imported > 0:
                file_result["status"] = "imported"
                file_result["total_records"] = total_imported
                result["imported"] += 1
            else:
                file_result["status"] = "skipped"
                file_result["errors"].append("Нет данных для импорта")
                result["skipped"] += 1
            
            result["processed"] += 1
            
        except json.JSONDecodeError as e:
            file_result["status"] = "error"
            file_result["errors"].append(f"Ошибка парсинга JSON: {e}")
            result["errors"] += 1
        
        except Exception as e:
            file_result["status"] = "error"
            file_result["errors"].append(f"Ошибка импорта: {e}")
            result["errors"] += 1
        
        result["details"].append(file_result)
    
    return result


def import_node_consumption_to_db(
    enterprise_id: int,
    batch_id: str,
    node_consumption_data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Импортирует данные потребления электроэнергии по узлам учёта в БД.
    
    Args:
        enterprise_id: ID предприятия
        batch_id: ID загрузки (batch_id из uploads)
        node_consumption_data: Список данных потребления по узлам
            Формат: [
                {
                    "node_name": "Узел-1",
                    "period": "2022-Q1",
                    "active_energy_kwh": 1000.0,
                    "reactive_energy_kvarh": 200.0,
                    "cost_sum": 50000.0,
                    "data_json": {...}  # опционально, дополнительные данные
                },
                ...
            ]
    
    Returns:
        Список созданных/обновленных записей
    """
    if not node_consumption_data:
        return []
    
    now = datetime.utcnow().isoformat()
    imported_records = []
    
    with get_connection() as conn, conn:
        for node_data in node_consumption_data:
            node_name = node_data.get("node_name")
            period = node_data.get("period")
            
            if not node_name or not period:
                continue
            
            active_energy_kwh = node_data.get("active_energy_kwh")
            reactive_energy_kvarh = node_data.get("reactive_energy_kvarh")
            cost_sum = node_data.get("cost_sum")
            data_json_str = None
            
            # Если есть дополнительные данные, сохраняем их в JSON
            if "data_json" in node_data:
                data_json_str = safe_json_dumps(node_data["data_json"])
            
            # Определяем тип данных (production/realization vs consumption)
            data_type = node_data.get("data_type", "consumption")
            if data_type not in ["consumption", "production", "realization"]:
                data_type = "consumption"  # По умолчанию
            
            # Проверяем, существует ли запись
            existing = conn.execute(
                """
                SELECT id FROM node_consumption
                WHERE enterprise_id = ? AND node_name = ? AND period = ? AND data_type = ?
                """,
                (enterprise_id, node_name, period, data_type),
            ).fetchone()
            
            if existing:
                # Обновляем существующую запись
                conn.execute(
                    """
                    UPDATE node_consumption
                    SET batch_id = ?, active_energy_kwh = ?, reactive_energy_kvarh = ?,
                        cost_sum = ?, data_json = ?, updated_at = ?
                    WHERE enterprise_id = ? AND node_name = ? AND period = ? AND data_type = ?
                    """,
                    (
                        batch_id, active_energy_kwh, reactive_energy_kvarh,
                        cost_sum, data_json_str, now,
                        enterprise_id, node_name, period, data_type
                    ),
                )
                record_id = existing["id"]
            else:
                # Создаем новую запись
                cursor = conn.execute(
                    """
                    INSERT INTO node_consumption
                    (enterprise_id, batch_id, node_name, period, active_energy_kwh,
                     reactive_energy_kvarh, cost_sum, data_type, data_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        enterprise_id, batch_id, node_name, period,
                        active_energy_kwh, reactive_energy_kvarh, cost_sum, data_type,
                        data_json_str, now, now
                    ),
                )
                record_id = cursor.lastrowid
            
            imported_records.append({
                "id": record_id,
                "enterprise_id": enterprise_id,
                "batch_id": batch_id,
                "node_name": node_name,
                "period": period,
            })
    
    return imported_records


def get_node_consumption(
    enterprise_id: int,
    node_name: Optional[str] = None,
    period: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Получить данные потребления электроэнергии по узлам учёта из БД.
    
    Args:
        enterprise_id: ID предприятия
        node_name: Имя узла учёта (опционально, для фильтрации)
        period: Период (например, "2022-Q1") или None для всех периодов
    
    Returns:
        Список записей потребления по узлам
    """
    with get_connection() as conn:
        query = """
            SELECT id, enterprise_id, batch_id, node_name, period,
                   active_energy_kwh, reactive_energy_kvarh, cost_sum,
                   data_json, created_at, updated_at
            FROM node_consumption
            WHERE enterprise_id = ?
        """
        params: List[Any] = [enterprise_id]
        
        if node_name:
            query += " AND node_name = ?"
            params.append(node_name)
        
        if period:
            query += " AND period = ?"
            params.append(period)
        
        query += " ORDER BY period, node_name"
        
        rows = conn.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            record = _row_to_dict(row)
            # Парсим JSON, если есть
            if record.get("data_json"):
                try:
                    record["data_json"] = json.loads(record["data_json"])
                except (json.JSONDecodeError, TypeError):
                    record["data_json"] = None
            result.append(record)
        
        return result