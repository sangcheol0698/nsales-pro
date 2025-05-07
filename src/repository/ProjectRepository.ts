import HttpRepository from '@/repository/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';

@singleton()
export default class ProjectRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getProjects(params: object) {
    return await this.httpRepository.get({
      path: '/api/v1/projects',
      params: params,
    });
  }
}
