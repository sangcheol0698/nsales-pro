# Sales Pro API 명세서

## 목차
1. [인증 API (Authentication)](#1-인증-api-authentication)
2. [회원 API (Member)](#2-회원-api-member)
3. [프로젝트 API (Project)](#3-프로젝트-api-project)
4. [직원 API (Employee)](#4-직원-api-employee)

## 1. 인증 API (Authentication)

### 1.1. 로그인 (Login)
- **URL**: `/api/v1/auths/login`
- **Method**: `POST`
- **권한**: 인증 불필요
- **설명**: 사용자 로그인을 처리합니다.
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

  - `username`: 사용자 이메일
  - `password`: 사용자 비밀번호
- **Response**: 성공 시 200 OK와 함께 세션 쿠키가 설정됩니다.

### 1.2. 로그아웃 (Logout)
- **URL**: `/api/v1/auths/logout`
- **Method**: `POST`
- **권한**: 인증 필요
- **설명**: 사용자 로그아웃을 처리합니다.
- **Response**: 성공 시 200 OK와 함께 세션 쿠키가 삭제됩니다.

### 1.3. 회원 등록 (Register)
- **URL**: `/api/v1/auths/register`
- **Method**: `POST`
- **권한**: 인증 불필요
- **설명**: 새로운 회원을 등록합니다.
- **Request Body**:
  ```json
  {
    "name": "string",    // 사용자 이름 (필수)
    "email": "string"    // 사용자 이메일 (필수, 이메일 형식)
  }
  ```
- **Response**: 성공 시 200 OK

### 1.4. 비밀번호 초기화 (Initialize Password)
- **URL**: `/api/v1/auths/initialize`
- **Method**: `PATCH`
- **권한**: 인증 불필요
- **설명**: 비밀번호를 초기화합니다.
- **Request Body**:
  ```json
  {
    "token": "string",            // 비밀번호 초기화 토큰 (필수)
    "newPassword": "string",      // 새 비밀번호 (필수)
    "newPasswordConfirm": "string" // 새 비밀번호 확인 (필수)
  }
  ```
- **Response**: 성공 시 200 OK

### 1.5. 비밀번호 찾기 (Find Password)
- **URL**: `/api/v1/auths/find-password`
- **Method**: `POST`
- **권한**: 인증 불필요
- **설명**: 비밀번호 찾기 요청을 처리합니다.
- **Request Body**:
  ```json
  {
    "email": "string"  // 사용자 이메일 (필수, 이메일 형식)
  }
  ```
- **Response**: 성공 시 200 OK

## 2. 회원 API (Member)

### 2.1. 내 정보 조회 (Get My Info)
- **URL**: `/api/v1/members/my`
- **Method**: `GET`
- **권한**: 인증 필요
- **설명**: 현재 로그인한 회원의 정보를 조회합니다.
- **Response**:
  ```json
  {
    "name": "string",    // 사용자 이름
    "username": "string" // 사용자 아이디(이메일)
  }
  ```

### 2.2. 비밀번호 변경 (Change Password)
- **URL**: `/api/v1/members/password`
- **Method**: `PATCH`
- **권한**: 인증 필요
- **설명**: 현재 로그인한 회원의 비밀번호를 변경합니다.
- **Request Body**:
  ```json
  {
    "password": "string",          // 현재 비밀번호 (필수)
    "newPassword": "string",       // 새 비밀번호 (필수)
    "newPasswordConfirm": "string" // 새 비밀번호 확인 (필수)
  }
  ```
- **Response**: 성공 시 200 OK

## 3. 프로젝트 API (Project)

### 3.1. 프로젝트 상세 조회 (Get Project Detail)
- **URL**: `/api/v1/projects/{id}`
- **Method**: `GET`
- **권한**: '프로젝트 편집' 또는 '프로젝트 조회' 권한 필요
- **설명**: 특정 프로젝트의 상세 정보를 조회합니다.
- **Path Parameters**:
  - `id`: 프로젝트 ID
- **Response**:
  ```json
  {
    "id": 0,                      // 프로젝트 ID
    "name": "string",             // 프로젝트 이름
    "code": "string",             // 프로젝트 코드
    "type": "SI" | "SM",          // 프로젝트 유형 (SI: 시스템 통합, SM: 시스템 유지보수)
    "status": "예약" | "진행중" | "완료", // 프로젝트 상태
    "contractDate": "2023-01-01", // 계약일
    "department": {               // 담당 부서 정보
      // 부서 정보 객체
    },
    "startDate": "2023-01-01",    // 시작일
    "endDate": "2023-12-31",      // 종료일
    "pmName": "string",           // 프로젝트 매니저 이름
    "pmPhone": "string",          // 프로젝트 매니저 전화번호
    "mainCompany": "string",      // 주 계약 회사
    "mainCompanyRep": "string",   // 주 계약 회사 담당자
    "mainCompanyRepPhone": "string", // 주 계약 회사 담당자 전화번호
    "clientCompany": "string",    // 고객사
    "clientCompanyRep": "string", // 고객사 담당자
    "clientCompanyRepPhone": "string", // 고객사 담당자 전화번호
    "expectedAmount": 0,          // 예상 금액
    "contractAmount": 0,          // 계약 금액
    "modifiedDateTime": "2023-01-01T00:00:00" // 수정일시
  }
  ```

### 3.2. 프로젝트 검색 (Search Projects)
- **URL**: `/api/v1/projects`
- **Method**: `GET`
- **권한**: '프로젝트 편집' 또는 '프로젝트 조회' 권한 필요
- **설명**: 조건에 맞는 프로젝트 목록을 조회합니다.
- **Query Parameters**:
  - `searchType`: 검색 유형 (시작일자, 종료일자, 계약일자)
  - `startDate`: 시작일
  - `endDate`: 종료일
  - `type`: 프로젝트 유형 (SI, SM)
  - `status`: 프로젝트 상태 (예약, 진행중, 완료)
  - `name`: 프로젝트 이름
  - `code`: 프로젝트 코드
  - `page`: 페이지 번호 (기본값: 0)
  - `size`: 페이지 크기 (기본값: 20)
  - `sort`: 정렬 기준 (예: name,asc)
- **Response**:
  ```json
  {
    "content": [
      {
        "id": 0,                      // 프로젝트 ID
        "code": "string",             // 프로젝트 코드
        "name": "string",             // 프로젝트 이름
        "type": "SI" | "SM",          // 프로젝트 유형
        "startDate": "2023-01-01",    // 시작일
        "endDate": "2023-12-31",      // 종료일
        "contractDate": "2023-01-01", // 계약일
        "contractAmount": 0,          // 계약 금액
        "mainCompany": "string",      // 주 계약 회사
        "clientCompany": "string",    // 고객사
        "status": "예약" | "진행중" | "완료" // 프로젝트 상태
      }
    ],
    "pageable": {
      // 페이징 정보
    },
    "totalElements": 0,
    "totalPages": 0,
    "last": true,
    "size": 20,
    "number": 0,
    "sort": {
      // 정렬 정보
    },
    "numberOfElements": 0,
    "first": true,
    "empty": true
  }
  ```

### 3.3. 프로젝트 생성 (Create Project)
- **URL**: `/api/v1/projects`
- **Method**: `POST`
- **권한**: '프로젝트 편집' 권한 필요
- **설명**: 새로운 프로젝트를 생성합니다.
- **Request Body**:
  ```json
  {
    "code": "string",             // 프로젝트 코드 (필수)
    "name": "string",             // 프로젝트 이름 (필수)
    "type": "SI" | "SM",          // 프로젝트 유형 (필수)
    "contractDate": "2023-01-01", // 계약일 (필수)
    "expectedAmount": 0,          // 예상 금액
    "contractAmount": 0,          // 계약 금액
    "departmentId": 0,            // 담당 부서 ID (필수)
    "pmName": "string",           // 프로젝트 매니저 이름
    "pmPhone": "string",          // 프로젝트 매니저 전화번호
    "startDate": "2023-01-01",    // 시작일
    "endDate": "2023-12-31",      // 종료일
    "mainCompany": "string",      // 주 계약 회사 (필수)
    "mainCompanyRep": "string",   // 주 계약 회사 담당자
    "mainCompanyRepPhone": "string", // 주 계약 회사 담당자 전화번호
    "clientCompany": "string",    // 고객사 (필수)
    "clientCompanyRep": "string", // 고객사 담당자
    "clientCompanyRepPhone": "string" // 고객사 담당자 전화번호
  }
  ```
- **Response**: 성공 시 200 OK

### 3.4. 프로젝트 수정 (Update Project)
- **URL**: `/api/v1/projects/{id}`
- **Method**: `PUT`
- **권한**: '프로젝트 편집' 권한 필요
- **설명**: 기존 프로젝트 정보를 수정합니다.
- **Path Parameters**:
  - `id`: 프로젝트 ID
- **Request Body**: 프로젝트 생성 요청과 동일한 형식
- **Response**: 성공 시 200 OK

### 3.5. 프로젝트 삭제 (Delete Project)
- **URL**: `/api/v1/projects/{id}`
- **Method**: `DELETE`
- **권한**: '프로젝트 편집' 권한 필요
- **설명**: 프로젝트를 삭제합니다.
- **Path Parameters**:
  - `id`: 프로젝트 ID
- **Response**: 성공 시 200 OK

### 3.6. 내 프로젝트 조회 (Get My Projects)
- **URL**: `/api/v1/projects/my`
- **Method**: `GET`
- **권한**: 인증 필요
- **설명**: 현재 로그인한 사용자의 프로젝트 목록을 조회합니다.
- **Response**: 프로젝트 검색 응답과 동일한 형식

## 4. 직원 API (Employee)

### 4.1. 직원 상세 조회 (Get Employee Detail)
- **URL**: `/api/v1/employees/{id}`
- **Method**: `GET`
- **권한**: '구성원 조회' 또는 '구성원 편집' 권한 필요
- **설명**: 특정 직원의 상세 정보를 조회합니다.
- **Path Parameters**:
  - `id`: 직원 ID
- **Response**:
  ```json
  {
    // 직원 상세 정보
  }
  ```

### 4.2. 내 직원 정보 조회 (Get My Employee Info)
- **URL**: `/api/v1/employees/my`
- **Method**: `GET`
- **권한**: 인증 필요
- **설명**: 현재 로그인한 사용자의 직원 정보를 조회합니다.
- **Response**:
  ```json
  {
    // 직원 정보
  }
  ```

### 4.3. 직원 검색 (Search Employees)
- **URL**: `/api/v1/employees`
- **Method**: `GET`
- **권한**: '구성원 조회' 또는 '구성원 편집' 권한 필요
- **설명**: 조건에 맞는 직원 목록을 조회합니다.
- **Query Parameters**:
  - 검색 조건 파라미터
  - 페이징 파라미터
- **Response**:
  ```json
  {
    "content": [
      {
        // 직원 정보
      }
    ],
    // 페이징 정보
  }
  ```

### 4.4. 직원 생성 (Create Employee)
- **URL**: `/api/v1/employees`
- **Method**: `POST`
- **권한**: '구성원 편집' 권한 필요
- **설명**: 새로운 직원을 생성합니다.
- **Request Body**:
  ```json
  {
    // 직원 생성 정보
  }
  ```
- **Response**: 성공 시 200 OK

### 4.5. 직원 수정 (Update Employee)
- **URL**: `/api/v1/employees/{id}`
- **Method**: `PUT`
- **권한**: '구성원 편집' 권한 필요
- **설명**: 기존 직원 정보를 수정합니다.
- **Path Parameters**:
  - `id`: 직원 ID
- **Request Body**:
  ```json
  {
    // 직원 수정 정보
  }
  ```
- **Response**: 성공 시 200 OK

### 4.6. 직원 삭제 (Delete Employee)
- **URL**: `/api/v1/employees/{id}`
- **Method**: `DELETE`
- **권한**: '구성원 편집' 권한 필요
- **설명**: 직원을 삭제합니다.
- **Path Parameters**:
  - `id`: 직원 ID
- **Response**: 성공 시 200 OK

### 4.7. 직원 퇴사 처리 (Employee Leave)
- **URL**: `/api/v1/employees/{id}/leave`
- **Method**: `POST`
- **권한**: '구성원 편집' 권한 필요
- **설명**: 직원의 퇴사 처리를 합니다.
- **Path Parameters**:
  - `id`: 직원 ID
- **Request Body**:
  ```json
  {
    "leaveDate": "2023-01-01" // 퇴사일
  }
  ```
- **Response**: 성공 시 200 OK
