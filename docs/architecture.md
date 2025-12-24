# System Architecture

## 1. Layered Architecture
- **Presentation Layer**: FastAPI Routers (Endpoints)
- **Business Layer**: Services & Dependencies (Auth, Validation)
- **Data Access Layer**: SQLAlchemy ORM Models
- **Database**: MySQL 8.0

## 2. Infrastructure (Docker Compose)
- **App Container**: FastAPI (Python 3.10)
- **DB Container**: MySQL 8.0 (Data Persistence via Volume)
- **Cache Container**: Redis (Rate Limiting, Session)

## 3. Deployment Flow
GitHub Main Branch -> Docker Compose Build -> JCloud VM Execution
