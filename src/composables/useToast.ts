import type { ExternalToast } from 'vue-sonner';
import { toast as sonnerToast } from 'vue-sonner';

// 기본 토스트 설정
const defaultOptions: ExternalToast = {
  duration: 5000,
  position: 'top-center',
};

// 성공 토스트 기본 스타일
const successStyle = {
  style: {
    backgroundColor: '#d4edda',
    color: '#155724',
    border: '1px solid #c3e6cb',
  },
};

// 에러 토스트 기본 스타일
const errorStyle = {
  style: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    border: '1px solid #f5c6cb',
  },
};

/**
 * 토스트 알림을 쉽게 사용하기 위한 컴포저블
 * @returns 토스트 메소드가 포함된 객체
 */
export function useToast() {
  /**
   * 성공 토스트 알림 표시
   * @param message - 표시할 메시지
   * @param options - 선택적 설정
   * @returns 토스트 ID
   */
  const success = (message: string, options?: ExternalToast) => {
    return sonnerToast.success(message, {
      ...defaultOptions,
      ...successStyle,
      ...options,
    });
  };

  /**
   * 에러 토스트 알림 표시
   * @param message - 표시할 메시지
   * @param options - 선택적 설정
   * @returns 토스트 ID
   */
  const error = (message: string, options?: ExternalToast) => {
    return sonnerToast.error(message, {
      ...defaultOptions,
      ...errorStyle,
      ...options,
    });
  };

  /**
   * 정보 토스트 알림 표시
   * @param message - 표시할 메시지
   * @param options - 선택적 설정
   * @returns 토스트 ID
   */
  const info = (message: string, options?: ExternalToast) => {
    return sonnerToast.info(message, {
      ...defaultOptions,
      ...options,
    });
  };

  /**
   * 경고 토스트 알림 표시
   * @param message - 표시할 메시지
   * @param options - 선택적 설정
   * @returns 토스트 ID
   */
  const warning = (message: string, options?: ExternalToast) => {
    return sonnerToast.warning(message, {
      ...defaultOptions,
      ...options,
    });
  };

  /**
   * 로딩 토스트 알림 표시
   * @param message - 표시할 메시지
   * @param options - 선택적 설정
   * @returns 토스트 ID
   */
  const loading = (message: string, options?: ExternalToast) => {
    return sonnerToast.loading(message, {
      ...defaultOptions,
      ...options,
    });
  };

  /**
   * 커스텀 토스트 알림 표시
   * @param message - 표시할 메시지
   * @param options - 선택적 설정
   * @returns 토스트 ID
   */
  const custom = (message: string, options?: ExternalToast) => {
    return sonnerToast(message, {
      ...defaultOptions,
      ...options,
    });
  };

  /**
   * 토스트 알림 닫기
   * @param id - 닫을 토스트의 ID
   */
  const dismiss = (id?: string | number) => {
    return sonnerToast.dismiss(id);
  };

  /**
   * 프로미스 토스트 알림 표시
   * @param promise - 추적할 프로미스
   * @param options - 선택적 설정
   * @returns 토스트 ID
   */
  const promise = <T>(
    promise: Promise<T> | (() => Promise<T>),
    options?: ExternalToast & {
      loading?: string;
      success?: string | ((data: T) => string);
      error?: string | ((error: any) => string);
    }
  ) => {
    return sonnerToast.promise(promise, {
      ...defaultOptions,
      ...options,
    });
  };

  return {
    success,
    error,
    info,
    warning,
    loading,
    custom,
    dismiss,
    promise,
  };
}
