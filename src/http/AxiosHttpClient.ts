import axios, { type AxiosError, type AxiosInstance, type AxiosResponse } from 'axios';
import HttpError from '@/http/HttpError.ts';

export type HttpRequestConfig = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  params?: any;
  body?: any;
};

export default class AxiosHttpClient {
  private readonly client: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: import.meta.env.VITE_API_BASE_TIMEOUT,
    timeoutErrorMessage: '요청 시간이 초과되었습니다.',
  });

  private async request(config: HttpRequestConfig) {
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

  public async get(config: HttpRequestConfig) {
    return this.request({ ...config, method: 'GET' });
  }

  public async post(config: HttpRequestConfig) {
    return this.request({ ...config, method: 'POST' });
  }

  public async put(config: HttpRequestConfig) {
    return this.request({ ...config, method: 'PUT' });
  }

  public async delete(config: HttpRequestConfig) {
    return this.request({ ...config, method: 'DELETE' });
  }

  public async patch(config: HttpRequestConfig) {
    return this.request({ ...config, method: 'PATCH' });
  }
}
