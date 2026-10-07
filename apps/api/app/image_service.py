import os
import uuid
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright


class ImageService:
    def __init__(self):
        # We find the main apps/api folder
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.template_dir = os.path.join(base_dir, "templates")

        # We will save the images in a new folder called "generated_images"
        self.output_dir = os.path.join(base_dir, "generated_images")
        os.makedirs(self.output_dir, exist_ok=True)

        # This tool reads our HTML file
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate_image(self, hook_text: str):
        try:
            # 1. Open the HTML file and insert the AI's hook text
            template = self.env.get_template("social_image.html")
            html_content = template.render(hook_text=hook_text)

            # 2. Create a random filename so we do not overwrite old images
            filename = f"post_{uuid.uuid4()}.png"
            filepath = os.path.join(self.output_dir, filename)

            # 3. Turn on the robot browser to take the picture
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Make it a perfect square for Instagram/LinkedIn
                page.set_viewport_size({"width": 1080, "height": 1080})

                # Load the HTML with the text, take a picture, and close!
                page.set_content(html_content)
                page.screenshot(path=filepath)
                browser.close()

            return filepath
        except Exception as e:
            print(f"Image Generation Error: {e}")
            return None


# Create one instance to use in other files
image_service = ImageService()
