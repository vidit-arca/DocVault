import os
import shutil
import io
from typing import List
from datetime import timedelta
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from minio import Minio
from minio.error import S3Error
from backend import models, database

# MinIO Configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "password123"
MINIO_BUCKET = "documents"

# Initialize MinIO Client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Ensure bucket exists
try:
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)
except Exception as e:
    print(f"Error connecting to MinIO: {e}")

# Ensure uploads directory exists (keeping for static frontend assets if needed, though we'll use MinIO for docs)
UPLOAD_DIR = "backend/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Initialize database
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Document Upload System")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_index():
    return FileResponse("frontend/index.html")

@app.post("/upload/")
async def upload_document(
    sub_category: str = Form(...),
    year: int = Form(...),
    month: str = Form(...),
    issue_date: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_extension = os.path.splitext(file.filename)[1]
    # Use sub_category for the prefix in MinIO
    object_name = f"{sub_category}/{title.replace(' ', '_')}_{issue_date}{file_extension}"

    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Upload directly to MinIO
        minio_client.put_object(
            MINIO_BUCKET,
            object_name,
            io.BytesIO(file_content),
            length=file_size,
            content_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MinIO Upload Error: {str(e)}")

    # Parsing logic: get filename without prefix
    # If object_name is "Notifications/file.pdf", file_name becomes "file.pdf"
    file_name_parsed = os.path.basename(object_name)

    # Map pdf_url based on sub_category
    url_mapping = {
        "Notifications": "https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks/notifications.html",
        "Circulars": "https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks/circulars.html",
        "Press Release": "https://www.mca.gov.in/content/mca/global/en/notifications-tender/news-updates/press-release.html",
        "News": "https://www.mca.gov.in/content/mca/global/en/notifications-tender/whats-new.html",
        "Notices": "https://www.mca.gov.in/content/mca/global/en/notifications-tender/notices-circulars.html",
        "Latest news": "https://www.mca.gov.in/content/mca/global/en/notifications-tender/news-updates/latest-news.html"
    }
    
    selected_pdf_url = url_mapping.get(sub_category, object_name)

    # Save metadata to DB
    db_document = models.Document(
        verticals="MCA", # Default as requested
        sub_category=sub_category,
        year=year,
        month=month,
        issue_date=issue_date,
        title=title,
        file_name=file_name_parsed,
        path=object_name,
        pdf_url=selected_pdf_url
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return {"message": "Document uploaded successfully", "document_id": db_document.id}

@app.get("/documents/")
def list_documents(db: Session = Depends(database.get_db)):
    documents = db.query(models.Document).all()
    
    # Enrich documents with presigned URLs for viewing
    for doc in documents:
        try:
            doc.presigned_url = minio_client.get_presigned_url(
                "GET",
                MINIO_BUCKET,
                doc.path,
                expires=timedelta(hours=1)
            )
        except Exception:
            doc.presigned_url = "#"
            
    return documents

@app.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(database.get_db)):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove from MinIO
    try:
        minio_client.remove_object(MINIO_BUCKET, db_document.path)
    except Exception as e:
        print(f"Error deleting from MinIO: {e}")
    
    db.delete(db_document)
    db.commit()
    return {"message": "Document deleted successfully"}
