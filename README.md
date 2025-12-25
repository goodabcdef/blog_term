# 📘 Term Project: High-Performance Blog API Server

## 1. 프로젝트 개요
본 프로젝트는 대규모 트래픽 처리를 고려하여 설계된 **RESTful 블로그 API 서버**입니다.
사용자 인증, 게시글 관리, 소셜 인터랙션(좋아요, 댓글), 시스템 관리 기능을 모듈식으로 구현하였으며, **Docker** 기반의 마이크로서비스 아키텍처와 **Redis** 캐싱을 통해 성능을 극대화했습니다.

### 🎯 주요 기능
- **고급 인증 시스템:** JWT (Access/Refresh) 토큰 및 **Firebase 소셜 로그인** 연동
- **권한 관리 (RBAC):** 일반 유저(`ROLE_USER`)와 관리자(`ROLE_ADMIN`)의 철저한 권한 분리
- **컨텐츠 관리:** 게시글/댓글 CRUD, 태그(Tag) 시스템, 이미지 업로드 시뮬레이션
- **성능 최적화:** **Redis**를 활용한 Global Rate Limiting (DDoS 방지) 및 조회수 캐싱
- **자동화 시스템:** GitHub Actions를 통한 **CI(Continuous Integration)** 파이프라인 구축
- **확장성:** **Docker Compose**를 이용한 App, DB, Redis 컨테이너 오케스트레이션

---

## 2. 실행 방법 (Getting Started)

### 🐳 Docker 실행 (권장)
Docker가 설치된 환경에서는 단 한 줄의 명령어로 DB, Redis, App을 모두 실행할 수 있습니다.

```bash
# 1. 환경 변수 설정 (필수)
# 제공된 .env.example을 복사하여 .env 파일을 생성하고 실제 값을 입력하세요.
cp .env.example .env

# 2. 서비스 실행 (빌드 및 데몬 실행)
# 코드가 수정되었을 경우 --build 옵션을 사용하여 재빌드합니다.
docker compose up -d --build

# 3. 로그 확인
docker compose logs -f app
```

### 💻 로컬 파이썬 실행 (개발용)
Docker 없이 로컬 환경에서 직접 구동하려면 아래 순서를 따릅니다.
(전제조건: 로컬에 MySQL(3306), Redis(6379)가 실행 중이어야 합니다.)

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 서버 실행
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
현재 JCloud 클라우드 서버에 배포되어 운영 중입니다.

- **Base URL:** `http://113.198.66.68:10235`
- **Swagger UI (API 문서):** [http://113.198.66.68:10235/swagger-ui](http://113.198.66.68:10235/swagger-ui)
- **Health Check:** `http://113.198.66.68:10235/health`

---

## 5. API 상세 명세 (API Reference)
본 프로젝트는 **RESTful 원칙**을 준수하며, 기능별로 모듈화된 라우터(`routers/`)를 통해 엔드포인트를 제공합니다.

### 🔐 1. 인증 (Authentication)
JWT 토큰 발급 및 보안 관련 기능을 담당합니다.
| Method | Endpoint | 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | 이메일/비밀번호 로그인 (JWT 발급) | All |
| `POST` | `/auth/refresh` | 만료된 Access Token 재발급 | All |
| `POST` | `/auth/google` | Firebase 연동 구글 소셜 로그인 | All |

### 📝 2. 게시글 (Blog Posts)
핵심 컨텐츠인 게시글을 관리합니다.
| Method | Endpoint | 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `GET` | `/posts` | 전체 게시글 목록 조회 (페이지네이션) | All |
| `POST` | `/posts` | 게시글 작성 | User+ |
| `GET` | `/posts/{id}` | 게시글 상세 조회 | All |

### ❤️ 3. 기능 및 소셜 (Features & Social)
태그, 좋아요, 댓글 등 부가 기능입니다.
| Method | Endpoint | 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `POST` | `/features/tags` | 새로운 태그 생성 | User+ |
| `POST` | `/features/posts/{id}/like` | 좋아요 토글 (Like/Unlike) | User+ |
| `POST` | `/posts/{id}/comments` | 댓글 작성 | User+ |
| `PUT` | `/features/comments/{id}` | 댓글 수정 | Owner |
| `DELETE` | `/features/comments/{id}` | 댓글 삭제 | Owner |

### 👤 4. 사용자 관리 (Users)
회원 정보 조회 및 개인 설정 관리입니다.
| Method | Endpoint | 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `GET` | `/users/me` | 내 정보 조회 | User+ |
| `PUT` | `/users/me/password` | 비밀번호 변경 | User+ |
| `DELETE` | `/users/me/deactivate` | 회원 탈퇴 | User+ |
| `GET` | `/users` | 전체 유저 목록 조회 | All |

### 👑 5. 관리자 전용 (Administration)
관리자(`ROLE_ADMIN`)만 접근 가능한 시스템 관리 기능입니다.
| Method | Endpoint | 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `GET` | `/admin/stats` | 전체 통계(유저/글/댓글 수) 조회 | **Admin** |
| `DELETE` | `/admin/users/{id}` | 특정 유저 강제 삭제 | **Admin** |
| `POST` | `/admin/users/{id}/ban` | 특정 유저 정지 처리 | **Admin** |

### ⚙️ 6. 시스템 (System)
서버 상태 모니터링 및 유틸리티입니다.
| Method | Endpoint | 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | 서버 및 Redis 연결 상태 점검 (Health Check) | All |
| `GET` | `/system/time` | 서버 시간 및 버전 정보 확인 | All |

---

## 6. 예제 계정 (Test Accounts)
서버 초기 구동 시 `seed_data.py`를 통해 생성된 테스트 계정입니다.

### 👤 일반 사용자 (User)
- **ID:** `user1@example.com`
- **PW:** `password123`
- **Role:** `ROLE_USER`

### 👑 관리자 (Admin)
- **ID:** `user0@example.com`
- **PW:** `password123`
- **Role:** `ROLE_ADMIN` (관리자 페이지 접근 가능)

---

## 7. 성능 및 보안 아키텍처

### 🚀 Performance
1.  **Redis Caching:** 조회수 증가 로직과 세션 관리에 In-Memory DB인 Redis를 사용하여 DB 부하 최소화.
2.  **Eager Loading:** SQLAlchemy의 `joinedload`를 사용하여 N+1 쿼리 문제 원천 차단.
3.  **Connection Pooling:** DB 연결을 효율적으로 재사용하여 대량의 요청 처리 가능.

### 🛡️ Security
1.  **Rate Limiting:** 특정 IP의 과도한 요청을 Redis 기반으로 차단하여 DDoS 공격 방어.
2.  **Secure Password:** `bcrypt` 알고리즘을 사용하여 비밀번호를 단방향 암호화하여 저장.
3.  **Input Validation:** Pydantic을 활용한 엄격한 데이터 타입 검증으로 SQL Injection 방지.

---

## 8. CI/CD 자동화 (Bonus)
안정적인 배포를 위해 **GitHub Actions**를 활용한 CI 파이프라인을 구축하였습니다.

- **워크플로우:** 코드가 Push되거나 PR이 생성되면 자동으로 실행.
- **주요 작업:**
    1. Python 3.10 환경 설정 및 의존성 설치
    2. **MySQL 8.0 & Redis 컨테이너** 자동 구동 (테스트 환경)
    3. 빌드 검증 및 `pytest` 자동 실행
- **확인 방법:** GitHub 저장소 상단의 **[Actions]** 탭에서 `CI (Build & Test)` 성공 내역(✅) 확인 가능.