# AGENTS.md

## Project Overview

**EAIP (Energy Audit and Information Platform)** is a comprehensive microservices-based system for automated energy auditing and passport generation in Uzbekistan. The system processes uploaded energy consumption files (Excel, PDF, Word, images), performs intelligent analysis, and generates standardized energy passports compliant with Uzbek regulatory requirements (ПКМ №690).

## Architecture

### Microservices Stack

**Infrastructure Ports:** 
- **gateway-auth** (8000): Authentication and API gateway
- **ingest** (8001): File upload, parsing, OCR, AI classification, aggregation
- **validate** (8002): Data validation and compliance checking
- **analytics** (8003): Trend analysis and forecasting
- **recommend** (8004): Energy efficiency recommendations
- **reports** (8005): PDF/Word report generation
- **management** (8006): System administration

**Storage:**
- **PostgreSQL 15**: Primary database for entities, uploads, and energy resource data
- **Redis 7**: Caching and session management
- **MinIO**: Object storage for uploaded files and generated reports

**Communication:** HTTP REST between services, orchestrated via Docker Compose

### Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **Excel/Word Processing:** openpyxl, python-docx
- **PDF Processing:** pdfplumber, PyMuPDF, pytesseract (OCR), tabula-py (table extraction)
- **AI/LLM Integration:** OpenAI API, DeepSeek API, Anthropic Claude (configurable)
- **Image Processing:** Pillow, pdf2image, Gemini Vision OCR
- **Data Science:** pandas, numpy
- **Containerization:** Docker & Docker Compose
- **Testing:** pytest

## Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Java Runtime Environment 11+ (for Tabula PDF table extraction)
- Tesseract OCR (optional, for scanned PDF/image text recognition)
- Poppler utilities (optional, for PDF to image conversion)

### Quick Start

```bash
# 1. Copy environment config
cp .env.example .env

# 2. Build and start all services
docker compose -f infra/docker-compose.yml up --build

# 3. Access services
# - Ingest web UI: http://localhost:8001/web/upload
# - Gateway: http://localhost:8000/health
# - All services have /health endpoints
```

### Development Setup (Manual)

```bash
# Per service:
cd services/<service>
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Run development server (example: ingest)
cd services/ingest
uvicorn main:app --reload --port 8001
```

## Commands

- **Build:** `docker compose -f infra/docker-compose.yml build`
- **Start:** `docker compose -f infra/docker-compose.yml up`
- **Lint:** `ruff check services/ tests/` (if ruff installed)
- **Test:** `pytest tests/ -v` or `pytest services/<service>/tests/ -v`
- **Dev server:** `cd services/ingest && uvicorn main:app --reload --port 8001`

## Key Modules & Features

### 1. Energy Aggregator (`services/ingest/utils/energy_aggregator.py`)

**Purpose:** Processes uploaded Excel files containing energy consumption data and aggregates them into standardized quarterly/annual formats.

**Capabilities:**
- Detects and parses multiple resource types: electricity, gas, heat, water, fuel, coal
- Handles both single-resource files (e.g., `gaz.xlsx`) and multi-resource files (e.g., `pererashod.xlsx`)
- Extracts monthly consumption data and aggregates by quarters (Q1-Q4)
- Normalizes Uzbek/Russian month names and consumption categories
- Outputs standardized JSON for database import and template filling
- Saves aggregated data to `AGGREGATED_DIR` (default: `/data/inbox/aggregated/`)

**Key Functions:**
- `aggregate_energy_data(file_path)`: Main aggregation entry point
- `aggregate_from_db_json(raw_json)`: Aggregates from pre-parsed database JSON
- `aggregate_usage_categories(file_path)`: Extracts usage categories for validation
- `distribute_categories_by_quarter()`: Maps categories to quarterly periods
- `should_aggregate_file(filename)`: Determines if file contains energy data

**Detection Logic:**
- Sheet names: `ГАЗ`, `СУВ`, `электр`, `ТОПЛИВО`, etc.
- Filename keywords: `потребление`, `газ`, `отопл`, `voda`, `kotel`
- Header heuristics for month columns and consumption units

### 2. Formula Restoration (`services/ingest/utils/ai_formula_restorer.py`)

**Purpose:** Automatically detects and restores broken Excel formulas (especially `#REF!` errors) in energy passport templates.

**Capabilities:**
- Scans all sheets for cells containing `#REF!` errors
- Analyzes neighboring cell patterns to infer correct formulas
- Restores cross-sheet references (e.g., `='Структура пр 2'!AM14`)
- Optional AI-assisted restoration for complex cases
- Logs restoration success and details

**Use Case:** Energy passport templates often have formulas referencing dynamically filled sheets. When data sources change, these become `#REF!` errors. This module restores them based on structural patterns.

**Integration Points:**
- Called in `main.py` after template filling
- Used in `tools/fill_energy_passport.py` during generation
- Flag: `HAS_FORMULA_RESTORER` controls availability

**Key Functions:**
- `restore_formulas_in_file(workbook)`: Scans and restores all broken formulas
- `restore_ref_error(workbook, sheet_name, cell_coordinate, formula)`: Restores specific #REF! error
- `_restore_by_pattern()`: Pattern-based inference from neighbors

### 3. Enterprise Classifier (`services/ingest/utils/enterprise_classifier.py`)

**Purpose:** Automatically determines enterprise type (industry sector, product type) based on uploaded file content and naming patterns.

**Capabilities:**
- Analyzes filenames and content to identify industry: energy, chemical, metallurgy, oil refining, food, manufacturing
- Distinguishes between enterprise's own data vs. consumer/customer data
- Weighted scoring: prioritizes files about the enterprise itself over customer files
- Returns industry, enterprise type, and product type classifications
- Confidence-based decisions with fallback to manual selection

**Use Case:** When users upload files for a new enterprise, the system can suggest the enterprise type instead of requiring manual input.

**Key Functions:**
- `analyze_filenames(filenames, enterprise_name)`: Analyzes file naming patterns
- `analyze_content(raw_json)`: Analyzes parsed file content
- `classify_enterprise(filenames, raw_json)`: Full classification with confidence

**Detection Keywords:**
- Energy: `энерг`, `электро`, `ТЭС`, `ГЭС`
- Chemical: `хим`, `азот`, `аммиак`, `удобрен`
- Metallurgy: `металл`, `сталь`, `прокат`
- Oil: `нефть`, `бензин`, `дизель`

### 4. PDF Validators (`services/ingest/utils/pdf_classifier.py` & related)

**Purpose:** Intelligent classification and validation of PDF documents for energy audits.

**Capabilities:**
- Classifies PDFs into: balance acts, consumption tables, calculations, contracts, protocols
- Detects scanned vs. native PDFs
- Triggers OCR when needed (Tesseract + Poppler)
- Extracts tables using multiple strategies: pdfplumber, tabula-py, PyMuPDF
- Handles Cyrillic text and Uzbek/Russian documents
- Validates table structure and data completeness

**OCR Pipeline:**
1. Detect if PDF is scanned (text extraction yields < 100 characters)
2. Convert pages to images (pdf2image + poppler)
3. Apply Tesseract OCR with Uzbek/Russian language packs
4. Extract tables from OCR-enhanced text
5. Fallback to Gemini Vision API for complex documents

**Integration:**
- `file_parser.py` calls PDF parsers based on file extension
- Progress tracking via `ProcessingStage.OCR`
- Results include `ocr_used`, `is_scanned`, `ocr_success` flags

### 5. Word Validators (`services/ingest/utils/word_readiness_validator.py`)

**Purpose:** Validates Word documents and checks readiness for energy passport generation.

**Capabilities:**
- Detects "ready reports" (pre-filled Word audit reports)
- Validates section completeness against ПКМ №690 requirements
- Checks for required data fields: enterprise info, resource data, calculations
- Returns readiness score (0.0-1.0) and missing sections
- Supports fallback to reference tables when data is incomplete

**ПКМ №690 Sections Validated:**
- Section 2: General enterprise information
- Section 3: Energy resource structure
- Section 4: Energy balance
- Section 5: Fuel consumption dynamics
- Section 6: Specific consumption rates
- Section 7: Energy efficiency measures

**Key Functions:**
- `validate_word_report_readiness(report_data)`: Full validation
- `can_generate_section(section_num, report_data)`: Per-section check
- Returns: `ready`, `completeness_score`, `missing_sections`, `warnings`

### 6. Intelligent Router (`services/ingest/utils/intelligent_router.py`)

**Purpose:** Central "brain" of the system that analyzes ANY uploaded file and determines optimal processing pipeline.

**Capabilities:**
- Fast analysis mode (2-3 sec): Quick classification
- Deep analysis mode (3-5 sec): Detailed routing with AI assistance
- Document type detection: energy passport, balance act, consumption table, calculation, contract, protocol
- Resource type detection: electricity, gas, water, heat, fuel, multiple resources
- Data type detection: meter readings, balance, tariffs, norms, consumption, production
- Period detection: monthly, quarterly, annual, multi-year
- Generates routing map with recommended processing modules and target tables

**Routing Map Output:**
```json
{
  "analysis": {
    "document_type": "balance_act",
    "resource_type": "electricity",
    "data_type": "meter_readings",
    "period": "monthly",
    "confidence": 0.92
  },
  "routing": {
    "primary_module": "balance_sheet_node_extractor",
    "target_tables": ["node_consumption", "aggregated_resources"],
    "processing_stages": ["parse", "validate", "aggregate", "import_db"]
  }
}
```

**Integration:**
- Called during file upload in `main.py`
- Stores routing_map in parsing_results and database
- Used by downstream services for intelligent processing

### 7. AI Content Classifier (`services/ingest/utils/ai_content_classifier.py`)

**Purpose:** LLM-powered content analysis for ambiguous or complex files.

**Capabilities:**
- Uses DeepSeek, OpenAI GPT-4, or Anthropic Claude (configurable)
- Analyzes file structure, headers, data patterns
- Returns resource type with confidence score
- Graceful fallback when AI unavailable
- Integrated into ResourceClassifier as secondary classification strategy

**Priority Flow:**
1. Rule-based classification (fast, deterministic)
2. AI classification (when rules uncertain)
3. Filename pattern analysis
4. Fallback to "other"

## Wave 1 Completion Status

**Date:** December 12, 2025  
**Status:** ✅ 80/80 files analyzed (100%)

### Summary

Wave 1 focused on auditing and organizing the codebase to establish a solid foundation for production deployment.

**Operations:**
- **KEEP:** 60 files (75%) - Core functionality maintained
- **MOVE:** 7 files - Reorganized for better structure
- **DELETE:** 6 files - Removed obsolete/duplicate code
- **UPDATE:** 5 files - Improved or refactored
- **CREATE:** 1 file - New required component

**Risk Levels:**
- **CRITICAL:** 20 files (protected, core infrastructure)
- **MEDIUM:** 35 files (important but refactorable)
- **LOW:** 24 files (documentation, scripts)

### Critical Files (Protected)

**Infrastructure (3):**
- `infra/docker-compose.yml`
- `.env.example`
- `services/*/requirements.txt`

**Core Services (7 main.py files):**
- `services/ingest/main.py` - Primary ingestion and routing logic
- `services/validate/main.py` - Data validation service
- `services/analytics/main.py` - Trend analysis
- `services/reports/main.py` - Report generation
- `services/recommend/main.py` - Recommendations engine
- `services/gateway-auth/main.py` - Authentication gateway
- `services/management/main.py` - System management

**Core Logic (10 modules):**
- `database.py` - Database operations
- `schemas.py` - Pydantic models
- `energy_aggregator.py` - Energy data aggregation (see Module #1)
- `ai_parser.py` - AI integration layer
- `file_parser.py` - Multi-format file parsing
- `readiness_validator.py` - Generation readiness checks
- `data_validator.py` - Data quality validation
- `intelligent_router.py` - Document routing (see Module #6)
- `energy_passport_calculations.py` - KPI calculations
- `ai_formula_restorer.py` - Formula restoration (see Module #2)

### Conflicts Resolved

1. ✅ `pyproject.toml` vs `requirements.txt` - Using requirements.txt consistently
2. ✅ `.env.example` - Root vs service-level configs clarified
3. ✅ `ai_config.py` vs `ai_settings.py` - Obsolete ai_config.py removed
4. ✅ Duplicate startup guides consolidated
5. ✅ Missing docker-compose.dev.yml noted for future creation

### Next Steps

- **Wave 2:** Audit 156 medium-priority files (documentation, utilities, tests)
- **Wave 3:** Audit 155 low-priority files (backups, logs, temporary scripts)
- Focus on test coverage expansion and performance optimization

## Development Priorities

### Completed (Wave 1)

✅ **AI Integration** (November 30, 2025)
- DeepSeek/OpenAI/Claude API support
- PDF Vision OCR
- AI content classification
- AI-enhanced table extraction

✅ **Enterprise Type Classification** (November 30, 2025)
- Automatic industry detection
- Content-based classification
- Weighted file analysis

✅ **Formula Restoration** (November 16, 2025)
- Automatic #REF! error detection
- Pattern-based restoration
- Cross-sheet reference fixing

✅ **Intelligent Document Routing** (December 2025)
- Universal file analysis
- Routing map generation
- Multi-strategy processing

✅ **PDF Table Extraction** (December 1, 2025)
- Tabula integration
- Java-based processing
- OCR fallback for scanned PDFs

✅ **Testing & QA** (December 1, 2025)
- Comprehensive energy passport validation
- Formula verification (1527 formulas tested)
- Detailed testing checklists

### In Progress

⏳ **Validation Service Enhancement**
- Currently: Stub implementation (always returns `passed: true`)
- Needed: Integration with data validators, compliance rules

⏳ **Analytics Service Development**
- Trend analysis algorithms
- Forecasting models
- Anomaly detection

⏳ **Recommendations Engine**
- Energy efficiency measure suggestions
- ROI calculations
- Regulatory compliance recommendations

### Upcoming (Post-Wave 1)

- Web interface improvements (React/Vue frontend)
- Real-time progress tracking with WebSockets
- Multi-user support and role-based access
- Batch processing for multiple files
- Report customization and templates
- Integration with external energy databases

## Technical Context for AI Agents

### Data Flow

1. **Upload** → User uploads files via web UI (`/web/upload`) or API (`/web/upload POST`)
2. **Parsing** → `file_parser.py` detects format and routes to specialized parsers
3. **Classification** → `IntelligentRouter` analyzes content and generates routing map
4. **Aggregation** → `energy_aggregator.py` extracts and normalizes energy data
5. **Specialized Parsing** → Equipment, nodes, envelope, balance acts processed
6. **Database Import** → Resources, nodes, consumption data stored in PostgreSQL
7. **Validation** → Data completeness and compliance checked
8. **Generation** → Energy passport template filled with aggregated data
9. **Formula Restoration** → Broken formulas detected and fixed
10. **Output** → Generated Excel/Word/PDF report saved and served

### Database Schema (Key Tables)

**enterprises**
- id, name, industry, enterprise_type, product_type

**uploads**
- id, batch_id (UUID), enterprise_id, filename, file_type, file_size, file_hash
- status (success/error/partial), parsing_summary (JSON)
- raw_json (full parsing results), editable_text
- created_at, parsed_updated_at

**resources**
- id, enterprise_id, batch_id, resource_type (electricity/gas/water/heat/fuel)
- period (Q1 2024, Q2 2024, etc.), consumption_value, unit, cost
- data_json (additional metadata)

**node_consumption**
- id, enterprise_id, batch_id, node_name
- period, active_energy_kwh, reactive_energy_kvarh, cost_sum
- data_json (TT coefficient, seal dates, notes)

### Environment Variables

**AI Configuration:**
```env
AI_ENABLED=true
AI_PROVIDER=deepseek  # or openai, anthropic
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
AI_PREFER_FOR_PDF=true
```

**Database:**
```env
POSTGRES_HOST=postgres
POSTGRES_USER=eaip
POSTGRES_PASSWORD=...
POSTGRES_DB=eaip_db
```

**Storage:**
```env
INBOX_DIR=/data/inbox
AGGREGATED_DIR=/data/inbox/aggregated
DATA_DIR=/data/inbox/temp
```

**Mode:**
```env
SYSTEM_MODE=debug  # or production
LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR
```

### Code Style & Conventions

- **Type hints:** Use Pydantic models for request/response schemas
- **Logging:** Use module-level loggers (`logger = logging.getLogger(__name__)`)
- **Error handling:** Graceful degradation with fallbacks
- **Comments:** Minimal; code should be self-documenting
- **Imports:** Standard library → third-party → local modules
- **Dependencies:** Check existing imports before adding new libraries
- **Async/await:** Not currently used (FastAPI handles async internally)
- **Testing:** pytest with fixtures in `tests/fixtures/`

### Common Patterns

**Service Structure:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Service Name", version="0.1.0")

@app.get("/health")
def health():
    return {"service": "service_name", "status": "ok"}

@app.post("/endpoint")
def endpoint_handler(payload: RequestModel):
    # Implementation
    return response_dict
```

**File Processing:**
```python
from pathlib import Path
from openpyxl import load_workbook

def process_file(file_path: str):
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    try:
        wb = load_workbook(file_path, data_only=True)
        # Process workbook
        return results
    except Exception as e:
        logger.exception(f"Error processing {file_path}")
        return None
```

**Database Operations:**
```python
import database

# Create
enterprise = database.get_or_create_enterprise("Enterprise Name")

# Read
upload = database.get_upload_by_batch(batch_id)
resources = database.get_resources_by_enterprise(enterprise_id)

# Import
imported = database.import_resource_to_db(
    enterprise_id=ent_id,
    batch_id=batch_id,
    resource_type="electricity",
    resource_data=aggregated_data
)
```

### Known Issues & Limitations

1. **Validation Service:** Currently stub implementation; needs real validation logic
2. **OCR Dependencies:** Tesseract and Poppler must be manually installed on host
3. **AI Rate Limits:** No built-in rate limiting for AI API calls
4. **Excel Headers:** Multi-row or merged cell headers can break column detection
5. **Language Detection:** Uzbek/Russian mixed content sometimes misclassified
6. **Large Files:** Files > 50MB rejected (configurable via MAX_FILE_SIZE)
7. **Concurrent Uploads:** Progress tracking may be unreliable for simultaneous uploads
8. **Formula Templates:** Limited to known patterns; complex custom formulas need AI

### Debugging Tips

**Check logs:**
```bash
docker compose -f infra/docker-compose.yml logs -f ingest
docker compose logs ingest | grep ERROR
```

**Inspect parsing results:**
```bash
curl http://localhost:8001/ingest/parse/{batch_id}
curl http://localhost:8001/api/batches/{batch_id}/canonical-debug
```

**Database queries:**
```bash
docker exec -it infra-postgres-1 psql -U eaip -d eaip_db
SELECT batch_id, filename, status FROM uploads ORDER BY created_at DESC LIMIT 10;
```

**Test endpoints:**
```bash
curl http://localhost:8001/health
curl http://localhost:8001/api/debug/extensions
```

## Additional Resources

- **README.md** - High-level project overview
- **WAVE1_COMPLETION_STATUS.md** - Detailed Wave 1 audit results
- **AI_INTEGRATION_DONE.md** - AI integration documentation
- **FORMULA_RESTORATION_COMPLETE.md** - Formula restoration details
- **P1_TASKS_COMPLETED.md** - Priority 1 task completion report
- **docs/EXCEL_PIPELINE_OVERVIEW.md** - Excel processing pipeline details
- **services/ingest/README.md** - Ingest service documentation
- **tests/README.md** - Testing guide

---

**Last Updated:** December 2025  
**Project Status:** Wave 1 Complete, Production Ready for Core Functionality  
**Next Milestone:** Wave 2 Audit & Validation Service Implementation
