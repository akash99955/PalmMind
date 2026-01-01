import sys
import os

# Ensure we can import app
sys.path.append(os.getcwd())

from app.core.config import get_settings
from app.db.vector_db import QdrantHandler

settings = get_settings()
print(f"SCRIPT_DEBUG: Env Var QDRANT_URL: '{os.environ.get('QDRANT_URL')}'")
print(f"SCRIPT_DEBUG: QDRANT_URL from settings: '{settings.QDRANT_URL}'")

try:
    handler = QdrantHandler()
    print("Handler initialized successfully")
except Exception as e:
    print(f"Handler failed: {e}")
