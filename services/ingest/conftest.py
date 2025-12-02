import os
from pathlib import Path


def pytest_configure(config):
    """Ensure tests under services/ingest use the service DB by default.

    This is safe for local development and CI: tests will use
    eaip_full_skeleton/services/ingest/ingest_data.db if present.
    """
    ingest_root = Path(__file__).resolve().parent
    default_db = ingest_root / "ingest_data.db"

    # Ensure repo root (C:\eaip) is on sys.path so tests can import package modules
    import sys
    repo_root = ingest_root.parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    if not os.environ.get("INGEST_DB_PATH") and default_db.exists():
        os.environ["INGEST_DB_PATH"] = str(default_db)
        try:
            import database as dbmod  # pylint: disable=import-error
            if hasattr(dbmod, "DB_PATH"):
                dbmod.DB_PATH = os.environ["INGEST_DB_PATH"]
        except Exception:
            pass
