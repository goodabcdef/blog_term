from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- User Profile ---
class UserProfileUpdate(BaseModel):
    is_active: Optional[bool] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# --- Tags ---
class TagCreate(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

# --- Likes ---
class LikeResponse(BaseModel):
    post_id: int
    like_count: int
    liked_by_me: bool

# --- Stats ---
class StatResponse(BaseModel):
    total_users: int
    total_posts: int
    total_comments: int

# --- File Upload ---
class FileUploadResponse(BaseModel):
    filename: str
    content_type: str
    url: str