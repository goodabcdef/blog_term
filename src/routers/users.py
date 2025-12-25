from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.dependencies import get_db
from src.models.user import User
from src.schemas.user import UserResponse
from src.schemas.extras import PasswordChange
from src.routers.blog import get_current_user
from src.core.security import get_password_hash, verify_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """내 정보 조회"""
    return current_user

@router.put("/me/password")
def change_password(pwd_in: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """비밀번호 변경"""
    if not verify_password(pwd_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    current_user.hashed_password = get_password_hash(pwd_in.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.delete("/me/deactivate")
def deactivate_my_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """회원 탈퇴"""
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted"}

@router.get("", response_model=List[UserResponse])
def read_all_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """전체 유저 조회 (관리자용 혹은 공개용)"""
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """특정 ID 유저 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user