import os
import uuid
import boto3
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import urllib.parse
from typing import Dict, Any, Optional

load_dotenv()

class ImageGenerationProvider:
    def generate(self, image_prompt: str, negative_prompt: Optional[str] = None) -> str:
        raise NotImplementedError

class PollinationsProvider(ImageGenerationProvider):
    def generate(self, image_prompt: str, negative_prompt: Optional[str] = None) -> str:
        if not image_prompt:
            return "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1080&auto=format&fit=crop"
            
        encoded_prompt = urllib.parse.quote(image_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
        return url

class ImageService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.template_dir = os.path.join(base_dir, "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        self.image_provider = PollinationsProvider()
        
        # Setup Cloudflare R2 connection
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.bucket_name = os.getenv("R2_BUCKET_NAME")
        
        if account_id and self.bucket_name:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
                region_name="auto",
            )
        else:
            self.s3_client = None

    def generate_image(self, hook_text: str, image_prompt: str = None, negative_prompt: str = None, design_instructions: Dict[str, Any] = None):
        try:
            template = self.env.get_template("social_image.html")
            
            # Use the provider
            bg_url = self.image_provider.generate(image_prompt, negative_prompt)
            
            if not design_instructions:
                design_instructions = {"overlay_opacity": 0.8, "text_position": "left"}

            html_content = template.render(
                hook_text=hook_text, 
                bg_url=bg_url,
                overlay_opacity=design_instructions.get("overlay_opacity", 0.8),
                text_position=design_instructions.get("text_position", "left")
            )

            filename = f"post_{uuid.uuid4()}.png"

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_viewport_size({"width": 1080, "height": 1080})
                page.set_content(html_content)
                # Take screenshot into memory as bytes
                screenshot_bytes = page.screenshot(type="png")
                browser.close()

            # Upload to Cloudflare R2 if configured
            if self.s3_client:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=screenshot_bytes,
                    ContentType='image/png'
                )
                
                # Return the actual public URL
                public_url_prefix = os.getenv("R2_PUBLIC_URL", "https://pub-8941136150af4e64a4f1c55035f11c98.r2.dev")
                return f"{public_url_prefix}/{filename}"
            else:
                # Fallback to local if no R2 configured
                output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_images")
                os.makedirs(output_dir, exist_ok=True)
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(screenshot_bytes)
                return filepath

        except Exception as e:
            print(f"Image Generation Error: {e}")
            return None

image_service = ImageService()
