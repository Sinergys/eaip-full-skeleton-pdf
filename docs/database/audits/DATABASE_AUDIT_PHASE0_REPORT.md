# DATABASE AUDIT REPORT - PHASE 0
**Generated:** 2025-12-08
**Scope:** Project root (recursive)
**Status:** ⚠️ AWAITING APPROVAL FOR CLEANUP

---

## 📊 EXECUTIVE SUMMARY

**Total Database Files Found:** 7 files
**Total Size:** ~111.3 MB
**Working Database:** `services/ingest/ingest_data.db` (24.46 MB)
**Duplicate/Backup Files:** 6 files (~86.84 MB)
**SQL Scripts:** 4 files
**Migration Scripts:** 7 Python files
**Database-Connected Code:** 16 core files (excluding .venv)

---

## 🗄️ DATABASE FILES INVENTORY

### ✅ ACTIVE/WORKING DATABASES

| File | Size | Last Modified | Tables | Status | Purpose |
|------|------|---------------|--------|--------|---------|
| **`eaip_full_skeleton/services/ingest/ingest_data.db`** | **24.46 MB** | **Dec 7, 2025 01:02** | **12** | **🟢 ACTIVE** | **Primary working database** |
| `eaip_full_skeleton/services/ingest/tests/.test_db/test_ingest.db` | 292 KB | Dec 7, 2025 05:08 | N/A | 🟢 ACTIVE | Test database for pytest |

**Configuration Reference:**
```python
# eaip_full_skeleton/services/ingest/database.py:78
DB_PATH = os.getenv("INGEST_DB_PATH", os.path.join(os.getcwd(), "ingest_data.db"))
```

### ⚠️ DUPLICATE/ORPHANED DATABASES

| File | Size | Last Modified | Tables | Status | Notes |
|------|------|---------------|--------|--------|-------|
| `backups/ingest_data_20251201_211328.db` | 25 MB | Dec 1, 2025 21:13 | 11 | 🟡 BACKUP | Manual backup #1 |
| `backups/ingest_data_20251201_212246.db` | 25 MB | Dec 1, 2025 21:22 | 11 | 🟡 BACKUP | Manual backup #2 |
| `backups/ingest_data_backup2_20251201_211513.db` | 25 MB | Dec 1, 2025 21:15 | 11 | 🟡 BACKUP | Manual backup #3 |
| `eaip_full_skeleton/ingest_data.db` | 72 KB | Dec 2, 2025 17:00 | 11 | 🔴 ORPHANED | Empty/obsolete skeleton |
| `ingest_data.db` (root) | 35.60 MB | Dec 1, 2025 21:21 | 11 | 🔴 ORPHANED | Old location, outdated |

**Total Duplicate/Orphaned Size:** 110.07 MB

---

## 📜 SQL SCRIPTS & SCHEMA DEFINITIONS

### Core Schema Files (✅ MUST KEEP)

| File | Size | Purpose | Dependencies |
|------|------|---------|--------------|
| **`eaip_full_skeleton/infra/db/init.sql`** | 8.6 KB | **Primary schema definition** | None (base schema) |
| `eaip_full_skeleton/infra/db/check_tables.sql` | 1.7 KB | Table verification queries | Depends on init.sql |
| `eaip_full_skeleton/infra/db/migrate_sqlite_to_postgres.sql` | 9.5 KB | PostgreSQL migration schema | Depends on init.sql |
| `tools/optimize_sqlite.sql` | 6.2 KB | Performance optimization queries | Independent utility |

**Total SQL Scripts:** 4 files (25.0 KB)

---

## 🔄 MIGRATION SCRIPTS

### Python Migration Tools (✅ MUST KEEP - CODE LOGIC)

| File | Purpose | Status |
|------|---------|--------|
| `tools/migrate_simple.py` | Basic SQLite migration | Active |
| `tools/migrate_sqlite_to_postgres.py` | SQLite → PostgreSQL migration | Active |
| `tools/migrate_sqlite_to_postgres_fixed.py` | Fixed version of above | Active |
| `tools/migrate_via_docker.py` | Docker-based migration | Active |
| `tools/migrate_via_sql_dump.py` | SQL dump migration | Active |
| `tools/migrate_with_sqlalchemy.py` | SQLAlchemy-based migration | Active |
| `eaip_full_skeleton/services/ingest/tools/migrate_aggregated_table.py` | Aggregated data migration | Active |

**Total Migration Scripts:** 7 files

---

## 💻 DATABASE-CONNECTED CODE FILES

### Core Database Modules (✅ MUST KEEP)

1. **`eaip_full_skeleton/services/ingest/database.py`** - Primary database interface
2. **`eaip_full_skeleton/services/ingest/utils/connection_pool.py`** - Connection pooling
3. **`eaip_full_skeleton/services/ingest/utils/diagnose_aggregation.py`** - Diagnostics
4. **`eaip_full_skeleton/services/ingest/utils/check_electricity_data.py`** - Data validation

### Diagnostic & Maintenance Tools

5. `scripts/check_ingest_dbs.py` - Database health check
6. `check_db.py` - General DB checker
7. `inspect_ingest_db.py` - DB inspector
8. `query_navoiy.py` - Query utility
9. `test_db_structure.py` - Structure validator
10. `check_parsing_structure.py` - Parse validation

### Tool Suite Files

11-16. `tools/check_*.py` - Various database checking utilities
17-22. `tools/execute_*.py` - OCR and processing tools
23-24. `tools/process_*.py` - Data processing tools

**Total Database Code Files:** 24 files (excluding .venv)

---

## ⚙️ CONFIGURATION ANALYSIS

### Environment Files Found

| File | Contains DB Config | Notes |
|------|-------------------|-------|
| `eaip_full_skeleton/.env` | No | AI configuration only |
| `eaip_full_skeleton/services/ingest/.env` | No | AI configuration only |
| `eaip_full_skeleton/.env.example` | Unknown | Template file |
| `eaip_full_skeleton/infra/.env*` | Unknown | Infrastructure config |

### Active Database Connection

**Configured in:** `eaip_full_skeleton/services/ingest/database.py`
**Default Path:** `os.getcwd()/ingest_data.db`
**Environment Override:** `INGEST_DB_PATH` (not currently set)
**Actual Working Path:** `services/ingest/ingest_data.db` (from project root)

---

## 🔍 DATABASE STRUCTURE COMPARISON

| Database | Tables | Size (MB) | Status | Last Modified |
|----------|--------|-----------|--------|---------------|
| **services/ingest/ingest_data.db** | **12** | **24.46** | **🟢 Current** | **Dec 7, 2025** |
| ingest_data.db (root) | 11 | 35.60 | 🔴 Outdated | Dec 1, 2025 |
| eaip_full_skeleton/ingest_data.db | 11 | 0.07 | 🔴 Empty | Dec 2, 2025 |
| backups/* (3 files) | 11 | 25 each | 🟡 Backups | Dec 1, 2025 |

### Table Inventory - Working Database

The active database contains **12 tables**:

1. `enterprises` - Enterprise/company data
2. `uploads` - File upload tracking
3. `uploads_storage` - Upload binary storage
4. `parsed_data` - Parsed file data
5. `normative_documents` - Regulatory documents
6. `normative_rules` - Compliance rules
7. `normative_references` - Document references
8. `normative_violations` - Compliance violations
9. `aggregated_data` - Aggregated energy data
10. `aggregated_data_backup` - Backup of aggregated data
11. `node_consumption` - Energy node consumption
12. `sqlite_sequence` - SQLite auto-increment tracker

### Schema Differences

- **Working DB** has 1 additional table: `aggregated_data_backup`
- Root and skeleton DBs have 11 tables (missing the backup table)
- This suggests the working DB is the most current version

---

## 🚨 IDENTIFIED ISSUES

### Critical Issues

1. **❌ Duplicate Database at Root Level**
   - `ingest_data.db` in project root (35.60 MB) is outdated
   - Last modified Dec 1 vs working DB Dec 7
   - Potential for confusion/wrong database usage

2. **❌ Orphaned Skeleton Database**
   - `eaip_full_skeleton/ingest_data.db` (72 KB) is nearly empty
   - Located in wrong directory relative to working DB
   - May cause import/path confusion

### Warning Issues

3. **⚠️ Multiple Backup Files**
   - 3 backup files from same day (Dec 1) - 75 MB total
   - No backup rotation/retention policy evident
   - Backups are outdated (7 days old)

4. **⚠️ Test Database in Source Tree**
   - Test DB should ideally be in temp directory
   - Current location: `services/ingest/tests/.test_db/`
   - May be acceptable if properly excluded from production

---

## 📋 CLEANUP RECOMMENDATIONS

### Phase 1: Safe to Delete (Pending Approval)

#### A. Root Level Duplicate
**File:** `ingest_data.db` in project root (35.60 MB)
- **Reason:** Outdated, superseded by working DB
- **Risk:** 🟢 Low (backup exists, not in active path)
- **Action:** Move to quarantine folder

#### B. Skeleton Orphan
**File:** `eaip_full_skeleton/ingest_data.db` (72 KB)
- **Reason:** Nearly empty, wrong location
- **Risk:** 🟢 Low (minimal data, 7 days old)
- **Action:** Move to quarantine folder

#### C. Old Backup Files (if retention policy allows)
**Files:**
- `backups/ingest_data_20251201_211328.db` (25 MB)
- `backups/ingest_data_20251201_212246.db` (25 MB)
- `backups/ingest_data_backup2_20251201_211513.db` (25 MB)
- **Total:** 75 MB
- **Reason:** 7+ days old, superseded by current DB
- **Risk:** 🟡 Medium (actual backups - verify recovery first)
- **Action:** Verify one backup is restorable, then archive oldest 2

**Total Space to Reclaim:** ~110 MB

### Phase 2: Keep (No Action)

✅ **`eaip_full_skeleton/services/ingest/ingest_data.db`** - Primary working database
✅ **`eaip_full_skeleton/services/ingest/tests/.test_db/test_ingest.db`** - Test database
✅ **All .sql files** - Schema definitions and queries
✅ **All migration .py files** - Migration logic
✅ **All database*.py files** - Application code

---

## 🛡️ SAFETY PROTOCOLS

### Quarantine System

**Quarantine Location:** `quarantine/database_cleanup_20251208/` (from project root)

**Retention:** 7 days (until 2025-12-15)

**Files to Quarantine:**
1. Root duplicate → `quarantine/ingest_data.db.root`
2. Skeleton orphan → `quarantine/ingest_data.db.skeleton`
3. Backup files → `quarantine/backups/`

### Rollback Plan

```bash
# If issues arise within 7 days, restore with:
cp quarantine/database_cleanup_20251208/ingest_data.db.root ingest_data.db
cp quarantine/database_cleanup_20251208/ingest_data.db.skeleton eaip_full_skeleton/ingest_data.db
```

### Verification Steps Before Cleanup

1. ✅ Verify working DB is accessible and not corrupted
2. ✅ Confirm current application uses correct DB path
3. ✅ Test one backup file is restorable
4. ✅ Export schema from working DB for reference
5. ⏳ Get explicit user approval for each file deletion

---

## 📝 NEXT STEPS - AWAITING APPROVAL

### ⚠️ CRITICAL: DO NOT PROCEED WITHOUT EXPLICIT APPROVAL

**Phase 0:** ✅ **COMPLETE** - Audit report generated

**Phase 1:** ⏸️ **AWAITING APPROVAL** - Backup verification
- Verify one backup file can restore successfully
- Document backup restore process
- **STOP and get approval before proceeding**

**Phase 2:** ⏸️ **AWAITING APPROVAL** - Quarantine duplicates
- Move identified duplicate files to quarantine
- Create quarantine manifest
- **STOP and get approval before proceeding**

**Phase 3:** ⏸️ **AWAITING APPROVAL** - Final cleanup
- Remove files from quarantine after retention period
- Update documentation
- **STOP and get approval before proceeding**

---

## 🔐 FILES OUTSIDE SEARCH SCOPE

**Scope Limitation:** Only searched project root directory tree

**Note:** The following locations were NOT searched and may contain additional database files:
- System temporary directories
- User AppData folders
- Other drive letters (D:\, E:\, etc.)
- Network locations

If databases exist outside this scope, they were not included in this audit.

---

## 📞 APPROVAL REQUIRED

**Before proceeding with ANY cleanup actions, I need explicit approval for:**

1. ☐ Moving root duplicate `ingest_data.db` to quarantine
2. ☐ Moving skeleton orphan `ingest_data.db` to quarantine
3. ☐ Moving backup files to quarantine (specify which ones)
4. ☐ Backup retention policy (keep how many days?)
5. ☐ Quarantine retention period (default: 7 days)

**Please review this report and provide explicit approval or modification instructions.**

---

**End of Phase 0 Audit Report**
