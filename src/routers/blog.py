from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import engine, Base
from src.models.blog import Post, Comment
from src.models.user import User
from src.schemas.blog import PostCreate, PostUpdate, PostResponse, PostListResponse, CommentCreate, CommentResponse
from src.dependencies import get_db
from src.core.security import create_access_token
from src.routers.auth import router as auth_router # 인증 의존성 재사용을 위해
from jose import jwt, JWTError
from src.core.config import settings
from fastapi.security import OAuth2PasswordBearer

# 테이블 생성
Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["Blog"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- 인증 도우미 함수 ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Post Endpoints ---

@router.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = Post(**post.dict(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/posts", response_model=PostListResponse)
def get_posts(
    page: int = 1, 
    size: int = 10, 
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    if keyword:
        query = query.filter(Post.title.contains(keyword) | Post.content.contains(keyword))
    
    total = query.count()
    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {"total": total, "page": page, "size": size, "items": posts}

@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if post_update.title:
        post.title = post_update.title
    if post_update.content:
        post.content = post_update.content
    
    db.commit()
    db.refresh(post)
    return post

@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(post)
    db.commit()
    return

# --- Comment Endpoints (Sub-resource) ---

@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_comment = Comment(content=comment.content, post_id=post_id, owner_id=current_user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments