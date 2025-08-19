import { beforeEach, describe, expect, it, vi } from 'vitest';
import PartnerRepository from '@/features/partner/repository/PartnerRepository';
import PageResponse from '@/core/common/PageResponse';

describe('PartnerRepository', () => {
  let partnerRepository: PartnerRepository;
  let mockHttpRepository: any;

  beforeEach(() => {
    // HttpRepository 모킹 (리포지토리가 기대하는 응답 형태)
    mockHttpRepository = {
      get: vi.fn().mockResolvedValue({
        page: 1,
        size: 10,
        totalPages: 1,
        totalElements: 1,
        content: [{ id: 1, name: '테스트 협력사', ceoName: '홍길동' }],
      }),
    };

    // 모킹된 객체로 리포지토리 생성
    partnerRepository = new PartnerRepository(mockHttpRepository);
  });

  describe('getPartners', () => {
    it('올바른 파라미터로 get 메소드를 호출해야 함', async () => {
      // 준비
      const params = { page: 1, limit: 10 };

      // 실행
      await partnerRepository.getPartners(params);

      // 검증
      expect(mockHttpRepository.get).toHaveBeenCalledWith({
        path: '/api/v1/partners',
        params,
      });
    });

    it('API에서 협력사 데��터를 반환해야 함', async () => {
      // 준비
      const params = { page: 1, limit: 10 };

      // 실행
      const result = await partnerRepository.getPartners(params);

      // 검증
      expect(result).toBeInstanceOf(PageResponse);
      expect(result.page).toBe(1);
      expect(result.totalElements).toBe(1);
      expect(result.content[0].id).toBe(1);
    });

    it('API 오류를 처��해야 함', async () => {
      // 준비
      const params = { page: 1, limit: 10 };
      const errorMessage = 'API Error';
      mockHttpRepository.get.mockRejectedValueOnce(new Error(errorMessage));

      // 실행 및 검증
      await expect(partnerRepository.getPartners(params)).rejects.toThrow(errorMessage);
    });
  });
});
