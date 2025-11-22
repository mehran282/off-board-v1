"""Check latest flyers"""
from database.connection import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text('SELECT "id", "title", "thumbnailUrl", "contentId" FROM "Flyer" ORDER BY "createdAt" DESC LIMIT 5'))
rows = result.fetchall()
print('Latest Flyers:')
for row in rows:
    print(f'  - {row[1]}:')
    print(f'    thumbnailUrl: {row[2][:100] if row[2] else "None"}...')
    print(f'    contentId: {row[3]}')
conn.close()

