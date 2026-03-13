from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    subdomain = Column(String)  # SEBI, RBI, IRDA, etc.
    title = Column(String)
    issue_date = Column(String) # Storing as string for simplicity or date
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
