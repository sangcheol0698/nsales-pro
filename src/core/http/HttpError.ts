import type { AxiosError } from 'axios';
import type { ZodError } from 'zod';

// API 에러 응답 데이터의 인터페이스 정의
interface ApiErrorResponse {
  code?: string;
  message?: string;
  status?: string;
  path?: string;
  timestamp?: string;
  validation?: Record<string, any>;
  detail?: string; // 일부 서버/프레임워크 호환
}

export default class HttpError {
  private readonly code: string;
  private readonly message: string;

  constructor(error: AxiosError | { code?: string; message: string }) {
    // 401 에러인 경우 세션 만료 메시지 설정
    if ((error as AxiosError).response) {
      const axiosErr = error as AxiosError;
      const status = axiosErr.response?.status;
      const errorData = axiosErr.response?.data as ApiErrorResponse | undefined;

      if (status === 401) {
        this.code = '401';
        this.message = '로그인 세션이 만료되었습니다. 다시 로그인해주세요.';
        return;
      }

      // 400 Bad Request는 서버 메시지를 그대로 노출 (요청 중복, 검증 실패 등 비즈니스 피드백)
      if (status === 400) {
        this.code = (errorData?.code as string) || '400';
        this.message = errorData?.message || errorData?.detail || axiosErr.response?.statusText || '요청이 올바르지 않습니다.';
        return;
      }

      // 그 외 상태 코드는 서버 메시지가 있으면 사용, 없으면 기본 메시지
      this.code = (errorData?.code as string) || String(status ?? '500');
      this.message = errorData?.message || errorData?.detail || '서버와의 연결이 원활하지 않습니다.';
      return;
    }

    // 커스텀 에러 객체 처리 (예: 클라이언트측 검증 에러)
    const custom = error as { code?: string; message: string };
    this.code = custom.code ?? '400';
    this.message = custom.message;
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

  static fromZodError(err: ZodError, code: string = 'VALIDATION') {
    // 첫 번째 이슈 메시지 또는 전체 메시지를 간결하게 변환
    const firstIssue = err.issues?.[0];
    const message = firstIssue?.message ?? '입력 값이 올바르지 않습니다.';
    return new HttpError({ code, message });
  }
}
