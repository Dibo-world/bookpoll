# 📋 BookPoll 로컬 개발 환경 설정 가이드

## ✅ 실행 방법 (localhost에서 DB 저장까지 완벽 가이드)

### 1단계: PostgreSQL 실행
```powershell
# docker-compose로 DB, Redis, RabbitMQ 동시 실행
docker-compose up -d postgres redis rabbitmq

# 또는 전체 컨테이너
docker-compose up
```

**확인:**
```powershell
# PostgreSQL 로그 확인
docker-compose logs postgres

# 연결 테스트
psql -h localhost -U postgres -d bookpoll -p 5435 -c "SELECT 1"
```

---

### 2단계: 각 마이크로서비스 실행

#### A. Auth-Service
```powershell
cd auth-service
pip install -r requirements.txt
python main.py
```
✅ 포트: http://localhost:8001

#### B. Book-Service  
```powershell
cd book-service
pip install -r requirements.txt
python main.py
```
✅ 포트: http://localhost:8002

#### C. Vote-Service
```powershell
cd vote-service
pip install -r requirements.txt
python main.py
```
✅ 포트: http://localhost:8003

#### D. Notify-Service (선택)
```powershell
cd notify-service
pip install -r requirements.txt
python main.py
```
✅ 포트: http://localhost:8004

---

### 3단계: 프론트엔드 로컬 서버 실행

#### 옵션 A: Python http.server (권장 - 간단함)
```powershell
cd frontend

# Python 3.x
python -m http.server 8080

# 또는
python -m http.server 5500
```
접속: http://localhost:8080 (또는 5500)

#### 옵션 B: Node.js http-server
```powershell
npm install -g http-server

cd frontend
http-server -p 8080
```

#### 옵션 C: VSCode Live Server 확장
1. VSCode에 "Live Server" 확장 설치
2. `frontend/auth.html` 우클릭
3. "Go Live" 클릭

---

## 🔍 설정 확인 사항

### ✅ 체크리스트

```
[ ] PostgreSQL 실행 중 (포트 5435)
    docker-compose ps | grep postgres

[ ] .env 파일 수정됨
    ✅ auth-service/.env → password@localhost:5435/bookpoll
    ✅ book-service/.env → password@localhost:5435/bookpoll  
    ✅ vote-service/.env → password@localhost:5435/bookpoll

[ ] 각 서비스 실행 중
    ✅ http://localhost:8001/health
    ✅ http://localhost:8002/health
    ✅ http://localhost:8003/health

[ ] 프론트엔드 서버 실행 중
    ✅ http://localhost:8080 (또는 http://localhost:5500)

[ ] CORS 설정 완료
    ✅ 모든 main.py에 8001-8004 포트 추가됨
```

---

## 🧪 테스트 순서

### 1️⃣ API 직접 테스트 (curl 또는 Postman)

**회원가입 테스트:**
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","username":"테스트"}'
```

**응답 (성공):**
```json
{
  "success": true,
  "data": {"userId": 1, "username": "테스트"},
  "message": "ok"
}
```

---

### 2️⃣ 프론트엔드 회원가입 테스트

1. http://localhost:8080/frontend/auth.html 접속
2. "회원가입" 탭 클릭
3. 정보 입력:
   - 사용자명: 테스트
   - 이메일: test@example.com
   - 비밀번호: test123
4. "회원가입" 버튼 클릭
5. 성공 메시지 확인

**DB 확인:**
```bash
psql -h localhost -U postgres -d bookpoll -p 5435
SELECT * FROM users;
```

---

### 3️⃣ 로그인 및 대시보드 테스트

1. 로그인 (test@example.com / test123)
2. dashboard.html로 자동 이동
3. 책 등록 테스트
4. 투표 생성 테스트

**DB 확인:**
```bash
SELECT * FROM books;
SELECT * FROM polls;
```

---

## ⚠️ 문제 해결

### ❌ "연결할 수 없습니다" 에러

**원인 1: PostgreSQL 미실행**
```powershell
docker-compose up -d postgres
docker-compose logs postgres
```

**원인 2: .env 파일 설정 오류**
```powershell
# 각 서비스 .env 확인
cat auth-service/.env
cat book-service/.env
cat vote-service/.env
```
반드시 모두:
- `password@localhost:5435/bookpoll`이어야 함

**원인 3: 서비스 미실행**
```powershell
# 각 포트 확인
netstat -ano | findstr 8001
netstat -ano | findstr 8002
netstat -ano | findstr 8003
```

---

### ❌ "CORS 에러" 또는 "No 'Access-Control-Allow-Origin' 헤더"

**원인: CORS 화이트리스트 문제**

main.py 수정 (모든 서비스):
```python
ALLOWED_ORIGINS = [
    "http://localhost:8080",  # 프론트엔드 서버
    "http://localhost:5500",
    "http://localhost:8001",  # 서비스 간 통신
    "http://localhost:8002",
    "http://localhost:8003",
    "http://localhost:8004",
]
```

---

### ❌ 데이터가 DB에 저장 안 됨

**1. API 응답 확인**
```javascript
// 개발자 도구 (F12) → Network 탭
// 회원가입 요청 확인
// 응답이 200 OK이고 success: true인지 확인
```

**2. 서비스 로그 확인**
```powershell
# 각 서비스 콘솔 출력 확인
# 에러 로그 있는지 확인
```

**3. DB 직접 확인**
```bash
psql -h localhost -U postgres -d bookpoll -p 5435
\dt  # 테이블 목록
SELECT * FROM users;  # 사용자 확인
SELECT * FROM books;  # 책 확인
```

---

## 🚀 명령어 모음 (한번에 실행)

### Windows PowerShell

**모든 서비스 시작:**
```powershell
# 터미널 1: Docker 컨테이너
docker-compose up

# 터미널 2: Auth Service
cd auth-service
python main.py

# 터미널 3: Book Service
cd book-service
python main.py

# 터미널 4: Vote Service
cd vote-service
python main.py

# 터미널 5: 프론트엔드
cd frontend
python -m http.server 8080
```

**한 번에 중지:**
```powershell
# Ctrl+C 또는
docker-compose down
```

---

## 📊 구조 확인

```
localhost:8080 (프론트엔드)
    ↓
    ├─→ localhost:8001 (Auth-Service)
    │   └─→ PostgreSQL (localhost:5435)
    │
    ├─→ localhost:8002 (Book-Service)
    │   └─→ PostgreSQL (localhost:5435)
    │
    ├─→ localhost:8003 (Vote-Service)
    │   ├─→ PostgreSQL (localhost:5435)
    │   └─→ Redis (localhost:6379)
    │
    └─→ localhost:8004 (Notify-Service)
        └─→ RabbitMQ (localhost:5672)
```

---

## ✅ 최종 확인

모두 성공하면:

1. ✅ auth.html에서 회원가입 → DB 저장
2. ✅ auth.html에서 로그인 → dashboard.html 이동
3. ✅ dashboard.html에서 책 등록 → DB 저장
4. ✅ dashboard.html에서 투표 생성 → DB 저장
5. ✅ 투표 참여 → DB 저장 + Redis 업데이트

이 모든 것이 작동하면 로컬 개발 환경이 완벽하게 구성된 것입니다! 🎉

