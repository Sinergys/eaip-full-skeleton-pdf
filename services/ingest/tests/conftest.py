import os
from pathlib import Path


def pytest_configure(config):
    """Set INGEST_DB_PATH to the service DB when running ingest tests locally.

    This makes tests deterministic when run from the repository root or CI
    without needing manual environment configuration.
    """
    # locate the ingest service root (two levels up from this tests dir)
    test_dir = Path(__file__).resolve().parent
    ingest_root = test_dir.parent
    default_db = ingest_root / "ingest_data.db"

    # Only set if not already configured in environment or CLI
    if not os.environ.get("INGEST_DB_PATH") and default_db.exists():
        os.environ["INGEST_DB_PATH"] = str(default_db)
        # Also set database module path for modules that may import it early
        try:
            import database as dbmod  # pylint: disable=import-error
            # override DB_PATH in module if present
            if hasattr(dbmod, "DB_PATH"):
                dbmod.DB_PATH = os.environ["INGEST_DB_PATH"]
        except Exception:
            # ignore - test imports may happen later
            pass
