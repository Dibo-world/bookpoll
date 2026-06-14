from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


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


@router.get("/notifications")
def get_notifications():
    data = [
        {
            "id": 1,
            "type": "vote_cast",
            "title": "새 투표가 반영되었습니다",
            "message": "사용자 투표 이벤트가 수신되었습니다.",
            "createdAt": "2026-06-14T02:30:00"
        }
    ]
    return ok(data=data, message="알림 목록 조회 성공")