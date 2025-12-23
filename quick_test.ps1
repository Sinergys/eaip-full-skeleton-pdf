# Quick test runner
$ErrorActionPreference = "Stop"
Set-Location "C:\eaip\eaip_full_skeleton\services\ingest"
$env:INGEST_DB_PATH = "tests\.test_db\test_ingest.db"
$env:SYSTEM_MODE = "debug"
& "C:\eaip\.venv\Scripts\pytest.exe" -v tests/test_api_e2e.py --tb=short
