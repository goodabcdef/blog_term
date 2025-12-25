from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from src.dependencies import get_db
from src.models.user import User
from src.models.blog import Post, Tag, Like, Comment
from src.schemas.extras import TagCreate, TagResponse
from src.schemas.blog import PostResponse, CommentResponse
from src.routers.blog import get_current_user

# 간단한 스키마들은 여기 정의하거나 src/schemas로 옮겨도 됨
class ReportCreate(BaseModel):
    reason: str

class Notification(BaseModel):
    id: int
    message: str
    is_read: bool

class CommentUpdate(BaseModel):
    content: str

router = APIRouter(tags=["Features"])

# --- [ Tags ] ---
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

# --- [ Likes & Social ] ---
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

@router.get("/posts/filter/popular", response_model=List[PostResponse])
def get_popular_posts(db: Session = Depends(get_db)):
    return db.query(Post).limit(5).all()

@router.get("/posts/filter/my", response_model=List[PostResponse])
def get_my_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Post).filter(Post.owner_id == current_user.id).all()

# --- [ Comments Actions ] ---
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

# --- [ Others ] ---
@router.post("/posts/{post_id}/report")
def report_post(post_id: int, report: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"message": "Report received", "post_id": post_id, "reason": report.reason}

@router.get("/notifications", response_model=List[Notification])
def get_notifications(current_user: User = Depends(get_current_user)):
    return [{"id": 1, "message": "Welcome!", "is_read": False}]

@router.post("/notifications/{noti_id}/read")
def read_notification(noti_id: int, current_user: User = Depends(get_current_user)):
    return {"message": "Marked as read"}