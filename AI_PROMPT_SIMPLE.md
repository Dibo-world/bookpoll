# BookPoll - 화면 구성 AI 프롬프트 (간편 버전)

아래 텍스트를 AI(ChatGPT, Claude 등)의 프롬프트로 바로 붙여넣기 하세요.

---

다음은 "BookPoll"이라는 독서 커뮤니티 투표 플랫폼의 구조입니다. 이 정보를 바탕으로 화면을 설계해주세요.

## 프로젝트 개요
- **프로젝트명**: BookPoll (독서 커뮤니티 투표 플랫폼)
- **기술스택**: FastAPI, PostgreSQL, RabbitMQ, Redis, JWT 인증
- **아키텍처**: 마이크로서비스 (4개 서비스)

## 폴더 구조
```
bookpoll/
├── auth-service/        (포트 8001) - 사용자 인증
├── book-service/        (포트 8002) - 도서 관리
├── vote-service/        (포트 8003) - 투표 관리
├── notify-service/      (포트 8004) - 알림 처리
└── k8s/                 - Kubernetes 배포 설정
```

## 1. AUTH-SERVICE (인증)

### 데이터 모델
- **User**: id, email, password(암호화), username, created_at

### API 엔드포인트
| 메소드 | 경로 | 설명 |
|--------|------|------|
| POST | /api/v1/auth/register | 회원가입 |
| POST | /api/v1/auth/login | 로그인 (JWT 토큰 발급) |
| GET | /api/v1/auth/me | 내 정보 조회 |

### 요청/응답
```
회원가입 요청:
POST /api/v1/auth/register
{ "email": "user@example.com", "password": "pass123", "username": "john" }

응답:
{ "success": true, "data": { "userId": 1, "username": "john" }, "message": "ok" }

로그인 요청:
POST /api/v1/auth/login
{ "email": "user@example.com", "password": "pass123" }

응답:
{ "success": true, "data": { "token": "JWT_TOKEN", "userId": 1, "username": "john" }, "message": "ok" }
```

## 2. BOOK-SERVICE (도서 관리)

### 데이터 모델
- **Book**: id, title, author, description, user_id, created_at, updated_at

### API 엔드포인트
| 메소드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/v1/books | 책 목록 조회 |
| GET | /api/v1/books/{id} | 책 상세 조회 |
| POST | /api/v1/books | 책 등록 (인증 필수) |
| PUT | /api/v1/books/{id} | 책 수정 (인증 필수) |
| DELETE | /api/v1/books/{id} | 책 삭제 (인증 필수) |

### 요청/응답
```
책 목록 조회:
GET /api/v1/books

응답:
{ "success": true, "data": [ { "id": 1, "title": "1984", "author": "George Orwell", "description": "디스토피아 소설", "userId": 1 }, ... ], "message": "ok" }

책 등록:
POST /api/v1/books
Header: X-User-Id: 1
{ "title": "1984", "author": "George Orwell", "description": "디스토피아 소설" }

응답:
{ "success": true, "data": { "id": 5, "title": "1984", "author": "George Orwell" }, "message": "ok" }
```

## 3. VOTE-SERVICE (투표 관리)

### 데이터 모델
- **Poll**: id, title, status(OPEN/CLOSED), created_at
- **PollBook**: id, poll_id, book_id (투표의 후보 책)
- **VoteLog**: id, poll_id, user_id, book_id, created_at (투표 기록, 사용자당 1표만)

### API 엔드포인트
| 메소드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/v1/polls | 투표 목록 조회 |
| POST | /api/v1/polls | 투표 생성 |
| POST | /api/v1/polls/{poll_id}/cast | 투표 참여 (인증 필수) |
| GET | /api/v1/polls/{poll_id}/results | 투표 결과 조회 |

### 요청/응답
```
투표 목록 조회:
GET /api/v1/polls

응답:
{ "success": true, "data": [ { "id": 1, "title": "2026 최고의 책", "status": "OPEN" }, ... ], "message": "ok" }

투표 생성:
POST /api/v1/polls
{ "title": "2026 최고의 책", "bookIds": [1, 2, 3, 4, 5] }

응답:
{ "success": true, "data": { "pollId": 7, "title": "2026 최고의 책" }, "message": "ok" }

투표 참여:
POST /api/v1/polls/7/cast
Header: X-User-Id: 1
{ "bookId": 2 }

응답:
{ "success": true, "data": { ... }, "message": "투표 완료" }
```

## 4. NOTIFY-SERVICE (알림)
- RabbitMQ에서 vote_events 큐 수신
- 투표 이벤트 처리 (로그, 이메일 등)

## 필수 페이지 (화면)

### 1. 인증 페이지
- 회원가입 페이지
- 로그인 페이지
- 프로필 페이지 (내 정보)

### 2. 도서 관리 페이지
- 책 목록 페이지 (전체 책 조회)
- 책 상세 페이지
- 책 등록 페이지 (인증 필수)
- 책 수정 페이지 (인증 필수)

### 3. 투표 페이지
- 투표 목록 페이지
- 투표 생성 페이지
- 투표 상세 페이지 (투표 참여)
- 투표 결과 페이지

## 인증 방식
- 현재: X-User-Id 헤더로 테스트
- 향후: Authorization: Bearer JWT_TOKEN 방식으로 변경

## API 응답 규칙
모든 응답은 다음 형식:
```json
{
  "success": true/false,
  "data": { /* 실제 데이터 */ },
  "message": "메시지"
}
```

---

위 정보를 바탕으로 다음을 설계해주세요:
1. 전체 사용자 흐름 (User Flow)
2. 각 페이지의 주요 구성 요소 (Components)
3. 데이터 흐름 다이어그램 (Data Flow)
4. 추천하는 UI/UX 디자인 구조

