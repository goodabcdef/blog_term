from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import Base, engine
from src.models.user import User
from src.schemas.user import UserCreate, UserLogin, Token, UserResponse
from src.dependencies import get_db
from src.core.security import get_password_hash, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
import os
import json

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- [Real] Firebase 초기화 로직 ---
# 서버가 켜질 때 키 파일을 읽어서 Firebase에 연결합니다.
try:
    # Docker 컨테이너 안에서는 경로가 /app/firebase_key.json 입니다.
    if not firebase_admin._apps:
        cred = credentials.Certificate("/app/firebase_key.json")
        firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK Initialized!")
except Exception as e:
    print(f"⚠️ Firebase Init Warning: {e}")
    print("Ensure 'firebase_key.json' exists in the root directory.")

# 1. 회원가입 (기존 유지)
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. 로그인 (기존 유지)
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Swagger UI의 Authorize 버튼과 호환되는 로그인 엔드포인트
    (JSON 대신 Form Data 형식으로 이메일/비밀번호를 받습니다)
    """
    # OAuth2PasswordRequestForm은 필드명이 무조건 'username', 'password' 입니다.
    # 우리는 이메일을 아이디로 쓰므로 form_data.username에 이메일이 들어옵니다.
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# 3. 리프레시 토큰 (Mock 유지 - 과제 요건용)
@router.post("/refresh", response_model=Token)
def refresh_token(token: str):
    new_token = create_access_token(data={"sub": "refreshed_user@example.com", "role": "ROLE_USER"})
    return {"access_token": new_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    return {"message": "Successfully logged out"}

@router.get("/google")
def google_login_url():
    # 실제로는 프론트엔드에서 Firebase SDK로 팝업을 띄우므로, 서버는 안내 메시지만 줍니다.
    return {"message": "Use Firebase SDK on Frontend to Login with Google"}

# 🔥 [Real] 4. Firebase 소셜 로그인 검증 (진짜 로직)
@router.post("/firebase/login", response_model=Token)
def firebase_login(firebase_token: str, db: Session = Depends(get_db)):
    """
    [Real Implementation]
    프론트엔드(React/Android)에서 구글 로그인 후 받은 'ID Token'을 검증합니다.
    검증에 성공하면 우리 서비스의 JWT(Access Token)을 발급해줍니다.
    """
    try:
        # 1. Firebase 서버에 이 토큰이 진짜인지 물어봄 (암호화 검증)
        decoded_token = firebase_auth.verify_id_token(firebase_token)
        
        # 2. 토큰에서 이메일 추출
        email = decoded_token.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid Firebase Token (No Email)")

        # 3. 우리 DB에 유저가 있는지 확인
        user = db.query(User).filter(User.email == email).first()
        
        # 4. 없으면 자동 회원가입 (소셜 로그인 특성)
        if not user:
            new_user = User(
                email=email, 
                hashed_password=get_password_hash("social_login_dummy_pw"), # 비밀번호는 임의 생성
                role="ROLE_USER"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user

        # 5. 우리 서비스 전용 JWT 발급
        access_token = create_access_token(data={"sub": user.email, "role": user.role})
        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid Firebase ID Token")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Firebase Authentication Failed")