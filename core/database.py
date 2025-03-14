# core/database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

# Define the path for the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of this script
db_path = os.path.join(BASE_DIR, 'data', 'jobs.db')
db_url = f'sqlite:///{db_path}'

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String)
    provider_id = Column(String, unique=True)
    title = Column(String)
    link = Column(String)
    applied_on = Column(DateTime, default=None)  # Applied is now a DateTime, defaults to None
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def create_connection():
    """Create a database connection and return the session."""
    engine = create_engine('sqlite:///jobs.db', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def close_connection(session):
    """Close the session."""
    session.close()
