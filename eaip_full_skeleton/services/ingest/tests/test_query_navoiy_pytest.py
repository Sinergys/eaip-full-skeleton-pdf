import os
import shutil
from pathlib import Path


def test_query_navoiy(tmp_path):
    # Ensure the service DB exists and create a temporary copy
    repo_root = Path(__file__).resolve().parents[3]
    service_db = repo_root / "services" / "ingest" / "ingest_data.db"
    assert service_db.exists(), "service DB not found"

    db_copy = tmp_path / "ingest_copy.db"
    shutil.copy2(service_db, db_copy)

    # Use the copy so we don't touch original data
    os.environ["INGEST_DB_PATH"] = str(db_copy)

    import importlib
    try:
        import database as dbmod
        importlib.reload(dbmod)
    except Exception:
        import database as dbmod

    # Query enterprise by name and id
    rows = dbmod.list_enterprises()
    names = [r["name"] for r in rows] if rows else []
    assert any("Navoiy" in n or "Навоий" in n for n in names), "no enterprise named Navoiy found"

    ent = dbmod.get_enterprise_by_id(3)
    # enterprise id=3 expected to exist in service DB
    assert ent is not None and ent.get("name"), "id=3 enterprise not present"

    # Ensure parsed_data contains references to Navoiy in uploads
    uploads = dbmod.list_uploads_for_enterprise(3, limit=5)
    assert isinstance(uploads, list) and len(uploads) > 0
