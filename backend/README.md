# NSales Pro Chat API

FastAPI 기반의 AI 채팅 서비스 API 서버입니다.

## 기능

- ✅ OpenAI GPT-3.5-turbo 기반 AI 채팅
- ✅ 실시간 스트리밍 채팅
- ✅ 채팅 세션 관리 (생성, 수정, 삭제)
- ✅ 메시지 히스토리 관리
- ✅ CORS 지원
- ✅ 메모리 기반 저장소 (개발용)

## 설치 및 실행

### 1. 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어서 OpenAI API 키를 설정하세요:

```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 3. 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 `http://localhost:8000`에서 실행됩니다.

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 기본

- `GET /` - API 정보
- `GET /api/v1/health` - 헬스 체크

### 채팅 세션 관리

- `POST /api/v1/chat/sessions` - 새 채팅 세션 생성
- `GET /api/v1/chat/sessions` - 채팅 세션 목록 조회
- `GET /api/v1/chat/sessions/{session_id}` - 특정 세션 조회
- `PATCH /api/v1/chat/sessions/{session_id}` - 세션 제목 수정
- `DELETE /api/v1/chat/sessions/{session_id}` - 세션 삭제

### 메시지 관리

- `GET /api/v1/chat/sessions/{session_id}/messages` - 메시지 히스토리 조회
- `POST /api/v1/chat/messages` - 메시지 전송 (일반)
- `POST /api/v1/chat/stream` - 메시지 전송 (스트리밍)
- `DELETE /api/v1/chat/messages/{message_id}` - 메시지 삭제
- `POST /api/v1/chat/messages/{message_id}/regenerate` - 메시지 재생성

## 예시 사용법

### 새 채팅 세션 생성

```bash
curl -X POST "http://localhost:8000/api/v1/chat/sessions" \
  -H "Content-Type: application/json" \
  -d '{"title": "영업 데이터 분석"}'
```

### 메시지 전송 (스트리밍)

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"content": "안녕하세요!", "sessionId": "session-id-here"}'
```

## 주의사항

- 현재 메모리 기반 저장소를 사용하므로 서버 재시작 시 데이터가 초기화됩니다.
- 실제 운영 환경에서는 PostgreSQL, MongoDB 등의 데이터베이스를 사용하는 것을 권장합니다.
- OpenAI API 키는 안전하게 관리하고 `.env` 파일을 커밋하지 마세요.

## 다음 단계

- [ ] 데이터베이스 연동 (SQLAlchemy + PostgreSQL)
- [ ] 사용자 인증 및 권한 관리
- [ ] 로깅 및 모니터링
- [ ] 레이트 리미팅
- [ ] 파일 업로드 지원