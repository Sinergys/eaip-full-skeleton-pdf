"""
Конфигурация pytest для всех тестов
"""
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock
import tempfile
import shutil

# Добавляем путь к сервисам
SERVICES_DIR = Path(__file__).parent.parent / "services" / "ingest"
sys.path.insert(0, str(SERVICES_DIR))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

# Настройка переменных окружения для тестов
os.environ.setdefault("AI_ENABLED", "false")
os.environ.setdefault("AI_PROVIDER", "deepseek")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_password")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("REDIS_PASSWORD", "test_redis")


@pytest.fixture
def temp_dir():
    """Создает временную директорию для тестов"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_ai_client():
    """Мок AI клиента"""
    client = Mock()
    client.process_prompt.return_value = {
        "text": "Mock AI response",
        "usage": {"total_tokens": 100},
        "model": "mock-model",
        "provider": "mock"
    }
    client.process_vision_prompt.return_value = {
        "text": "Mock vision response",
        "usage": {"total_tokens": 200},
        "model": "mock-vision-model",
        "provider": "mock"
    }
    client.get_usage_metrics.return_value = {
        "total_requests": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "average_response_time": 0.0,
        "errors_count": 0
    }
    client.is_available.return_value = True
    return client


@pytest.fixture
def sample_energy_passport_data():
    """Mock данные энергетического паспорта"""
    return {
        "enterprise": {
            "id": 1,
            "name": "Тестовое предприятие",
            "inn": "1234567890",
            "address": "Тестовый адрес",
            "director_name": "Иванов И.И.",
            "industry": "Производство",
            "reporting_year": 2024
        },
        "resources": {
            "electricity": {
                "Q1": {"consumption": 1000.0, "cost": 50000.0},
                "Q2": {"consumption": 1200.0, "cost": 60000.0},
                "Q3": {"consumption": 1100.0, "cost": 55000.0},
                "Q4": {"consumption": 1300.0, "cost": 65000.0}
            },
            "gas": {
                "Q1": {"consumption": 500.0, "cost": 25000.0},
                "Q2": {"consumption": 600.0, "cost": 30000.0},
                "Q3": {"consumption": 550.0, "cost": 27500.0},
                "Q4": {"consumption": 650.0, "cost": 32500.0}
            }
        },
        "equipment": [
            {
                "name": "Насос",
                "power_kw": 10.5,
                "quantity": 2,
                "hours_per_year": 8760
            }
        ],
        "envelope": {
            "total_area_m2": 1000.0,
            "total_heat_loss": 50000.0
        }
    }


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Создает тестовый PDF файл"""
    # В реальных тестах можно использовать реальный PDF
    pdf_path = temp_dir / "test.pdf"
    # Создаем минимальный PDF (заглушка)
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 0\ntrailer\n<<\n/Root 1 0 R\n>>\nstartxref\n0\n%%EOF")
    return str(pdf_path)


@pytest.fixture
def sample_excel_path(temp_dir):
    """Создает тестовый Excel файл"""
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Данные"
    ws.append(["Месяц", "Потребление", "Стоимость"])
    ws.append(["Январь", 100, 5000])
    ws.append(["Февраль", 120, 6000])
    excel_path = temp_dir / "test.xlsx"
    wb.save(excel_path)
    return str(excel_path)


@pytest.fixture
def mock_redis():
    """Мок Redis клиента"""
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.exists.return_value = False
    return redis_mock


@pytest.fixture
def mock_postgres():
    """Мок PostgreSQL соединения"""
    conn_mock = Mock()
    cursor_mock = Mock()
    conn_mock.cursor.return_value = cursor_mock
    cursor_mock.fetchone.return_value = None
    cursor_mock.fetchall.return_value = []
    cursor_mock.execute.return_value = None
    return conn_mock

