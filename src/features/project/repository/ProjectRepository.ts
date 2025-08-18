import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import ProjectSearch from '@/features/project/entity/ProjectSearch.ts';
import ProjectStats from '@/features/project/entity/ProjectStats.ts';
import ProjectCreate from '@/features/project/entity/ProjectCreate.ts';
import ProjectUpdate from '@/features/project/entity/ProjectUpdate.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { createExcelFormData, downloadBlob, generateExcelFilename, extractFilenameFromResponse } from '@/core/utils/ExcelUtils.ts';

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

  // 프로젝트 생성
  public async createProject(project: ProjectCreate): Promise<void> {
    await this.httpRepository.post({
      path: '/api/v1/projects',
      data: project.toRequest(),
    });
  }

  // 프로젝트 통계 조회
  public async getProjectStats(): Promise<ProjectStats> {
    const response = await this.httpRepository.get({
      path: '/api/v1/projects/stats',
    });

    return ProjectStats.fromResponse(response);
  }

  // 엑셀 다운로드 (현재 데이터)
  public async downloadExcel(params: object): Promise<void> {
    const response = await this.httpRepository.downloadFile({
      path: '/api/v1/projects/excel/download',
      params: params,
    });

    const filename = extractFilenameFromResponse(response, generateExcelFilename('projects'));
    const blob = await response.blob();
    downloadBlob(blob, filename);
  }

  // 엑셀 샘플 다운로드
  public async downloadSample(): Promise<void> {
    const response = await this.httpRepository.downloadFile({
      path: '/api/v1/projects/excel/sample',
    });

    const filename = extractFilenameFromResponse(response, generateExcelFilename('projects_sample'));
    const blob = await response.blob();
    downloadBlob(blob, filename);
  }

  // 엑셀 업로드
  public async uploadExcel(file: File, onProgress?: (progress: number) => void): Promise<void> {
    const formData = createExcelFormData(file);

    await this.httpRepository.upload({
      path: '/api/v1/projects/excel/upload',
      data: formData,
      onProgress: onProgress,
    });
  }

  // 프로젝트 수정
  public async updateProject(project: ProjectUpdate): Promise<void> {
    await this.httpRepository.put({
      path: `/api/v1/projects/${project.id}`,
      data: project,
    });
  }

  // 프로젝트 삭제
  public async deleteProject(id: number): Promise<void> {
    await this.httpRepository.delete({
      path: `/api/v1/projects/${id}`,
    });
  }
}
