# WAVE 1: АНАЛИЗ 22 ДОПОЛНИТЕЛЬНЫХ ФАЙЛОВ
## ГРУППЫ 5-11 - КОНКРЕТНЫЕ ОПЕРАЦИИ

**Дата:** 11 декабря 2025  
**Файлов проанализировано:** 22  
**Общий прогресс Wave 1:** 50/80 файлов (62.5%)

---

## ГРУППА 5: CI/CD И ИНФРАСТРУКТУРА (3 файла)

### 📄 1. .github/workflows/tests.yml

**Dependency Scan:**
- ✅ NOT REFERENCED in code (это нормально для CI/CD)
- 🔗 **ЗАВИСИТ ОТ:**
  - tools/fill_energy_passport.py
  - domain/energy_passport_calculations.py
  - scripts/test_reference_*.py
  - data/fixtures/reference_enterprise_*.json

**Conflict Detection:** НЕТ

**Конкретная операция:**
```bash
KEEP: .github/workflows/tests.yml
REASON: 
  - Критический CI/CD workflow
  - Автоматическое тестирование reference enterprises
  - Запускается при изменениях в ключевых модулях
  - ❌ НЕ ТРОГАТЬ без понимания CI/CD
```

**Risk Level:** 🔴 CRITICAL  
**Priority:** CRITICAL

---

### 📄 2. eaip_full_skeleton/infra/docker-compose.yml

**Dependency Scan:**
- ✅ NOT REFERENCED in code  
- 🔗 **ЗАВИСИТ ОТ:**
  - .env (переменные окружения)
  - services/*/Dockerfile (все 7 сервисов)
  - PostgreSQL, Redis, MinIO images

**Content Analysis:**
```yaml
Services defined: 7 microservices + 3 infrastructure
- gateway-auth (port 8000)
- ingest (port 8001)
- validate (port 8002)
- analytics (port 8003)
- recommend (port 8004)
- reports (port 8005)
- management (port 8006)
Infrastructure: postgres, redis, minio
```

**Conflict Detection:**
- ⚠️ **ПОТЕНЦИАЛЬНЫЙ:** docker-compose.dev.yml отсутствует (был в списке, но файл не найден)

**Конкретная операция:**
```bash
KEEP: eaip_full_skeleton/infra/docker-compose.yml
REASON:
  - Production orchestration конфигурация
  - Определяет всю микросервисную архитектуру
  - Критично для deployment
  - ❌ ИЗМЕНЕНИЯ ТРЕБУЮТ ПОЛНОГО ТЕСТИРОВАНИЯ DEPLOYMENT
```

**Risk Level:** 🔴 CRITICAL  
**Priority:** CRITICAL

---

### 📄 3. eaip_full_skeleton/infra/docker-compose.dev.yml

**Status:** ❌ **FILE NOT FOUND**

**Конкретная операция:**
```bash
NO FILE: docker-compose.dev.yml
ACTION: DOCUMENT ABSENCE
REASON:
  - Файл был в анализе EAIP_ANALYSIS_SUMMARY.md
  - Фактически отсутствует в проекте
  - Возможно был удален или никогда не существовал
RECOMMENDATION: Удалить из списков файлов проекта
```

**Risk Level:** ⚠️ MEDIUM (документационный риск)  
**Priority:** LOW

---

## ГРУППА 6: ROOT КОНФИГУРАЦИЯ (4 файла)

### 📄 4. config/ocr.yml

**Конкретная операция:**
```bash
KEEP: config/ocr.yml
REASON:
  - OCR processing configuration
  - Используется tools/ocr_*.py скриптами
  - Настройки распознавания текста из PDF
```

**Risk Level:** 🟡 MEDIUM  
**Priority:** HIGH

---

### 📄 5. pyproject.toml

**Dependency Scan:**
- 🔗 Используется для определения зависимостей Python проекта
- ⚠️ **ПОТЕНЦИАЛЬНЫЙ КОНФЛИКТ** с requirements.txt

**Конкретная операция:**
```bash
UPDATE: pyproject.toml
ACTION: Синхронизировать с requirements.txt
REASON:
  - Современный стандарт Python packaging
  - Может быть несинхронизирован с requirements.txt
  - Проверить актуальность зависимостей
CHECK:
  - Сравнить dependencies с requirements.txt
  - Обновить версии пакетов
  - Добавить недостающие зависимости
```

**Risk Level:** 🟡 MEDIUM  
**Priority:** HIGH

---

### 📄 6. requirements.txt

**Dependency Scan:**
- 🔴 **КРИТИЧЕСКИЙ** - используется всеми установочными скриптами
- 🔗 Ссылается из .github/workflows/tests.yml
- ⚠️ Потенциальный конфликт с pyproject.toml

**Конкретная операция:**
```bash
KEEP: requirements.txt
UPDATE: При необходимости синхронизации с pyproject.toml
REASON:
  - Main dependency list для проекта
  - Используется CI/CD
  - Критично для установки окружения
  - ✅ Проверить синхронизацию с pyproject.toml
```

**Risk Level:** 🔴 CRITICAL  
**Priority:** CRITICAL

---

### 📄 7. .env.example

**Dependency Scan:**
- 🔗 Template для создания .env
- ⚠️ **ПОТЕНЦИАЛЬНЫЙ КОНФЛИКТ** с services/ingest/.env.example

**Конкретная операция:**
```bash
UPDATE: .env.example
ACTION: Синхронизировать с services/ingest/.env.example
REASON:
  - Root environment template
  - Может не включать все переменные из service-specific .env
VERIFY:
  - Все AI_* переменные присутствуют
  - Database credentials
  - API keys placeholders
CROSS-REFERENCE: services/ingest/.env.example
```

**Risk Level:** 🟡 MEDIUM  
**Priority:** MEDIUM

---

### 📄 8. eaip_full_skeleton/services/ingest/.env.example

**Dependency Scan:**
- 🔗 Используется settings/ai_settings.py
- ⚠️ Потенциальный конфликт с root .env.example

**Конкретная операция:**
```bash
KEEP: services/ingest/.env.example
UPDATE: Добавить cross-reference в root .env.example
REASON:
  - Service-specific environment template
  - Документирует AI configuration
  - Более детальный чем root .env.example
DOCUMENT:
  - Различия с root .env.example
  - Какие переменные специфичны для ingest service
```

**Risk Level:** 🟡 MEDIUM  
**Priority:** HIGH

---

## ГРУППА 7: АРХИТЕКТУРНАЯ ДОКУМЕНТАЦИЯ (2 файла)

### 📄 9. docs/EAIP_ARCHITECTURE.md

**Dependency Scan:**
- ✅ REFERENCED в docs/EAIP_TZ.md (подтверждено анализом Группы 1)
- 🔗 Core architectural documentation

**Конкретная операция:**
```bash
KEEP: docs/EAIP_ARCHITECTURE.md
REASON:
  - Core architectural reference
  - Ссылается из EAIP_TZ.md
  - Essential for understanding system design
  - ❌ НЕ УДАЛЯТЬ - Referenced документ
```

**Risk Level:** 🟢 LOW  
**Priority:** CRITICAL

---

### 📄 10. docs/PROJECT_DOCUMENTATION.md

**Конкретная операция:**
```bash
KEEP: docs/PROJECT_DOCUMENTATION.md
REASON:
  - Main documentation hub
  - Navigation center для всей документации
  - Links to other critical docs
```

**Risk Level:** 🟢 LOW  
**Priority:** HIGH

---

## ГРУППА 8: РУКОВОДСТВА (2 файла)

### 📄 11. docs/SERVICES_STARTUP_GUIDE.md

**Conflict Detection:**
- ⚠️ **ПОТЕНЦИАЛЬНОЕ ПЕРЕСЕЧЕНИЕ** с docs/QUICK_START_ENERGY_PASSPORT.md

**Конкретная операция:**
```bash
KEEP: docs/SERVICES_STARTUP_GUIDE.md
VERIFY: Content overlap с QUICK_START_ENERGY_PASSPORT.md
REASON:
  - General service startup instructions
  - Covers all 7 microservices
  - May overlap with specific quick starts
ACTION: Если большое дублирование - рассмотреть MERGE
```

**Risk Level:** 🟢 LOW  
**Priority:** HIGH

---

### 📄 12. docs/QUICK_START_ENERGY_PASSPORT.md

**Конкретная операция:**
```bash
KEEP: docs/QUICK_START_ENERGY_PASSPORT.md
VERIFY: Content overlap с SERVICES_STARTUP_GUIDE.md
REASON:
  - Feature-specific quick start (energy passport)
  - More focused than general guide
  - Different audience than SERVICES_STARTUP_GUIDE
```

**Risk Level:** 🟢 LOW  
**Priority:** MEDIUM

---

## ГРУППА 9: DATABASE PLANNING (2 файла)

### 📄 13. docs/DATABASE_CONSOLIDATION_PLAN.md

**Dependency Scan:**
- 🔗 Links to docs/MIGRATION_CHECKLIST.md
- 🔗 References services/ingest/database.py

**Конкретная операция:**
```bash
KEEP: docs/DATABASE_CONSOLIDATION_PLAN.md
UPDATE: Status as migration progresses
REASON:
  - Database architecture planning document
  - Important for future refactoring
  - Связан с MIGRATION_CHECKLIST.md
ACTION: Update completion status regularly
```

**Risk Level:** 🟡 MEDIUM  
**Priority:** HIGH

---

### 📄 14. docs/MIGRATION_CHECKLIST.md

**Dependency Scan:**
- 🔗 Tracks DATABASE_CONSOLIDATION_PLAN.md progress
- Recent (05.12.2025) - актуальный

**Конкретная операция:**
```bash
KEEP: docs/MIGRATION_CHECKLIST.md
UPDATE: Mark completed tasks
REASON:
  - Active task tracking document
  - Recent (05.12.2025)
  - Tracks database consolidation progress
ACTION: Update regularly as tasks complete
```

**Risk Level:** 🟡 MEDIUM  
**Priority:** HIGH

---

## ГРУППА 10: SERVICE ENTRY POINTS (3 файла)

### 📄 15. services/analytics/main.py

**Dependency Scan:**
- ✅ Standalone microservice (1.1 KB)
- 🔗 Запускается через docker-compose.yml

**Конкретная операция:**
```bash
KEEP: services/analytics/main.py
REASON:
  - Analytics microservice entry point
  - Standalone service - minimal dependencies
  - Small file (1.1 KB) - simple service
```

**Risk Level:** 🟡 MEDIUM  
**Priority:** MEDIUM

---

### 📄 16. services/gateway-auth/main.py

**Dependency Scan:**
- 🔴 **SECURITY-CRITICAL** - authentication gateway
- 🔗 First service in docker-compose (port 8000)

**Конкретная операция:**
```bash
KEEP: services/gateway-auth/main.py
REASON:
  - Authentication gateway service
  - 🔴 SECURITY-CRITICAL component
  - ❌ ANY CHANGES REQUIRE SECURITY REVIEW
  - Entry point for all authenticated requests
```

**Risk Level:** 🔴 CRITICAL  
**Priority:** CRITICAL

---

### 📄 17. services/validate/main.py

**Конкретная операция:**
```bash
KEEP: services/validate/main.py
REASON:
  - Validation microservice entry point
  - Data validation logic
  - Standalone service (port 8002)
```

**Risk Level:** 🟡 MEDIUM  
**Priority:** HIGH

---

## ГРУППА 11: API & QUALITY DOCS (5 файлов)

### 📄 18. docs/API_DOCUMENTATION.md

**Конкретная операция:**
```bash
UPDATE: docs/API_DOCUMENTATION.md
ACTION: Verify sync with actual endpoints
REASON:
  - API reference documentation
  - Must stay in sync with services/*/main.py
  - Review all endpoints
VERIFY:
  - All 7 microservices endpoints documented
  - Request/response schemas up to date
  - Authentication requirements current
```

**Risk Level:** 🟢 LOW  
**Priority:** HIGH

---

### 📄 19. docs/TECHNICAL_DEBT.md

**Конкретная операция:**
```bash
UPDATE: docs/TECHNICAL_DEBT.md
ACTION: Review and update debt items
REASON:
  - Living document for tracking technical debt
  - Should be updated as debt is resolved
  - Add new debt items as discovered
ACTIONS:
  - Mark resolved items as complete
  - Add debt from Wave 1 analysis
  - Prioritize remaining debt
```

**Risk Level:** 🟢 LOW  
**Priority:** MEDIUM

---

### 📄 20. docs/CODE_QUALITY_CHECKS.md

**Dependency Scan:**
- ✅ REFERENCED в docs/EAIP_TZ.md (confirmed)
- 🔗 Links to tools/check_*.py scripts

**Конкретная операция:**
```bash
KEEP: docs/CODE_QUALITY_CHECKS.md
REASON:
  - Code quality standards document
  - Referenced by EAIP_TZ.md (critical dependency)
  - Defines quality procedures
  - ❌ DO NOT DELETE - Referenced document
```

**Risk Level:** 🟢 LOW  
**Priority:** HIGH

---

### 📄 21. services/ingest/models/schemas.py

**Dependency Scan:**
- 🔴 **CRITICAL IMPORT** by services/ingest/main.py
- 📦 Contains: ValidateRequest, EnterpriseCreate, EditablePayload
- ✅ Confirmed in Group 12 analysis

**Конкретная операция:**
```bash
KEEP: services/ingest/models/schemas.py
REASON:
  - 🔴 CRITICAL: Imported by main.py
  - Pydantic models for API
  - ValidateRequest, EnterpriseCreate, EditablePayload
  - ❌ DO NOT MODIFY without API compatibility testing
  - ❌ DO NOT MOVE - will break imports in main.py
STATUS: Already analyzed in Group 12 - confirmed CRITICAL
```

**Risk Level:** 🔴 CRITICAL  
**Priority:** CRITICAL

---

### 📄 22. services/ingest/database.py

**Dependency Scan:**
- 🔴 **CRITICAL** - all database operations
- 🔗 Referenced in DATABASE_CONSOLIDATION_PLAN.md
- 🔗 Imported by main.py

**Конкретная операция:**
```bash
KEEP: services/ingest/database.py
REASON:
  - 🔴 CRITICAL: Database layer module
  - All DB operations go through this file
  - Referenced in consolidation planning docs
  - ❌ CHANGES REQUIRE FULL INTEGRATION TESTING
  - ❌ DO NOT REFACTOR without comprehensive test coverage
```

**Risk Level:** 🔴 CRITICAL  
**Priority:** CRITICAL

---

## СВОДНАЯ СТАТИСТИКА 22 ФАЙЛОВ:

| Операция | Количество | Файлы |
|----------|------------|-------|
| **KEEP** | 18 | Большинство критических файлов |
| **UPDATE** | 4 | pyproject.toml, .env.example, API_DOCUMENTATION.md, TECHNICAL_DEBT.md |
| **DOCUMENT ABSENCE** | 1 | docker-compose.dev.yml (не существует) |
| **VERIFY OVERLAP** | 2 | SERVICES_STARTUP_GUIDE + QUICK_START (пересечение?) |

### По Risk Level:

| Risk | Количество | Примеры |
|------|------------|---------|
| 🔴 CRITICAL | 7 | tests.yml, docker-compose.yml, requirements.txt, gateway-auth, schemas.py, database.py |
| 🟡 MEDIUM | 9 | ocr.yml, pyproject.toml, .env files, service entry points |
| 🟢 LOW | 6 | Documentation files |

### По Priority:

| Priority | Количество |
|----------|------------|
| CRITICAL | 9 |
| HIGH | 10 |
| MEDIUM | 3 |

---

## КОНФЛИКТЫ ОБНАРУЖЕННЫЕ:

### КОНФЛИКТ 5.1: pyproject.toml vs requirements.txt
**Тип:** Потенциальная несинхронизация зависимостей  
**Action:** UPDATE pyproject.toml для синхронизации

### КОНФЛИКТ 5.2: .env.example (root vs service)
**Тип:** Дублирование конфигурации  
**Action:** UPDATE для cross-reference

### КОНФЛИКТ 5.3: SERVICES_STARTUP_GUIDE vs QUICK_START_ENERGY_PASSPORT
**Тип:** Потенциальное дублирование содержания  
**Action:** VERIFY overlap

### КОНФЛИКТ 5.4: docker-compose.dev.yml
**Тип:** Отсутствующий файл  
**Action:** DOCUMENT ABSENCE, удалить из списков

---

## ИТОГО ПО WAVE 1 (50 ФАЙЛОВ):

### Проанализировано:
- **Группы 1-4, 13:** 28 файлов
- **Группы 5-12:** 22 файла
- **ВСЕГО:** 50 файлов из 80 Wave 1

### Статистика операций (50 файлов):

| Операция | Groups 1-4,13 | Groups 5-12 | Всего |
|----------|---------------|-------------|-------|
| KEEP | 13 | 18 | 31 |
| DELETE | 5 | 0 | 5 |
| MOVE | 7 | 0 | 7 |
| UPDATE | 1 | 4 | 5 |
| CREATE | 1 | 0 | 1 |
| VERIFY/DOCUMENT | 2 | 3 | 5 |

### Критические файлы:
- **CRITICAL (DO NOT TOUCH):** 16 файлов
- **HIGH PRIORITY:** 20 файлов
- **MEDIUM/LOW:** 14 файлов

---

**Дата завершения:** 11 декабря 2025  
**Статус:** ✅ 50 файлов проанализировано, готово к handover
