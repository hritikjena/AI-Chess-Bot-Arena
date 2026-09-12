import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

for model in client.models.list():
    if "generateContent" in model.supported_actions and "gemini" in model.name:
        print(model.name)

# Optional: Test a completion with the new model
try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Explain in one sentence why controlling the center is useful in chess."
    )
    print("\nTest generate_content (gemini-3.6-flash):")
    print(response.text)
except Exception as e:
    print(f"\ngenerate_content error: {e}")
