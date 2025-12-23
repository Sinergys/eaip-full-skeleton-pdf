import sqlite3, sys, os
p = sys.argv[1]
print('DB:', p, 'exists:', os.path.exists(p))
try:
    conn = sqlite3.connect(p, timeout=2)
    cur = conn.cursor()
    try:
        print('Tables:', [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
    except Exception as e:
        print('tables error:', e)
    try:
        print('enterprises:', cur.execute('SELECT id,name FROM enterprises LIMIT 5').fetchall())
    except Exception as e:
        print('enterprises error:', e)
    try:
        print('id3:', cur.execute('SELECT id,name FROM enterprises WHERE id=3').fetchone())
    except Exception as e:
        print('id3 error:', e)
    try:
        print('uploads:', cur.execute('SELECT id,batch_id,filename,created_at FROM uploads ORDER BY created_at DESC LIMIT 5').fetchall())
    except Exception as e:
        print('uploads error:', e)
    try:
        print('PRAGMA journal_mode:', cur.execute("PRAGMA journal_mode;").fetchone())
        print('PRAGMA locking_mode:', cur.execute("PRAGMA locking_mode;").fetchone())
    except Exception as e:
        print('pragma error:', e)
except Exception as e:
    print('connect error:', e)
finally:
    try:
        conn.close()
    except:
        pass
