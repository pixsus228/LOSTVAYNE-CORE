import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class JarvisLogic:
    def __init__(self):
        # Синхронізував назву з вашим .env
        self.api_key = os.getenv("GG_API_KEY")
        if not self.api_key:
            print("⚠️ УВАГА: Сер, API ключ не знайдено в .env!")
            return

        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-1.5-flash"

    async def think(self, prompt):
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Сер, виникла помилка зв'язку: {str(e)}"
