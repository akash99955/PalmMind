import io
from fastapi import UploadFile
from pypdf import PdfReader
from app.services.llm_service import llm_service
from app.db.vector_db import qdrant_handler
from app.db.models import DocumentMetadata
from qdrant_client.http import models
from sqlalchemy.orm import Session
import uuid

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

    def chunk_text(self, text: str, strategy: str = "recursive") -> list[str]:
        if strategy == "fixed":
            return self._chunk_fixed(text)
        elif strategy == "recursive":
             return self._chunk_recursive(text)
        else:
            raise ValueError("Unknown chunking strategy")

    def _chunk_fixed(self, text: str, chunk_size=500, overlap=50) -> list[str]:
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i : i + chunk_size])
        return chunks

    def _chunk_recursive(self, text: str, target_size=500) -> list[str]:
        # Simple recursive implementation
        separators = ["\n\n", "\n", ". ", " ", ""]
        final_chunks = []
        
        def split(text, separators, current_size):
            if len(text) <= current_size:
                final_chunks.append(text)
                return
            
            # If no separators left, just hard slice
            if not separators:
                final_chunks.extend([text[i:i+current_size] for i in range(0, len(text), current_size)])
                return

            sep = separators[0]
            pieces = text.split(sep)
            new_pieces = []
            
            # Reconstruct chunks
            current_chunk = ""
            for piece in pieces:
                if len(current_chunk) + len(piece) + len(sep) <= current_size:
                    current_chunk += (sep + piece) if current_chunk else piece
                else:
                    if current_chunk:
                        new_pieces.append(current_chunk)
                    current_chunk = piece
            if current_chunk:
                new_pieces.append(current_chunk)
                
            for piece in new_pieces:
                if len(piece) <= current_size:
                    final_chunks.append(piece)
                else:
                    split(piece, separators[1:], current_size)
        
        split(text, separators, target_size)
        return final_chunks

    async def ingest_document(self, file: UploadFile, strategy: str, db: Session):
        # 1. Extract
        text = await self.extract_text(file)
        
        # 2. Chunk
        chunks = self.chunk_text(text, strategy)
        
        # 3. Save Metadata (DB)
        db_doc = DocumentMetadata(filename=file.filename)
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        # 4. Embed & Store (Vector DB)
        points = []
        for i, chunk in enumerate(chunks):
            embedding = llm_service.get_embedding(chunk)
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "document_id": db_doc.id,
                        "filename": file.filename,
                        "chunk_index": i
                    }
                )
            )
        
        qdrant_handler.upsert_vectors(points)
        return {"document_id": db_doc.id, "chunks": len(chunks)}

ingestion_service = IngestionService()
