import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Use standard postgresql driver (psycopg2) compatible with GeoPandas and GeoAlchemy2
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://orca_user:orca_password@localhost:5432/orca_marine")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
