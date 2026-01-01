from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.rag_service import rag_service

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    query: str

@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        result = await rag_service.chat_with_data(request.session_id, request.query, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
