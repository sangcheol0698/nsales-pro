import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import PartnerSearch from '@/features/partner/entity/PartnerSearch.ts';
import PartnerStats from '@/features/partner/entity/PartnerStats.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { createExcelFormData, downloadBlob, generateExcelFilename, extractFilenameFromResponse } from '@/core/utils/ExcelUtils.ts';

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

  // 협력사 통계 조회
  public async getPartnerStats(): Promise<PartnerStats> {
    const response = await this.httpRepository.get({
      path: '/api/v1/partners/stats',
    });

    return PartnerStats.fromResponse(response);
  }

  // 엑셀 다운로드 (현재 데이터)
  public async downloadExcel(params: object): Promise<void> {
    const response = await this.httpRepository.downloadFile({
      path: '/api/v1/partners/excel/download',
      params: params,
    });

    const filename = extractFilenameFromResponse(response, generateExcelFilename('partners'));
    const blob = await response.blob();
    downloadBlob(blob, filename);
  }

  // 엑셀 샘플 다운로드
  public async downloadSample(): Promise<void> {
    const response = await this.httpRepository.downloadFile({
      path: '/api/v1/partners/excel/sample',
    });

    const filename = extractFilenameFromResponse(response, generateExcelFilename('partners_sample'));
    const blob = await response.blob();
    downloadBlob(blob, filename);
  }

  // 엑셀 업로드
  public async uploadExcel(file: File, onProgress?: (progress: number) => void): Promise<void> {
    const formData = createExcelFormData(file);

    await this.httpRepository.upload({
      path: '/api/v1/partners/excel/upload',
      data: formData,
      onProgress: onProgress,
    });
  }
}
