from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import redis
import os

# [수정] Redis 연결 (필수 요건 충족용)
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

from src.routers import auth, blog, users, admin, system, features

app = FastAPI(
    title="Term Project Blog API",
    version="1.0.0",
    docs_url="/swagger-ui",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# [추가] Global Rate Limit (필수 요건: 도배 방지)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    # Redis를 이용해 1초에 10번 이상 요청 시 차단 (429 Too Many Requests)
    key = f"rate_limit:{client_ip}"
    current = redis_client.get(key)
    
    if current and int(current) > 10:
        return JSONResponse(
            status_code=429, # [상태코드 추가] 429
            content={"message": "Too Many Requests (Rate Limit Exceeded)"}
        )
    
    pipe = redis_client.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, 1) # 1초 뒤 초기화
    pipe.execute()
    
    response = await call_next(request)
    return response

# 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "timestamp": str(int(time.time())),
            "path": request.url.path,
            "status": 500,
            "code": "INTERNAL_SERVER_ERROR",
            "message": str(exc),
            "details": {}
        }
    )

app.include_router(auth.router)
app.include_router(blog.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(system.router)
app.include_router(features.router)

# 헬스체크 (Redis 상태도 확인)
@app.get("/health", status_code=200)
async def health_check():
    try:
        redis_ping = redis_client.ping()
        redis_status = "ok" if redis_ping else "error"
    except:
        redis_status = "down"
        
    return {
        "status": "ok", 
        "redis": redis_status,
        "version": "1.0.0", 
        "timestamp": str(int(time.time()))
    }

@app.get("/")
async def root():
    return {"message": "Welcome to Term Project API"}