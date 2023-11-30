from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()

# Database URL for SQLAlchemy
DB_STRING = os.getenv("DB_STRING")

# Create SQLAlchemy engine
engine = create_engine(DB_STRING)

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