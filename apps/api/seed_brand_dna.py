import sys
import os
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import BrandDNA

def seed():
    db = SessionLocal()
    existing = db.query(BrandDNA).filter(BrandDNA.version == 1).first()
    if existing:
        print("Brand DNA v1 already exists.")
        return

    dna = BrandDNA(
        version=1,
        is_active=True,
        colors={
            "primary": "#051c11",
            "secondary": "#104128",
            "accent": "#00FFAA",
            "text_primary": "#FFFFFF",
            "text_secondary": "#e2e8f0"
        },
        typography={
            "heading_font": "Inter, sans-serif",
            "body_font": "Inter, sans-serif",
            "hook_weight": 900,
            "subtext_weight": 400
        },
        layout={
            "padding": "100px 80px",
            "logo_position": "footer_left",
            "hook_alignment": "left"
        },
        restrictions={
            "do_not_use": ["generic robotic themes", "low quality stock photos", "colors that clash with neon green"],
            "must_use": ["deep green gradients for readability", "neon green accents"]
        }
    )
    db.add(dna)
    db.commit()
    print("Successfully seeded Brand DNA v1!")

if __name__ == "__main__":
    seed()
