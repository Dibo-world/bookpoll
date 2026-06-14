# 🔧 데이터 저장 안 되는 문제 - 종합 해결 가이드

## 🎯 해결된 문제들

### ❌ 문제 1: 데이터베이스 연결 실패 (원인 찾음 ✅)

**문제:**
```
.env 파일의 설정 ≠ docker-compose.yml 설정
```

**원인:**
| 항목 | .env (이전) | docker-compose (정답) | 수정 후 |
|------|-----------|------------------|--------|
| 비밀번호 | 1234 | password | ✅ password |
| 호스트 포트 | 5432-5434 | 5435 | ✅ 5435 |
| DB 이름 | authdb, bookdb, votedb | bookpoll (통합) | ✅ bookpoll |
| 패스워드 | 1234 | password | ✅ password |

**해결책: ✅ 이미 수정 완료**
- auth-service/.env
- book-service/.env
- vote-service/.env

---

### ❌ 문제 2: CORS 에러 (원인 찾음 ✅)

**증상:**
```
"No 'Access-Control-Allow-Origin' header is present on the requested resource"
```

**원인:**
- 프론트엔드 포트가 CORS 화이트리스트에 없음
- 서비스 간 통신 포트 (8001-8004) 미등록

**해결책: ✅ 이미 수정 완료**
- auth-service/main.py
- book-service/main.py
- vote-service/main.py
- notify-service/main.py

---

## 🚀 지금 해야 할 것

### 1단계: 모든 서비스 재시작
```powershell
# 1. 현재 실행 중인 모든 서비스 중지 (Ctrl+C)

# 2. Docker 컨테이너 재시작
docker-compose restart postgres redis rabbitmq

# 3. 각 서비스 다시 실행 (새 터미널 열어서)
# 터미널 1
cd auth-service
python main.py

# 터미널 2
cd book-service
python main.py

# 터미널 3
cd vote-service
python main.py

# 터미널 4
cd frontend
python -m http.server 8080
```

### 2단계: 헬스체크 확인
```bash
# 각 서비스 연결 테스트
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health

# 모두 {"status": "ok", "service": "..."} 반환해야 함
```

### 3단계: API 직접 테스트

**회원가입 테스트:**
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123",
    "username": "테스트사용자"
  }'
```

**예상 응답 (성공):**
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "username": "테스트사용자"
  },
  "message": "ok"
}
```

**DB 확인:**
```bash
psql -h localhost -U postgres -d bookpoll -p 5435 -c "SELECT * FROM users;"
```

### 4단계: 프론트엔드 테스트

1. **auth.html 접속**
   ```
   http://localhost:8080/frontend/auth.html
   (또는 http://localhost:5500 if using Live Server)
   ```

2. **회원가입 진행**
   - 사용자명: 테스트사용자
   - 이메일: testuser@example.com
   - 비밀번호: password123
   - "회원가입" 버튼 클릭

3. **성공 확인**
   - ✅ "회원가입이 완료되었습니다" 메시지
   - ✅ 1.5초 후 로그인 탭으로 자동 이동

4. **DB 저장 확인**
   ```bash
   psql -h localhost -U postgres -d bookpoll -p 5435
   SELECT id, username, email FROM users;
   ```

---

## 🐛 여전히 문제가 있다면?

### 시나리오 1: "서버와 통신할 수 없습니다" 에러

**원인 확인:**
```javascript
// 개발자 도구 (F12) → Console 탭 확인
// 에러 메시지 : 
// - "Failed to fetch" → 서버 미실행
// - "CORS error" → CORS 설정 문제
// - "ERR_NAME_NOT_RESOLVED" → 호스트명 오류
```

**해결:**
1. 모든 터미널에서 서비스 실행 중인지 확인
2. 포트 충돌 확인:
   ```bash
   netstat -ano | findstr 8001
   netstat -ano | findstr 8002
   ```
3. 방화벽 설정 확인

---

### 시나리오 2: 회원가입은 성공하는데 DB에 없음

**원인: 트랜잭션 커밋 실패**

auth_router.py 확인:
```python
# 이 부분이 있어야 함
db.commit()  # ← 중요!
db.refresh(user)
```

**확인 방법:**
```bash
# 1. auth-service 콘솔 로그 확인
# SQLAlchemy INSERT 쿼리가 출력되는지 확인

# 2. PostgreSQL 로그 확인
docker-compose logs postgres

# 3. 수동으로 데이터 삽입
psql -h localhost -U postgres -d bookpoll -p 5435
INSERT INTO users (email, password, username) VALUES ('manual@test.com', 'hashed', 'manual');
```

---

### 시나리오 3: 특정 서비스만 안 됨 (예: book-service)

**book-service 로그 확인:**
```bash
# book-service 터미널 확인
# ERROR나 Exception 메시지 있는지 확인
```

**예상 에러와 해결:**

| 에러 메시지 | 원인 | 해결 |
|-----------|------|------|
| `(psycopg2.OperationalError)` | DB 연결 실패 | .env 파일 확인 |
| `No such table: books` | 테이블 미생성 | `Base.metadata.create_all()` 확인 |
| `sqlalchemy.exc.IntegrityError` | 제약조건 위반 | 데이터 유효성 확인 |

---

## 📋 최종 점검 리스트

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 데이터베이스 접속 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] auth-service/.env 수정 완료
    DATABASE_URL=postgresql://postgres:password@localhost:5435/bookpoll
    
[ ] book-service/.env 수정 완료
    DATABASE_URL=postgresql://postgres:password@localhost:5435/bookpoll
    
[ ] vote-service/.env 수정 완료
    DATABASE_URL=postgresql://postgres:password@localhost:5435/bookpoll

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ CORS 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] auth-service/main.py ALLOWED_ORIGINS 수정
    - localhost:8001, 8002, 8003, 8004 포함
    
[ ] book-service/main.py ALLOWED_ORIGINS 수정
    - localhost:8001, 8002, 8003, 8004 포함
    
[ ] vote-service/main.py ALLOWED_ORIGINS 수정
    - localhost:8001, 8002, 8003, 8004 포함
    
[ ] notify-service/main.py ALLOWED_ORIGINS 수정
    - localhost:8001, 8002, 8003, 8004 포함

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 서비스 실행 확인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] PostgreSQL 실행 중
    docker-compose ps
    
[ ] Auth-Service 실행 중
    http://localhost:8001/health
    
[ ] Book-Service 실행 중
    http://localhost:8002/health
    
[ ] Vote-Service 실행 중
    http://localhost:8003/health
    
[ ] 프론트엔드 서버 실행 중
    http://localhost:8080 (또는 5500)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 기능 테스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] 회원가입 → 로그인 → 대시보드
[ ] 책 등록 → DB에 저장됨 확인
[ ] 투표 생성 → DB에 저장됨 확인
[ ] 투표 참여 → DB에 저장됨 확인
```

---

## 💡 Quick Start 한줄 명령어

```bash
# 모든 것을 한 번에 확인하는 스크립트
psql -h localhost -U postgres -d bookpoll -p 5435 -c "\
SELECT COUNT(*) as user_count FROM users; \
SELECT COUNT(*) as book_count FROM books; \
SELECT COUNT(*) as poll_count FROM polls;"
```

**정상 응답:**
```
 user_count | book_count | poll_count
────────────────────────────────────
     1      |      1     |     1
```

---

## 📞 추가 도움 필요시

### 1. 콘솔 에러 스크린샷
- F12 → Console 탭 → 에러 메시지 캡처

### 2. 서비스 로그
- 각 터미널의 출력 내용 캡처

### 3. DB 상태 확인
```bash
# 테이블 생성 확인
psql -h localhost -U postgres -d bookpoll -p 5435 -c "\dt"

# 데이터 확인
psql -h localhost -U postgres -d bookpoll -p 5435 -c "SELECT * FROM users LIMIT 1;"
```

