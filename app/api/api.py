from fastapi import APIRouter
from app.api.endpoints import ingest, chat

api_router = APIRouter()
api_router.include_router(ingest.router, tags=["ingest"])
api_router.include_router(chat.router, tags=["chat"])
