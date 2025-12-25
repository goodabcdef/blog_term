from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.dependencies import get_db  # <--- 이렇게 바꿔주세요!
from src.models.user import User
from src.models.blog import Post, Comment
from src.schemas.extras import StatResponse
from src.routers.blog import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats", response_model=StatResponse)
def get_stats(db: Session = Depends(get_db)):
    """전체 통계 요약 (유저/글/댓글 수)"""
    return {
        "total_users": db.query(User).count(),
        "total_posts": db.query(Post).count(),
        "total_comments": db.query(Comment).count()
    }

@router.delete("/users/{user_id}", status_code=204)
def admin_delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """유저 강제 삭제"""
    if current_user.role != "ROLE_ADMIN": raise HTTPException(status_code=403, detail="Admin only")
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return

@router.post("/users/{user_id}/ban")
def admin_ban_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """유저 정지 처리"""
    if current_user.role != "ROLE_ADMIN": raise HTTPException(status_code=403, detail="Admin only")
    return {"message": f"User {user_id} has been banned."}

@router.get("/config")
def get_system_config(current_user: User = Depends(get_current_user)):
    """시스템 설정 조회"""
    if current_user.role != "ROLE_ADMIN": raise HTTPException(status_code=403, detail="Admin only")
    return {"allow_registrations": True, "maintenance_mode": False}