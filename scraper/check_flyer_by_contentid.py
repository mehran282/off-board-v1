"""Check flyer by contentId"""
from database.connection import engine
from sqlalchemy import text

content_id = '46a3ed9f-20d3-47fc-b426-6641f88b6a8f'

conn = engine.connect()
result = conn.execute(text('SELECT "id", "title", "thumbnailUrl", "contentId" FROM "Flyer" WHERE "contentId" = :content_id'), {'content_id': content_id})
row = result.fetchone()
if row:
    print(f'Flyer found:')
    print(f'  Title: {row[1]}')
    print(f'  thumbnailUrl: {row[2][:100] if row[2] else "None"}...')
    print(f'  contentId: {row[3]}')
else:
    print('Flyer not found with contentId:', content_id)
conn.close()

