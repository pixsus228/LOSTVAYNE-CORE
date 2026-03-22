import os
import google.generativeai as genai
from dotenv import load_dotenv

# Завантажив налаштування
load_dotenv()
api_key = os.getenv("GG_API_KEY")

if not api_key:
    print("❌ Сер, GG_API_KEY не знайдено в .env!")
else:
    genai.configure(api_key=api_key)
    print("--- ДОСТУПНІ МОДЕЛІ ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Доступно: {m.name}")
    except Exception as e:
        print(f"Помилка доступу: {e}")