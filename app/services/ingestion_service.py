import io
from fastapi import UploadFile
from pypdf import PdfReader
from app.db.models import DocumentMetadata
from sqlalchemy.orm import Session

class IngestionService:
    async def extract_text(self, file: UploadFile) -> str:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            text = ""
            pdf_reader = PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif filename.endswith('.txt'):
            return content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    async def ingest_document(self, file: UploadFile, strategy: str, db: Session):
        # 1. Extract
        text = await self.extract_text(file)
        
        # 2. Save to SQL (No more Qdrant)
        db_doc = DocumentMetadata(
            filename=file.filename,
            content=text
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        return {"document_id": db_doc.id, "filename": file.filename}

ingestion_service = IngestionService()
