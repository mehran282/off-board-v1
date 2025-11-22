"""Database connection setup"""
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with connection pooling
# Ensure the URL uses postgresql:// instead of postgres:// for SQLAlchemy
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Remove pool=true from connection string as it's not valid for psycopg2
# SQLAlchemy handles pooling via poolclass parameter
if 'pool=true' in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace('&pool=true', '').replace('?pool=true', '?').replace('&pool=true&', '&')

# Remove channel_binding=require as it's not supported by psycopg2
# SSL is handled via sslmode=require
if 'channel_binding=require' in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace('&channel_binding=require', '').replace('?channel_binding=require', '?').replace('&channel_binding=require&', '&')

# Configure SSL for Neon database
connect_args = {}
if 'sslmode=require' in DATABASE_URL:
    connect_args = {
        'sslmode': 'require',
    }

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
    connect_args=connect_args,
)

