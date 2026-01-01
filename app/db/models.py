from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentMetadata(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    # Storing associated vector_ids might be useful if needed, 
    # but strictly separating metadata (SQL) vs Vectors (Qdrant) is fine too.
    # We can query SQL by filename or ID.

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    date = Column(String) # Keeping as string for simplicity to match extraction, or could extract date object
    time = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
