from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import ForeignKey

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False) # e.g., ADMIN, MARKETING_MANAGER

class BrandDNA(Base):
    __tablename__ = "brand_dna"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(Integer, nullable=False, unique=True)
    colors = Column(JSONB, nullable=False)
    typography = Column(JSONB, nullable=False)
    layout = Column(JSONB, nullable=False)
    restrictions = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ContentContext(Base):
    __tablename__ = "content_contexts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_post_id = Column(UUID(as_uuid=True), ForeignKey("content_posts.id"), nullable=False)
    content_type = Column(String, nullable=True)
    category = Column(String, nullable=True)
    event = Column(String, nullable=True)
    season = Column(String, nullable=True)
    visual_mood = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ContentPost(Base):
    __tablename__ = "content_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=True)
    topic = Column(String, nullable=False)
    status = Column(String, nullable=False, default="DRAFT")
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ContentVersion(Base):
    __tablename__ = "content_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_post_id = Column(UUID(as_uuid=True), ForeignKey("content_posts.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    caption = Column(String, nullable=True)
    image_prompt = Column(String, nullable=True)
    negative_prompt = Column(String, nullable=True)
    brand_dna_version = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="PENDING_REVIEW")
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
