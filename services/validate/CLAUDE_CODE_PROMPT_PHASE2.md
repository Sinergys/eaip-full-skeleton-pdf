# 🤖 Claude Code Prompt - Phase 2 Implementation

## 📋 Контекст проекта

Вы - эксперт по Python/FastAPI, работающий над модулем автоматической валидации Word документов для энергоаудита в проекте EAIP.

**Phase 1 (ЗАВЕРШЕНА):**
- ✅ Создана базовая структура проекта
- ✅ Настроены endpoints, конфигурация, модели
- ✅ Созданы скелеты основных классов

**Phase 2 (ВАША ЗАДАЧА):**
Реализовать полную функциональность обработки Word документов согласно техническому заданию.

---

## 🎯 Цель Phase 2

Реализовать **4 ключевых модуля** для автоматической проверки и корректировки отчётов энергоаудита:

1. **DocxProcessor** - Извлечение текста и объектов из DOCX
2. **AIProcessor** - Интеграция с Ollama и DeepSeek API
3. **DocumentAssembler** - Сборка финального документа с GOST форматированием
4. **OrchestratorService** - Полная реализация pipeline обработки

---

## 📂 Расположение файлов

**Базовая директория:** `C:\eaip\eaip_full_skeleton\services\validate\`

**Файлы для реализации:**
```
services/validate/
├── services/
│   ├── orchestrator.py        ⏳ РЕАЛИЗОВАТЬ полностью
│   ├── docx_processor.py      🆕 СОЗДАТЬ
│   ├── ai_processor.py        🆕 СОЗДАТЬ
│   └── document_assembler.py  🆕 СОЗДАТЬ
└── db/
    └── cache.py               ⏳ ДОРАБОТАТЬ интеграцию
```

---

## 🔧 Модуль 1: DocxProcessor

**Файл:** `services/docx_processor.py`

### Задачи:

1. **Извлечение текста** из DOCX с сохранением структуры
2. **Извлечение объектов** (изображения, таблицы, графики, формулы)
3. **Замена объектов маркерами** вида `[[OBJ_001]]`
4. **Обработка таблиц** с merged cells (используй опыт из python-docx issues)

### Технические требования:

```python
from pathlib import Path
from typing import Dict, Any, List
from docx import Document
from ..core.models import ExtractedObject

class DocxProcessor:
    """
    Обработка DOCX документов: извлечение текста и объектов.
    Соответствует разделу 3.1.3 ТЗ.
    """
    
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
        # РЕАЛИЗОВАТЬ:
        # 1. Открыть документ через python-docx
        # 2. Извлечь все параграфы текста
        # 3. Найти все InlineShapes (картинки)
        # 4. Найти все таблицы
        # 5. Заменить объекты на маркеры [[OBJ_NNN]]
        # 6. Сохранить объекты с метаданными
        pass
    
    def _extract_images(self, document: Document) -> Dict[str, ExtractedObject]:
        """Извлечь все изображения из документа."""
        # РЕАЛИЗОВАТЬ
        pass
    
    def _extract_tables(self, document: Document) -> Dict[str, ExtractedObject]:
        """
        Извлечь все таблицы из документа.
        
        ВАЖНО: Обрабатывать merged cells корректно!
        """
        # РЕАЛИЗОВАТЬ
        pass
    
    def _extract_charts(self, document: Document) -> Dict[str, ExtractedObject]:
        """Извлечь графики/диаграммы."""
        # РЕАЛИЗОВАТЬ (опционально, если есть в документах)
        pass
    
    def _replace_with_marker(
        self, 
        paragraph, 
        obj_id: str, 
        obj_type: str
    ) -> None:
        """Заменить объект в параграфе на маркер [[OBJ_XXX]]."""
        # РЕАЛИЗОВАТЬ
        pass
```

### Интеграция:

**Используй существующие утилиты:**
- `utils.exceptions.ProcessingError` для ошибок
- `core.models.ExtractedObject` для объектов

**Пример из проекта EAIP:**
```python
# Посмотри как обрабатываются DOCX в:
# C:\eaip\eaip_full_skeleton\services\ingest\parsers\word_parser.py
```

### Проблемы с merged cells:

**Известная проблема:** python-docx плохо работает с merged cells.

**Решение:**
```python
from docx.table import _Cell

def _get_merged_cell_value(cell: _Cell) -> str:
    """Handle merged cells correctly."""
    # Если ячейка merged, берём значение из первой ячейки диапазона
    if cell._tc.tcPr is not None:
        gridSpan = cell._tc.tcPr.gridSpan
        if gridSpan is not None:
            # Это merged cell
            pass
    return cell.text
```

---

## 🔧 Модуль 2: AIProcessor

**Файл:** `services/ai_processor.py`

### Задачи:

1. **Интеграция с Ollama** (локальная AI) для предварительного анализа
2. **Интеграция с DeepSeek API** для основной корректировки
3. **Retry механизм** с exponential backoff
4. **Парсинг ответов** DeepSeek с валидацией формата

### Технические требования:

```python
import httpx
import json
import asyncio
from typing import Dict, Any, Optional

from ..core.config import Settings
from ..core.models import OllamaAnalysisResult, DeepSeekCorrectionResult
from ..utils.prompts import create_ollama_prompt, create_deepseek_prompt
from ..utils.exceptions import OllamaError, DeepSeekError, DeepSeekFormatError

class AIProcessor:
    """
    Процессор для работы с AI сервисами (Ollama + DeepSeek).
    Соответствует разделу 3.1.5 ТЗ.
    """
    
    def __init__(
        self,
        ollama_url: str,
        deepseek_api_key: str,
        deepseek_url: str
    ):
        self.ollama_url = ollama_url
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_url = deepseek_url
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def analyze_with_ollama(
        self,
        chunk_text: str
    ) -> OllamaAnalysisResult:
        """
        Анализ текста через Ollama (предварительная проверка).
        
        Args:
            chunk_text: Текст чанка для анализа
        
        Returns:
            OllamaAnalysisResult с issues и fixes
        
        Raises:
            OllamaError: При ошибках Ollama
        """
        # РЕАЛИЗОВАТЬ:
        # 1. Создать промпт через create_ollama_prompt()
        # 2. Отправить POST запрос к Ollama API
        # 3. Распарсить JSON ответ
        # 4. Вернуть OllamaAnalysisResult
        
        # Пример запроса к Ollama:
        # POST http://localhost:11434/api/generate
        # {
        #   "model": "llama3.1",
        #   "prompt": "...",
        #   "stream": false
        # }
        pass
    
    async def analyze_with_deepseek(
        self,
        chunk: str,
        ollama_report: OllamaAnalysisResult,
        pkm_requirements: str
    ) -> DeepSeekCorrectionResult:
        """
        Корректировка текста через DeepSeek API.
        
        Args:
            chunk: Текст чанка с маркерами
            ollama_report: Результат анализа Ollama
            pkm_requirements: Требования ПКМ 690
        
        Returns:
            DeepSeekCorrectionResult с исправленным текстом
        
        Raises:
            DeepSeekError: При ошибках API
            DeepSeekFormatError: При неверном формате ответа
        """
        # РЕАЛИЗОВАТЬ:
        # 1. Создать промпт через create_deepseek_prompt()
        # 2. Отправить POST к DeepSeek API с retry
        # 3. Распарсить ответ (извлечь текст между маркерами)
        # 4. Валидировать формат
        # 5. Вернуть DeepSeekCorrectionResult
        
        # Пример запроса к DeepSeek:
        # POST https://api.deepseek.com/v1/chat/completions
        # Headers: {"Authorization": "Bearer API_KEY"}
        # {
        #   "model": "deepseek-chat",
        #   "messages": [
        #     {"role": "system", "content": "..."},
        #     {"role": "user", "content": "..."}
        #   ],
        #   "max_tokens": 4000
        # }
        pass
    
    async def _retry_with_backoff(
        self,
        func,
        max_retries: int = 2,
        initial_delay: float = 5.0
    ):
        """
        Retry decorator с exponential backoff.
        
        РЕАЛИЗОВАТЬ согласно разделу 3.2 ТЗ.
        """
        pass
    
    def _parse_deepseek_response(self, response_text: str) -> tuple[str, list[str]]:
        """
        Парсинг ответа DeepSeek с извлечением текста и рекомендаций.
        
        Формат ответа:
        [START_OF_CORRECTED_TEXT]
        ...текст...
        [END_OF_CORRECTED_TEXT]
        
        ---
        [CHUNK_RECOMMENDATIONS]
        1. ...
        [END_OF_RECOMMENDATIONS]
        
        ВАЖНО: Валидировать наличие всех маркеров!
        """
        # РЕАЛИЗОВАТЬ
        pass
    
    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()
```

### Интеграция:

**Используй существующие утилиты:**
- `utils.prompts.create_ollama_prompt()`
- `utils.prompts.create_deepseek_prompt()`
- `core.constants` для маркеров ответа

**Пример retry механизма:**
```python
async def _retry_with_backoff(self, func, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except httpx.TimeoutException as e:
            if attempt == max_retries:
                raise DeepSeekTimeoutError(f"Timeout after {max_retries} retries")
            await asyncio.sleep(2 ** attempt * 5)  # 5s, 10s, 20s
```

---

## 🔧 Модуль 3: DocumentAssembler

**Файл:** `services/document_assembler.py`

### Задачи:

1. **Загрузка GOST шаблона** из `templates/pcm690/energy_audit_template.docx`
2. **Вставка исправленного текста** с применением стилей
3. **Восстановление объектов** (замена `[[OBJ_XXX]]` на оригинальные объекты)
4. **Добавление секции "AI Summary and Recommendations"**
5. **Сохранение финального документа** как `[Original]_Проверенный.docx`

### Технические требования:

```python
from pathlib import Path
from typing import Dict, List
from docx import Document
from docx.shared import Pt, Cm

from ..core.models import ExtractedObject, ProcessingSummary

class DocumentAssembler:
    """
    Сборка финального DOCX документа на основе шаблона.
    Соответствует разделу 3.1.7 ТЗ.
    """
    
    def __init__(self, template_path: Path):
        self.template_path = template_path
        
        # Валидация существования шаблона
        if not template_path.exists():
            raise TemplateError(f"Template not found: {template_path}")
    
    async def assemble_document(
        self,
        corrected_text: str,
        objects: Dict[str, ExtractedObject],
        recommendations: List[str],
        summary: ProcessingSummary,
        original_filename: str
    ) -> str:
        """
        Создать финальный документ на основе шаблона.
        
        Args:
            corrected_text: Исправленный текст с маркерами [[OBJ_XXX]]
            objects: Словарь извлечённых объектов
            recommendations: Список рекомендаций
            summary: Итоговая сводка
            original_filename: Имя оригинального файла
        
        Returns:
            Путь к созданному файлу [Original]_Проверенный.docx
        
        Raises:
            DocumentAssemblyError: При ошибках сборки
        """
        # РЕАЛИЗОВАТЬ:
        # 1. Загрузить шаблон
        # 2. Применить стили ГОСТ
        # 3. Вставить исправленный текст
        # 4. Заменить маркеры на объекты
        # 5. Добавить секцию рекомендаций
        # 6. Сохранить документ
        pass
    
    def _load_template(self) -> Document:
        """Загрузить GOST шаблон."""
        # РЕАЛИЗОВАТЬ
        pass
    
    def _insert_corrected_text(
        self,
        document: Document,
        text: str
    ) -> None:
        """
        Вставить исправленный текст в документ.
        
        Применить стили ГОСТ:
        - Шрифт: Times New Roman
        - Размер: 14pt для основного текста
        - Межстрочный интервал: 1.5
        - Отступы по ГОСТ
        """
        # РЕАЛИЗОВАТЬ
        pass
    
    def _restore_objects(
        self,
        document: Document,
        objects: Dict[str, ExtractedObject]
    ) -> None:
        """
        Найти все маркеры [[OBJ_XXX]] и заменить на оригинальные объекты.
        
        ВАЖНО: 
        - Сохранить подписи к объектам
        - Применить форматирование по ГОСТ
        """
        # РЕАЛИЗОВАТЬ
        pass
    
    def _add_recommendations_section(
        self,
        document: Document,
        recommendations: List[str],
        summary: ProcessingSummary
    ) -> None:
        """
        Добавить секцию "AI Summary and Recommendations" в конец документа.
        
        Формат:
        - Заголовок секции
        - Краткая сводка (summary)
        - Список рекомендаций
        """
        # РЕАЛИЗОВАТЬ
        pass
    
    def _apply_gost_formatting(self, document: Document) -> None:
        """
        Применить форматирование по ГОСТ:
        - Поля: 2см сверху/снизу, 3см слева, 1см справа
        - Шрифт: Times New Roman 14pt
        - Интервал: 1.5
        - Выравнивание: по ширине
        """
        # РЕАЛИЗОВАТЬ
        pass
```

### Интеграция:

**Используй шаблон:**
```python
# Путь к шаблону берётся из settings
template_path = settings.GOST_TEMPLATE_PATH
# C:\eaip\templates\pcm690\energy_audit_template.docx
```

**Пример форматирования по ГОСТ:**
```python
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Установка полей
sections = document.sections
for section in sections:
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1)

# Форматирование параграфа
paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
paragraph.paragraph_format.line_spacing = 1.5
run = paragraph.runs[0]
run.font.name = 'Times New Roman'
run.font.size = Pt(14)
```

---

## 🔧 Модуль 4: OrchestratorService (Полная реализация)

**Файл:** `services/orchestrator.py`

### Задачи:

**Реализовать полный pipeline** из технического задания (разделы 3.1.2 - 3.1.8).

### Технические требования:

```python
async def process_report(
    self,
    file_path: str,
    file_hash: str,
    original_filename: str
) -> str:
    """
    Главный pipeline обработки отчёта.
    
    ПОЛНАЯ РЕАЛИЗАЦИЯ всех шагов из ТЗ раздел 3.1:
    
    1. Извлечение контента (3.1.3)
    2. Разбивка на чанки (3.1.4)
    3. Обработка каждого чанка:
       - Ollama анализ
       - DeepSeek корректировка
    4. Агрегация результатов (3.1.6)
    5. Сборка финального документа (3.1.7)
    6. Возврат пути к файлу
    """
    # РЕАЛИЗОВАТЬ полностью
    pass
```

### Реализовать методы:

1. **`_extract_content()`** - вызов DocxProcessor
2. **`_create_chunks()`** - разбивка текста на чанки ~20k токенов
3. **`_process_chunk()`** - обработка одного чанка через AI
4. **`_load_pkm_requirements()`** - загрузка требований ПКМ 690
5. **`_merge_chunks()`** - объединение исправленных чанков
6. **`_create_summary()`** - формирование итоговой сводки

### Chunking Strategy:

```python
def _create_chunks(self, text: str, max_tokens: int = 20000) -> List[TextChunk]:
    """
    Разбить текст на чанки с учётом разрывов секций.
    
    Логика:
    1. Использовать tiktoken для подсчёта токенов
    2. Искать границы секций/глав
    3. Если разрыв внутри секции:
       - В конец чанка: [[SECTION_INTERRUPTED_AT_CHAPTER_X]]
       - В начало следующего: [[CONTINUATION_OF_CHAPTER_X]]
    """
    from ..utils.helpers import count_tokens
    from ..core.constants import (
        SECTION_INTERRUPTED_PREFIX,
        CONTINUATION_PREFIX
    )
    
    # РЕАЛИЗОВАТЬ
    pass
```

### Загрузка ПКМ 690:

```python
async def _load_pkm_requirements(self) -> str:
    """
    Загрузить требования ПКМ 690 из существующего модуля.
    
    ИНТЕГРАЦИЯ с existing code:
    from eaip_full_skeleton.services.ingest.domain.pkm690_sections import (
        PKM690_SECTIONS
    )
    """
    # Импортировать существующую структуру
    from pathlib import Path
    import sys
    
    # Добавить путь к ingest модулю
    ingest_path = Path(__file__).parent.parent.parent.parent / "ingest"
    sys.path.insert(0, str(ingest_path))
    
    from domain.pkm690_sections import PKM690_SECTIONS
    
    # Собрать требования в текст
    sections_text = []
    for section in PKM690_SECTIONS:
        sections_text.append(
            f"{section.pkm690_number}. {section.pkm690_title}\n"
        )
        if section.template:
            sections_text.append(section.template)
    
    return "\n\n".join(sections_text)
```

---

## 🔧 Модуль 5: CacheManager (Доработка)

**Файл:** `db/cache.py`

### Задачи:

**Интеграция с существующей БД EAIP** из `services/ingest/database.py`

### Технические требования:

```python
async def get(self, file_hash: str) -> Optional[str]:
    """
    Получить результат из кеша по хешу файла.
    
    ИНТЕГРАЦИЯ с existing database.py:
    
    from pathlib import Path
    import sys
    
    # Добавить путь к ingest
    ingest_path = Path(__file__).parent.parent.parent.parent / "ingest"
    sys.path.insert(0, str(ingest_path))
    
    from database import find_duplicate_upload
    
    # Поиск дубликата
    duplicate = find_duplicate_upload(
        enterprise_id=0,  # Системный ID для Word validator
        filename="word_validation",
        file_size=0,
        file_hash=file_hash
    )
    
    if duplicate and duplicate.get('status') == 'completed':
        # Вернуть путь к кешированному результату
        return duplicate.get('result_path')
    
    return None
    """
    # РЕАЛИЗОВАТЬ
    pass

async def set(
    self,
    file_hash: str,
    result_path: str,
    original_filename: str,
    file_size: int
) -> None:
    """
    Сохранить результат в кеш.
    
    ИНТЕГРАЦИЯ с existing database.py:
    
    from database import create_upload, save_parsed_content
    
    # Создать запись о загрузке
    batch_id = f"word_validator_{file_hash[:16]}"
    
    upload = create_upload(
        batch_id=batch_id,
        enterprise_id=0,  # Системный
        filename=original_filename,
        file_type="docx",
        file_size=file_size,
        status="completed",
        file_hash=file_hash
    )
    
    # Сохранить путь к результату
    save_parsed_content(
        batch_id=batch_id,
        raw_json={"result_path": result_path},
        editable_text=""
    )
    """
    # РЕАЛИЗОВАТЬ
    pass
```

---

## ✅ Checklist для Phase 2

### После реализации проверь:

**DocxProcessor:**
- [ ] Корректно извлекает текст из DOCX
- [ ] Извлекает изображения с metadata
- [ ] Извлекает таблицы (включая merged cells)
- [ ] Заменяет объекты на маркеры [[OBJ_XXX]]
- [ ] Обрабатывает ошибки корректно

**AIProcessor:**
- [ ] Успешно подключается к Ollama
- [ ] Успешно подключается к DeepSeek API
- [ ] Парсит JSON ответ от Ollama
- [ ] Парсит форматированный ответ от DeepSeek
- [ ] Retry механизм работает при ошибках
- [ ] Timeout обрабатывается корректно

**DocumentAssembler:**
- [ ] Загружает GOST шаблон
- [ ] Вставляет текст с правильным форматированием
- [ ] Восстанавливает изображения по маркерам
- [ ] Восстанавливает таблицы по маркерам
- [ ] Добавляет секцию рекомендаций
- [ ] Сохраняет файл с правильным именем

**OrchestratorService:**
- [ ] Pipeline выполняется полностью
- [ ] Chunking работает корректно (~20k tokens)
- [ ] Маркеры разрыва секций добавляются
- [ ] Все чанки обрабатываются
- [ ] Результаты агрегируются правильно
- [ ] Финальный документ создаётся

**CacheManager:**
- [ ] Интеграция с existing БД работает
- [ ] Поиск дубликатов работает
- [ ] Сохранение в кеш работает
- [ ] Кеш возвращается корректно

**Integration Tests:**
- [ ] End-to-end тест с реальным DOCX файлом
- [ ] Кеш работает (второй запрос возвращает кеш)
- [ ] Большой файл обрабатывается (~200 страниц)
- [ ] Ошибки обрабатываются gracefully

---

## 🧪 Тестирование

### Тестовый файл:

```
C:\Users\DELL\Desktop\Navoiy IES\отчёт коректировка.docx
```

### Пример теста:

```python
import asyncio
from pathlib import Path
from services.orchestrator import OrchestratorService
from core.config import settings

async def test_full_pipeline():
    """Тест полного pipeline."""
    
    test_file = Path(r"C:\Users\DELL\Desktop\Navoiy IES\отчёт коректировка.docx")
    
    orchestrator = OrchestratorService(settings)
    
    result = await orchestrator.process_report(
        file_path=str(test_file),
        file_hash="test_hash_123",
        original_filename=test_file.name
    )
    
    print(f"✅ Результат: {result}")
    assert Path(result).exists()
    assert result.endswith("_Проверенный.docx")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
```

---

## 📚 Полезные ресурсы

**python-docx документация:**
- https://python-docx.readthedocs.io/

**Примеры из проекта EAIP:**
```
C:\eaip\eaip_full_skeleton\services\ingest\parsers\word_parser.py
C:\eaip\eaip_full_skeleton\services\ingest\domain\pkm690_sections.py
C:\eaip\eaip_full_skeleton\services\ingest\database.py
```

**DeepSeek API:**
- https://api-docs.deepseek.com/

**Ollama API:**
- http://localhost:11434/api

---

## ⚠️ Важные замечания

1. **Размер чанков:** Строго 20k токенов максимум (не 100k как в исходном ТЗ!)
2. **Маркеры:** КРИТИЧЕСКИ важно сохранять все `[[OBJ_XXX]]` и `[[SECTION_...]]`
3. **GOST форматирование:** Применять строго по стандарту
4. **Интеграция с БД:** Использовать existing functions из `database.py`
5. **Error handling:** Все ошибки логировать и обрабатывать gracefully

---

## 🎯 Приоритеты реализации

**Высокий приоритет:**
1. OrchestratorService (основной pipeline)
2. DocxProcessor (извлечение контента)
3. AIProcessor (интеграция с AI)

**Средний приоритет:**
4. DocumentAssembler (сборка документа)
5. CacheManager (интеграция с БД)

**Низкий приоритет:**
- Оптимизации производительности
- Дополнительные валидации

---

## 📝 Финальные инструкции

**После реализации:**

1. Запусти тесты
2. Проверь все checklist items
3. Создай файл `PHASE2_COMPLETION_REPORT.md` с отчётом
4. Зафиксируй известные проблемы в `KNOWN_ISSUES.md`

**Формат отчёта:**
```markdown
# Phase 2 Completion Report

## ✅ Реализовано:
- [ список ]

## 🐛 Известные проблемы:
- [ список ]

## 🧪 Результаты тестов:
- [ результаты ]

## 📊 Метрики:
- Время обработки тестового файла: X секунд
- Размер итогового файла: Y MB
- Количество рекомендаций: Z
```

---

**Удачи в реализации! 🚀**
