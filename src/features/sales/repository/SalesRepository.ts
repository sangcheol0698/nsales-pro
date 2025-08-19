import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import SalesStats from '@/features/sales/entity/SalesStats.ts';
import type { SalesSearch } from '@/features/sales/entity/SalesSearch.ts';
import PageResponse from '@/core/common/PageResponse.ts';

@singleton()
export default class SalesRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getSales(params: object): Promise<PageResponse<SalesSearch>> {
    const response = await this.httpRepository.get({
      path: '/api/v1/sales',
      params: params,
    });
    
    // 백엔드에서 배열로 반환되므로 PageResponse로 래핑
    // 실제로는 백엔드에서 페이지네이션을 지원하지 않으므로 전체 데이터를 한 페이지로 처리
    const page = parseInt(params.page as string) || 0;
    const size = parseInt(params.size as string) || response.length;
    const startIndex = page * size;
    const endIndex = startIndex + size;
    const paginatedContent = response.slice(startIndex, endIndex);
    
    return new PageResponse<SalesSearch>({
      page: page,
      size: size,
      totalPages: Math.ceil(response.length / size),
      totalElements: response.length,
      content: paginatedContent,
    });
  }

  // 매출 통계 조회
  public async getSalesStats(): Promise<SalesStats> {
    const response = await this.httpRepository.get({
      path: '/api/v1/sales/stats',
    });

    return SalesStats.fromResponse(response);
  }
}