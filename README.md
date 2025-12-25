# 📘 Term Project: High-Performance Blog API Server

## 1. 프로젝트 개요
본 프로젝트는 대규모 트래픽 처리를 고려하여 설계된 **RESTful 블로그 API 서버**입니다.
사용자 인증부터 게시글 관리, 소셜 기능(좋아요, 댓글), 그리고 시스템 관리까지 포함된 완전한 백엔드 솔루션을 제공합니다.

### 🎯 주요 기능
- **고급 인증 시스템:** JWT 기반 Access/Refresh 토큰 처리 및 **Firebase 소셜 로그인** 연동
- **권한 관리 (RBAC):** 일반 유저(`ROLE_USER`)와 관리자(`ROLE_ADMIN`)의 엄격한 권한 분리
- **컨텐츠 관리:** 게시글/댓글 CRUD, 태그(Tag) 시스템, 좋아요(Like) 토글
- **성능 최적화:** **Redis**를 활용한 Global Rate Limiting (DDOS 방지) 및 조회수 캐싱
- **확장성:** **Docker Compose** 기반의 컨테이너 환경 구성 (App, MySQL, Redis)

---

## 2. 실행 방법 (Getting Started)

### 🐳 Docker 실행 (권장)
Docker가 설치된 환경에서는 단 한 줄의 명령어로 DB, Redis, App을 모두 실행할 수 있습니다.

```bash
# 1. 환경 변수 설정 (필수)
# 제공된 .env.example을 복사하여 .env 파일을 생성하고 실제 값을 입력하세요.
cp .env.example .env

# 2. 서비스 실행 (빌드 및 데몬 실행)
docker compose up -d --build

# 3. 로그 확인
docker compose logs -f app
```

### 💻 로컬 파이썬 실행 (개발용)
Docker 없이 로컬 환경에서 직접 구동하려면 아래 순서를 따릅니다.
(전제조건: 로컬에 MySQL(3306), Redis(6379)가 실행 중이어야 합니다.)

```bash
# 1. 가상환경 생성 및 활성화 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 데이터베이스 마이그레이션 (테이블 생성)
# (본 프로젝트는 SQLAlchemy가 시작 시 자동으로 테이블을 생성하므로 별도 명령어가 필요 없습니다.)

# 4. 서버 실행
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## 3. 환경변수 설명 (.env)
`.env.example` 파일을 참고하여 아래 변수들을 설정해야 합니다.

| 변수명 | 설명 | 예시 |
|---|---|---|
| `MYSQL_USER` | DB 접속 계정 | `user` |
| `MYSQL_PASSWORD` | DB 접속 비밀번호 | `password` |
| `DATABASE_URL` | SQLAlchemy 접속 문자열 | `mysql+pymysql://user:password@db:3306/termdb` |
| `SECRET_KEY` | JWT 서명용 비밀키 | `term_project_super_secret_key` |
| `REDIS_URL` | Redis 접속 주소 | `redis://redis:6379/0` |
| `FIREBASE_CRED_PATH` | Firebase 키 파일 경로 | `/app/firebase_key.json` |

---

## 4. 배포 주소 (Deployment)
현재 JCloud 서버에 배포되어 운영 중입니다.

- **Base URL:** `http://113.198.66.68:10235`
- **Swagger UI (API 문서):** [http://113.198.66.68:10235/swagger-ui](http://113.198.66.68:10235/swagger-ui)
- **Health Check:** `http://113.198.66.68:10235/health`

---

## 5. 인증 플로우 및 권한 (Auth & RBAC)

### 🔐 인증 방식
1. **일반 로그인:** Email/Password → 서버 검증 → `Access Token` + `Refresh Token` 발급
2. **소셜 로그인:** Client (Google Login) → Firebase ID Token 획득 → 서버 전송 → 검증 후 자체 JWT 발급
3. **API 요청:** Header에 `Authorization: Bearer <Access Token>` 포함하여 요청

### 👮‍♂️ 역할 및 권한표
| API 구분 | ROLE_USER (일반) | ROLE_ADMIN (관리자) |
|---|---|---|
| **게시글 조회** | ✅ 전체 가능 | ✅ 전체 가능 |
| **게시글 작성** | ✅ 본인 글만 | ✅ 전체 가능 |
| **게시글 삭제** | ✅ 본인 글만 | ✅ **모든 유저의 글 삭제 가능** |
| **댓글/좋아요** | ✅ 가능 | ✅ 가능 |
| **관리자 페이지** | ❌ 접근 불가 (`403 Forbidden`) | ✅ 유저 관리, 통계 조회 가능 |

---

## 6. 예제 계정 (Test Accounts)
서버 실행 시 `seed_data.py`에 의해 자동으로 생성되는 테스트 계정입니다.

### 👤 일반 사용자 (User)
- **ID:** `user1@example.com`
- **PW:** `password123`
- **설명:** 일반적인 게시글 작성, 수정, 댓글 달기 테스트용

### 👑 관리자 (Admin)
- **ID:** `user0@example.com`
- **PW:** `password123`
- **설명:** `/admin` 엔드포인트 접근 및 강제 삭제 권한 테스트용

---

## 7. DB 연결 정보 (테스트용)
채점 및 테스트를 위해 DB에 직접 접속해야 할 경우 아래 정보를 사용하십시오.

- **Host:** `113.198.66.68`
- **Port:** `3306` (Docker 내부), 외부 접속 시 포트 확인 필요
- **Database:** `termdb`
- **User:** `root` (관리자) / `user` (앱 전용)
- **Password:** `rootpassword` / `password`

---

## 8. 엔드포인트 요약

| Method | Endpoint | 설명 | 권한 |
|---|---|---|---|
| `POST` | `/auth/login` | 일반 로그인 (JWT 발급) | Any |
| `POST` | `/auth/refresh` | 토큰 갱신 | Any |
| `GET` | `/posts` | 게시글 목록 (페이지네이션) | Any |
| `POST` | `/posts` | 게시글 작성 | User+ |
| `POST` | `/posts/{id}/like` | 게시글 좋아요 토글 | User+ |
| `GET` | `/admin/stats` | 전체 통계 조회 | **Admin** |
| `GET` | `/health` | 서버 상태 확인 | Any |

*(전체 API 명세는 Swagger UI를 참고해주세요)*

---

## 9. 성능 및 보안 고려사항

### 🚀 성능 (Performance)
1. **Redis Caching:** 반복적인 DB 부하를 줄이기 위해 세션 및 조회수 로직에 Redis 적용
2. **Eager Loading:** SQLAlchemy의 `joinedload`를 사용하여 N+1 쿼리 문제 해결
3. **Pagination:** 대량의 데이터 조회 시 `offset/limit` 기반 페이지네이션 적용

### 🛡️ 보안 (Security)
1. **Rate Limiting:** Redis 기반의 미들웨어를 적용하여 특정 IP의 과도한 요청 차단 (DDoS 방어)
2. **Password Hashing:** `bcrypt` 알고리즘을 사용하여 비밀번호를 안전하게 암호화 저장
3. **Input Validation:** Pydantic을 사용하여 모든 입력값의 타입과 형식을 엄격하게 검증

---

## 10. 한계와 개선 계획
- **검색 기능:** 현재 MySQL `LIKE` 쿼리를 사용 중이나, 추후 **Elasticsearch**를 도입하여 전문 검색(Full-text Search) 성능을 개선할 계획입니다.
- **HTTPS 적용:** 현재 HTTP로 통신 중이나, 실서비스 배포 시 **SSL 인증서(Let's Encrypt)**를 적용하여 통신 보안을 강화할 예정입니다.

---

## 11. 가점 항목 구현 (Bonus Features)

### 🔄 CI/CD Pipeline (GitHub Actions)
안정적인 개발 및 배포를 위해 **GitHub Actions**를 활용한 CI(Continuous Integration) 파이프라인을 구축하였습니다.

- **기능:** 코드가 `main` 브랜치에 Push 되거나 Pull Request가 생성될 때마다 자동 실행
- **워크플로우 프로세스:**
    1. **Environment:** Ubuntu-latest 환경에서 실행
    2. **Services:** 테스트를 위해 격리된 MySQL 8.0 및 Redis 컨테이너 자동 구동
    3. **Install:** Python 3.10 환경 설정 및 `requirements.txt` 의존성 설치
    4. **Test:** 빌드 검증 및 테스트 스크립트 실행
- **설정 파일 위치:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- **확인 방법:** GitHub 저장소 상단의 **[Actions]** 탭에서 `CI (Build & Test)` 워크플로우의 성공 내역(✅)을 확인할 수 있습니다.