import sqlite3
import os
p=r'C:\eaip\eaip_full_skeleton\services\ingest\ingest_data.db'
print('DB path:', p)
if not os.path.exists(p):
    print('DB not found')
    raise SystemExit(1)
conn=sqlite3.connect(p)
c=conn.cursor()
rows=c.execute("SELECT name,type FROM sqlite_master WHERE type IN ('table','view')").fetchall()
print('Tables/Views count:', len(rows))
for r in rows:
    print(' -', r[0], r[1])

# list tables and row counts
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables=[r[0] for r in c.fetchall()]
for t in tables:
    try:
        cnt=c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    except Exception as e:
        cnt='?'
    print(f'Table {t}: rows={cnt}')
    if isinstance(cnt, int) and cnt>0:
        sample=c.execute(f'SELECT * FROM "{t}" LIMIT 3').fetchall()
        print('  sample rows:', sample)

# search for "Navoiy" occurrences in text columns
found=False
for t in tables:
    try:
        cols=[row[1] for row in conn.execute(f'PRAGMA table_info("{t}")')]
        for col in cols:
            try:
                res=conn.execute(f"SELECT COUNT(*) FROM \"{t}\" WHERE \"{col}\" LIKE '%Navoiy%' COLLATE NOCASE").fetchone()[0]
                if res>0:
                    print(f"Found 'Navoiy' in table {t} column {col}: {res} rows")
                    found=True
            except Exception:
                pass
    except Exception:
        pass

if not found:
    print('No match for "Navoiy" in any table')

conn.close()