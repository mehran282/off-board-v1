"""Check flyer thumbnail in database"""
from database.connection import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text('SELECT "id", "title", "thumbnailUrl", "pdfUrl" FROM "Flyer" WHERE "thumbnailUrl" IS NULL LIMIT 5'))
rows = result.fetchall()
print('Flyers without thumbnailUrl:')
for row in rows:
    print(f'  - {row[1]}: thumbnailUrl={row[2]}, pdfUrl={row[3]}')
conn.close()

