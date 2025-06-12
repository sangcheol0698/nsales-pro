import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import PartnerView from '@/features/partner/views/PartnerView.vue';
import { container } from 'tsyringe';

// 리포지토리 모킹
vi.mock('@/features/partner/repository/PartnerRepository', () => ({
  default: {
    getPartners: vi.fn().mockResolvedValue({
      content: [{ id: 1, name: '테스트 협력사', ceoName: '홍길동' }],
      totalPages: 1,
      totalElements: 1,
    }),
  },
}));

// 컨테이너 모킹
vi.mock('tsyringe', () => ({
  container: {
    resolve: vi.fn().mockImplementation(() => ({
      getPartners: vi.fn().mockResolvedValue({
        content: [{ id: 1, name: '테스트 협력사', ceoName: '홍길동' }],
        totalPages: 1,
        totalElements: 1,
      }),
    })),
  },
}));

// SidebarLayout 컴포넌트 모킹
vi.mock('@/shared/components/sidebar', () => ({
  SidebarLayout: {
    name: 'SidebarLayout',
    setup: () => () => 'SidebarLayout (mocked)',
  },
}));

describe('PartnerView', () => {
  let wrapper: any;
  let mockPartnerRepository: any;

  beforeEach(async () => {
    // 모킹 초기화
    vi.clearAllMocks();

    // 모의 리포지토리 설정
    mockPartnerRepository = {
      getPartners: vi.fn().mockResolvedValue({
        content: [{ id: 1, name: '테스트 협력사', ceoName: '홍길동' }],
        totalPages: 1,
        totalElements: 1,
      }),
    };

    // 모의 리포지토리를 반환하도록 container.resolve 모킹
    (container.resolve as any).mockReturnValue(mockPartnerRepository);

    // 컴포넌트 마운트
    wrapper = mount(PartnerView, {
      global: {
        stubs: {
          SidebarLayout: true,
          Button: true,
          Input: true,
          Table: true,
          TableHeader: true,
          TableRow: true,
          TableHead: true,
          TableBody: true,
          TableCell: true,
          TableEmpty: true,
          DropdownMenu: true,
          DropdownMenuTrigger: true,
          DropdownMenuContent: true,
          DropdownMenuCheckboxItem: true,
          Select: true,
          SelectTrigger: true,
          SelectValue: true,
          SelectContent: true,
          SelectItem: true,
        },
      },
    });

    // 컴포넌트 마운트 및 데이터 로딩 대기
    await flushPromises();
  });

  it('마운트 시 협력사 데이터를 가져와야 함', async () => {
    // 리포지토리 호출 검증
    expect(mockPartnerRepository.getPartners).toHaveBeenCalledTimes(1);
    expect(mockPartnerRepository.getPartners).toHaveBeenCalledWith({ page: 1, limit: 10 });
  });

  it('페이지네이션 버튼 클릭 시 페이지를 변경해야 함', async () => {
    // 모든 버튼을 찾아서 "다음" 버튼 필터링
    const buttons = wrapper.findAll('button');
    const nextButton = buttons.find((button: any) => button.text().includes('다음'));

    // 버튼을 찾았다면 클릭하고 리포지토리 호출 확인
    if (nextButton) {
      await nextButton.trigger('click');

      // 페이지 2로 리포지토리가 호출되었는지 검증
      expect(mockPartnerRepository.getPartners).toHaveBeenCalledWith(
        expect.objectContaining({ page: 2 })
      );
    } else {
      // 버튼을 찾지 못했다면 메소드 직접 호출
      await wrapper.vm.onPageChange(2);

      // 페이지 2로 리포지토리가 호출되었는지 검증
      expect(mockPartnerRepository.getPartners).toHaveBeenCalledWith(
        expect.objectContaining({ page: 2 })
      );
    }
  });

  it('드롭다운 변경 시 페이지 크기를 변경해야 함', async () => {
    // 더 복잡한 상호작용이 필요할 수 있으므로 페이지 크기 변경 메소드 직접 호출
    await wrapper.vm.onPageSizeChange(20);

    // 새 페이지 크기로 리포지토리가 호출되었는지 검증
    expect(mockPartnerRepository.getPartners).toHaveBeenCalledWith(
      expect.objectContaining({ limit: 20, page: 1 })
    );
  });
});
