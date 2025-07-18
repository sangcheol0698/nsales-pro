import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch.ts';
import EmployeeMyInfo from '@/features/employee/entity/EmployeeMyInfo.ts';
import PageResponse from '@/core/common/PageResponse.ts';

@singleton()
export default class EmployeeRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getEmployees(params: object): Promise<PageResponse<EmployeeSearch>> {
    const response = await this.httpRepository.get({
      path: '/api/v1/employees',
      params: params,
    });

    // Transform the raw content array into EmployeeSearch instances
    const transformedContent = response.content.map((item: any) =>
      EmployeeSearch.fromResponse(item)
    );

    // Create and return a PageRe
    // sponse with the transformed content
    return new PageResponse<EmployeeSearch>({
      page: response.page,
      size: response.size,
      totalPages: response.totalPages,
      totalElements: response.totalElements,
      content: transformedContent,
    });
  }

  // 내 직원 정보 조회
  public async getMyEmployee(): Promise<EmployeeMyInfo> {
    const response = await this.httpRepository.get({
      path: '/api/v1/employees/my',
    });

    return EmployeeMyInfo.fromResponse(response);
  }
}
