import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker  # Updated import here
from .db_config import db_url

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
# Use the new `declarative_base` location
Base = declarative_base()

# Define the path for the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'data', 'jobs.db')  # Ensure the 'data' directory exists or is created
if not os.path.exists(os.path.join(BASE_DIR, 'data')):
    os.makedirs(os.path.join(BASE_DIR, 'data'))  # Create 'data' directory if it does not exist
db_url = db_url

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String, nullable=False)
    provider_id = Column(Integer, nullable=False)
    title = Column(String)
    link = Column(String)
    is_quick_apply = Column(Boolean, default=False, nullable=False)
    applied_on = Column(DateTime, default=None)  # Applied is now a DateTime, defaults to None
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (UniqueConstraint('provider', 'provider_id', name='_provider_provider_id_uc'),)

def create_connection():
    """Create a database connection and return the session."""
    engine = create_engine(db_url, echo=True)  # Use the db_url that includes the path
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def close_connection(session):
    """Close the session."""
    session.close()

def open_session():
    Session = sessionmaker(bind=create_engine(db_url))
    return Session()

def close_session(session):
    session.close()