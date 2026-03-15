from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class Incident(Base):
    __tablename__ = 'incidents'

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, index=True)
    description = Column(String)
    severity = Column(Float)

# Database connection setup using Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_DB_URL", "postgresql://user:password@db.supabase.co:5432/postgres")
engine = create_engine(SUPABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)