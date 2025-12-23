import os
import shutil
from pathlib import Path


def test_check_ingest_dbs(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    service_db = repo_root / "services" / "ingest" / "ingest_data.db"
    root_db = repo_root.parent / "ingest_data.db"

    # both files should exist (one is root-copy that may be older)
    assert service_db.exists(), "service DB not found"
    assert root_db.exists(), "root ingest_data.db not found"

    # copy both to inspect safely
    s_copy = tmp_path / "svc.db"
    r_copy = tmp_path / "root.db"
    shutil.copy2(service_db, s_copy)
    shutil.copy2(root_db, r_copy)

    os.environ["INGEST_DB_PATH"] = str(s_copy)
    import importlib
    try:
        import database as dbmod
        importlib.reload(dbmod)
    except Exception:
        import database as dbmod

    # Service DB must have enterprise id=3 and uploads > 0
    ent = dbmod.get_enterprise_by_id(3)
    assert ent is not None
    uploads = dbmod.list_uploads_for_enterprise(3)
    assert len(uploads) > 0

    # Now check root DB via direct sqlite (should be smaller/outdated)
    import sqlite3
    conn = sqlite3.connect(str(r_copy))
    cur = conn.cursor()
    root_ent = cur.execute('SELECT id FROM enterprises WHERE id=3').fetchone()
    root_uploads = cur.execute('SELECT COUNT(*) FROM uploads WHERE enterprise_id=3').fetchone()
    # root DB must not have enterprise id=3 (older copy) or zero uploads
    assert root_ent is None or (root_uploads and root_uploads[0] == 0)
    conn.close()
