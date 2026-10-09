import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .models import BrandDNA
from .schemas import TopicAnalysisResponse, AIGenerationResponse
from PIL import Image
import glob

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY is missing!")
        self.client = genai.Client(api_key=api_key)

    def load_active_brand_dna(self, db: Session) -> dict:
        dna = db.query(BrandDNA).filter(BrandDNA.is_active == True).order_by(BrandDNA.version.desc()).first()
        if not dna:
            return {"colors": {}, "typography": {}, "layout": {}, "restrictions": {}}
        return {
            "version": dna.version,
            "colors": dna.colors,
            "typography": dna.typography,
            "layout": dna.layout,
            "restrictions": dna.restrictions
        }

    def select_references(self, context: TopicAnalysisResponse):
        # In a fully scaled system, this would query a VisualReference table based on tags.
        # For now, we load core brand references and a context-matching reference from our local pool.
        images = []
        img_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge", "reference_images")
        all_imgs = glob.glob(os.path.join(img_dir, "*.*"))
        
        # Rule: Always include the logo/core brand identity (ref1.png)
        core_img = os.path.join(img_dir, "ref1.png")
        if os.path.exists(core_img):
            images.append(Image.open(core_img))
            
        # Select one contextual reference based on category
        context_img = None
        if context.classification.category.upper() == "FESTIVAL" or context.classification.event:
            # ref2.png is our Vesak/Cultural reference
            context_img = os.path.join(img_dir, "ref2.png")
        else:
            # ref3.png is our Technical/B2B reference
            context_img = os.path.join(img_dir, "ref3.png")
            
        if context_img and os.path.exists(context_img):
            images.append(Image.open(context_img))
            
        return images

    def _generate_with_fallback(self, contents, schema):
        models = ['gemini-flash-latest', 'gemini-pro-latest', 'gemini-3.5-flash', 'gemini-3.8-flash']
        last_error = None
        for model in models:
            try:
                print(f"Attempting generation with {model}...")
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema
                    )
                )
                print(f"Success with {model}!")
                return response
            except Exception as e:
                print(f"Model {model} failed: {e}")
                last_error = e
        raise last_error

    def analyze_context(self, topic: str) -> TopicAnalysisResponse:
        prompt = f"""
        Analyze the following social media topic: "{topic}"
        Identify the content type, category, event, season, and suggest visual direction hints.
        """
        try:
            response = self._generate_with_fallback(prompt, TopicAnalysisResponse)
            return TopicAnalysisResponse.model_validate_json(response.text)
        except Exception as e:
            print(f"Context Analysis Error: {e}")
            raise e

    def generate_post(self, topic: str, db: Session):
        # Phase 1: Context Detection
        context = self.analyze_context(topic)
        
        # Phase 2: Brand DNA & Reference Selection
        brand_dna = self.load_active_brand_dna(db)
        references = self.select_references(context)
        
        # Phase 3: AI Generation
        prompt = f"""
        You are an expert social media manager and visual director for HadesReality.
        
        TOPIC: {topic}
        
        DETECTED CONTEXT:
        {context.model_dump_json(indent=2)}
        
        BRAND DNA (CRITICAL STRICT RULES):
        {json.dumps(brand_dna, indent=2)}
        
        INSTRUCTIONS:
        1. Automatically correct any spelling or grammar mistakes in the TOPIC.
        2. Write a short, catchy hook with perfect English grammar.
        3. Write a professional caption (focus on automation/saving time for B2B, or respectful wishes for cultural events) with flawless spelling and grammar.
        4. Create a highly detailed `image_prompt` for the background image. The background MUST fit the context (e.g. servers for B2B, lanterns for Vesak) while incorporating our Brand DNA colors naturally. DO NOT request text, logos, or typography in the image prompt.
        5. Look at the attached reference images. One is our core brand layout, the other is a contextual example. Use them as inspiration for the layout, spacing, and brand mood.
        """
        
        contents_payload = [prompt] + references
        
        try:
            response = self._generate_with_fallback(contents_payload, AIGenerationResponse)
            result = AIGenerationResponse.model_validate_json(response.text)
            return {
                "hook": result.content.hook,
                "caption": result.content.caption,
                "hashtags": " ".join(result.content.hashtags),
                "image_prompt": result.image_prompt,
                "negative_prompt": result.negative_prompt,
                "design_instructions": result.design_instructions.model_dump(),
                "context": context.model_dump(),
                "brand_dna_version": brand_dna.get("version", 1)
            }
        except Exception as e:
            print(f"AI Generation Error: {e}")
            raise e

    def revise_post(self, topic: str, current_caption: str, current_image_prompt: str, feedback: str, db: Session):
        context = self.analyze_context(topic)
        brand_dna = self.load_active_brand_dna(db)
        references = self.select_references(context)
        
        prompt = f"""
        You are an expert social media manager and visual director for HadesReality.
        
        TOPIC: {topic}
        DETECTED CONTEXT: {context.model_dump_json(indent=2)}
        BRAND DNA: {json.dumps(brand_dna, indent=2)}
        
        CURRENT CAPTION: "{current_caption}"
        CURRENT IMAGE PROMPT: "{current_image_prompt}"
        
        USER FEEDBACK: "{feedback}"
        
        INSTRUCTIONS:
        1. Automatically correct any spelling or grammar mistakes in the USER FEEDBACK and TOPIC.
        2. Rewrite the caption and/or image prompt to exactly match the user's feedback.
        3. Ensure the final output has absolutely perfect English spelling and grammar.
        4. Strictly adhere to the Brand DNA and context.
        """
        
        contents_payload = [prompt] + references
        
        try:
            response = self._generate_with_fallback(contents_payload, AIGenerationResponse)
            result = AIGenerationResponse.model_validate_json(response.text)
            return {
                "hook": result.content.hook,
                "caption": result.content.caption,
                "hashtags": " ".join(result.content.hashtags),
                "image_prompt": result.image_prompt,
                "negative_prompt": result.negative_prompt,
                "design_instructions": result.design_instructions.model_dump(),
                "context": context.model_dump(),
                "brand_dna_version": brand_dna.get("version", 1)
            }
        except Exception as e:
            print(f"AI Revision Error: {e}")
            raise e

ai_service = AIService()
