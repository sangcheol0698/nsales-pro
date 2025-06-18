import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import PartnerSearch from '@/features/partner/entity/PartnerSearch.ts';
import PageResponse from '@/core/common/PageResponse.ts';

@singleton()
export default class PartnerRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getPartners(params: object): Promise<PageResponse<PartnerSearch>> {
    const response = await this.httpRepository.get({
      path: '/api/v1/partners',
      params: params,
    });

    // Transform the raw content array into PartnerSearch instances
    const transformedContent = response.content.map((item: any) => PartnerSearch.fromResponse(item));

    // Create and return a PageResponse with the transformed content
    return new PageResponse<PartnerSearch>({
      page: response.page,
      size: response.size,
      totalPages: response.totalPages,
      totalElements: response.totalElements,
      content: transformedContent
    });
  }
}
