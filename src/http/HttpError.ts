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
    this.code = errorData?.code ?? '500';
    this.message = errorData?.message ?? '서버와의 연결이 원활하지 않습니다.';
  }

  public getCode() {
    return this.code;
  }

  public getMessage() {
    return this.message;
  }
}
