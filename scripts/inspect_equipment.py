import json
import sqlite3
from pathlib import Path

DB_PATH = Path("eaip_full_skeleton/services/ingest/ingest_data.db")


def main() -> None:
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    query = """
        SELECT uploads.batch_id, uploads.filename, parsed_data.raw_json
        FROM uploads
        JOIN parsed_data ON parsed_data.upload_id = uploads.id
        WHERE uploads.filename LIKE ?
        ORDER BY uploads.created_at DESC
        LIMIT 1
    """

    row = conn.execute(query, ("%oborudovanie%",)).fetchone()
    conn.close()

    if not row:
        print("No oborudovanie upload found.")
        return

    data = json.loads(row["raw_json"])
    parsing = data.get("parsing", {})
    sheets = parsing.get("data", {}).get("sheets", [])

    print("batch_id:", row["batch_id"])
    print("sheets count:", len(sheets))

    if sheets:
        sheet = sheets[0]
        print("First sheet name:", sheet.get("name"))
        print("Sample rows:")
        for idx, r in enumerate(sheet.get("rows", [])[:10], 1):
            print(idx, r)


if __name__ == "__main__":
    main()


