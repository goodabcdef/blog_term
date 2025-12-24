# 2025-2 Term Project: Blog Service API

FastAPI와 Docker를 활용하여 구축한 블로그 서비스 REST API입니다.
게시글/댓글 CRUD, 태그, 좋아요, 검색, 통계, 관리자 기능 등을 포함하여 **30개 이상의 엔드포인트**를 제공합니다.

## 🚀 기술 스택
- **Language**: Python 3.10
- **Framework**: FastAPI
- **Database**: MySQL 8.0
- **Cache**: Redis
- **Container**: Docker & Docker Compose

## 🛠 실행 방법

### 1. 사전 요구사항
- Docker 및 Docker Compose가 설치되어 있어야 합니다.

### 2. 실행 명령어 (로컬/서버 공통)
```bash
# 1. 저장소 클론
git clone [본인_깃허브_주소]
cd term-project

# 2. 환경 변수 설정 (.env.example 복사)
cp .env.example .env

# 3. 서비스 실행 (빌드 및 실행)
docker compose up -d --build

# 4. 시드 데이터 생성 (테스트 데이터 200개 자동 생성)
docker compose exec app python seed_data.py
```

## 🔗 접속 주소
- **API 문서 (Swagger UI)**: `http://113.198.66.68:10235/swagger-ui`
- **API 문서 (ReDoc)**: `http://113.198.66.68:10235/redoc`
- **Health Check**: `http://113.198.66.68:10235/health`

## 🔑 테스트 계정
시드 데이터를 실행하면 아래 계정이 자동 생성됩니다.

| 역할 | 이메일 | 비밀번호 | 비고 |
|---|---|---|---|
| **관리자 (Admin)** | `user0@example.com` | `password123` | 모든 권한 보유 |
| **일반 유저 (User)** | `user1@example.com` | `password123` | 일반적인 CRUD 가능 |

## 📋 API 요약 (총 33개 엔드포인트)

| 태그 | 메서드 | 경로 | 설명 | 권한 |
|---|---|---|---|---|
| **Auth** | POST | `/auth/signup` | 회원가입 | 누구나 |
| **Auth** | POST | `/auth/login` | 로그인 (JWT 발급) | 누구나 |
| **Auth** | POST | `/auth/refresh` | 토큰 갱신 | 누구나 |
| **Blog** | GET | `/posts` | 게시글 목록 (검색/정렬/페이징) | 누구나 |
| **Blog** | POST | `/posts` | 게시글 작성 | 로그인 |
| **Blog** | POST | `/posts/{id}/comments` | 댓글 작성 | 로그인 |
| **Extras** | POST | `/posts/{id}/like` | 좋아요 토글 | 로그인 |
| **Extras** | GET | `/stats/summary` | 전체 통계 조회 | 로그인 |
| **Extras** | POST | `/files/upload` | 파일 업로드 | 로그인 |
| **Admin** | DELETE | `/admin/users/{id}` | 유저 강제 탈퇴 | 관리자 |

*(자세한 명세는 Swagger UI를 참고하세요)*

## 🔒 보안 및 성능 고려사항
1. **JWT 인증**: Access/Refresh 토큰 분리 및 검증
2. **비밀번호 암호화**: bcrypt 알고리즘 사용
3. **환경변수 분리**: 민감 정보는 `.env`로 관리 (Repo 제외)
4. **Redis 캐싱**: 세션 관리 및 빈번한 조회 데이터 캐싱 준비
5. **Rate Limiting**: Nginx/Code 레벨에서의 요청 제한 고려

