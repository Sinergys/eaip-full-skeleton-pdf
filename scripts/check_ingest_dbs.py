import sqlite3
import os

paths = [r'C:\eaip\ingest_data.db', r'C:\eaip\eaip_full_skeleton\services\ingest\ingest_data.db']

for p in paths:
    print('\nDB:', p)
    if not os.path.exists(p):
        print('  -> not found')
        continue
    try:
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        row = cur.execute("SELECT id,name,industry,enterprise_type,product_type FROM enterprises WHERE id=3").fetchone()
        print('  id=3 ->', row)
        cnt = cur.execute("SELECT COUNT(*) FROM enterprises WHERE name LIKE '%Navoiy%' COLLATE NOCASE").fetchone()
        print('  Navoiy count ->', cnt)
        uploads = cur.execute('SELECT COUNT(*) FROM uploads WHERE enterprise_id=3').fetchone()
        print('  uploads count ->', uploads)
    except Exception as e:
        print('  Error querying', p, e)
    finally:
        try:
            conn.close()
        except:
            pass

print('\nDone')
