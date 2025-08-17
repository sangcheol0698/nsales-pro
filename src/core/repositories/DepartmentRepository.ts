import { inject, singleton } from 'tsyringe';
import HttpRepository from '@/core/http/HttpRepository.ts';
import Department from '@/core/entities/Department.ts';

@singleton()
export default class DepartmentRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}
  
  async getDepartments(): Promise<Department[]> {
    const response = await this.httpRepository.get({
      path: '/api/v1/departments',
    });
    return response.map((item: any) => Department.fromResponse(item));
  }
}