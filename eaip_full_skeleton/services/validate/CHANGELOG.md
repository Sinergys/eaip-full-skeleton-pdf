# Changelog - Word Document Validator

Все значимые изменения в проекте будут документированы здесь.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Changed
- Улучшен парсинг ответов DeepSeek API с 4 стратегиями fallback

---

## [0.2.1] - 2024-12-14

### Fixed
- **[CRITICAL]** Исправлена ошибка парсинга DeepSeek API ответов
  - Проблема: `DeepSeekFormatError: Missing [END_OF_CORRECTED_TEXT] marker`
  - Решение: Добавлен гибкий парсинг с 4 стратегиями fallback
  - Файлы: `services/ai_processor.py`
  - Impact: Устранены сбои при обработке документов

### Changed
- Метод `_parse_deepseek_response()` теперь использует 4 стратегии:
  1. Точные маркеры (original)
  2. Regex гибкий поиск
  3. Текст до рекомендаций
  4. Весь ответ (fallback)
- Добавлено подробное логирование парсинга

### Added
- Импорт `re` в `ai_processor.py` для regex поиска
- Комментарии в коде объясняющие каждую стратегию парсинга

---

## [0.2.0] - 2024-12-14

### Added
- **Phase 2 Complete**: Полная реализация обработки Word документов
- `services/docx_processor.py` - извлечение текста и объектов
- `services/ai_processor.py` - интеграция с Ollama и DeepSeek
- `services/document_assembler.py` - сборка финального документа
- Полная реализация `services/orchestrator.py`

### Changed
- Исправлены импорты (относительные → абсолютные)
- Обновлена конфигурация Ollama модели

---

## [0.1.0] - 2024-12-14

### Added
- **Phase 1 Complete**: Базовая инфраструктура
- Структура проекта и директории
- API endpoints (`/api/v1/check-report/`, `/api/v1/health`)
- Конфигурация (`core/config.py`, `core/constants.py`)
- Модели данных (`core/models.py`)
- Утилиты (исключения, хелперы, промпты)
- Менеджер кеша (скелет)
- FastAPI приложение с Swagger UI
- Документация (README, Quick Start, Phase 2 Prompt)

### Fixed
- Конфликты зависимостей (httpx версия)
- Загрузка .env файла через python-dotenv

---

## Типы изменений

- `Added` - новые функции
- `Changed` - изменения в существующей функциональности
- `Deprecated` - функции которые скоро будут удалены
- `Removed` - удалённые функции
- `Fixed` - исправления багов
- `Security` - исправления безопасности

---

## Версионирование

Проект следует [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH (например, 1.2.3)
- MAJOR - несовместимые изменения API
- MINOR - новая функциональность (обратно совместимая)
- PATCH - исправления багов (обратно совместимые)
