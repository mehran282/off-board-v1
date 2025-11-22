"""Debug flyer data"""
from database.connection import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text('SELECT "id", "title", "contentId", "publishedFrom" FROM "Flyer" ORDER BY "createdAt" DESC LIMIT 1'))
row = result.fetchone()
print('Latest Flyer:', row)
conn.close()

