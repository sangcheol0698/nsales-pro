import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';

@singleton()
export default class EmployeeRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getEmployees(params: object) {
    return await this.httpRepository.get({
      path: '/api/v1/employees',
      params: params,
    });
  }
}