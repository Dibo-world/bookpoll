# 🚀 BookPoll 로컬 개발 - 완벽한 실행 가이드

## ✅ 수정된 사항

### docker-compose.yml 업데이트
```
✅ Redis 서비스 추가 (vote-service 필요)
✅ vote-service에 redis 의존성 추가
✅ notify-service 추가
✅ 모든 서비스에 올바른 환경변수 설정
✅ redis_data 볼륨 추가
```

---

## 🎯 실행 방법 (선택 1가지)

### 방법 A: Docker Compose로 모든 것 실행 (권장)

```powershell
# 1. 모든 컨테이너 시작 (postgres, redis, rabbitmq, 모든 서비스)
docker-compose up -d

# 2. 상태 확인
docker-compose ps

# 예상 출력:
# CONTAINER ID   IMAGE                      STATUS
# xxxxxxxx       postgres:15                Up...
# xxxxxxxx       redis:7                    Up...
# xxxxxxxx       rabbitmq:3-management      Up...
# xxxxxxxx       bookpoll-auth-service      Up...
# xxxxxxxx       bookpoll-book-service      Up...
# xxxxxxxx       bookpoll-vote-service      Up...
# xxxxxxxx       bookpoll-notify-service    Up...

# 3. 로그 확인
docker-compose logs -f auth-service

# 4. 특정 포트 테스트
curl http://localhost:8001/health
```

---

### 방법 B: 로컬 Python에서 직접 실행 (localhost 개발)

이 방식을 선택하면 **Python 서비스만 localhost에서 실행하고, 데이터베이스는 Docker에서**:

```powershell
# 1단계: Docker에서 DB 서비스만 시작
docker-compose up -d postgres redis rabbitmq

# 2단계: 각 서비스를 localhost에서 실행 (새 터미널 각각)

# 터미널 1: Auth Service
cd auth-service
python main.py

# 터미널 2: Book Service  
cd book-service
python main.py

# 터미널 3: Vote Service
cd vote-service
python main.py

# 터미널 4: Notify Service
cd notify-service
python main.py

# 터미널 5: 프론트엔드 (로컬 웹 서버)
cd frontend
python -m http.server 8080
```

**주의: 이 방식의 .env 파일 설정**
```
DATABASE_URL=postgresql://postgres:password@localhost:5435/bookpoll
REDIS_URL=redis://localhost:6379/0
```

---

## 🔍 방법 선택 가이드

| 항목 | 방법 A (Docker) | 방법 B (로컬) |
|------|----------------|-------------|
| 설정 복잡도 | ⭐ 간단 | ⭐⭐ 복잡 |
| 시작 속도 | 빠름 | 느림 |
| 프로덕션 환경과 유사 | ✅ 예 | ❌ 아니오 |
| 개발/디버깅 | ⭐⭐ 중간 | ⭐⭐⭐ 최고 |
| Python 디버거 사용 | ❌ 어려움 | ✅ 쉬움 |

**추천: 처음에는 방법 A (Docker)로 시작하세요!**

---

## 🧪 테스트 확인

### 1️⃣ 헬스체크

```bash
# 모든 서비스가 정상 실행 중인지 확인
curl http://localhost:8001/health  # Auth
curl http://localhost:8002/health  # Book
curl http://localhost:8003/health  # Vote
curl http://localhost:8004/health  # Notify

# 예상 응답
# {"status": "ok", "service": "auth-service"}
```

### 2️⃣ 회원가입 API 테스트

```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "username": "테스트사용자"
  }'

# 성공 응답
# {"success": true, "data": {"userId": 1, "username": "테스트사용자"}, "message": "ok"}
```

### 3️⃣ DB 데이터 확인

```bash
# PostgreSQL 접속 (포트 5435)
psql -h localhost -U postgres -d bookpoll -p 5435

# 사용자 조회
SELECT * FROM users;

# 책 조회
SELECT * FROM books;

# 투표 조회
SELECT * FROM polls;
```

### 4️⃣ 프론트엔드 테스트

```
1. 브라우저에서 http://localhost:8080/frontend/auth.html 접속
2. "회원가입" 탭 클릭
3. 정보 입력 후 "회원가입" 버튼
4. 성공 메시지 확인
5. DB에서 data 확인: SELECT * FROM users;
```

---

## ⚠️ 일반적인 문제 해결

### ❌ "no such service: redis" 에러
✅ 수정됨 - docker-compose.yml에 Redis 추가됨

### ❌ "Cannot connect to Redis" 에러
```powershell
# Redis 실행 확인
docker-compose ps | grep redis

# Redis 상태 확인
docker-compose logs redis

# 재시작
docker-compose restart redis
```

### ❌ "Connection refused" - 데이터베이스 연결 안 됨

**방법 A 사용 시:**
```bash
docker-compose logs postgres
docker-compose restart postgres
```

**방법 B 사용 시:**
```bash
# .env 파일 확인
cat auth-service/.env
# 반드시 다음을 포함:
# DATABASE_URL=postgresql://postgres:password@localhost:5435/bookpoll
```

### ❌ CORS 에러

✅ 수정됨 - 모든 main.py의 ALLOWED_ORIGINS 설정 완료

이 에러가 여전히 나면:
```bash
# 브라우저 개발자 도구 (F12) → Console 탭 확인
# 정확한 에러 메시지 확인
```

---

## 📊 방법별 실행 명령어

### 방법 A: Docker Compose (완전 자동화)

```bash
# 시작
docker-compose up -d

# 종료
docker-compose down

# 로그 보기
docker-compose logs -f

# 재시작
docker-compose restart

# 컨테이너 제거 및 다시 시작
docker-compose down
docker-compose up -d
```

### 방법 B: 로컬 Python

```bash
# 시작 (5개 터미널)
# 터미널 1
docker-compose up -d postgres redis rabbitmq

# 터미널 2-5 각각
python main.py   # (각 서비스 폴더에서)

# 종료
# Ctrl+C (각 터미널에서)
docker-compose down
```

---

## 🎯 최종 체크리스트

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
방법 A: Docker Compose 사용
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] docker-compose.yml 수정됨 (redis, notify 추가)
[ ] docker-compose up -d 실행
[ ] docker-compose ps (7개 컨테이너 보임)
[ ] curl http://localhost:8001/health (성공)
[ ] 회원가입 API 테스트 (성공)
[ ] http://localhost:8080/frontend/auth.html (회원가입 성공)
[ ] DB SELECT * FROM users; (데이터 있음)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
방법 B: 로컬 Python 사용
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] .env 파일 확인 (password@localhost:5435)
[ ] docker-compose up -d postgres redis rabbitmq
[ ] 각 서비스 python main.py 실행
[ ] curl http://localhost:8001/health (성공)
[ ] 회원가입 API 테스트 (성공)
[ ] http://localhost:8080/frontend/auth.html (회원가입 성공)
[ ] DB SELECT * FROM users; (데이터 있음)
```

---

## 🚀 빠른 시작 (복사-붙여넣기)

### Docker Compose 방식
```powershell
# 1. 시작
docker-compose up -d

# 2. 상태 확인
docker-compose ps

# 3. 헬스 체크
curl http://localhost:8001/health

# 4. 완료!
# http://localhost:8080/frontend/auth.html 접속
```

### 로컬 Python 방식
```powershell
# 1. DB 서비스만 시작
docker-compose up -d postgres redis rabbitmq

# 2. 새 터미널 5개 열기 (각각 실행)
cd auth-service && python main.py
cd book-service && python main.py
cd vote-service && python main.py
cd notify-service && python main.py
cd frontend && python -m http.server 8080

# 3. 완료!
# http://localhost:8080/frontend/auth.html 접속
```

---

## 📞 문제 해결

**모든 설정이 올바른지 확인:**
```bash
# 1. docker-compose.yml 확인
cat docker-compose.yml | grep -A 5 redis

# 2. .env 파일 확인
cat auth-service/.env
cat vote-service/.env

# 3. 포트 사용 확인
netstat -ano | findstr 8001
netstat -ano | findstr 5435
netstat -ano | findstr 6379

# 4. Docker 컨테이너 상태
docker-compose ps
docker-compose logs
```

완벽합니다! 이제 올바르게 실행되어야 합니다! 🎉

