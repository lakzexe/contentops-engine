import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class Dummy(BaseModel):
    test: str

models_to_test = [
    "gemini-2.5-pro",
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3-pro-image",
    "aqa",
]

for m in models_to_test:
    print(f"Testing {m}...")
    try:
        response = client.models.generate_content(
            model=m,
            contents="say hello",
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Dummy
            )
        )
        print(f"SUCCESS: {m}")
        break
    except Exception as e:
        print(f"FAILED: {e}")
