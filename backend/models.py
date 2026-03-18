from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    verticals = Column(String, default="MCA")
    sub_category = Column(String)
    year = Column(Integer)
    month = Column(String)
    issue_date = Column(String)
    title = Column(String)
    pdf_url = Column(String)
    file_name = Column(String)
    path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
