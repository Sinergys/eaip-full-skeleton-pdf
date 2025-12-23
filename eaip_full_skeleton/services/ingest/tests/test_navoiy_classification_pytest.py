import os
import shutil
from pathlib import Path


def test_navoiy_classification(tmp_path):
    """Pytest that verifies classification for Navoiy IES using a temporary copy of the DB.

    This test copies the service DB into a temporary file and sets INGEST_DB_PATH to it
    so we don't modify production/dev DB while asserting expected classification values.
    """
    repo_root = Path(__file__).resolve().parents[3]
    service_db = repo_root / "services" / "ingest" / "ingest_data.db"
    assert service_db.exists(), f"service DB not found: {service_db}"

    copy_db = tmp_path / "ingest_data_copy.db"
    shutil.copy2(service_db, copy_db)

    # Ensure tests use the copy
    os.environ["INGEST_DB_PATH"] = str(copy_db)

    # Import database module after env var is set
    import importlib

    # If database module was previously imported in the test process, reload to pick up DB_PATH change
    try:
        import database as dbmod
        importlib.reload(dbmod)
    except Exception:
        # Import if not present in sys.modules
        import database as dbmod

    # Ensure enterprise exists
    enterprise = dbmod.get_enterprise_by_id(3)
    assert enterprise is not None, "Navoiy enterprise (id=3) not found in test DB copy"

    # Collect uploads (filenames) and run classifier
    uploads = dbmod.list_uploads_for_enterprise(3)
    filenames = [u.get("filename", "") for u in uploads if u.get("filename")]

    # Import classifier and run
    from utils.enterprise_classifier import classify_enterprise

    industry, enterprise_type, product_type = classify_enterprise(enterprise["name"], filenames)

    # We expect: энергетика, ТЭС, электроэнергия
    assert industry == "энергетика"
    assert enterprise_type == "ТЭС"
    assert product_type == "электроэнергия"

    # Update into DB copy (should succeed) and check
    dbmod.update_enterprise_type(3, industry=industry, enterprise_type=enterprise_type, product_type=product_type)
    updated = dbmod.get_enterprise_by_id(3)
    assert updated.get("industry") == industry
    assert updated.get("enterprise_type") == enterprise_type
    assert updated.get("product_type") == product_type
