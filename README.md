# BookPoll — 독서 커뮤니티 투표 플랫폼

## 기술 스택
- Language: Python 3.11
- Framework: FastAPI
- ORM: SQLAlchemy 2.0 + Alembic
- DB: PostgreSQL 15, Redis 7
- 메시징: RabbitMQ (3-3에서 추가)

## 브랜치 전략
- main: 배포 브랜치 (직접 push 금지)
- develop: 통합 브랜치
- feat/{서비스명}-{기능}: 작업 브랜치

## 커밋 메시지 규칙
feat: 기능 추가
fix: 버그 수정
chore: 설정 변경
docs: 문서 수정

## API 규칙
- URL: /api/v1/{리소스(복수)}
- 응답: { "success": bool, "data": {}, "message": "string" }
- 인증헤더: Authorization: Bearer {token}

## 서비스 포트
- auth-service:   8001
- book-service:   8002
- vote-service:   8003
- notify-service: 8004