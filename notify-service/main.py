from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="Notify Service", version="1.0.0")

# 인메모리 알림 저장소 (서비스 재시작 시 초기화 — 입문 단계 OK)
notifications = []

class EventPayload(BaseModel):
    eventType: str          # VOTE_CAST | BOOK_REGISTERED
    userId: int
    bookTitle: Optional[str] = ""

def ok(data=None, message="ok", status_code=200):
    return JSONResponse(status_code=status_code,
                        content={"success": True, "data": data, "message": message})

# ── 이벤트 수신 (내부 전용 — 3-3에서 RabbitMQ로 교체) ────
@app.post("/api/v1/notify/event")
def receive_event(body: EventPayload):
    if body.eventType == "VOTE_CAST":
        message = f"'{body.bookTitle}' 책에 새 투표가 도착했어요!"
    elif body.eventType == "BOOK_REGISTERED":
        message = f"새 책 '{body.bookTitle}'이 등록됐어요!"
    else:
        message = "새 알림이 있어요."

    notifications.append({
        "userId": body.userId,
        "message": message,
        "eventType": body.eventType,
        "createdAt": datetime.utcnow().isoformat()
    })
    return ok(message="이벤트 처리 완료")

# ── 내 알림 목록 조회 ─────────────────────────────────────
@app.get("/api/v1/notify/messages")
def get_messages(x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        return JSONResponse(status_code=401,
                            content={"success": False, "data": None, "message": "인증 필요"})
    my_list = [n for n in notifications if str(n["userId"]) == x_user_id]
    return ok(my_list)

@app.get("/health")
def health():
    return {"status": "ok", "service": "notify-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)