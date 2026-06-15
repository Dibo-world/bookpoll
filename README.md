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

# 실행 코드 정리

💻 1. Docker 및 Minikube 초기화 (터미널 1)
```
# [1] 도커 데스크탑 앱이 켜진 상태에서, 미니쿠베 클러스터 기동
minikube start --driver=docker

# [2] 인그레스(bookpoll.local) 활성화를 위한 터널 개방 (창을 닫지 말고 그대로 유지)
minikube tunnel
```
🔌 2. 포트 포워딩 및 개발 도구 연결 (터미널 2)
```
# PostgreSQL (HeidiSQL 접속용)
kubectl port-forward svc/postgres 5432:5432 -n bookpoll

# RabbitMQ 대시보드 (http://localhost:15672)
kubectl port-forward svc/rabbitmq 15672:15672 -n bookpoll

# ArgoCD 대시보드 (https://localhost:8080)
kubectl port-forward svc/argocd-server -n argo 8080:443

# Grafana 대시보드 (http://localhost:3000)
kubectl port-forward svc/grafana -n monitoring 3000:80

# Kiali 대시보드 (http://localhost:20001)
kubectl port-forward svc/kiali -n istio-system 20001:20001
```

🚀 3. Git 안전 푸시 (터미널 3)
```
# [1] 수정한 파일 전체 스테이징
git add .

# [2] 커밋 메시지 작성
git commit -m "docs: 최종 제출본 리드미 및 인그레스 반영"

# [3] 원격 저장소 꼬임 무시하고 내 컴퓨터 상태로 대못 박기 (강제 푸시)
git push origin main -f
```
🗄️ 4. HeidiSQL 데이터베이스 연결 설정 가이드
```
kubectl port-forward svc/postgres 5432:5432 -n bookpoll

⚙️ HeidiSQL 세션 관리자 설정 값
HeidiSQL을 실행하고 [신규] 버튼을 누른 뒤 오른쪽 설정 창을 아래와 같이 채워 넣습니다.
네트워크 유형 (Network Type): PostgreSQL
호스트명 / IP (Hostname / IP): 127.0.0.1 (또는 localhost)
사용자 (User): postgres (설계 시 지정한 DB 마스터 아이디)
암호 (Password): [본인이 설정한 PostgreSQL 비밀번호]
포트 (Port): 5432
데이터베이스 (Database): bookpoll (또는 생성한 기본 데이터베이스 명칭)

💡 연결 팁: 설정을 다 적으셨다면 좌측 하단의 **[저장]**을 누르고 **[열기]**를 누르면 쿠버네티스 내부 DB 안으로 안전하게 진입하여 테이블 구조를 눈으로 확인하실 수 있습니다!
```
