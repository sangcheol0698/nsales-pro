import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';

@singleton()
export default class PartnerRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getPartners(params: object) {
    return await this.httpRepository.get({
      path: '/api/v1/partners',
      params: params,
    });
  }
}
