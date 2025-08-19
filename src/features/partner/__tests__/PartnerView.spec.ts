import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import PartnerView from '../views/PartnerView.vue';
import { container } from 'tsyringe';

// tsyringe를 먼저 모킹 (inject/singleton/container)
vi.mock('tsyringe', () => {
  const mockRepo = {
    getPartners: vi.fn().mockResolvedValue({
      content: [
        { id: 1, name: '테스트 협력사', ceoName: '홍길동', salesRepName: '김영업', salesRepPhone: '010-1234-5678' },
      ],
      totalPages: 1,
      totalElements: 1,
    }),
  };
  return {
    container: { resolve: vi.fn(() => mockRepo) },
    singleton: () => (target: any) => target,
    inject: () => () => {
    },
  };
});

// 리포지토리 모킹
vi.mock('../repository/PartnerRepository', () => ({
  default: {
    getPartners: vi.fn().mockResolvedValue({
      content: [
        { id: 1, name: '테스트 협력사', ceoName: '홍길동', salesRepName: '김영업', salesRepPhone: '010-1234-5678' },
      ],
      totalPages: 1,
      totalElements: 1,
    }),
  },
}));

// SidebarLayout 컴포넌트 모킹
vi.mock('@/shared/components/sidebar', () => ({
  SidebarLayout: { name: 'SidebarLayout', setup: () => () => 'SidebarLayout (mocked)' },
}));

describe('PartnerView', () => {
  let wrapper: any;
  let mockPartnerRepository: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockPartnerRepository = {
      getPartners: vi.fn().mockResolvedValue({
        content: [
          { id: 1, name: '테스트 협력사', ceoName: '홍길동', salesRepName: '김영업', salesRepPhone: '010-1234-5678' },
        ],
        totalPages: 1,
        totalElements: 1,
      }),
    };
    (container as any).resolve.mockReturnValue(mockPartnerRepository);

    wrapper = mount(PartnerView, {
      global: {
        stubs: {
          SidebarLayout: true,
          Button: true,
          Input: true,
          DropdownMenu: true,
          DropdownMenuTrigger: true,
          DropdownMenuContent: true,
          DropdownMenuCheckboxItem: true,
          Table: true,
          TableHeader: true,
          TableRow: true,
          TableHead: true,
          TableBody: true,
          TableCell: true,
          TableEmpty: true,
          Select: true,
          SelectTrigger: true,
          SelectValue: true,
          SelectContent: true,
          SelectItem: true,
          FlexRender: true,
        },
      },
    });
  });

  it('마운트 시 협력사 데이터를 가져와야 함', async () => {
    await wrapper.vm.$nextTick();
    expect(mockPartnerRepository.getPartners).toHaveBeenCalled();
  });

  it('레이아웃이 렌더링되어야 함', async () => {
    expect(wrapper.find('sidebar-layout-stub').exists()).toBe(true);
  });
});
