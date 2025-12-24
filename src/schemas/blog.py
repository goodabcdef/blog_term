from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from src.schemas.user import UserResponse

# --- Comment Schemas ---
class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    owner_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# --- Post Schemas ---
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(PostBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class PostListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[PostResponse]