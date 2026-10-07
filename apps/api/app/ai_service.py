import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY is missing!")
            
        # The new package uses a "Client"
        self.client = genai.Client(api_key=api_key)

    def load_knowledge_base(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "brand_guidelines.md")
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Could not load knowledge base: {e}")
            return "No brand guidelines found."

    def generate_post(self, topic: str):
        brand_rules = self.load_knowledge_base()

        prompt = f"""
        You are a professional social media manager.
        
        Here is the Knowledge Base and Brand Guidelines you MUST follow:
        {brand_rules}
        
        ---
        Write a social media post about this topic: {topic}
        
        Return ONLY a JSON object with these exact keys:
        - "caption": The main text of the post following the template.
        - "hook": A short, catchy opening sentence.
        - "hashtags": A string of 3 to 5 relevant hashtags.
        - "image_prompt": A detailed description for an AI image generator, using our Color Themes.
        """
        
        try:
            # The new way to send the request
            response = self.client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
            
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return None

# Create one instance to use in other files
ai_service = AIService()
