"""Check flyers with thumbnailUrl"""
from database.connection import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text('SELECT "id", "title", "thumbnailUrl", "pdfUrl" FROM "Flyer" WHERE "thumbnailUrl" IS NOT NULL ORDER BY "createdAt" DESC LIMIT 5'))
rows = result.fetchall()
print('Flyers WITH thumbnailUrl:')
for row in rows:
    print(f'  - {row[1]}: thumbnailUrl={row[2][:80] if row[2] else None}...')
conn.close()

