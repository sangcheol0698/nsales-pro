import { beforeEach, describe, expect, it, vi } from 'vitest';
import PartnerRepository from '@/features/partner/repository/PartnerRepository';

describe('PartnerRepository', () => {
  let partnerRepository: PartnerRepository;
  let mockHttpRepository: any;

  beforeEach(() => {
    // HttpRepository 모킹
    mockHttpRepository = {
      get: vi.fn().mockResolvedValue({
        data: {
          content: [{ id: 1, name: '테스트 협력사', ceoName: '홍길동' }],
          totalPages: 1,
          totalElements: 1,
        },
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

    it('API에서 협력사 데이터를 반환해야 함', async () => {
      // 준비
      const params = { page: 1, limit: 10 };
      const expectedResponse = {
        content: [{ id: 1, name: '테스트 협력사', ceoName: '홍길동' }],
        totalPages: 1,
        totalElements: 1,
      };

      // 실행
      const result = await partnerRepository.getPartners(params);

      // 검증
      expect(result.data).toEqual(expectedResponse);
    });

    it('API 오류를 처리해야 함', async () => {
      // 준비
      const params = { page: 1, limit: 10 };
      const errorMessage = 'API Error';
      mockHttpRepository.get.mockRejectedValueOnce(new Error(errorMessage));

      // 실행 및 검증
      await expect(partnerRepository.getPartners(params)).rejects.toThrow(errorMessage);
    });
  });
});
