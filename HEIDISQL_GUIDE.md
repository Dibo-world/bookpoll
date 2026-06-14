# 📊 BookPoll 데이터 흐름 및 HeidiSQL 연결 가이드

## 🔍 데이터 저장 흐름

### 1️⃣ 데이터가 어디로 들어가는가?

```
프론트엔드 (http://localhost:8080)
    ↓
    ├─→ 회원가입 요청 → Auth-Service (8001)
    │       ↓
    │   PostgreSQL:5435/bookpoll → users 테이블
    │
    ├─→ 책 등록 요청 → Book-Service (8002)
    │       ↓
    │   PostgreSQL:5435/bookpoll → books 테이블
    │
    ├─→ 투표 생성/참여 → Vote-Service (8003)
    │       ├─→ PostgreSQL:5435/bookpoll → polls, poll_books, vote_logs 테이블
    │       └─→ Redis:6379 → 투표 결과 캐시
    │
    └─→ 알림 수신 → Notify-Service (8004)
            ↓
        RabbitMQ → 메시지 큐
```

### 📍 데이터베이스 위치

```
데이터베이스 유형: PostgreSQL 15
위치: Docker 컨테이너 (postgres)
호스트: localhost
포트: 5435
사용자: postgres
비밀번호: password
데이터베이스명: bookpoll
```

---

## 🎯 현재 저장되는 데이터 구조

### 📋 테이블 목록

```
1. users
   - id (PK)
   - email (unique)
   - password (bcrypt 암호화)
   - username
   - created_at

2. books
   - id (PK)
   - title
   - author
   - description
   - user_id (책을 등록한 사용자)
   - created_at
   - updated_at

3. polls
   - id (PK)
   - title
   - status (OPEN, CLOSED)
   - created_at

4. poll_books
   - id (PK)
   - poll_id (FK)
   - book_id

5. vote_logs
   - id (PK)
   - poll_id (FK)
   - user_id
   - book_id
   - created_at
   - UNIQUE(poll_id, user_id) - 사용자당 1표만
```

---

## 🔌 HeidiSQL 연결 가이드

### Step 1: HeidiSQL 설치

1. https://www.heidisql.com/download.php 방문
2. "Installer (64 bit)" 다운로드
3. 설치 진행

### Step 2: HeidiSQL 실행 및 새 연결 생성

1. **HeidiSQL 실행**
2. 좌측 "새로 만들기" 버튼 클릭
3. 또는 "세션 관리자" → "새로 만들기"

### Step 3: 연결 정보 입력

다음 정보를 정확히 입력하세요:

```
연결 이름: BookPoll-Local (또는 원하는 이름)
호스트명/IP: 127.0.0.1 (또는 localhost)
포트: 5435
사용자: postgres
비밀번호: password
데이터베이스: bookpoll (선택사항 - 연결 후에도 가능)

**중요: 포트는 5432가 아니라 5435입니다!**
```

### Step 4: 연결 테스트

"테스트" 또는 "연결 테스트" 버튼 클릭

**성공 메시지:**
```
성공적으로 연결되었습니다!
```

### Step 5: 저장 및 연결

1. "저장" 버튼 클릭
2. "열기" 버튼 클릭 → 연결 완료

---

## 📸 HeidiSQL 연결 스크린샷 가이드

### 연결 설정 화면

```
┌─────────────────────────────────┐
│ 세션 연결 설정                    │
├─────────────────────────────────┤
│                                  │
│ ✓ 호스트명/IP: 127.0.0.1        │
│ ✓ 포트: 5435                     │
│ ✓ 사용자: postgres              │
│ ✓ 비밀번호: password            │
│ ✓ 데이터베이스: bookpoll        │
│                                  │
│ [테스트] [저장] [열기]          │
│                                  │
└─────────────────────────────────┘
```

---

## ✅ 연결 후 확인사항

### 1️⃣ 데이터베이스 확인

```
좌측 트리 → bookpoll → 테이블
┣ users
┣ books
┣ polls
┣ poll_books
└ vote_logs
```

### 2️⃣ 실제 데이터 확인

**users 테이블 조회:**
```
1. 좌측에서 "users" 우클릭
2. "SELECT * FROM `users`" 선택
3. 또는 직접 쿼리 입력:

SELECT id, email, username, created_at FROM users;
```

**books 테이블 조회:**
```sql
SELECT id, title, author, user_id, created_at FROM books;
```

**투표 데이터 조회:**
```sql
SELECT id, title, status FROM polls;
```

### 3️⃣ 데이터 흐름 실시간 확인

1. 회원가입 후 HeidiSQL 새로고침 (F5)
2. users 테이블에 새 행 추가되는지 확인
3. 책 등록 후 books 테이블 확인
4. 투표 참여 후 vote_logs 테이블 확인

---

## 🧪 데이터 저장 확인 테스트

### 테스트 시나리오

```
1️⃣ 회원가입 (auth.html)
   ├─ 정보: test@example.com / 비밀번호123 / 테스터
   ├─ DB 확인: SELECT * FROM users WHERE email='test@example.com';
   └─ 결과: 1행 확인

2️⃣ 로그인 및 책 등록 (dashboard.html)
   ├─ 책: "1984", "George Orwell", "설명..."
   ├─ DB 확인: SELECT * FROM books ORDER BY created_at DESC LIMIT 1;
   └─ 결과: 새 책 행 확인

3️⃣ 투표 생성
   ├─ 투표: "2026 최고의 책"
   ├─ 후보: 1984, 동물농장 등 선택
   ├─ DB 확인: SELECT * FROM polls WHERE title='2026 최고의 책';
   └─ 결과: 투표 및 후보 데이터 확인

4️⃣ 투표 참여
   ├─ "1984"에 투표
   ├─ DB 확인: SELECT * FROM vote_logs ORDER BY created_at DESC LIMIT 1;
   └─ 결과: 투표 기록 저장 확인
```

---

## 🔍 HeidiSQL에서 자주 사용하는 쿼리

### 모든 데이터 개요

```sql
-- 1. 전체 사용자 수
SELECT COUNT(*) as total_users FROM users;

-- 2. 모든 등록된 책
SELECT id, title, author, username FROM books
JOIN users ON books.user_id = users.id
ORDER BY books.created_at DESC;

-- 3. 모든 투표 및 투표율
SELECT 
  p.id,
  p.title,
  COUNT(vl.id) as total_votes,
  COUNT(DISTINCT vl.user_id) as unique_voters
FROM polls p
LEFT JOIN vote_logs vl ON p.id = vl.poll_id
GROUP BY p.id, p.title;

-- 4. 특정 투표의 결과
SELECT 
  pb.book_id,
  b.title,
  COUNT(vl.id) as vote_count
FROM poll_books pb
LEFT JOIN vote_logs vl ON pb.poll_id = vl.poll_id AND pb.book_id = vl.book_id
LEFT JOIN books b ON pb.book_id = b.id
WHERE pb.poll_id = 1
GROUP BY pb.book_id, b.title
ORDER BY vote_count DESC;

-- 5. 사용자의 투표 기록
SELECT 
  u.username,
  p.title as poll_title,
  b.title as voted_book,
  vl.created_at
FROM vote_logs vl
JOIN users u ON vl.user_id = u.id
JOIN polls p ON vl.poll_id = p.id
JOIN books b ON vl.book_id = b.id
WHERE u.id = 1
ORDER BY vl.created_at DESC;
```

---

## 🚨 문제 해결

### ❌ "127.0.0.1에 연결할 수 없습니다"

**원인:** PostgreSQL 컨테이너가 실행 중이 아님

```bash
# Docker 컨테이너 상태 확인
docker-compose ps

# PostgreSQL만 시작
docker-compose up -d postgres
```

### ❌ "포트 5435가 이미 사용 중입니다"

```bash
# 포트 확인
netstat -ano | findstr 5435

# 충돌하는 프로세스 종료
taskkill /PID <프로세스ID> /F

# Docker 재시작
docker-compose restart postgres
```

### ❌ "사용자 인증 실패"

```
확인사항:
- 사용자명: postgres (정확히)
- 비밀번호: password (정확히)
- 데이터베이스: bookpoll (정확히)
```

---

## 📊 데이터 현황 대시보드

### HeidiSQL에서 빠른 확인

**실행 순서:**
1. HeidiSQL → bookpoll 데이터베이스 연결
2. 좌측 "쿼리" 탭 열기
3. 다음 쿼리 실행:

```sql
-- 모든 테이블의 행 개수
SELECT 
  'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'books', COUNT(*) FROM books
UNION ALL
SELECT 'polls', COUNT(*) FROM polls
UNION ALL
SELECT 'poll_books', COUNT(*) FROM poll_books
UNION ALL
SELECT 'vote_logs', COUNT(*) FROM vote_logs;
```

**예상 결과:**
```
table_name    | row_count
─────────────────────────
users         | 1
books         | 3
polls         | 2
poll_books    | 6
vote_logs     | 5
```

---

## 💡 팁

### 1. 자동 새로고침 설정

```
HeidiSQL → 도구 → 옵션 → 쿼리 → "자동 새로고침" 활성화
```

### 2. 즐겨찾기 쿼리 저장

```
자주 쓰는 쿼리 작성 → 마우스 우클릭 → "즐겨찾기에 저장"
```

### 3. 데이터 백업

```
좌측 "bookpoll" → 우클릭 → "백업" → SQL 파일로 저장
```

---

## 📋 데이터 흐름 요약

| 기능 | API | DB 테이블 | 확인 방법 |
|------|-----|----------|---------|
| 회원가입 | POST /auth/register | users | SELECT * FROM users; |
| 책 등록 | POST /books | books | SELECT * FROM books; |
| 투표 생성 | POST /polls | polls, poll_books | SELECT * FROM polls; |
| 투표 참여 | POST /polls/{id}/cast | vote_logs | SELECT * FROM vote_logs; |
| 알림 | GET /notifications | (Redis/메모리) | Redis CLI 또는 로그 |

---

## ✨ 완벽한 설정 후

```
✅ HeidiSQL에서 bookpoll 연결됨
✅ 모든 테이블 (users, books, polls, poll_books, vote_logs) 보임
✅ 회원가입/책 등록/투표 시 실시간으로 데이터 추가되는 것 확인 가능
✅ 모든 데이터가 PostgreSQL에 영구 저장됨
```

이제 모든 데이터의 흐름을 실시간으로 모니터링할 수 있습니다! 🎉

