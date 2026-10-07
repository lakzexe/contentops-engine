from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import ContentPost, ContentVersion
from pydantic import BaseModel
from .ai_service import ai_service
from .image_service import image_service
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="HadesReality Marketing API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://[IP_ADDRESS]"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],
)


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

    # 2. Ask the AI to write the content (using our Knowledge Base!)
    ai_result = ai_service.generate_post(post.topic)

    # 3. If the AI was successful, save its work and create the image
    if ai_result:
        # --> THIS IS THE NEW LINE! Generate the image using the AI's hook!
        image_path = image_service.generate_image(
            ai_result.get("hook", "Check this out!"))
        print(f"SUCCESS! Image saved at: {image_path}")

        new_version = ContentVersion(
            content_post_id=db_post.id,
            version_number=1,
            caption=ai_result.get("caption"),
            # We still save the prompt just in case
            image_prompt=ai_result.get("image_prompt"),
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


@app.get("/api/content")
def list_content(db: Session = Depends(get_db)):
    posts = db.query(ContentPost).all()
    return posts
