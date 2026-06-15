Markdown
# BookPoll — 독서 커뮤니티 투표 플랫폼

## 🛠️ 기술 스택
- **Language:** Python 3.11
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0 + Alembic
- **DB:** PostgreSQL 15, Redis 7
- **메시징:** RabbitMQ (3-3에서 추가)

## 🔀 브랜치 전략
- `main`: 배포 브랜치 (직접 push 금지)
- `develop`: 통합 브랜치
- `feat/{서비스명}-{기능}`: 작업 브랜치

## 📝 커밋 메시지 규칙
- `feat`: 기능 추가
- `fix`: 버그 수정
- `chore`: 설정 변경
- `docs`: 문서 수정

## 🌐 API 규칙
- **URL:** `/api/v1/{리소스(복수)}`
- **응답:** `{ "success": bool, "data": {}, "message": "string" }`
- **인증헤더:** `Authorization: Bearer {token}`

---

## 🔌 쿠버네티스 인프라 환경 및 포트 정보

### 1. 내부 서비스 포트 (Service Ports)
- **auth-service:** 8001
- **book-service:** 8002
- **vote-service:** 8003
- **notify-service:** 8004

### 2. 로컬 모니터링 및 개발 툴 접속 가이드 (Port-Forwarding)
> 💡 주의: 아래 명령어를 실행한 터미널 창을 유지해야 접속 주소로 정상 접근이 가능합니다.

| 도구명 | 포트 포워딩 실행 명령어 | 웹 브라우저 접속 주소 (URL) | 접속 계정 정보 |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | `kubectl port-forward svc/postgres 5432:5432 -n bookpoll` | `127.0.0.1:5432` (HeidiSQL 연동) | 설정한 DB 계정 |
| **RabbitMQ** | `kubectl port-forward svc/rabbitmq 15672:15672 -n bookpoll` | `http://localhost:15672` | `guest` / `guest` |
| **ArgoCD** | `kubectl port-forward svc/argocd-server -n argo 8080:443` | `https://localhost:8080` | `guest` / `7xhT7Ski0psUVmCU` |
| **Grafana** | `kubectl port-forward svc/grafana -n monitoring 3000:80` | `http://localhost:3000` | `istioctl dashboard grafana` 가능 |
| **Kiali (Istio)** | `kubectl port-forward svc/kiali -n istio-system 20001:20001` | `http://localhost:20001` | `istioctl dashboard kiali` 가능 |

---

## 🛣️ Ingress 기반 단일 엔드포인트 접속 환경 (최종 제출본)

Minikube Ingress 애드온 및 `minikube tunnel`을 활용하여 하나의 도메인과 경로 기반 라우팅(Path-based Routing)으로 서비스를 통합했습니다.

- **기본 접속 도메인:** `http://bookpoll.local` (로컬 `hosts` 파일에 `127.0.0.1 bookpoll.local` 등록 필요)

### 경로별 라우팅 주소
- **프론트엔드 메인 화면:** `http://bookpoll.local/frontend/dashboard.html`
- **로그인/인증 화면:** `http://bookpoll.local/frontend/auth.html`
- **인증 API 백엔드:** `http://bookpoll.local/auth`
- **도서 API 백엔드:** `http://bookpoll.local/book`
- **투표 API 백엔드:** `http://bookpoll.local/vote`
- **알림 API 백엔드:** `http://bookpoll.local/notify`

---

## 🏃‍♂️ 핵심 실행 명령어 모음 Cheat-Sheet

### 💻 1. Docker 및 Minikube 초기화 (터미널 1)
```powershell
# [1] 도커 데스크탑 앱이 켜진 상태에서, 미니쿠베 클러스터 기동
minikube start --driver=docker

# [2] 인그레스(bookpoll.local) 활성화를 위한 터널 개방 (창을 닫지 말고 그대로 유지)
minikube tunnel
🔌 2. 포트 포워딩 및 개발 도구 연결 (터미널 2)
PowerShell
# PostgreSQL (HeidiSQL 접속용)
kubectl port-forward svc/postgres 5432:5432 -n bookpoll

# RabbitMQ 대시보드 (http://localhost:15672)
kubectl port-forward svc/rabbitmq 15672:15672 -n bookpoll

# ArgoCD 대시보드 (https://localhost:8080)
kubectl port-forward svc/argocd-server -n argo 8080:443
🚀 3. Git 푸시 명령어 (터미널 3)
PowerShell
git add .
git commit -m "docs: 최종 제출본 리드미 및 인그레스 반영"
git push origin main -f
🗄️ 4. HeidiSQL 데이터베이스 연결 설정 가이드
네트워크 유형 (Network Type): PostgreSQL

호스트명 / IP (Hostname / IP): 127.0.0.1 (또는 localhost)

사용자 (User): postgres

암호 (Password): [설정한 DB 비밀번호]

포트 (Port): 5432

데이터베이스 (Database): bookpoll


---

### 🚀 2단계: 터미널에서 밀어 올리기

파일을 위 내용으로 깔끔하게 저장하셨다면, 터미널창을 켜고 아래 3줄을 순서대로 입력해 깃허브로 보냅니다. 충돌 잔해를 모두 지웠기 때문에 이번엔 확실하게 올라갑니다.

```powershell
git add .
git commit -m "fix: 리드미 병합 충돌 해결 및 최종본 업로드"
git push origin main -f