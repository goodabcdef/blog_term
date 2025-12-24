FROM python:3.10-slim

WORKDIR /app

# 패키지 설치 (카카오 미러 사용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirror.kakao.com/pypi/simple

# 소스 복사
COPY . .

# 실행 (8080 포트로 실행)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]