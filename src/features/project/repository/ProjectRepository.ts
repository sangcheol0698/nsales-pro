import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import ProjectSearch from '@/features/project/entity/ProjectSearch.ts';
import ProjectStats from '@/features/project/entity/ProjectStats.ts';
import PageResponse from '@/core/common/PageResponse.ts';

@singleton()
export default class ProjectRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getProjects(params: object): Promise<PageResponse<ProjectSearch>> {
    const response = await this.httpRepository.get({
      path: '/api/v1/projects',
      params: params,
    });

    // Transform the raw content array into ProjectSearch instances
    const transformedContent = response.content.map((item: any) => ProjectSearch.fromResponse(item));

    // Create and return a PageResponse with the transformed content
    return new PageResponse<ProjectSearch>({
      page: response.page,
      size: response.size,
      totalPages: response.totalPages,
      totalElements: response.totalElements,
      content: transformedContent
    });
  }

  public async getProject(id: number): Promise<ProjectSearch> {
    const response = await this.httpRepository.get({
      path: `/api/v1/projects/${id}`,
    });

    return ProjectSearch.fromResponse(response);
  }

  // 프로젝트 통계 조회
  public async getProjectStats(): Promise<ProjectStats> {
    const response = await this.httpRepository.get({
      path: '/api/v1/projects/stats',
    });

    return ProjectStats.fromResponse(response);
  }
}
