from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.ingestion_service import ingestion_service

router = APIRouter()

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    strategy: str = Form("recursive"), # recursive or fixed
    db: Session = Depends(get_db)
):
    try:
        result = await ingestion_service.ingest_document(file, strategy, db)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
