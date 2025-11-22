"""Check specific flyer"""
from database.connection import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text("SELECT \"id\", \"title\", \"contentId\", \"publishedFrom\" FROM \"Flyer\" WHERE \"url\" LIKE '%2500912090%' LIMIT 1"))
row = result.fetchone()
print('Flyer 2500912090:', row)
conn.close()

