# EAIP — Full Skeleton (Cursor-ready)

Microservices (FastAPI), docker-compose, client placeholder, and Cursor config.

## Quick start (compose)
```bash
cp .env.example .env
docker compose up --build
```
Services: http://localhost:8000..8006 `/health` endpoints.

## Manual dev
Activate venv per service and run uvicorn (see each service README).

## PDF Generation

The reports service generates PDF files with full Cyrillic support using DejaVuSans TTF font.

### Generate Demo PDF

```powershell
cd infra
docker compose build reports
docker compose up -d reports
pwsh -ExecutionPolicy Bypass -File .\audit_demo.ps1
```

The script will:
1. Ingest demo data
2. Validate it
3. Run analytics forecast
4. Generate recommendations
5. Create PDF report with Cyrillic text support

Output: `infra/passport_demo1_full.pdf`

### Features

- ✅ Full Cyrillic character support in PDF documents
- ✅ Automatic font registration at service startup
- ✅ Startup readiness check for reliable script execution
- ✅ Bold text support via font family registration

See [CHANGELOG.md](CHANGELOG.md) for detailed technical information.
