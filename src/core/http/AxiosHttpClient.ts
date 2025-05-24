import axios, { type AxiosError, type AxiosInstance, type AxiosResponse } from 'axios';
import HttpError from '@/core/http/HttpError.ts';
import { singleton } from 'tsyringe';

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
  });

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