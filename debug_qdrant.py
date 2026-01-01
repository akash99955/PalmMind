from qdrant_client import QdrantClient
try:
    client = QdrantClient(path="./qdrant_db_debug")
    print("Client type:", type(client))
    print("Has search:", hasattr(client, "search"))
    print("Dir:", dir(client))
except Exception as e:
    print("Error:", e)
