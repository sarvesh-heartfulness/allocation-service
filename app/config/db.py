from dotenv import load_dotenv
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Database URL for SQLAlchemy
DB_STRING = os.getenv("DB_STRING")

# declarative base
Base = declarative_base()

# Create SQLAlchemy engine
engine = create_engine(DB_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Check if database is connected
def check_db_connection():
    try:
        conn = engine.connect()
        conn.close()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()