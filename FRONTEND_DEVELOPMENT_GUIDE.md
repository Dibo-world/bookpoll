# BookPoll - 프론트엔드 개발 가이드 (AI용 프롬프트)

다음 정보를 AI에게 전달해서 화면을 설계받을 때 사용하세요.

---

## 📋 기본 정보

BookPoll 프로젝트의 프론트엔드를 개발하고 있습니다. 현재 `dashboard.html`에서 도서 관리와 투표 관리 기능을 구현했고, 이제 마이페이지를 추가하려고 합니다.

## 🔌 현재 백엔드 스펙

### 1. 실시간 알림 방식

**방식: REST API 폴링 (WebSocket ❌)**

```
GET http://localhost:8004/api/v1/notify/messages
Headers: { X-User-Id: {userId} }

응답:
{
  "success": true,
  "data": [
    {
      "userId": 1,
      "message": "'1984' 책에 새 투표가 도착했어요!",
      "eventType": "VOTE_CAST",
      "createdAt": "2026-06-13T10:30:00"
    }
  ],
  "message": "ok"
}

사용방법: 3초마다 setInterval()로 이 API를 호출해서 새 알림 체크
```

**알림 타입:**
- `VOTE_CAST`: 누군가 책에 투표함
- `BOOK_REGISTERED`: 새 책이 등록됨

### 2. 도서 관리 API

#### 도서 수정 ✅
```
PUT http://localhost:8002/api/v1/books/{book_id}
Headers: { X-User-Id: {userId} }

요청 본문:
{
  "title": "수정된 제목",
  "author": "수정된 저자",
  "description": "수정된 설명"
}

응답: { "success": true, "data": { "id": 1, "title": "...", "author": "..." }, "message": "ok" }

에러:
- 404: 책이 없음
- 403: 자신이 등록한 책만 수정 가능
```

#### 도서 삭제 ✅
```
DELETE http://localhost:8002/api/v1/books/{book_id}
Headers: { X-User-Id: {userId} }

응답: { "success": true, "data": null, "message": "삭제 완료" }

에러:
- 404: 책이 없음
- 403: 자신이 등록한 책만 삭제 가능
```

### 3. 투표 관련 API

#### 투표 목록 조회 ✅
```
GET http://localhost:8003/api/v1/votes/polls

응답:
{
  "success": true,
  "data": [
    { "id": 7, "title": "2026 최고의 책", "status": "OPEN" },
    ...
  ],
  "message": "ok"
}
```

#### 투표 참여 ✅
```
POST http://localhost:8003/api/v1/votes/polls/{poll_id}/cast
Headers: { X-User-Id: {userId} }

요청: { "bookId": 2 }

응답: { "success": true, "data": { "message": "투표 완료", "bookId": 2 }, "message": "ok" }

에러:
- 401: 로그인 필요
- 404: 투표 없음
- 409: 이미 투표함
```

#### 투표 결과 조회 ✅
```
GET http://localhost:8003/api/v1/votes/polls/{poll_id}/result

응답:
{
  "success": true,
  "data": {
    "pollId": 7,
    "pollTitle": "2026 최고의 책",
    "results": [
      { "bookId": 2, "votes": 15, "rank": 1 },
      { "bookId": 1, "votes": 8, "rank": 2 },
      ...
    ]
  },
  "message": "ok"
}
```

#### ❌ 나의 투표 기록 (미구현)
**현재 없음** - 백엔드 개발 필요
- 필요한 API: `GET /api/v1/votes/my-votes` (또는 `/votes/history`)
- 내용: 현재 사용자가 투표한 모든 투표 목록 (투표명, 선택한 책, 투표 일시 등)

### 4. 인증 API ✅

#### 로그인 (이미 auth.html에서 구현)
```
POST http://localhost:8001/api/v1/auth/login

응답:
{
  "success": true,
  "data": {
    "token": "JWT_TOKEN",
    "userId": 1,
    "username": "john_doe"
  },
  "message": "ok"
}

localStorage에 저장:
- localStorage.setItem('userId', 1)
- localStorage.setItem('username', 'john_doe')
```

---

## 🎨 마이페이지 구현 계획

### 위치: dashboard.html에 새 탭 추가

**메뉴 구조:**
```
사이드바
├── 📖 도서 관리
├── 📊 투표 관리
└── 👤 마이페이지 (새로 추가)
```

**마이페이지 탭 2개:**

### 탭 1: 내가 등록한 도서 (즉시 구현 가능)

**표시 정보:**
- 도서 제목
- 저자
- 설명
- 등록 일시 (선택)
- 수정 버튼 (본인 책만)
- 삭제 버튼 (본인 책만)

**로직:**
1. 전체 도서 목록 조회 (GET /api/v1/books)
2. 현재 로그인한 userId와 book.userId가 같은 것만 필터링
3. 수정 클릭 → 모달에서 제목/저자/설명 수정 → PUT /api/v1/books/{id}
4. 삭제 클릭 → 확인 후 DELETE /api/v1/books/{id}

### 탭 2: 나의 투표 기록 (백엔드 준비 필요)

**표시 정보:**
- 투표 제목
- 내가 투표한 책 이름
- 투표 날짜/시간
- 결과 보기 버튼

**필요한 API:**
```
GET /api/v1/votes/my-votes (또는 /history)
응답:
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
    ...
  ],
  "message": "ok"
}
```

---

## 📦 현재 코드 상태

### dashboard.html의 구조

```javascript
// 현재 메뉴
- switchMenu('book')   // 도서 관리
- switchMenu('vote')   // 투표 관리

// 현재 섹션 (section-book, section-vote)
// → 새로 추가: section-mypage

// 현재 함수들
- loadBooks()           // 도서 목록 조회
- handleRegisterBook()  // 도서 등록
- deleteBook()          // 도서 삭제 (미구현)
- loadPolls()           // 투표 목록 조회
- handleCreateVote()    // 투표 생성
- viewPollDetail()      // 투표 참여

// 추가할 함수들
- loadMyBooks()         // 내가 등록한 도서만
- handleUpdateBook()    // 도서 수정
- loadMyVotes()         // 내 투표 기록 (백엔드 준비 필요)
```

---

## 🎯 구현 우선순위

### 1단계: 즉시 구현 (현재 API로 가능)
1. 사이드바에 "👤 마이페이지" 메뉴 추가
2. `section-mypage` 섹션 생성
3. 탭 2개로 분리 (내 도서 / 투표 기록)
4. **내가 등록한 도서 탭:**
   - 도서 목록에서 userId 필터링
   - 수정 버튼 → 모달 (form)
   - 삭제 버튼 (확인 후 DELETE)

### 2단계: 백엔드 준비 후 (1주일 후 정도)
5. `/api/v1/votes/my-votes` API 구현 완료되면
6. 투표 기록 탭 구현

### 3단계: 선택 (나중)
7. 알림 폴링을 WebSocket으로 개선

---

## 💡 개발 팁

### 수정 모달 만드는 방법
```javascript
// book-modal과 비슷하게 book-edit-modal 생성
// 수정 버튼 클릭 시:
// 1. 해당 도서 정보를 폼에 채우기
// 2. 모달 오픈
// 3. 제출하면 PUT /api/v1/books/{id} 호출

async function handleUpdateBook(bookId) {
  const payload = {
    title: document.getElementById('edit-book-title').value,
    author: document.getElementById('edit-book-author').value,
    description: document.getElementById('edit-book-desc').value
  };
  
  const res = await fetch(`http://localhost:8002/api/v1/books/${bookId}`, {
    method: 'PUT',
    headers: { 
      'Content-Type': 'application/json',
      'X-User-Id': userId 
    },
    body: JSON.stringify(payload)
  });
  
  const result = await res.json();
  if (result.success) {
    showToast('책이 수정되었습니다!');
    closeModal('book-edit-modal');
    loadMyBooks();
  } else {
    showToast(result.message, false);
  }
}
```

### 삭제 확인
```javascript
async function deleteBook(bookId) {
  if (!confirm('정말 삭제하시겠습니까?')) return;
  
  const res = await fetch(`http://localhost:8002/api/v1/books/${bookId}`, {
    method: 'DELETE',
    headers: { 'X-User-Id': userId }
  });
  
  const result = await res.json();
  if (result.success) {
    showToast('책이 삭제되었습니다!');
    loadMyBooks();
  } else {
    showToast(result.message, false);
  }
}
```

---

## 🎬 다음 단계

**지금 구현할 사항:**
1. dashboard.html에 마이페이지 섹션 추가
2. 내 도서 필터링 및 수정/삭제 UI
3. 알림 폴링 기능 (선택)

**백엔드 요청:**
- `/api/v1/votes/my-votes` API 구현 요청

**나중에:**
- 투표 기록 탭 구현 (API 준비 후)
- WebSocket 실시간 알림 (성능 개선)

