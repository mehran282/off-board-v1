"""Check new flyers with contentId"""
from database.connection import engine
from sqlalchemy import text

conn = engine.connect()
# Check flyers with contentId
result = conn.execute(text('SELECT "id", "title", "thumbnailUrl", "contentId", "createdAt" FROM "Flyer" WHERE "contentId" IS NOT NULL ORDER BY "createdAt" DESC LIMIT 5'))
rows = result.fetchall()
print('Flyers WITH contentId:')
for row in rows:
    print(f'  - {row[1]}:')
    print(f'    thumbnailUrl: {row[2][:100] if row[2] else "None"}...')
    print(f'    contentId: {row[3]}')
    print(f'    createdAt: {row[4]}')
    print()

# Check latest flyers regardless of contentId
result2 = conn.execute(text('SELECT "id", "title", "thumbnailUrl", "contentId", "createdAt" FROM "Flyer" ORDER BY "createdAt" DESC LIMIT 3'))
rows2 = result2.fetchall()
print('\nLatest 3 Flyers (all):')
for row in rows2:
    print(f'  - {row[1]}:')
    print(f'    thumbnailUrl: {row[2][:100] if row[2] else "None"}...')
    print(f'    contentId: {row[3]}')
    print(f'    createdAt: {row[4]}')
    print()
conn.close()

