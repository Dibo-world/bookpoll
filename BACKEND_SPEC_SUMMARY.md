# 📋 백엔드 스펙 요약 (1장 정리)

## Q1. 실시간 알림 통신 방식

### 답변
**현재: REST API 폴링 (WebSocket/SSE 미구현)**

| 항목 | 내용 |
|------|------|
| **방식** | 3초마다 GET 요청으로 폴링 |
| **엔드포인트** | `GET http://localhost:8004/api/v1/notify/messages` |
| **인증** | `X-User-Id: {userId}` 헤더 |
| **구현** | ✅ notify-service/main.py에 구현됨 |
| **WebSocket** | ❌ 미구현 |
| **SSE** | ❌ 미구현 |

### 코드 예시
```javascript
// 3초마다 알림 체크
setInterval(async () => {
  const res = await fetch('http://localhost:8004/api/v1/notify/messages', {
    headers: { 'X-User-Id': userId }
  });
  const data = await res.json();
  // data.data[] 배열에 새 알림 있음
}, 3000);
```

### 알림 타입
- **VOTE_CAST**: 투표가 진행됨 → "'책이름' 책에 새 투표가 도착했어요!"
- **BOOK_REGISTERED**: 책이 등록됨 → "새 책 '책이름'이 등록됐어요!"

---

## Q2. 마이페이지 API 엔드포인트

### 2-1. 도서 수정 API

| 항목 | 내용 |
|------|------|
| **구현 상태** | ✅ 완료 |
| **메소드** | `PUT` |
| **URL** | `http://localhost:8002/api/v1/books/{book_id}` |
| **인증** | `X-User-Id: {userId}` 헤더 필수 |
| **파일** | book-service/app/routes/book_router.py |

**요청:**
```json
{
  "title": "수정된 제목",
  "author": "수정된 저자",
  "description": "수정된 설명"
}
```

**응답 (200):**
```json
{
  "success": true,
  "data": { "id": 1, "title": "...", "author": "..." },
  "message": "ok"
}
```

**에러:**
- 404: 책이 없음
- 403: 자신이 등록한 책만 수정 가능
- 401: 인증 필요

---

### 2-2. 도서 삭제 API

| 항목 | 내용 |
|------|------|
| **구현 상태** | ✅ 완료 |
| **메소드** | `DELETE` |
| **URL** | `http://localhost:8002/api/v1/books/{book_id}` |
| **인증** | `X-User-Id: {userId}` 헤더 필수 |
| **파일** | book-service/app/routes/book_router.py |

**응답 (200):**
```json
{
  "success": true,
  "data": null,
  "message": "삭제 완료"
}
```

---

### 2-3. 나의 투표 기록 API

| 항목 | 내용 |
|------|------|
| **구현 상태** | ❌ 미구현 |
| **필요한 메소드** | `GET` |
| **필요한 URL** | `http://localhost:8003/api/v1/votes/my-votes` (또는 `/history`) |
| **인증** | `X-User-Id: {userId}` 헤더 필수 |
| **담당** | vote-service 개발자 |

**기대 응답 형태:**
```json
{
  "success": true,
  "data": [
    {
      "pollId": 7,
      "pollTitle": "2026 최고의 책",
      "votedBookId": 2,
      "votedBookTitle": "1984",
      "votedAt": "2026-06-13T10:30:00"
    },
    {
      "pollId": 5,
      "pollTitle": "동물농장 vs 1984",
      "votedBookId": 3,
      "votedBookTitle": "동물농장",
      "votedAt": "2026-06-12T15:45:00"
    }
  ],
  "message": "ok"
}
```

---

## Q3. 마이페이지 UI 위치

### 추천: dashboard.html에 탭으로 추가

#### 현재 구조
```
dashboard.html
├── 사이드바 메뉴
│   ├── 📖 도서 관리
│   └── 📊 투표 관리
└── 메인 영역
    ├── section-book
    └── section-vote
```

#### 추천 구조 (마이페이지 추가)
```
dashboard.html
├── 사이드바 메뉴
│   ├── 📖 도서 관리
│   ├── 📊 투표 관리
│   └── 👤 마이페이지 (새로)
└── 메인 영역
    ├── section-book
    ├── section-vote
    └── section-mypage (새로)
        ├── tab: 내가 등록한 도서
        └── tab: 나의 투표 기록
```

### 장점
✅ 한 화면(dashboard.html)에서 모든 기능 관리  
✅ 탭으로 전환 가능 (사용자 경험 일관성)  
✅ 별도 페이지 불필요  
✅ 사이드바로 빠른 네비게이션  

### 마이페이지 내용

#### 탭 1: 내가 등록한 도서 (즉시 구현 가능)
```
┌─────────────────────────────────┐
│ 📚 내가 등록한 도서               │
├─────────────────────────────────┤
│ [1984]                [수정][삭제] │
│ George Orwell                  │
│ 디스토피아 소설                  │
├─────────────────────────────────┤
│ [동물농장]            [수정][삭제] │
│ George Orwell                  │
│ 풍자 소설                       │
└─────────────────────────────────┘
```

**구현 방법:**
1. 전체 도서 목록 조회 (GET /api/v1/books)
2. 현재 userId와 일치하는 책만 필터링
3. 수정/삭제 버튼 추가 (본인 책만)

**필요한 API:**
- ✅ GET /api/v1/books (이미 구현)
- ✅ PUT /api/v1/books/{id} (이미 구현)
- ✅ DELETE /api/v1/books/{id} (이미 구현)

---

#### 탭 2: 나의 투표 기록 (백엔드 준비 필요)
```
┌──────────────────────────────────┐
│ 📊 나의 투표 기록                  │
├──────────────────────────────────┤
│ 투표명: 2026 최고의 책             │
│ 선택: 1984                      │
│ 일시: 2026-06-13 10:30   [결과보기] │
├──────────────────────────────────┤
│ 투표명: 동물농장 vs 1984           │
│ 선택: 동물농장                     │
│ 일시: 2026-06-12 15:45   [결과보기] │
└──────────────────────────────────┘
```

**구현 방법:**
1. GET /api/v1/votes/my-votes 호출
2. 투표 기록 목록 표시
3. "결과보기" → 클릭하면 GET /api/v1/votes/polls/{pollId}/result 호출

**필요한 API:**
- ❌ GET /api/v1/votes/my-votes (미구현 - 백엔드 필요)
- ✅ GET /api/v1/votes/polls/{id}/result (이미 구현)

---

## 📊 구현 체크리스트

### Phase 1: 즉시 구현 가능 (현재 코드)

- [ ] dashboard.html 사이드바에 "👤 마이페이지" 메뉴 추가
- [ ] switchMenu('mypage') 함수 추가
- [ ] section-mypage 섹션 생성
- [ ] 탭 UI (내 도서 / 투표 기록)
- [ ] 내 도서 필터링 (userId 기반)
- [ ] 도서 수정 모달 생성
- [ ] 도서 수정 함수 (PUT /api/v1/books/{id})
- [ ] 도서 삭제 함수 (DELETE /api/v1/books/{id})
- [ ] 알림 폴링 기능 (3초마다 GET /api/v1/notify/messages)

### Phase 2: 백엔드 준비 후

- [ ] vote-service에 GET /api/v1/votes/my-votes 구현 요청
- [ ] 투표 기록 탭 구현
- [ ] 투표 결과 보기 모달

### Phase 3: 향후 개선

- [ ] WebSocket 또는 SSE로 알림 개선
- [ ] 폴링 제거

---

## 🚀 다음 액션

### 즉시 (지금)
1. BACKEND_SPEC_ANALYSIS.md 참고
2. dashboard.html에서 마이페이지 섹션 추가
3. 내 도서 탭 구현

### 1주일 후
1. 백엔드팀에 GET /api/v1/votes/my-votes 구현 확인
2. 투표 기록 탭 구현

### 선택사항
- 알림 WebSocket/SSE 개선

