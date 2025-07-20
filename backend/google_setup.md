# Google Services 설정 가이드

NSales Pro에서 Google Calendar와 Gmail을 사용하기 위한 설정 방법입니다.

## 1. Google Cloud Console 설정

### 1.1 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. 프로젝트 이름: `NSales Pro` (또는 원하는 이름)

### 1.2 API 활성화

1. **API 및 서비스 > 라이브러리** 메뉴로 이동
2. 다음 API들을 검색하여 활성화:
    - `Google Calendar API`
    - `Gmail API`

### 1.3 OAuth2 클라이언트 ID 생성

1. **API 및 서비스 > 사용자 인증 정보** 메뉴로 이동
2. **+ 사용자 인증 정보 만들기** → **OAuth 클라이언트 ID** 선택
3. 애플리케이션 유형: **웹 애플리케이션**
4. 이름: `NSales Pro Backend`
    5. **승인된 리디렉션 URI** 추가:
       ```
       http://localhost:8000/api/v1/google/callback
       ```
6. **만들기** 클릭

### 1.4 OAuth 동의 화면 설정

1. **OAuth 동의 화면** 메뉴로 이동
2. 사용자 유형: **외부** 선택 (개인용) 또는 **내부** (조직용)
3. 필수 정보 입력:
    - 앱 이름: `NSales Pro`
    - 사용자 지원 이메일: 본인 이메일
    - 개발자 연락처 정보: 본인 이메일
4. **범위** 단계에서 다음 범위 추가:
    - `../auth/calendar`
    - `../auth/gmail.modify`
    - `../auth/gmail.send`
    - `../auth/gmail.readonly`

## 2. 인증 정보 다운로드

1. 생성된 OAuth 클라이언트 ID에서 **JSON 다운로드** 클릭
2. 다운로드된 파일을 `credentials.json`으로 이름 변경
3. 파일을 다음 위치에 저장:
   ```
   /Users/sangcheol/IdeaProjects/nsales-pro/frontend/backend/credentials.json
   ```

## 3. credentials.json 파일 형식

다운로드된 파일은 다음과 같은 형식이어야 합니다:

```json
{
  "web": {
    "client_id": "your-client-id.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": [
      "http://localhost:8000/api/v1/google/callback"
    ]
  }
}
```

## 4. 서버 실행 및 인증

### 4.1 서버 실행

```bash
cd /Users/sangcheol/IdeaProjects/nsales-pro/frontend/backend
python main.py
```

### 4.2 Google 인증 진행

1. 브라우저에서 접속:
   ```
   http://localhost:8000/api/v1/google/auth
   ```
2. 반환된 `auth_url`로 이동
3. Google 계정으로 로그인
4. 권한 승인
5. 자동으로 프론트엔드로 리디렉션

### 4.3 인증 상태 확인

```bash
curl http://localhost:8000/api/v1/google/status
```

응답 예시:

```json
{
  "authenticated": true,
  "services_available": true
}
```

## 5. 사용 가능한 AI 명령어

인증 완료 후 다음과 같은 자연어 명령어를 사용할 수 있습니다:

### 📅 캘린더 관련

- "오늘 일정 확인해줘"
- "내일 오후 3시에 팀 미팅 일정 잡아줘"
- "이번 주 빈 시간 알려줘"
- "다음 주 화요일 2시간 회의 가능한 시간 찾아줘"

### 📧 이메일 관련

- "김과장님께 회의 일정 메일 보내줘"
- "최근 받은 중요한 메일 확인해줘"
- "subject:프로젝트 검색해서 메일 목록 보여줘"

### 🔄 통합 작업

- "내일 일정 확인하고 김대리님께 빈 시간 알려주는 메일 보내줘"
- "회의실 예약하고 참석자들에게 알림 메일 발송해줘"

## 6. 문제 해결

### 6.1 인증 오류

- `credentials.json` 파일 경로 확인
- Google Cloud Console에서 API 활성화 상태 확인
- OAuth 동의 화면 설정 완료 여부 확인

### 6.2 권한 오류

- OAuth 범위(scope) 설정 확인
- 사용자 계정 권한 확인

### 6.3 토큰 만료

- `token.pickle` 파일 삭제 후 재인증
- 브라우저에서 다시 `/api/v1/google/auth` 접속

## 7. 보안 주의사항

- `credentials.json`과 `token.pickle` 파일은 절대 git에 커밋하지 마세요
- `.gitignore`에 다음 항목 추가:
  ```
  credentials.json
  token.pickle
  ```
- 프로덕션 환경에서는 환경 변수로 관리하세요