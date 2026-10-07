from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# connect to the PostgreSQL running in Docker
# Since FastAPI might run on the host for dev, we use localhost.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://hadesuser:hadespassword@localhost:5432/hadesreality_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
