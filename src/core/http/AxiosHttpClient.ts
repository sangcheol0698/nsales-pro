import axios, { type AxiosError, type AxiosInstance, type AxiosResponse } from 'axios';
import HttpError from '@/core/http/HttpError.ts';
import { singleton } from 'tsyringe';
import router from '@/core/router';
import { useToast } from '@/core/composables';
import { useAuthStore } from '@/core/stores/auth.store';
import type { ZodTypeAny } from 'zod';

export type HttpRequestConfig = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  params?: any;
  body?: any;
  data?: any;
  // 선��적 스키마 검증 훅
  requestSchema?: ZodTypeAny;
  responseSchema?: ZodTypeAny;
};

@singleton()
export default class AxiosHttpClient {
  private readonly client: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: import.meta.env.VITE_API_BASE_TIMEOUT,
    timeoutErrorMessage: '요청 시간이 초과되었습니다.',
    withCredentials: true,
    xsrfCookieName: 'XSRF-TOKEN',
    xsrfHeaderName: 'X-XSRF-TOKEN',
  });

  constructor() {
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 요청 인터셉터 추가
    this.client.interceptors.request.use(
      (config) => {
        // 쿠키에서 XSRF-TOKEN 값을 추출하는 함수
        const getCookieValue = (name: string): string | null => {
          const match = document.cookie.match(new RegExp('(^|;\\s*)(' + name + ')=([^;]*)'));
          return match ? decodeURIComponent(match[3]) : null;
        };

        const xsrfToken = getCookieValue('XSRF-TOKEN');
        if (xsrfToken) {
          config.headers['X-XSRF-TOKEN'] = xsrfToken;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      },
    );

    // 응답 인터��터
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error: AxiosError) => {
        // 401 Unauthorized 에러 처리 (세션 만료)
        if (error.response?.status === 401) {
          const authStore = useAuthStore();
          authStore.logout();

          // 현재 경로가 로그인 페이지가 아닌 경우에만 리다이렉트
          if (!router.currentRoute.value.path.startsWith('/auths/')) {
            const toast = useToast();
            toast.error('세션 만료', {
              description: '로그인 세션이 만료되었습니다. 다시 로그인해주세요.',
            });

            // 로그인 페이지로 리다이렉트 (세션 만료 표시)
            router.push({
              name: 'login',
              query: { expired: 'true' },
            });
          }
        }
        return Promise.reject(error);
      },
    );
  }

  public async request(config: HttpRequestConfig) {
    // 요청 바디 스키마 검증 (옵션)
    if (config.requestSchema && (config.body ?? config.data)) {
      const body = config.body ?? config.data;
      const parsed = config.requestSchema.safeParse(body);
      if (!parsed.success) {
        throw HttpError.fromZodError(parsed.error, 'REQUEST_VALIDATION');
      }
    }

    return this.client
      .request({
        method: config.method,
        url: config.path,
        params: config.params,
        data: config.body || config.data,
      })
      .then((response: AxiosResponse) => {
        // 응답 스키마 검증 (옵션)
        if (config.responseSchema) {
          const parsed = config.responseSchema.safeParse(response.data);
          if (!parsed.success) {
            throw HttpError.fromZodError(parsed.error, 'RESPONSE_VALIDATION');
          }
          return parsed.data;
        }
        return response.data;
      })
      .catch((error: unknown) => {
        // 이미 포장된 HttpError면 그대로 전달
        if (error instanceof HttpError) {
          return Promise.reject(error);
        }
        return Promise.reject(new HttpError(error as AxiosError));
      });
  }

  public async downloadFile(config: HttpRequestConfig): Promise<Response> {
    try {
      const response = await this.client.request({
        method: config.method,
        url: config.path,
        params: config.params,
        responseType: 'blob',
      });

      // Response 객체와 유사한 형태로 반환
      return {
        blob: () => Promise.resolve(response.data),
        headers: {
          get: (name: string) => response.headers[name.toLowerCase()],
        },
        ok: response.status >= 200 && response.status < 300,
        status: response.status,
        statusText: response.statusText,
      } as Response;
    } catch (error) {
      throw new HttpError(error as AxiosError);
    }
  }

  public async upload(config: HttpRequestConfig & { onProgress?: (progress: number) => void }) {
    try {
      const response = await this.client.request({
        method: config.method,
        url: config.path,
        data: config.data,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (config.onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
            config.onProgress(progress);
          }
        },
      });

      return response.data;
    } catch (error) {
      throw new HttpError(error as AxiosError);
    }
  }
}
