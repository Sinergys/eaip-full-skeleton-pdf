# 🤖 ПРОМТ ДЛЯ CLAUDE CODE: Обновление Validate Service и Интеграция

**Дата:** 18 декабря 2024  
**Проект:** EAIP Full Skeleton  
**Задачи:** 3 пункта (обязательный + интеграция + тесты)

---

## 📋 КОНТЕКСТ ПРОЕКТА

### Структура проекта EAIP
```
C:\eaip\eaip_full_skeleton\
├── services/
│   ├── validate/          # Word Document Validator (порт 8002)
│   │   ├── main.py        # ✅ Уже исправлен на 8002
│   │   ├── README_WORD_VALIDATOR.md  # ❌ Требует обновления
│   │   └── api/v1/endpoints/word_validation.py
│   ├── ingest/            # File Upload Service (порт 8001)
│   │   ├── main.py
│   │   └── web/
│   │       ├── upload.html
│   │       └── results.html  # 🎯 Сюда добавить кнопку
│   └── [другие сервисы...]
└── infra/
    └── docker-compose.local.yml
```

### Validate Service API
- **Endpoint:** `POST /api/v1/check-report/`
- **Порт:** 8002 (был 8003, уже исправлен в main.py)
- **Функция:** Валидация Word документов по ПКМ №690
- **Возврат:** Проверенный DOCX файл

### Веб-интерфейс
- **Ingest Service:** порт 8001
- **Страница результатов:** `/web/results.html`
- **Параметр:** `batchId` (ID загруженного файла)

---

## 🎯 ЗАДАЧА 1: ОБНОВИТЬ ДОКУМЕНТАЦИЮ (ОБЯЗАТЕЛЬНО)

### Файл для изменения
**Путь:** `C:\eaip\eaip_full_skeleton\services\validate\README_WORD_VALIDATOR.md`

### Что изменить
Заменить все упоминания порта **8003** на **8002** в 4 местах:

#### Изменение 1 (строка ~48)
**Было:**
```bash
uvicorn main:app --reload --port 8003
```

**Должно быть:**
```bash
uvicorn main:app --reload --port 8002
```

#### Изменение 2 (строка ~56)
**Было:**
```bash
curl -X POST "http://localhost:8003/api/v1/check-report/" \
  -F "file=@report.docx"
```

**Должно быть:**
```bash
curl -X POST "http://localhost:8002/api/v1/check-report/" \
  -F "file=@report.docx"
```

#### Изменение 3 (строка ~139)
**Было:**
```markdown
- Swagger UI: http://localhost:8003/docs
```

**Должно быть:**
```markdown
- Swagger UI: http://localhost:8002/docs
```

#### Изменение 4 (строка ~140)
**Было:**
```markdown
- ReDoc: http://localhost:8003/redoc
```

**Должно быть:**
```markdown
- ReDoc: http://localhost:8002/redoc
```

### Команда для проверки
```powershell
# Убедиться что все изменения сделаны
Select-String -Path "C:\eaip\eaip_full_skeleton\services\validate\README_WORD_VALIDATOR.md" -Pattern "8003"
# Должно вернуть 0 результатов
```

---

## 🎯 ЗАДАЧА 2: ДОБАВИТЬ ИНТЕГРАЦИЮ В ВЕБ-ИНТЕРФЕЙС

### Цель
Добавить кнопку "Проверить Word документ" в страницу результатов, которая отправляет DOCX файл на validate service и скачивает проверенный документ.

### Файл для изменения
**Путь:** `C:\eaip\eaip_full_skeleton\services\ingest\web\results.html`

### Что добавить

#### 1. HTML разметка для кнопки (добавить после секции генерации паспорта)

Найти секцию с кнопками генерации (примерно строка 600-800) и добавить:

```html
<!-- Word Document Validation Section -->
<div class="card" id="wordValidationCard" style="display: none;">
    <h2>🔍 Проверка Word документа (ПКМ №690)</h2>
    <p class="hint">
        Если у вас есть готовый Word документ энергоаудита, вы можете проверить его 
        на соответствие требованиям ПКМ №690 и получить исправленную версию.
    </p>
    
    <div style="margin: 16px 0;">
        <input 
            type="file" 
            id="wordDocInput" 
            accept=".docx"
            style="display: none;"
        />
        <label for="wordDocInput" class="button" style="display: inline-block; cursor: pointer;">
            📄 Выбрать Word документ (.docx)
        </label>
        <span id="wordDocName" style="margin-left: 12px; color: #6b7280;"></span>
    </div>
    
    <button 
        id="validateWordBtn" 
        type="button" 
        style="display: none;"
        onclick="validateWordDocument()"
    >
        ✓ Проверить документ
    </button>
    
    <div id="wordValidationStatus" class="status" style="display: none;"></div>
    
    <div id="wordValidationProgress" style="display: none; margin-top: 16px;">
        <div class="progress-bar-wrapper">
            <div class="progress-bar" id="wordValidationProgressBar"></div>
        </div>
        <div class="progress-message" id="wordValidationProgressMessage">
            Проверка документа...
        </div>
    </div>
</div>
```

#### 2. JavaScript функции (добавить в конец блока <script>)

```javascript
// ============ Word Document Validation ============

// Показать карточку валидации Word документов
function showWordValidationCard() {
    const card = document.getElementById('wordValidationCard');
    if (card) {
        card.style.display = 'block';
        // Прокрутить к карточке
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Обработчик выбора файла
document.addEventListener('DOMContentLoaded', function() {
    const wordDocInput = document.getElementById('wordDocInput');
    const wordDocName = document.getElementById('wordDocName');
    const validateBtn = document.getElementById('validateWordBtn');
    
    if (wordDocInput) {
        wordDocInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                if (!file.name.endsWith('.docx')) {
                    alert('Пожалуйста, выберите файл формата .docx');
                    wordDocInput.value = '';
                    return;
                }
                
                const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
                wordDocName.textContent = `${file.name} (${fileSizeMB} МБ)`;
                validateBtn.style.display = 'inline-block';
            } else {
                wordDocName.textContent = '';
                validateBtn.style.display = 'none';
            }
        });
    }
});

// Функция валидации Word документа
async function validateWordDocument() {
    const fileInput = document.getElementById('wordDocInput');
    const statusDiv = document.getElementById('wordValidationStatus');
    const progressDiv = document.getElementById('wordValidationProgress');
    const progressBar = document.getElementById('wordValidationProgressBar');
    const progressMessage = document.getElementById('wordValidationProgressMessage');
    const validateBtn = document.getElementById('validateWordBtn');
    
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert('Пожалуйста, выберите Word документ для проверки');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Проверка размера файла (максимум 100 МБ)
    const maxSizeMB = 100;
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
        alert(`Размер файла (${fileSizeMB.toFixed(2)} МБ) превышает максимально допустимый (${maxSizeMB} МБ)`);
        return;
    }
    
    // Подготовка FormData
    const formData = new FormData();
    formData.append('file', file);
    
    // Показать прогресс
    if (statusDiv) statusDiv.style.display = 'none';
    if (progressDiv) progressDiv.style.display = 'block';
    if (progressBar) progressBar.style.width = '10%';
    if (progressMessage) progressMessage.textContent = 'Загрузка файла на сервер...';
    if (validateBtn) validateBtn.disabled = true;
    
    try {
        console.log('Отправка запроса на валидацию Word документа...');
        
        // Отправка запроса на validate service
        const response = await fetch('http://localhost:8002/api/v1/check-report/', {
            method: 'POST',
            body: formData
        });
        
        if (progressBar) progressBar.style.width = '50%';
        if (progressMessage) progressMessage.textContent = 'Обработка документа AI системой...';
        
        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage = `Ошибка сервера (${response.status})`;
            try {
                const errorData = JSON.parse(errorText);
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                errorMessage = errorText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        if (progressBar) progressBar.style.width = '90%';
        if (progressMessage) progressMessage.textContent = 'Получение проверенного документа...';
        
        // Получить проверенный файл
        const blob = await response.blob();
        
        if (progressBar) progressBar.style.width = '100%';
        if (progressMessage) progressMessage.textContent = 'Документ проверен успешно!';
        
        // Создать имя файла с суффиксом "_Проверенный"
        const originalName = file.name.replace('.docx', '');
        const checkedFileName = `${originalName}_Проверенный.docx`;
        
        // Скачать файл
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = checkedFileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
        
        // Показать успех
        if (statusDiv) {
            statusDiv.className = 'status success';
            statusDiv.style.display = 'block';
            statusDiv.textContent = `✓ Документ успешно проверен и скачан: ${checkedFileName}`;
        }
        
        // Скрыть прогресс через 2 секунды
        setTimeout(() => {
            if (progressDiv) progressDiv.style.display = 'none';
        }, 2000);
        
        console.log('Документ успешно проверен и скачан');
        
    } catch (error) {
        console.error('Ошибка при проверке документа:', error);
        
        if (statusDiv) {
            statusDiv.className = 'status error';
            statusDiv.style.display = 'block';
            statusDiv.textContent = `Ошибка: ${error.message}`;
        }
        
        if (progressDiv) progressDiv.style.display = 'none';
        
        alert(`Ошибка при проверке документа:\n${error.message}`);
        
    } finally {
        if (validateBtn) validateBtn.disabled = false;
    }
}

// Добавить кнопку для показа секции валидации в главном меню действий
// (вызвать после загрузки страницы)
document.addEventListener('DOMContentLoaded', function() {
    // Найти блок с кнопками действий и добавить новую кнопку
    const actionsContainer = document.querySelector('.actions');
    if (actionsContainer && !document.getElementById('showWordValidationBtn')) {
        const showValidationBtn = document.createElement('button');
        showValidationBtn.id = 'showWordValidationBtn';
        showValidationBtn.type = 'button';
        showValidationBtn.style.cssText = 'background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);';
        showValidationBtn.textContent = '🔍 Проверить Word документ';
        showValidationBtn.onclick = showWordValidationCard;
        actionsContainer.appendChild(showValidationBtn);
    }
});
```

### Стилизация (если нужно добавить новые стили)

Добавить в блок `<style>`:

```css
.button {
    padding: 12px 20px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    text-decoration: none;
}

.button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 20px rgba(79, 70, 229, 0.25);
}
```

---

## 🎯 ЗАДАЧА 3: СОЗДАТЬ ИНТЕГРАЦИОННЫЕ ТЕСТЫ

### Цель
Создать автоматические тесты для проверки:
1. Работы validate API
2. Интеграции веб-интерфейса с validate service
3. Корректности обработки документов

### Создать новую директорию и файлы

**Путь:** `C:\eaip\eaip_full_skeleton\services\validate\tests\`

### 3.1. Создать `conftest.py`

```python
"""
Pytest configuration for validate service tests.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def test_docx_file():
    """Fixture providing path to test DOCX file."""
    # Create a simple test DOCX file
    from docx import Document
    
    doc = Document()
    doc.add_heading('Тестовый энергоаудит', 0)
    doc.add_paragraph('Это тестовый документ для проверки.')
    doc.add_heading('1. Введение', level=1)
    doc.add_paragraph('Тестовое содержание раздела.')
    
    test_file = Path(__file__).parent / 'test_data' / 'test_report.docx'
    test_file.parent.mkdir(exist_ok=True)
    doc.save(str(test_file))
    
    return test_file


@pytest.fixture
def api_base_url():
    """Base URL for validate API."""
    return "http://localhost:8002"
```

### 3.2. Создать `test_validate_api.py`

```python
"""
Integration tests for validate service API.
"""
import pytest
import requests
from pathlib import Path


class TestValidateAPI:
    """Test validate service API endpoints."""
    
    def test_health_endpoint(self, api_base_url):
        """Test /health endpoint."""
        response = requests.get(f"{api_base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data['service'] == 'validate'
        assert data['status'] == 'ok'
    
    def test_check_report_endpoint_exists(self, api_base_url):
        """Test that check-report endpoint exists."""
        # Send request without file (should fail but endpoint should exist)
        response = requests.post(f"{api_base_url}/api/v1/check-report/")
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code == 422
    
    def test_check_report_with_file(self, api_base_url, test_docx_file):
        """Test document validation with a real file."""
        with open(test_docx_file, 'rb') as f:
            files = {'file': ('test_report.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(
                f"{api_base_url}/api/v1/check-report/",
                files=files,
                timeout=300  # 5 minutes timeout for AI processing
            )
        
        # Check response
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        # Check that we received a file
        assert len(response.content) > 0
        
        # Save validated file for manual inspection
        output_file = Path(__file__).parent / 'test_data' / 'test_report_validated.docx'
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Validated file saved to: {output_file}")
    
    def test_check_report_invalid_file(self, api_base_url):
        """Test validation with invalid file type."""
        # Create a fake txt file
        fake_file = Path(__file__).parent / 'test_data' / 'fake.txt'
        fake_file.parent.mkdir(exist_ok=True)
        fake_file.write_text('This is not a DOCX file')
        
        with open(fake_file, 'rb') as f:
            files = {'file': ('fake.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(
                f"{api_base_url}/api/v1/check-report/",
                files=files
            )
        
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_check_report_large_file(self, api_base_url):
        """Test validation rejects files over size limit."""
        # Create a file larger than 100MB (use sparse file for speed)
        large_file = Path(__file__).parent / 'test_data' / 'large.docx'
        large_file.parent.mkdir(exist_ok=True)
        
        # Create 101MB file
        with open(large_file, 'wb') as f:
            f.write(b'x' * (101 * 1024 * 1024))
        
        try:
            with open(large_file, 'rb') as f:
                files = {'file': ('large.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                response = requests.post(
                    f"{api_base_url}/api/v1/check-report/",
                    files=files,
                    timeout=10
                )
            
            # Should reject large file
            assert response.status_code in [400, 413, 422]
        finally:
            # Cleanup
            if large_file.exists():
                large_file.unlink()
```

### 3.3. Создать `test_web_integration.py`

```python
"""
Integration tests for web interface with validate service.
"""
import pytest
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.integration
class TestWebIntegration:
    """Test web interface integration with validate service."""
    
    @pytest.fixture
    def driver(self):
        """Selenium WebDriver fixture."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_validate_button_exists(self, driver):
        """Test that validate button exists on results page."""
        driver.get('http://localhost:8001/web/results.html?batchId=test')
        
        # Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # Check for validate button
        button = driver.find_element(By.ID, 'showWordValidationBtn')
        assert button is not None
        assert 'Проверить Word документ' in button.text
    
    def test_validate_button_shows_card(self, driver):
        """Test that clicking validate button shows validation card."""
        driver.get('http://localhost:8001/web/results.html?batchId=test')
        
        # Click button
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'showWordValidationBtn'))
        )
        button.click()
        
        # Check card is visible
        card = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'wordValidationCard'))
        )
        assert card.is_displayed()
    
    def test_file_upload_and_validation(self, driver, test_docx_file):
        """Test full workflow: upload file and validate."""
        driver.get('http://localhost:8001/web/results.html?batchId=test')
        
        # Show validation card
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'showWordValidationBtn'))
        )
        button.click()
        
        # Upload file
        file_input = driver.find_element(By.ID, 'wordDocInput')
        file_input.send_keys(str(test_docx_file.absolute()))
        
        # Click validate button
        validate_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'validateWordBtn'))
        )
        validate_btn.click()
        
        # Wait for success message (may take time for AI processing)
        success_message = WebDriverWait(driver, 300).until(
            EC.visibility_of_element_located((By.ID, 'wordValidationStatus'))
        )
        
        assert 'успешно' in success_message.text.lower()
```

### 3.4. Создать `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    integration: Integration tests (deselect with '-m "not integration"')
    slow: Slow tests (deselect with '-m "not slow"')
addopts = 
    -v
    --tb=short
    --strict-markers
```

### 3.5. Создать `requirements-test.txt`

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
requests==2.31.0
selenium==4.15.2
python-docx==1.1.0
```

### Команды для запуска тестов

```powershell
# Установить зависимости
cd C:\eaip\eaip_full_skeleton\services\validate
pip install -r requirements-test.txt

# Запустить все тесты
pytest tests/

# Запустить только API тесты
pytest tests/test_validate_api.py -v

# Запустить без интеграционных тестов (без Selenium)
pytest tests/ -m "not integration" -v

# Запустить с подробным выводом
pytest tests/ -v -s
```

---

## ✅ ПРОВЕРОЧНЫЙ ЧЕКЛИСТ

После выполнения всех задач проверить:

### Задача 1: Документация
- [ ] В `README_WORD_VALIDATOR.md` все порты 8003 заменены на 8002
- [ ] Команда `Select-String -Pattern "8003"` ничего не находит
- [ ] Документация корректно отображается

### Задача 2: Веб-интеграция
- [ ] Кнопка "Проверить Word документ" видна на странице results.html
- [ ] При клике открывается секция валидации
- [ ] Можно выбрать DOCX файл
- [ ] При отправке запрос идёт на `http://localhost:8002/api/v1/check-report/`
- [ ] Проверенный файл скачивается с суффиксом "_Проверенный"
- [ ] Показываются статус и прогресс
- [ ] Ошибки обрабатываются корректно

### Задача 3: Тесты
- [ ] Директория `tests/` создана
- [ ] Все 5 файлов созданы
- [ ] `pytest tests/` запускается без ошибок импорта
- [ ] Тест `/health` проходит
- [ ] Тесты API работают (кроме тестов с реальными файлами, если сервис не запущен)

---

## 🚀 ПОРЯДОК ВЫПОЛНЕНИЯ

### Шаг 1: Обновить документацию (5 минут)
1. Открыть `services/validate/README_WORD_VALIDATOR.md`
2. Найти и заменить все "8003" на "8002" (4 места)
3. Сохранить файл
4. Проверить через `Select-String`

### Шаг 2: Добавить веб-интеграцию (30 минут)
1. Открыть `services/ingest/web/results.html`
2. Добавить HTML разметку для карточки валидации
3. Добавить JavaScript функции
4. Добавить CSS стили (если нужно)
5. Проверить в браузере:
   - Открыть http://localhost:8001/web/results.html?batchId=test
   - Проверить наличие кнопки
   - Проверить работу функционала

### Шаг 3: Создать тесты (20 минут)
1. Создать директорию `services/validate/tests/`
2. Создать 5 файлов тестов
3. Установить зависимости: `pip install -r requirements-test.txt`
4. Запустить тесты: `pytest tests/ -v`

### Шаг 4: Финальная проверка (10 минут)
1. Запустить validate service: `python main.py`
2. Запустить ingest service: `cd ../ingest && python main.py`
3. Открыть браузер: http://localhost:8001/web/results.html
4. Проверить полный workflow:
   - Нажать кнопку "Проверить Word документ"
   - Выбрать тестовый DOCX файл
   - Нажать "Проверить документ"
   - Дождаться скачивания проверенного файла
5. Запустить тесты: `pytest tests/ -v`

---

## 💡 ПОДСКАЗКИ ДЛЯ CLAUDE CODE

### Для поиска нужных секций в HTML
```
В results.html искать:
- Секцию с кнопками: <div class="actions">
- Секцию генерации паспорта: "Генерация энергопаспорта"
- Блок <script>: для добавления JavaScript
- Блок <style>: для добавления CSS
```

### Для проверки портов
```powershell
# Проверить что validate service слушает на 8002
netstat -ano | findstr :8002

# Проверить что ingest service слушает на 8001
netstat -ano | findstr :8001
```

### Для отладки
```javascript
// Добавить в JavaScript функцию валидации
console.log('Validate API URL:', 'http://localhost:8002/api/v1/check-report/');
console.log('File size:', file.size, 'bytes');
console.log('File name:', file.name);
```

---

## 📝 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После выполнения всех задач:

1. ✅ Документация актуальна (порт 8002 везде)
2. ✅ Веб-интерфейс имеет кнопку проверки документов
3. ✅ Пользователь может загрузить DOCX и получить проверенный файл
4. ✅ Есть автоматические тесты для проверки работоспособности
5. ✅ Система готова к использованию

---

**Конец промта. Удачи в выполнении! 🚀**
