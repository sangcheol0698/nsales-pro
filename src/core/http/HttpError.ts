import type { AxiosError } from 'axios';

// API 에러 응답 데이터의 인터페이스 정의
interface ApiErrorResponse {
  code?: string;
  message?: string;
}

export default class HttpError {
  private readonly code: string;
  private readonly message: string;

  constructor(error: AxiosError) {
    // response.data를 ApiErrorResponse 타입으로 캐스팅
    const errorData = error.response?.data as ApiErrorResponse;

    // 401 에러인 경우 세션 만료 메시지 설정
    if (error.response?.status === 401) {
      this.code = '401';
      this.message = '로그인 세션이 만료되었습니다. 다시 로그인해주세요.';
    } else {
      this.code = errorData?.code ?? '500';
      this.message = errorData?.message ?? '서버와의 연결이 원활하지 않습니다.';
    }
  }

  public getCode() {
    return this.code;
  }

  public getMessage() {
    return this.message;
  }

  public isSessionExpired() {
    return this.code === '401';
  }
}
