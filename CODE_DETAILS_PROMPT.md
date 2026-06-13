# BookPoll - 각 서비스 코드 상세 프롬프트

## Auth-Service 상세 정보

### models.py - User 데이터 모델
```python
from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__ = "users"

    id         : Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    email      : Mapped[str]      = mapped_column(String(120), unique=True, nullable=False)
    password   : Mapped[str]      = mapped_column(String(255), nullable=False)  # bcrypt 암호화
    username   : Mapped[str]      = mapped_column(String(80), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

### auth_router.py - 인증 API 엔드포인트
**주요 기능:**
- POST /api/v1/auth/register - 회원가입
  - 요청: email, password, username
  - bcrypt로 비밀번호 암호화 후 저장
  - 응답: userId, username

- POST /api/v1/auth/login - 로그인
  - 요청: email, password
  - 비밀번호 검증 후 JWT 토큰 생성
  - JWT 토큰 유효시간: 24시간 (JWT_EXPIRE_HOURS)
  - 응답: JWT token, userId, username

- GET /api/v1/auth/me - 내 정보 조회
  - 인증 필수 (Authorization 헤더)
  - 토큰에서 userId 추출해서 사용자 정보 반환
  - 응답: email, username, userId

**에러 처리:**
- 409 Conflict: 이미 존재하는 이메일
- 401 Unauthorized: 잘못된 이메일/비밀번호
- 400 Bad Request: 필수 필드 누락

### 응답 포맷
```python
def ok(data=None, message="ok", status_code=200):
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "data": data, "message": message}
    )

def err(message="error", status_code=400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "data": None, "message": message}
    )
```

---

## Book-Service 상세 정보

### models.py - Book 데이터 모델
```python
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Book(Base):
    __tablename__ = "books"

    id          : Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    title       : Mapped[str]      = mapped_column(String(200), nullable=False)
    author      : Mapped[str]      = mapped_column(String(100), nullable=False)
    description : Mapped[str]      = mapped_column(Text, default="")
    user_id     : Mapped[int]      = mapped_column(Integer, nullable=False)
    created_at  : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at  : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                   onupdate=datetime.utcnow)
```

### book_router.py - 책 관리 API 엔드포인트
**주요 기능:**

1. GET /api/v1/books - 책 목록 조회
   - 전체 책을 최신순으로 반환
   - 응답: [{id, title, author, description, userId}, ...]

2. GET /api/v1/books/{book_id} - 책 상세 조회
   - 특정 책의 정보 반환
   - 응답: {id, title, author, description}
   - 404: 책을 찾을 수 없음

3. POST /api/v1/books - 책 등록
   - 인증 필수 (X-User-Id 헤더)
   - 요청: title, author, description(선택)
   - 응답: {id, title, author} (201 Created)
   - 401: 인증 필요

4. PUT /api/v1/books/{book_id} - 책 수정
   - 인증 필수
   - 요청: title(선택), author(선택), description(선택)
   - 선택 사항은 null이면 기존 값 유지
   - 응답: {id, title, author, description}

5. DELETE /api/v1/books/{book_id} - 책 삭제
   - 인증 필수
   - 책을 데이터베이스에서 삭제
   - 응답: {message: "삭제됨"}

**인증 헤더:**
```python
def get_user_id(x_user_id: Optional[str] = Header(None)) -> Optional[int]:
    """X-User-Id 헤더에서 사용자 ID 추출"""
    return int(x_user_id) if x_user_id else None
```

---

## Vote-Service 상세 정보

### models.py - 투표 관련 데이터 모델
```python
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Poll(Base):
    """투표"""
    __tablename__ = "polls"
    id         : Mapped[int]      = mapped_column(Integer, primary_key=True)
    title      : Mapped[str]      = mapped_column(String(200), nullable=False)
    status     : Mapped[str]      = mapped_column(String(20), default="OPEN")  # OPEN, CLOSED
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PollBook(Base):
    """투표의 후보 책"""
    __tablename__ = "poll_books"
    id      : Mapped[int] = mapped_column(Integer, primary_key=True)
    poll_id : Mapped[int] = mapped_column(Integer, ForeignKey("polls.id"), nullable=False)
    book_id : Mapped[int] = mapped_column(Integer, nullable=False)

class VoteLog(Base):
    """투표 기록 (중복 투표 방지)"""
    __tablename__ = "vote_logs"
    id         : Mapped[int]      = mapped_column(Integer, primary_key=True)
    poll_id    : Mapped[int]      = mapped_column(Integer, nullable=False)
    user_id    : Mapped[int]      = mapped_column(Integer, nullable=False)
    book_id    : Mapped[int]      = mapped_column(Integer, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 사용자당 1표만 가능
    __table_args__ = (
        UniqueConstraint("poll_id", "user_id", name="uq_one_vote_per_user"),
    )
```

### vote_router.py - 투표 API 엔드포인트
**주요 기능:**

1. POST /api/v1/polls - 투표 생성
   - 요청: title, bookIds (후보 책 ID 배열)
   - Poll 레코드 생성 후 각 책에 대해 PollBook 생성
   - 응답: {pollId, title} (201 Created)

2. GET /api/v1/polls - 투표 목록 조회
   - status = "OPEN"인 투표만 반환
   - 응답: [{id, title, status}, ...]

3. POST /api/v1/polls/{poll_id}/cast - 투표 참여
   - 인증 필수 (X-User-Id 헤더)
   - 요청: bookId
   - 검증:
     * 투표가 존재하고 OPEN 상태?
     * 사용자가 이미 투표했나? (VoteLog 확인)
   - 로직:
     * Redis에서 투표 수 증가: incr("poll:{poll_id}:book:{bookId}")
     * VoteLog에 기록 저장 (중복 투표 방지)
     * RabbitMQ로 vote_cast 이벤트 발행
   - 응답: {pollId, bookId} (200)
   - 에러:
     * 401: 인증 필요
     * 404: 투표가 없거나 종료됨
     * 409: 이미 투표함

4. GET /api/v1/polls/{poll_id}/results - 투표 결과 조회
   - Redis에서 투표 집계 데이터 조회
   - 각 책의 투표 수 계산
   - 응답: [{bookId, votes}, ...] (투표 수 순 정렬)

**Redis 사용:**
- Key: poll:{poll_id}:book:{book_id}
- Value: 투표 수
- 이유: 실시간 집계를 위해 메모리 DB 사용 (빠른 조회/업데이트)

**RabbitMQ 이벤트:**
```python
def publish_vote_event(poll_id, user_id, book_id):
    channel.basic_publish(
        exchange='',
        routing_key='vote_events',
        body=json.dumps({
            'event': 'vote_cast',
            'pollId': poll_id,
            'userId': user_id,
            'bookId': book_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    )
```

---

## Notify-Service 상세 정보

### consumer.py - RabbitMQ 메시지 처리
```python
import pika
import json

def callback(ch, method, properties, body):
    """RabbitMQ 메시지 콜백"""
    data = json.loads(body)
    print(f"[notify-service] 메시지 수신: {data}")
    
    # 메시지 처리 로직
    # - 이메일 발송
    # - 로그 저장
    # - 알림 생성 등
    
    # 메시지 확인
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    """RabbitMQ 메시지 소비자 시작"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()
    channel.queue_declare(queue="vote_events", durable=True)
    channel.basic_consume(queue="vote_events", on_message_callback=callback)
    print("[notify-service] 메시지 대기 중...")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
```

**처리하는 이벤트:**
- vote_cast: 투표가 진행되었을 때
  - 구독자들에게 알림 발송
  - 투표 통계 업데이트
  - 실시간 알림 (WebSocket 등으로 프론트엔드에 전달)

---

## 데이터 흐름 정리

### 시나리오 1: 회원가입 및 로그인
```
1. 사용자가 회원가입 폼 작성
2. POST /api/v1/auth/register 호출
3. auth-service에서 비밀번호 암호화 후 DB 저장
4. 사용자 정보 반환
5. 사용자가 로그인
6. POST /api/v1/auth/login 호출
7. JWT 토큰 생성 및 반환
8. 프론트엔드에서 토큰 저장 (로컬스토리지/쿠키)
```

### 시나리오 2: 책 등록 및 투표
```
1. 로그인된 사용자가 책 등록
2. POST /api/v1/books (X-User-Id: 1 헤더)
3. book-service에서 Book 생성 후 DB 저장
4. 책 ID 반환
5. 관리자가 투표 생성
6. POST /api/v1/polls {title: "...", bookIds: [1, 2, 3, ...]}
7. vote-service에서 Poll 및 PollBook 생성
8. 사용자가 투표 참여
9. POST /api/v1/polls/{poll_id}/cast {bookId: 2}
10. vote-service에서 중복 체크 후 Redis 업데이트
11. VoteLog DB 저장
12. RabbitMQ에 vote_cast 이벤트 발행
13. notify-service가 이벤트 수신 및 처리 (알림, 로그 등)
```

---

## 서비스별 주요 파일 체크리스트

### Auth-Service
- ✅ models.py - User 모델
- ✅ auth_router.py - register, login, me 엔드포인트
- ✅ config.py - JWT_SECRET, JWT_EXPIRE_HOURS 설정

### Book-Service
- ✅ models.py - Book 모델
- ✅ book_router.py - GET/POST/PUT/DELETE 엔드포인트
- ✅ database.py - DB 연결 설정

### Vote-Service
- ✅ models.py - Poll, PollBook, VoteLog 모델
- ✅ vote_router.py - 투표 CRUD 및 투표 참여 엔드포인트
- ✅ database.py - DB 및 Redis 연결 설정
- ✅ rabbitmq.py - 이벤트 발행 로직

### Notify-Service
- ✅ consumer.py - RabbitMQ 메시지 처리

---

## 주의사항

1. **인증:**
   - 현재는 X-User-Id 헤더로 테스트 (직접 사용자 ID 전달)
   - 실제 운영 환경에서는 Authorization: Bearer {JWT_TOKEN} 사용
   - auth-service의 /verify 엔드포인트를 다른 서비스에서 호출해서 토큰 검증

2. **중복 투표 방지:**
   - VoteLog 테이블에 UNIQUE 제약 (poll_id, user_id)
   - 사용자당 1투표만 가능

3. **실시간 집계:**
   - Redis를 사용해서 투표 결과를 실시간 저장
   - PostgreSQL은 VoteLog 저장용 (분석/감사용)

4. **응답 포맷:**
   - 모든 API 응답은 {success, data, message} 형식
   - HTTP 상태 코드도 함께 사용 (201, 401, 404, 409 등)

