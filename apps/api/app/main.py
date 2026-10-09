import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import ContentPost, ContentVersion
from pydantic import BaseModel
from .ai_service import ai_service
from .image_service import image_service
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="HadesReality Marketing API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://[IP_ADDRESS]"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],
)

# This lets Next.js view the images in the generated_images folder
app.mount("/images", StaticFiles(directory="generated_images"), name="images")


class PostCreate(BaseModel):
    topic: str
    title: str = None


@app.get("/")
def read_root():
    return {"message": "Welcome to HadesReality ContentOps API"}


@app.post("/api/content")
def create_content(post: PostCreate, db: Session = Depends(get_db)):
    # 1. Create the new post
    db_post = ContentPost(
        topic=post.topic, title=post.title, status="GENERATING")
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    try:
        # 2. Ask the AI to write the content
        ai_result = ai_service.generate_post(post.topic, db)

        # 3. If the AI was successful, save its work and create the image
        if ai_result:
            # Save Context
            from .models import ContentContext
            ctx_data = ai_result.get("context", {}).get("classification", {})
            db_context = ContentContext(
                content_post_id=db_post.id,
                content_type=ctx_data.get("content_type"),
                category=ctx_data.get("category"),
                event=ctx_data.get("event"),
                season=ctx_data.get("season")
            )
            db.add(db_context)

            # Generate Image
            image_path = image_service.generate_image(
                ai_result.get("hook", "Check this out!"),
                ai_result.get("image_prompt"),
                negative_prompt=ai_result.get("negative_prompt"),
                design_instructions=ai_result.get("design_instructions")
            )
            print(f"SUCCESS! Image saved at: {image_path}")

            new_version = ContentVersion(
                content_post_id=db_post.id,
                version_number=1,
                caption=ai_result.get("caption"),
                image_prompt=ai_result.get("image_prompt"),
                negative_prompt=ai_result.get("negative_prompt"),
                brand_dna_version=ai_result.get("brand_dna_version"),
                image_path=image_path,
                status="PENDING_REVIEW"
            )
            db.add(new_version)

            # 4. Update the main post status
            db_post.status = "PENDING_REVIEW"
            db.commit()

            return {"message": "Content generated and ready for review", "post_id": db_post.id}
        else:
            # If the AI failed
            db_post.status = "FAILED"
            db.commit()
            return {"message": "AI generation failed", "post_id": db_post.id}
            
    except Exception as e:
        print(f"Content generation failed: {e}")
        db_post.status = "FAILED"
        db.commit()
        return {"error": str(e), "post_id": db_post.id}


@app.get("/api/content")
def list_content(db: Session = Depends(get_db)):
    posts = db.query(ContentPost).all()
    return posts


@app.get("/api/content/{post_id}")
def get_post_details(post_id: str, db: Session = Depends(get_db)):
    # Find the post and its newest version
    post = db.query(ContentPost).filter(ContentPost.id == post_id).first()
    version = db.query(ContentVersion).filter(ContentVersion.content_post_id == post_id).order_by(ContentVersion.version_number.desc()).first()
    
    if not post or not version:
        return {"error": "Not found"}
    
    image_url = version.image_path
    if image_url and not image_url.startswith("http"):
        image_filename = os.path.basename(version.image_path)
        image_url = f"http://localhost:8000/images/{image_filename}"
        
    return {
        "id": post.id,
        "topic": post.topic,
        "status": post.status,
        "caption": version.caption,
        "image_url": image_url,
        "scheduled_for": post.scheduled_for.isoformat() if post.scheduled_for else None
    }

class ApprovePayload(BaseModel):
    scheduled_time: str = None

@app.post("/api/content/{post_id}/approve")
def approve_content(post_id: str, payload: ApprovePayload = None, db: Session = Depends(get_db)):
    post = db.query(ContentPost).filter(ContentPost.id == post_id).first()
    version = db.query(ContentVersion).filter(ContentVersion.content_post_id == post_id).order_by(ContentVersion.version_number.desc()).first()
    
    if post and version:
        post.status = "APPROVED"
        version.status = "APPROVED"
        
        if payload and payload.scheduled_time:
            from datetime import datetime
            # Basic parsing of ISO format or similar
            try:
                post.scheduled_for = datetime.fromisoformat(payload.scheduled_time.replace("Z", "+00:00"))
            except ValueError:
                pass # ignore if parsing fails for now
                
        db.commit()
        
        # --- NEW CODE: Send Webhook to n8n ---
        import urllib.request
        import json
        import os
        
        webhook_url = "http://localhost:5678/webhook-test/5317da35-fc6c-47d2-b506-6ddfac76a35e"
        
        image_url = version.image_path
        if image_url and not image_url.startswith("http"):
            image_filename = os.path.basename(version.image_path)
            image_url = f"http://localhost:8000/images/{image_filename}"
        
        webhook_payload = {
            "post_id": str(post.id),
            "topic": post.topic,
            "caption": version.caption,
            "image_url": image_url,
            "scheduled_time": payload.scheduled_time if payload else None
        }
        
        try:
            req = urllib.request.Request(webhook_url, method="POST")
            req.add_header('Content-Type', 'application/json')
            data = json.dumps(webhook_payload).encode('utf-8')
            urllib.request.urlopen(req, data=data)
            print("Successfully sent webhook to n8n!")
        except Exception as e:
            print(f"Failed to send webhook to n8n: {e}")
        # ------------------------------------
        
        return {"message": "Post successfully approved!"}
    
    return {"error": "Could not find post to approve."}

class FeedbackCreate(BaseModel):
    feedback: str

@app.post("/api/content/{post_id}/revise")
def revise_content(post_id: str, payload: FeedbackCreate, db: Session = Depends(get_db)):
    post = db.query(ContentPost).filter(ContentPost.id == post_id).first()
    version = db.query(ContentVersion).filter(ContentVersion.content_post_id == post_id).order_by(ContentVersion.version_number.desc()).first()
    
    if not post or not version:
        return {"error": "Not found"}

    # 1. Ask the AI to revise the content based on feedback
    revised_result = ai_service.revise_post(
        topic=post.topic,
        current_caption=version.caption,
        current_image_prompt=version.image_prompt,
        feedback=payload.feedback,
        db=db
    )

    if revised_result:
        # 2. Generate a new image with the revised hook/prompt
        image_path = image_service.generate_image(
            revised_result.get("hook", "Check this out!"),
            revised_result.get("image_prompt"),
            negative_prompt=revised_result.get("negative_prompt"),
            design_instructions=revised_result.get("design_instructions")
        )
            
        # 3. Create the new version
        new_version = ContentVersion(
            content_post_id=post.id,
            version_number=version.version_number + 1,
            caption=revised_result.get("caption"),
            image_prompt=revised_result.get("image_prompt"),
            negative_prompt=revised_result.get("negative_prompt"),
            brand_dna_version=revised_result.get("brand_dna_version"),
            image_path=image_path,
            status="PENDING_REVIEW"
        )
        db.add(new_version)
        db.commit()
        
        return {"message": "Revision created successfully!", "version": new_version.version_number}
        
    return {"error": "AI revision failed."}
