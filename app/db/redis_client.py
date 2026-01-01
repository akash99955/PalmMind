import redis
import json
from app.core.config import get_settings

settings = get_settings()

class RedisHandler:
    def __init__(self):
        self.use_redis = settings.USE_REDIS
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed, switching to in-memory: {e}")
                self.use_redis = False
        
        if not self.use_redis:
            self.memory_store = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        message = {"role": role, "content": content}
        if self.use_redis:
            key = f"chat:{session_id}"
            self.redis_client.rpush(key, json.dumps(message))
        else:
            if session_id not in self.memory_store:
                self.memory_store[session_id] = []
            self.memory_store[session_id].append(message)
    
    def get_history(self, session_id: str):
        if self.use_redis:
            key = f"chat:{session_id}"
            messages = self.redis_client.lrange(key, 0, -1)
            return [json.loads(m) for m in messages]
        else:
            return self.memory_store.get(session_id, [])

redis_handler = RedisHandler()
