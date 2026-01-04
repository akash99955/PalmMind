import time
import google.generativeai as genai
from google.api_core import exceptions
from app.core.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

class LLMService:
    def __init__(self):
        self.chat_model = genai.GenerativeModel('gemini-2.5-flash')

    def _retry_operation(self, func, *args, **kwargs):
        retries = 5
        delay = 5
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except exceptions.ResourceExhausted:
                if i == retries - 1:
                    raise
                print(f"Quota exceeded, retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            except Exception as e:
                if "429" in str(e):
                    if i == retries - 1:
                        raise
                    print(f"Rate limit hit, retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                raise e

    def generate_response(self, prompt: str) -> str:
        response = self._retry_operation(
            self.chat_model.generate_content,
            prompt
        )
        return response.text

llm_service = LLMService()
