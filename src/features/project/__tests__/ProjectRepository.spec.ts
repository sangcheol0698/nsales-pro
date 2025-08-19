import { beforeEach, describe, expect, it, vi } from 'vitest';
import ProjectRepository from '@/features/project/repository/ProjectRepository';
import ProjectCreate from '@/features/project/entity/ProjectCreate';
import PageResponse from '@/core/common/PageResponse';

// tsyringe 모킹을 import 이전에 선언
vi.mock('tsyringe', () => ({
  singleton: () => (target: any) => target,
  inject: () => () => {
  },
  container: { resolve: vi.fn(() => ({})) },
}));

describe('ProjectRepository', () => {
  let repo: ProjectRepository;
  let http: any;

  beforeEach(() => {
    http = {
      get: vi.fn(),
      post: vi.fn(),
      downloadFile: vi.fn(),
      upload: vi.fn(),
    };
    // @ts-ignore
    repo = new ProjectRepository(http);
  });

  it('getProjects: 호출 파라미터와 매핑 결과를 검증', async () => {
    const params = { page: 1, size: 5 };
    http.get.mockResolvedValueOnce({
      page: 1,
      size: 5,
      totalPages: 1,
      totalElements: 1,
      content: [
        {
          id: 101,
          code: 'P-101',
          name: '신규 프로젝트',
          type: 'SI',
          startDate: '2024-01-01',
          endDate: '2024-06-01',
          contractDate: '2023-12-15',
          contractAmount: 123000000,
          mainCompany: '주관사',
          clientCompany: '고객사',
          status: '진행중',
          createdAt: '2024-01-01',
          updatedAt: '2024-01-02',
          modifiedDateTime: '2024-01-02T10:00:00',
        },
      ],
    });

    const page = await repo.getProjects(params);

    expect(http.get).toHaveBeenCalledWith({ path: '/api/v1/projects', params });
    expect(page).toBeInstanceOf(PageResponse);
    expect(page.content[0].id).toBe(101);
    expect(page.content[0].name).toBe('신규 프로젝트');
  });

  it('getProject: 단일 매핑', async () => {
    http.get.mockResolvedValueOnce({ id: 55, name: '단일 프로젝트', code: 'P-055', status: '완료' });
    const proj = await repo.getProject(55);
    expect(http.get).toHaveBeenCalledWith({ path: '/api/v1/projects/55' });
    expect(proj.id).toBe(55);
    expect(proj.name).toBe('단일 프로젝트');
  });

  it('createProject: 요청 바디 변환(toRequest) 및 호출', async () => {
    const dto = new ProjectCreate({
      code: 'P-777',
      name: '테스트 생성',
      type: 'SI',
      contractDate: '2025-01-01',
      departmentId: 9,
      mainCompany: '주관사',
      clientCompany: '고객사',
    });

    await repo.createProject(dto);

    expect(http.post).toHaveBeenCalledWith({
      path: '/api/v1/projects',
      data: dto.toRequest(),
    });
  });
});
