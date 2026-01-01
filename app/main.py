from fastapi import FastAPI
from app.api.api import api_router
from app.db.session import engine
from app.db.models import Base

# Create DB Tables
Base.metadata.create_all(bind=engine)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="RAG Backend")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router)

@app.get("/")
def root():
    return FileResponse('app/static/index.html')
