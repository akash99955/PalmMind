import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

print("Listing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
