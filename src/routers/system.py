from fastapi import APIRouter, HTTPException, Response, File, UploadFile
from datetime import datetime
from pydantic import BaseModel
from src.schemas.extras import FileUploadResponse

# 스키마 정의 (다른 곳에서 안 쓰면 여기에 둬도 무방)
class SystemInfo(BaseModel):
    server_time: datetime
    status: str
    version: str

router = APIRouter(tags=["System"])

@router.get("/system/time", response_model=SystemInfo)
def get_system_time():
    """서버 시간 및 버전 확인"""
    return {"server_time": datetime.now(), "status": "operational", "version": "1.0.0"}

@router.post("/files/upload", response_model=FileUploadResponse)
def upload_file(file: UploadFile = File(...)):
    """파일 업로드 (Mock)"""
    return {"filename": file.filename, "content_type": file.content_type, "url": f"http://fake-s3/{file.filename}"}

@router.get("/test/status/{code}")
def force_status_code(code: int):
    """(테스트용) 강제로 특정 HTTP 상태코드 반환"""
    status_map = {
        204: 204, 400: 400, 401: 401, 403: 403, 404: 404,
        409: 409, 422: 422, 429: 429, 500: 500, 503: 503
    }
    
    if code in status_map:
        if code == 204: return Response(status_code=204)
        raise HTTPException(status_code=code, detail=f"Forced {code}")
        
    return {"message": "OK", "code": code}