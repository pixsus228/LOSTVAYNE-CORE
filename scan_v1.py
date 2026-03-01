import google.generativeai as genai
# Використовую Ваш ключ для перевірки доступних ресурсів
genai.configure(api_key="AIzaSyCmPdfidqaXHw85o3Xw-wWVqRaOuBmSWf4")

print("--- ДОСТУПНІ МОДЕЛІ (STABLE V1) ---")
try:
    for m in genai.list_models():
        # Шукаю моделі, які підтримують генерацію контенту
        if 'generateContent' in m.supported_generation_methods:
            print(f"Доступно: {m.name}")
except Exception as e:
    print(f"Помилка доступу: {e}")