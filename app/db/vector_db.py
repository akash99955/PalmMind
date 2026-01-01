from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import get_settings

settings = get_settings()

class QdrantHandler:
    def __init__(self):
        if settings.QDRANT_URL.startswith("http"):
            self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        else:
            self.client = QdrantClient(path=settings.QDRANT_URL)
        
        self.collection_name = "documents"
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Create collection if it doesn't exist. 
            # Vector size for Gemini embeddings (text-embedding-004) is 768.
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
            )

    def upsert_vectors(self, points):
        """
        points: List of models.PointStruct
        """
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, vector, top_k=5):
        return self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k
        ).points

qdrant_handler = QdrantHandler()
