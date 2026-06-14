# AI용 초간단 프롬프트 (복사 붙여넣기용)

다음을 AI(ChatGPT, Claude 등)에 바로 붙여넣으세요.

---

**상황:**
BookPoll이라는 책 투표 커뮤니티 앱을 개발하고 있습니다. 현재 dashboard.html에서 도서 관리와 투표 관리 기능이 구현되어 있고, 마이페이지 기능을 추가하려고 합니다.

**현재 기술 스택:**
- Frontend: Vanilla JS + Tailwind CSS
- Backend: FastAPI (Python)
- 포트: auth(8001), book(8002), vote(8003), notify(8004)

---

## 백엔드 스펙

### 1. 실시간 알림
- **방식:** REST API 폴링 (3초마다)
- **API:** GET `http://localhost:8004/api/v1/notify/messages`
- **헤더:** `X-User-Id: {userId}`
- **응답:**
```json
{
  "data": [
    { "userId": 1, "message": "'1984'에 새 투표가 도착했어요!", "eventType": "VOTE_CAST", "createdAt": "2026-06-13T10:30:00" }
  ]
}
```

### 2. 도서 수정 API ✅
```
PUT http://localhost:8002/api/v1/books/{book_id}
헤더: X-User-Id: {userId}

요청: { "title": "...", "author": "...", "description": "..." }
응답: { "success": true, "data": { "id": 1, "title": "...", "author": "..." } }

에러: 404(없음), 403(본인만), 401(인증)
```

### 3. 도서 삭제 API ✅
```
DELETE http://localhost:8002/api/v1/books/{book_id}
헤더: X-User-Id: {userId}

응답: { "success": true, "message": "삭제 완료" }

에러: 404(없음), 403(본인만), 401(인증)
```

### 4. 나의 투표 기록 API ❌ (미구현)
아직 백엔드에 없음. 향후 다음과 같은 API가 필요:
```
GET http://localhost:8003/api/v1/votes/my-votes
헤더: X-User-Id: {userId}

응답 (예상):
{
  "data": [
    { "pollId": 7, "pollTitle": "2026 최고의 책", "votedBookTitle": "1984", "votedAt": "2026-06-13T10:30:00" }
  ]
}
```

### 5. 투표 결과 API ✅
```
GET http://localhost:8003/api/v1/votes/polls/{poll_id}/result

응답:
{
  "data": {
    "pollId": 7,
    "pollTitle": "2026 최고의 책",
    "results": [
      { "bookId": 2, "votes": 15, "rank": 1 },
      { "bookId": 1, "votes": 8, "rank": 2 }
    ]
  }
}
```

---

## UI 기획

### 마이페이지 위치
- **위치:** dashboard.html에 새 탭 추가
- **사이드바 메뉴:**
  - 📖 도서 관리
  - 📊 투표 관리
  - 👤 마이페이지 (새로 추가)

### 마이페이지 탭

#### 탭 1: 내가 등록한 도서 (즉시 구현)
```
┌──────────────────────────────┐
│ 내가 등록한 도서              │
├──────────────────────────────┤
│ [1984]            [수정][삭제] │
│ George Orwell               │
│ 디스토피아 소설              │
├──────────────────────────────┤
│ [동물농장]        [수정][삭제] │
│ George Orwell               │
│ 풍자 소설                   │
└──────────────────────────────┘
```

**기능:**
- 현재 로그인 사용자가 등록한 책만 표시
- [수정] 클릭 → 모달에서 제목/저자/설명 수정
- [삭제] 클릭 → 확인 후 삭제

#### 탭 2: 나의 투표 기록 (백엔드 준비 후)
```
┌──────────────────────────────────┐
│ 나의 투표 기록                     │
├──────────────────────────────────┤
│ 투표명: 2026 최고의 책            │
│ 선택: 1984                      │
│ 일시: 2026-06-13 10:30 [결과보기] │
├──────────────────────────────────┤
│ 투표명: 동물농장 vs 1984          │
│ 선택: 동물농장                    │
│ 일시: 2026-06-12 15:45 [결과보기] │
└──────────────────────────────────┘
```

**기능:**
- 현재 사용자의 투표 기록 표시
- [결과보기] 클릭 → 해당 투표의 결과를 모달에서 표시

---

## 요청

위 정보를 바탕으로 다음을 설계해주세요:

1. **마이페이지 HTML 구조 및 CSS** (Tailwind로 구성)
   - 메뉴 추가 (사이드바에 마이페이지)
   - 탭 2개 UI
   - 도서 카드 컴포넌트
   - 투표 기록 카드 컴포넌트

2. **마이페이지 JavaScript 로직**
   - switchMenu('mypage') 함수
   - loadMyBooks() - 내 도서만 필터링
   - handleUpdateBook() - PUT 요청으로 수정
   - deleteBook() - DELETE 요청으로 삭제
   - loadMyVotes() - 투표 기록 로드 (백엔드 준비 후)
   - viewVoteResult() - 투표 결과 모달

3. **도서 수정 모달**
   - 기존 도서 정보 폼에 채우기
   - 수정 제출 로직

4. **투표 결과 모달**
   - 투표 결과를 순위 목록으로 표시 (바 차트 또는 테이블)

5. **알림 폴링 기능**
   - 3초마다 GET /api/v1/notify/messages 호출
   - 새 알림 표시 (토스트 또는 배지)
   - 알림 타입 (VOTE_CAST, BOOK_REGISTERED)에 따른 다른 메시지

---

**현재 dashboard.html 코드 상태:**
- 이미 기본 구조 있음 (도서 관리, 투표 관리)
- Toast 알림 시스템 구현됨
- API 헤더 구성 완료 (X-User-Id)
- 모달 열고 닫기 기능 구현됨

위 정보로 마이페이지 추가 코드를 생성해주세요!

