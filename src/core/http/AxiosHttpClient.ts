import axios, { type AxiosError, type AxiosInstance, type AxiosResponse } from 'axios';
import HttpError from '@/core/http/HttpError.ts';
import { singleton } from 'tsyringe';
import router from '@/core/router';
import { useToast } from '@/core/composables';
export type HttpRequestConfig = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  params?: any;
  body?: any;
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
    // 요청 인터셉터 추가 - XSRF 토큰을 쿠키에서 가져와 헤더에 설정
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
      }
    );

    // 응답 인터셉터
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // 401 Unauthorized 에러 처리 (세션 만료)
        if (error.response?.status === 401) {
          // 로컬 스토리지에서 사용자 정보 제거
          localStorage.removeItem('user');

          // 현재 경로가 로그인 페이지가 아닌 경우에만 리다이렉트
          if (!router.currentRoute.value.path.startsWith('/auths/')) {
            const toast = useToast();
            toast.error('세션 만료', { 
              description: '로그인 세션이 만료되었습니다. 다시 로그인해주세요.' 
            });

            // 로그인 페이지로 리다이렉트 (세션 만료 표시)
            router.push({ 
              name: 'login',
              query: { expired: 'true' }
            });
          }
        }
        return Promise.reject(error);
      }
    );
  }

  public async request(config: HttpRequestConfig) {
    return this.client
      .request({
        method: config.method,
        url: config.path,
        params: config.params,
        data: config.body,
      })
      .then((response: AxiosResponse) => {
        return response.data;
      })
      .catch((error: AxiosError) => {
        return Promise.reject(new HttpError(error));
      });
  }
}
