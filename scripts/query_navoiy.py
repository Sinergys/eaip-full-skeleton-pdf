import sqlite3
p=r'C:\eaip\eaip_full_skeleton\services\ingest\ingest_data.db'
conn=sqlite3.connect(p)
c=conn.cursor()
print('Enterprises matching Navoiy:')
for row in c.execute("SELECT id, name FROM enterprises WHERE name LIKE '%Navoiy%' COLLATE NOCASE"):
    print(row)
print('\nUploads matching Navoiy:')
for row in c.execute("SELECT id, batch_id, filename, created_at FROM uploads WHERE filename LIKE '%Navoiy%' COLLATE NOCASE"):
    print(row)
print('\nParsed data rows containing Navoiy (first 5 ids):')
for row in c.execute("SELECT pd.upload_id, u.batch_id, u.filename FROM parsed_data pd JOIN uploads u ON pd.upload_id = u.id WHERE pd.raw_json LIKE '%Navoiy%' COLLATE NOCASE LIMIT 5"):
    print(row)
conn.close()