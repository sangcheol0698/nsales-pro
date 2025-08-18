// filepath: /Users/sangcheol/IdeaProjects/nsales-pro/frontend/src/features/employee/__tests__/EmployeeRepository.spec.ts
import { beforeEach, describe, expect, it, vi } from 'vitest';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository';
import PageResponse from '@/core/common/PageResponse';

// tsyringe 모킹을 import 이전에 선언
vi.mock('tsyringe', () => ({
  singleton: () => (target: any) => target,
  inject: () => () => {
  },
  container: { resolve: vi.fn(() => ({})) },
}));

describe('EmployeeRepository', () => {
  let repo: EmployeeRepository;
  let http: any;

  beforeEach(() => {
    http = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      downloadFile: vi.fn(),
      upload: vi.fn(),
    };
    // @ts-ignore: inject decorator is ignored for direct construction in tests
    repo = new EmployeeRepository(http);
  });

  it('getEmployees: 호출 파라미터와 매핑 결과를 검증', async () => {
    const params = { page: 1, size: 10 };
    http.get.mockResolvedValueOnce({
      page: 1,
      size: 10,
      totalPages: 1,
      totalElements: 1,
      content: [
        {
          id: 7,
          code: 'E-007',
          name: '홍길동',
          email: 'hong@example.com',
          phoneNumber: '010-1111-2222', // phoneNumber로 들어와도 매핑
          rank: '대리',
          grade: 'B',
          type: '정규직',
          status: '재직',
          department: { id: 3, name: '개발팀' }, // department.name -> teamName
          createdAt: '2024-01-01',
          updatedAt: '2024-06-01',
          modifiedDateTime: '2024-06-01T10:00:00',
        },
      ],
    });

    const page = await repo.getEmployees(params);

    expect(http.get).toHaveBeenCalledWith({ path: '/api/v1/employees', params });
    expect(page).toBeInstanceOf(PageResponse);
    expect(page.content[0].id).toBe(7);
    expect(page.content[0].teamName).toBe('개발팀');
    expect(page.content[0].phone).toBe('010-1111-2222');
  });

  it('getEmployee: 단일 조회 매핑', async () => {
    http.get.mockResolvedValueOnce({
      id: 9,
      name: '임꺽정',
      email: 'lim@example.com',
      departmentId: 5,
      teamName: '플랫폼팀',
      phone: '010-3333-4444',
      createdAt: '2024-03-02',
      updatedAt: '2024-03-03',
    });

    const emp = await repo.getEmployee(9);
    expect(http.get).toHaveBeenCalledWith({ path: '/api/v1/employees/9' });
    expect(emp.id).toBe(9);
    expect(emp.teamName).toBe('플랫폼팀');
    expect(emp.phone).toBe('010-3333-4444');
  });

  it('getEmployeeStats: 매핑', async () => {
    http.get.mockResolvedValueOnce({ totalEmployees: 10, activeEmployees: 9, newHires: 1, averageTenure: 3 });
    const stats = await repo.getEmployeeStats();
    expect(http.get).toHaveBeenCalledWith({ path: '/api/v1/employees/stats' });
    expect(stats.totalEmployees).toBe(10);
    expect(stats.activeEmployees).toBe(9);
  });
});
