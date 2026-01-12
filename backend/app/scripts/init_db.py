"""
Database initialization script.
Creates all tables and enables PostGIS extension.

Usage: python -m app.scripts.init_db
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.database import sync_engine, Base
from app.models import *  # noqa: F401, F403 - Import all models


def init_database():
    """Initialize database with PostGIS and create all tables"""
    print("Initializing database...")

    with sync_engine.connect() as conn:
        # Enable PostGIS extension
        print("Enabling PostGIS extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()

    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=sync_engine)

    print("Database initialized successfully!")


if __name__ == "__main__":
    init_database()
