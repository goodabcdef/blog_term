# API Design Strategy & Specification

## 1. 디자인 원칙 (Design Principles)
본 프로젝트의 API는 **RESTful Architecture** 원칙을 준수하며, 클라이언트와 서버의 의존성을 줄이고 확장성을 고려하여 설계되었습니다.

### 1.1 Resource Oriented Architecture (ROA)
- URI는 동사(Verb)가 아닌 **명사(Resource)** 위주로 구성하였습니다. (e.g., `GET /users` O, `GET /getUsers` X)
- 행위는 HTTP Method(GET, POST, PUT, DELETE)를 통해 명시적으로 표현하였습니다.
- 계층적 리소스 구조를 채택하였습니다. (e.g., `POST /posts/{id}/comments`)

### 1.2 Stateless & Scalable
- 모든 요청은 **Stateless**하게 처리되며, 세션 상태를 서버 메모리에 저장하지 않습니다.
- 인증 상태는 **JWT (JSON Web Token)**을 통해 관리하여 Scale-out에 유리한 구조를 갖췄습니다.
- **Redis**를 활용한 Rate Limiting을 적용하여 트래픽 폭주 시 서버를 보호합니다.

---

## 2. 인증 및 보안 설계 (Authentication & Security)

### 2.1 Dual Token System (JWT)
- **Access Token**: 짧은 만료 시간(30분)을 가지며 API 접근 시 사용.
- **Refresh Token**: 긴 만료 시간(7일)을 가지며 Access Token 재발급 시 사용.
- **Role Based Access Control (RBAC)**:
    - `ROLE_USER`: 일반적인 CRUD 수행 가능.
    - `ROLE_ADMIN`: 시스템 설정, 유저 강제 탈퇴 등 관리자 권한 수행.

### 2.2 External Identity Provider (IdP)
- **Firebase Auth**와 연동하여 소셜 로그인(Google 등)의 확장성을 확보했습니다.
- 클라이언트로부터 전달받은 ID Token을 서버 측에서 검증(Verify) 후 자체 JWT를 발급하는 **Exchange Pattern**을 사용합니다.

---

## 3. 응답 및 에러 처리 표준 (Response Standards)

### 3.1 성공 응답 (Success)
- 리소스 조회 시 불필요한 래핑 없이 데이터 객체 또는 배열을 직접 반환하여 Payload 크기를 최적화했습니다.
- 생성(`201`) 및 삭제(`204`) 시 적절한 Status Code를 엄격하게 준수합니다.

### 3.2 에러 응답 (Error Handling)
모든 에러는 일관된 JSON 포맷을 반환하여 클라이언트가 예측 가능한 처리를 할 수 있도록 설계했습니다.

```json
{
  "timestamp": "2025-12-24T12:00:00Z",
  "path": "/api/posts",
  "status": 400,
  "code": "INVALID_PARAMETER",
  "message": "입력 값이 유효하지 않습니다.",
  "details": { "email": "이메일 형식이 잘못되었습니다." }
}
```

---

## 4. 데이터 처리 전략

### 4.1 Pagination & Sorting
- 대용량 데이터 조회 시 성능 저하를 막기 위해 `offset` 기반 페이지네이션을 적용했습니다.
- Query Parameter: `?page=1&size=10&sort=created_at,desc`

### 4.2 N+1 문제 해결
- SQLAlchemy의 `joinedload` (Eager Loading) 전략을 사용하여 게시글 조회 시 작성자(User) 및 태그(Tags) 정보를 단일 쿼리로 가져오도록 최적화했습니다.
