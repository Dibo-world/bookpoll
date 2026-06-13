# 📚 BookPoll 프로젝트 - AI 화면 구성용 프롬프트

## 🎯 프로젝트 개요
**BookPoll** - 독서 커뮤니티 투표 플랫폼
- 사용자가 책을 등록하고, 읽을 책을 투표하는 플랫폼
- 마이크로서비스 아키텍처 기반
- Kubernetes + Istio로 배포

---

## 📂 프로젝트 전체 폴더 구조

```
bookpoll/
├── curl/                          # API 테스트 스크립트
├── docker-compose.yml             # 로컬 환경 구성
├── README.md                       # 프로젝트 문서
│
├── auth-service/                  # 인증 서비스
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── config.py              # 환경변수, JWT 설정
│       ├── database.py            # DB 연결 설정
│       ├── models.py              # User 모델
│       └── routes/
│           └── auth_router.py     # 회원가입, 로그인, 인증 확인 API
│
├── book-service/                  # 도서 관리 서비스
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── config.py              # 환경변수 설정
│       ├── database.py            # DB 연결 설정
│       ├── models.py              # Book 모델
│       └── routes/
│           └── book_router.py     # 책 CRUD API
│
├── vote-service/                  # 투표 관리 서비스
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── config.py              # 환경변수 설정
│       ├── consumer.py            # RabbitMQ 메시지 소비자
│       ├── database.py            # DB 연결 설정
│       ├── models.py              # Poll, PollBook, VoteLog 모델
│       ├── rabbitmq.py            # RabbitMQ 메시지 발행
│       └── routes/
│           └── vote_router.py     # 투표 CRUD API
│
├── notify-service/                # 알림 서비스
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       └── consumer.py            # RabbitMQ 메시지 소비자 (알림 처리)
│
└── k8s/                           # Kubernetes 배포 설정
    ├── app-config.yaml            # ConfigMap
    ├── auth-service.yaml          # auth-service 배포
    ├── book-service.yaml          # book-service 배포
    ├── vote-service.yaml          # vote-service 배포
    ├── notify-service.yaml        # notify-service 배포
    ├── postgres.yaml              # PostgreSQL
    ├── rabbitmq.yaml              # RabbitMQ
    ├── redis.yaml                 # Redis (캐시)
    ├── ingress.yaml               # Ingress 설정
    ├── istio-routing.yaml         # Istio 라우팅
    ├── istio-mtls.yaml            # Istio mTLS
    ├── jwt-secret.yaml            # JWT Secret
    ├── rbac.yaml                  # 권한 설정
    ├── servicemonitor.yaml        # Prometheus 모니터링
    ├── argocd-app.yaml            # ArgoCD 배포
    └── permissive.yaml            # Istio 정책
```

---

## 🔧 기술 스택

| 계층 | 기술 |
|------|------|
| **언어/프레임워크** | Python 3.11, FastAPI |
| **데이터베이스** | PostgreSQL 15 |
| **캐시** | Redis 7 |
| **메시징** | RabbitMQ 3 |
| **ORM** | SQLAlchemy 2.0 + Alembic |
| **인증** | JWT + bcrypt |
| **배포** | Docker, Kubernetes, Istio |
| **모니터링** | Prometheus |
| **CI/CD** | ArgoCD |

---

## 🚀 서비스별 상세 가이드

### 1️⃣ AUTH-SERVICE (포트: 8001)
**목적**: 사용자 인증 및 JWT 토큰 발급

#### 📊 데이터 모델
```python
# User 테이블
- id (PK): 사용자 ID
- email: 이메일 (unique)
- password: 암호화된 비밀번호 (bcrypt)
- username: 사용자명
- created_at: 가입 일시
```

#### 🔌 API 엔드포인트

| 메소드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/v1/auth/register` | 회원가입 | ❌ |
| POST | `/api/v1/auth/login` | 로그인 | ❌ |
| GET | `/api/v1/auth/me` | 내 정보 조회 | ✅ |
| POST | `/api/v1/auth/verify` | 토큰 검증 | ✅ |

#### 📝 요청/응답 예시

**회원가입**
```json
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "username": "john_doe"
}

응답 (201):
{
  "success": true,
  "data": {
    "userId": 1,
    "username": "john_doe"
  },
  "message": "ok"
}
```

**로그인**
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

응답 (200):
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "userId": 1,
    "username": "john_doe"
  },
  "message": "ok"
}
```

#### 🔑 주요 코드 파일
- [auth-service/app/models.py](./auth-service/app/models.py) - User 모델
- [auth-service/app/routes/auth_router.py](./auth-service/app/routes/auth_router.py) - 인증 API 엔드포인트

---

### 2️⃣ BOOK-SERVICE (포트: 8002)
**목적**: 도서 정보 관리 및 CRUD 기능

#### 📊 데이터 모델
```python
# Book 테이블
- id (PK): 책 ID
- title: 책 제목
- author: 저자
- description: 책 설명
- user_id (FK): 등록한 사용자 ID
- created_at: 등록 일시
- updated_at: 수정 일시
```

#### 🔌 API 엔드포인트

| 메소드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/v1/books` | 책 목록 조회 | ❌ |
| GET | `/api/v1/books/{book_id}` | 책 상세 조회 | ❌ |
| POST | `/api/v1/books` | 책 등록 | ✅ |
| PUT | `/api/v1/books/{book_id}` | 책 수정 | ✅ |
| DELETE | `/api/v1/books/{book_id}` | 책 삭제 | ✅ |

#### 📝 요청/응답 예시

**책 등록**
```json
POST /api/v1/books
Header: X-User-Id: 1

{
  "title": "1984",
  "author": "George Orwell",
  "description": "디스토피아 소설"
}

응답 (201):
{
  "success": true,
  "data": {
    "id": 5,
    "title": "1984",
    "author": "George Orwell"
  },
  "message": "ok"
}
```

**책 목록 조회**
```json
GET /api/v1/books

응답 (200):
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "1984",
      "author": "George Orwell",
      "description": "디스토피아 소설",
      "userId": 1
    },
    ...
  ],
  "message": "ok"
}
```

#### 🔑 주요 코드 파일
- [book-service/app/models.py](./book-service/app/models.py) - Book 모델
- [book-service/app/routes/book_router.py](./book-service/app/routes/book_router.py) - 도서 API 엔드포인트

---

### 3️⃣ VOTE-SERVICE (포트: 8003)
**목적**: 투표 관리 및 실시간 투표 집계

#### 📊 데이터 모델
```python
# Poll 테이블 (투표)
- id (PK): 투표 ID
- title: 투표 제목
- status: 투표 상태 (OPEN, CLOSED)
- created_at: 생성 일시

# PollBook 테이블 (투표 후보)
- id (PK): 
- poll_id (FK): 투표 ID
- book_id: 책 ID

# VoteLog 테이블 (투표 기록)
- id (PK):
- poll_id (FK): 투표 ID
- user_id: 사용자 ID
- book_id: 책 ID
- created_at: 투표 일시
- 제약: 사용자당 1투표만 가능 (UNIQUE(poll_id, user_id))
```

#### 🔌 API 엔드포인트

| 메소드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/v1/polls` | 투표 생성 | ❌ |
| GET | `/api/v1/polls` | 투표 목록 조회 | ❌ |
| POST | `/api/v1/polls/{poll_id}/cast` | 투표 참여 | ✅ |
| GET | `/api/v1/polls/{poll_id}/results` | 투표 결과 조회 | ❌ |

#### 📝 요청/응답 예시

**투표 생성**
```json
POST /api/v1/polls
{
  "title": "2026년 최고의 책",
  "bookIds": [1, 2, 3, 4, 5]
}

응답 (201):
{
  "success": true,
  "data": {
    "pollId": 7,
    "title": "2026년 최고의 책"
  },
  "message": "ok"
}
```

**투표 참여**
```json
POST /api/v1/polls/7/cast
Header: X-User-Id: 1

{
  "bookId": 2
}

응답 (200):
{
  "success": true,
  "data": {...},
  "message": "투표 완료"
}
```

#### 🔑 주요 코드 파일
- [vote-service/app/models.py](./vote-service/app/models.py) - Poll, PollBook, VoteLog 모델
- [vote-service/app/routes/vote_router.py](./vote-service/app/routes/vote_router.py) - 투표 API 엔드포인트
- [vote-service/app/rabbitmq.py](./vote-service/app/rabbitmq.py) - 투표 이벤트 발행 로직

---

### 4️⃣ NOTIFY-SERVICE (포트: 8004)
**목적**: 투표 이벤트 구독 및 알림 처리

#### 🔌 기능
- RabbitMQ `vote_events` 큐에서 메시지 수신
- 투표 이벤트 처리 (로그, 이메일 등)

#### 📝 메시지 형식 (RabbitMQ)
```json
{
  "event": "vote_cast",
  "pollId": 7,
  "userId": 1,
  "bookId": 2,
  "timestamp": "2026-06-13T10:30:00"
}
```

#### 🔑 주요 코드 파일
- [notify-service/app/consumer.py](./notify-service/app/consumer.py) - RabbitMQ 메시지 처리

---

## 🔄 시스템 흐름도

### 회원가입 → 로그인 흐름
```
사용자 입력
    ↓
Auth-Service (register/login)
    ↓
JWT 토큰 발급
    ↓
프론트엔드에서 토큰 저장
```

### 책 등록 및 투표 흐름
```
로그인된 사용자
    ↓
Book-Service (책 등록)
    ↓
저장된 Book ID
    ↓
Vote-Service (투표 생성)
    ↓
사용자 투표 참여
    ↓
RabbitMQ 이벤트 발행
    ↓
Notify-Service (알림 처리)
```

---

## 🔐 인증 헤더 규칙

### 테스트 단계 (현재)
```
X-User-Id: {userId}
```

### 운영 단계 (계획)
```
Authorization: Bearer {JWT_TOKEN}
```

---

## 🌐 API 응답 규칙

### 성공 응답 (200, 201)
```json
{
  "success": true,
  "data": {
    // 실제 데이터
  },
  "message": "성공 메시지"
}
```

### 실패 응답 (400, 401, 404, 409, 500)
```json
{
  "success": false,
  "data": null,
  "message": "에러 메시지"
}
```

---

## 💾 로컬 환경 설정

### Docker Compose로 실행
```bash
docker-compose up
```

### 서비스별 접속 정보
- **Auth-Service**: http://localhost:8001
- **Book-Service**: http://localhost:8002
- **Vote-Service**: http://localhost:8003
- **PostgreSQL**: localhost:5435 (user: postgres, pwd: password)
- **RabbitMQ**: http://localhost:15672 (user: guest, pwd: guest)

---

## 📋 커밋 메시지 규칙

```
feat:  기능 추가
fix:   버그 수정
chore: 설정 변경
docs:  문서 수정
```

---

## 🎨 화면 구성 시 필요한 페이지

### 1. 인증 페이지
- 회원가입
- 로그인
- 프로필 조회 (내 정보)

### 2. 도서 관리 페이지
- 책 목록 조회
- 책 상세 조회
- 책 등록 (인증 필수)
- 책 수정 (인증 필수)
- 책 삭제 (인증 필수)

### 3. 투표 페이지
- 진행 중인 투표 목록
- 투표 생성
- 투표 참여
- 투표 결과 조회

### 4. 알림 페이지 (향후)
- 투표 알림
- 결과 알림

---

## 📞 연락처 및 지원
프로젝트 관리자: 클라우드 학습자
