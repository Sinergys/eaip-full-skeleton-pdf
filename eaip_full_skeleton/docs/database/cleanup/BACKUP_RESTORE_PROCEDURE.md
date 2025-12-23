# Database Backup Restoration Procedure

## Tested and Verified: 2025-12-08

### Backup File Details
- **Primary Backup**: `backups/ingest_data_20251201_211328.db`
- **File Size**: 35.60 MB
- **Integrity Check**: PASSED (ok)
- **Tables**: 12 (11 data tables + sqlite_sequence)

### Verification Results
✅ Database opens successfully in SQLite
✅ Contains all expected tables with data
✅ No corruption errors during query operations
✅ Sample queries execute correctly

### Table Inventory
1. enterprises: 3 rows
2. uploads: 252 rows
3. parsed_data: 251 rows
4. uploads_storage: 221 rows
5. normative_documents: 6 rows
6. normative_rules: 1 row
7. normative_references: 0 rows
8. aggregated_data_backup: 0 rows
9. aggregated_data: 36 rows
10. node_consumption: 569 rows
11. normative_violations: 0 rows

## Restoration Procedure

### Quick Restore (Emergency)
```bash
# Stop application first
# Copy backup to working location
cp "backups/ingest_data_20251201_211328.db" "eaip_full_skeleton/services/ingest/ingest_data.db"
# Restart application
```

### Safe Restore (Recommended)
```bash
# 1. Stop application
# 2. Backup current database (if exists)
timestamp=$(date +%Y%m%d_%H%M%S)
cp "eaip_full_skeleton/services/ingest/ingest_data.db" "backups/pre_restore_${timestamp}.db"

# 3. Verify backup integrity
python -c "
import sqlite3
conn = sqlite3.connect('backups/ingest_data_20251201_211328.db')
cursor = conn.cursor()
cursor.execute('PRAGMA integrity_check')
print(cursor.fetchone()[0])
conn.close()
"

# 4. If integrity check passes, restore
cp "backups/ingest_data_20251201_211328.db" "eaip_full_skeleton/services/ingest/ingest_data.db"

# 5. Verify restoration
python -c "
import sqlite3
conn = sqlite3.connect('eaip_full_skeleton/services/ingest/ingest_data.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM enterprises')
print(f'Enterprises: {cursor.fetchone()[0]}')
conn.close()
"

# 6. Restart application
```

### Python Script Method
```python
import sqlite3
import shutil
from datetime import datetime

def restore_backup(backup_path, target_path):
    # Verify backup integrity
    conn = sqlite3.connect(backup_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA integrity_check')
    integrity = cursor.fetchone()[0]
    conn.close()

    if integrity != 'ok':
        raise Exception(f"Backup integrity check failed: {integrity}")

    # Create safety backup of current database
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safety_backup = f"backups/pre_restore_{timestamp}.db"
    shutil.copy2(target_path, safety_backup)

    # Restore from backup
    shutil.copy2(backup_path, target_path)

    print(f"✅ Database restored successfully")
    print(f"Safety backup created at: {safety_backup}")

# Usage
restore_backup(
    'backups/ingest_data_20251201_211328.db',
    'eaip_full_skeleton/services/ingest/ingest_data.db'
)
```

## Additional Backup Files Available
- `backups/ingest_data_backup2_20251201_211513.db` (Secondary safety backup)

## Notes
- Always stop the application before restoring
- Verify backup integrity before restoration
- Create a safety backup of current state before restoring
- Test restored database before resuming operations
