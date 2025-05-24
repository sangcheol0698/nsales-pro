import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';

@singleton()
export default class SalesRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getSales(params: object) {
    return await this.httpRepository.get({
      path: '/api/v1/sales',
      params: params,
    });
  }
}