# CRITICAL FILES LIST - DO NOT MODIFY
## EAIP Project

**Date:** 11 December 2025  
**Total Critical:** 16 files

---

## 🔴 TIER 1: ABSOLUTELY CRITICAL (Infrastructure)

### CI/CD & Deployment
1. `.github/workflows/tests.yml`
   - **Why Critical:** Automated testing pipeline
   - **Protection:** Any changes break CI/CD
   - **Dependencies:** All test scripts, fixtures

2. `eaip_full_skeleton/infra/docker-compose.yml`
   - **Why Critical:** Production orchestration, 7 microservices
   - **Protection:** Deployment will fail
   - **Dependencies:** All services/*/Dockerfile, .env

3. `requirements.txt`
   - **Why Critical:** Main dependency list for entire project
   - **Protection:** Environment setup fails
   - **Dependencies:** CI/CD, all Python modules

---

## 🔴 TIER 2: CODE CRITICAL (Core Modules)

### Main Services
4. `services/ingest/main.py` (204.7 KB)
   - **Why Critical:** Main data processing service
   - **Imports:** 18 project modules
   - **Protection:** System core, DO NOT refactor without tests

5. `services/ingest/models/schemas.py`
   - **Why Critical:** Pydantic models for API
   - **Imported by:** main.py
   - **Contains:** ValidateRequest, EnterpriseCreate, EditablePayload
   - **Protection:** API breaks if modified

6. `services/ingest/database.py`
   - **Why Critical:** All database operations
   - **Imported by:** main.py, multiple modules
   - **Protection:** Data layer, full testing required

7. `services/ingest/utils/energy_aggregator.py` (104.6 KB)
   - **Why Critical:** 6 functions used by main.py
   - **Protection:** Business logic core

### Security
8. `services/gateway-auth/main.py`
   - **Why Critical:** Authentication gateway
   - **Protection:** SECURITY REVIEW REQUIRED for any change

---

## 🔴 TIER 3: CONFIGURATION CRITICAL

9. `pyproject.toml`
   - **Why Critical:** Python project configuration
   - **Dependencies:** requirements.txt sync needed

10. `.env.example` (root)
    - **Why Critical:** Environment template
    - **Cross-ref:** services/ingest/.env.example

11. `services/ingest/.env.example`
    - **Why Critical:** AI configuration template
    - **Dependencies:** settings/ai_settings.py

12. `config/ocr.yml`
    - **Why Critical:** OCR processing config
    - **Dependencies:** tools/ocr_*.py

---

## 🔴 TIER 4: DOCUMENTATION CRITICAL (Referenced)

13. `docs/EAIP_TZ.md`
    - **Why Critical:** Main technical specification
    - **References:** EAIP_ARCHITECTURE.md, CODE_QUALITY_CHECKS.md
    - **Protection:** Referenced by other docs

14. `docs/EAIP_ARCHITECTURE.md`
    - **Why Critical:** Core architecture doc
    - **Referenced by:** EAIP_TZ.md
    - **Protection:** DO NOT DELETE

15. `docs/CODE_QUALITY_CHECKS.md`
    - **Why Critical:** Quality standards
    - **Referenced by:** EAIP_TZ.md
    - **Protection:** DO NOT DELETE

---

## 🔴 TIER 5: SERVICE ENTRY POINTS

16. `services/*/main.py` (analytics, validate, reports, management, recommend)
    - **Why Critical:** Microservice entry points
    - **Protection:** Service-specific logic

---

## MODIFICATION REQUIREMENTS

### Before modifying ANY critical file:

**CRITICAL (Tier 1-2):**
1. ✅ Full backup
2. ✅ Run all tests
3. ✅ Code review (2+ reviewers)
4. ✅ Staging deployment test
5. ✅ Rollback plan ready
6. ✅ Team notification

**CONFIGURATION (Tier 3):**
1. ✅ Backup
2. ✅ Test in dev environment
3. ✅ Validate all dependent services
4. ✅ Update documentation

**DOCUMENTATION (Tier 4):**
1. ✅ Check all references
2. ✅ Update cross-references
3. ✅ Version in git

---

## CONTACT FOR CHANGES

**Infrastructure (Tier 1):** DevOps Lead  
**Core Code (Tier 2):** Tech Lead + Senior Developer  
**Configuration (Tier 3):** Senior Developer  
**Documentation (Tier 4):** Tech Writer + Developer

---

**Last Updated:** 11 December 2025  
**Analyst:** Claude Sonnet 4.5 (Wave 1)
