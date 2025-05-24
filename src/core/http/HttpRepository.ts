import AxiosHttpClient, { type HttpRequestConfig } from '@/core/http/AxiosHttpClient.ts';
import { inject, singleton } from 'tsyringe';

@singleton()
export default class HttpRepository {
  constructor(@inject(AxiosHttpClient) private readonly httpClient: AxiosHttpClient) {}

  public async get(config: HttpRequestConfig) {
    return this.httpClient.request({ ...config, method: 'GET' });
  }

  public async post(config: HttpRequestConfig) {
    return this.httpClient.request({ ...config, method: 'POST' });
  }

  public async put(config: HttpRequestConfig) {
    return this.httpClient.request({ ...config, method: 'PUT' });
  }

  public async delete(config: HttpRequestConfig) {
    return this.httpClient.request({ ...config, method: 'DELETE' });
  }

  public async patch(config: HttpRequestConfig) {
    return this.httpClient.request({ ...config, method: 'PATCH' });
  }
}