import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


class JarvisLogic:
    def __init__(self):
        self.api_key = os.getenv("GG_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-1.5-flash"

        # Зафіксував Ваш авторський стиль
        self.system_instruction = (
            "Ти — JARVIS, особистий асистент на LOSTVAYNE-LOQ. "
            "Звертайся до користувача 'Сер'. Відповідай лаконічно, технічно та українською."
        )

    async def think(self, prompt):
        try:
            # Примусово чищу промпт для стабільності
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt.strip(),
                config={'system_instruction': self.system_instruction}
            )
            return response.text
        except Exception as e:
            return f"Сер, виникла помилка зв'язку з нейромережею: {str(e)}"