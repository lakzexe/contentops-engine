from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ContentContent(BaseModel):
    hook: str = Field(description="A short, catchy opening sentence.")
    caption: str = Field(description="The main text of the post.")
    hashtags: List[str] = Field(description="List of relevant hashtags.")

class ContentClassification(BaseModel):
    content_type: str = Field(description="E.g., TECHNICAL, EDUCATIONAL, FESTIVAL")
    category: str = Field(description="E.g., Cybersecurity, Vesak, Cloud Computing")
    event: Optional[str] = Field(description="Specific event if applicable, e.g., Vesak, Anniversary")
    season: Optional[str] = Field(description="Specific season if applicable")

class VisualDirection(BaseModel):
    subject: str = Field(description="The main visual subject of the background image.")
    environment: str = Field(description="The physical or digital setting.")
    mood: str = Field(description="The feeling or atmosphere of the image.")
    lighting: str = Field(description="Lighting style (e.g., warm, neon, cinematic).")
    composition: str = Field(description="How the elements are arranged.")
    visual_elements: List[str] = Field(description="Specific objects that must be present.")
    supporting_colors: List[str] = Field(description="Colors to include in the background.")

class TopicAnalysisResponse(BaseModel):
    classification: ContentClassification
    visual_direction_hints: List[str] = Field(description="High-level hints on what visual elements match this context (e.g. 'lanterns', 'servers', 'cake').")

class DesignInstructions(BaseModel):
    overlay_opacity: float = Field(default=0.8, description="Opacity of the dark gradient overlay (0.0 to 1.0). Use lower values if background is dark, higher if bright.")
    text_position: str = Field(default="left", description="left, center, or right")

class AIGenerationResponse(BaseModel):
    content: ContentContent
    visual_direction: VisualDirection
    image_prompt: str = Field(description="A highly detailed image generation prompt for Stable Diffusion based on the visual_direction.")
    negative_prompt: str = Field(description="Negative prompt to prevent unwanted elements (e.g., text, logos, watermarks).")
    design_instructions: DesignInstructions
