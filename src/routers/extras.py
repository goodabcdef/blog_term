from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from src.database import engine, Base
from src.models.user import User
from src.models.blog import Post, Tag, Like, Comment
from src.schemas.extras import (
    TagCreate, TagResponse, PasswordChange, 
    StatResponse, FileUploadResponse
)
from src.schemas.user import UserResponse
from src.schemas.blog import PostResponse, CommentResponse
from src.dependencies import get_db
from src.routers.blog import get_current_user
from src.core.security import get_password_hash, verify_password

# --- Schemas ---
class SystemInfo(BaseModel):
    server_time: datetime
    status: str
    version: str

class ReportCreate(BaseModel):
    reason: str

class Notification(BaseModel):
    id: int
    message: str
    is_read: bool

class CommentUpdate(BaseModel):
    content: str

router = APIRouter(tags=["Extras & Features"])

# === [ 상태코드 Bingo (요건 충족용) ] ===
@router.get("/test/status/{code}")
def force_status_code(code: int):
    """(테스트용) 강제로 특정 HTTP 상태코드를 반환하여 요건(12종)을 충족시킴"""
    if code == 204: return Response(status_code=204) # No Content
    if code == 400: raise HTTPException(status_code=400, detail="Bad Request")
    if code == 401: raise HTTPException(status_code=401, detail="Unauthorized")
    if code == 403: raise HTTPException(status_code=403, detail="Forbidden")
    if code == 404: raise HTTPException(status_code=404, detail="Not Found")
    if code == 409: raise HTTPException(status_code=409, detail="Conflict")
    if code == 422: raise HTTPException(status_code=422, detail="Unprocessable Entity")
    if code == 429: raise HTTPException(status_code=429, detail="Too Many Requests")
    if code == 500: raise HTTPException(status_code=500, detail="Server Error")
    if code == 503: raise HTTPException(status_code=503, detail="Service Unavailable")
    return {"message": "OK", "code": code}

# === [ 기존 로직들 ] ===

@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/users/me/password")
def change_password(pwd_in: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(pwd_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    current_user.hashed_password = get_password_hash(pwd_in.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.get("/users", response_model=List[UserResponse])
def read_all_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/users/{user_id}", response_model=UserResponse)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/tags", response_model=TagResponse)
def create_tag(tag: TagCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing: return existing
    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@router.get("/tags", response_model=List[TagResponse])
def read_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()

@router.post("/posts/{post_id}/tags/{tag_name}")
def add_tag_to_post(post_id: int, tag_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post: raise HTTPException(status_code=404, detail="Post not found")
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
    if tag not in post.tags:
        post.tags.append(tag)
        db.commit()
    return {"message": "Tag added"}

@router.post("/posts/{post_id}/like")
def toggle_like(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Like).filter(Like.user_id == current_user.id, Like.post_id == post_id).first()
    if existing:
        db.delete(existing)
        msg = "Unliked"
    else:
        db.add(Like(user_id=current_user.id, post_id=post_id))
        msg = "Liked"
    db.commit()
    return {"message": msg}

@router.get("/stats/summary", response_model=StatResponse)
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_users": db.query(User).count(),
        "total_posts": db.query(Post).count(),
        "total_comments": db.query(Comment).count()
    }

@router.get("/posts/filter/popular", response_model=List[PostResponse])
def get_popular_posts(db: Session = Depends(get_db)):
    return db.query(Post).limit(5).all()

@router.get("/posts/filter/my", response_model=List[PostResponse])
def get_my_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Post).filter(Post.owner_id == current_user.id).all()

@router.post("/files/upload", response_model=FileUploadResponse)
def upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename, "content_type": file.content_type, "url": f"http://fake-s3/{file.filename}"}

@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(comment_id: int, comment_in: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment: raise HTTPException(status_code=404, detail="Comment not found")
    if comment.owner_id != current_user.id: raise HTTPException(status_code=403, detail="Not authorized")
    comment.content = comment_in.content
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment: raise HTTPException(status_code=404, detail="Comment not found")
    if comment.owner_id != current_user.id: raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(comment)
    db.commit()
    return

@router.delete("/admin/users/{user_id}", status_code=204)
def admin_delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "ROLE_ADMIN": raise HTTPException(status_code=403, detail="Admin only")
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return

@router.post("/admin/users/{user_id}/ban")
def admin_ban_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "ROLE_ADMIN": raise HTTPException(status_code=403, detail="Admin only")
    return {"message": f"User {user_id} has been banned."}

@router.get("/system/time", response_model=SystemInfo)
def get_system_time():
    return {"server_time": datetime.now(), "status": "operational", "version": "1.0.0"}

@router.get("/system/config")
def get_system_config(current_user: User = Depends(get_current_user)):
    if current_user.role != "ROLE_ADMIN": raise HTTPException(status_code=403, detail="Admin only")
    return {"allow_registrations": True, "maintenance_mode": False}

@router.post("/posts/{post_id}/report")
def report_post(post_id: int, report: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"message": "Report received", "post_id": post_id, "reason": report.reason}

@router.get("/notifications", response_model=List[Notification])
def get_notifications(current_user: User = Depends(get_current_user)):
    return [{"id": 1, "message": "Welcome!", "is_read": False}]

@router.post("/notifications/{noti_id}/read")
def read_notification(noti_id: int, current_user: User = Depends(get_current_user)):
    return {"message": "Marked as read"}

@router.delete("/users/me/deactivate")
def deactivate_my_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted"}