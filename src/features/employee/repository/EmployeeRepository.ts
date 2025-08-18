import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch.ts';
import EmployeeMyInfo from '@/features/employee/entity/EmployeeMyInfo.ts';
import EmployeeStats from '@/features/employee/entity/EmployeeStats.ts';
import EmployeeCreate from '@/features/employee/entity/EmployeeCreate.ts';
import EmployeeUpdate from '@/features/employee/entity/EmployeeUpdate.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { createExcelFormData, downloadBlob, generateExcelFilename, extractFilenameFromResponse } from '@/core/utils/ExcelUtils.ts';

@singleton()
export default class EmployeeRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getEmployees(params: object): Promise<PageResponse<EmployeeSearch>> {
    const response = await this.httpRepository.get({
      path: '/api/v1/employees',
      params: params,
    });

    // Transform the raw content array into EmployeeSearch instances
    const transformedContent = response.content.map((item: any) =>
      EmployeeSearch.fromResponse(item)
    );

    // Create and return a PageRe
    // sponse with the transformed content
    return new PageResponse<EmployeeSearch>({
      page: response.page,
      size: response.size,
      totalPages: response.totalPages,
      totalElements: response.totalElements,
      content: transformedContent,
    });
  }

  // 내 직원 정보 조회
  public async getMyEmployee(): Promise<EmployeeMyInfo> {
    const response = await this.httpRepository.get({
      path: '/api/v1/employees/my',
    });

    return EmployeeMyInfo.fromResponse(response);
  }

  // 직원 통계 조회
  public async getEmployeeStats(): Promise<EmployeeStats> {
    const response = await this.httpRepository.get({
      path: '/api/v1/employees/stats',
    });

    return EmployeeStats.fromResponse(response);
  }

  // 엑셀 다운로드 (현재 데이터)
  public async downloadExcel(params: object): Promise<void> {
    const response = await this.httpRepository.downloadFile({
      path: '/api/v1/employees/excel/download',
      params: params,
    });

    const filename = extractFilenameFromResponse(response, generateExcelFilename('employees'));
    const blob = await response.blob();
    downloadBlob(blob, filename);
  }

  // 엑셀 샘플 다운로드
  public async downloadSample(): Promise<void> {
    const response = await this.httpRepository.downloadFile({
      path: '/api/v1/employees/excel/sample',
    });

    const filename = extractFilenameFromResponse(response, generateExcelFilename('employees_sample'));
    const blob = await response.blob();
    downloadBlob(blob, filename);
  }

  // 엑셀 업로드
  public async uploadExcel(file: File, onProgress?: (progress: number) => void): Promise<void> {
    const formData = createExcelFormData(file);

    await this.httpRepository.upload({
      path: '/api/v1/employees/excel/upload',
      data: formData,
      onProgress: onProgress,
    });
  }

  // 연봉 엑셀 업로드
  public async uploadSalaryExcel(file: File, onProgress?: (progress: number) => void): Promise<void> {
    const formData = createExcelFormData(file);

    await this.httpRepository.upload({
      path: '/api/v1/employees/excel/upload/sales',
      data: formData,
      onProgress: onProgress,
    });
  }

  // 구성원 생성
  public async createEmployee(employee: EmployeeCreate): Promise<void> {
    await this.httpRepository.post({
      path: '/api/v1/employees',
      data: employee,
    });
  }

  // 구성원 수정
  public async updateEmployee(employee: EmployeeUpdate): Promise<void> {
    await this.httpRepository.put({
      path: `/api/v1/employees/${employee.id}`,
      data: employee,
    });
  }

  // 구성원 삭제
  public async deleteEmployee(id: number): Promise<void> {
    await this.httpRepository.delete({
      path: `/api/v1/employees/${id}`,
    });
  }

  // 구성원 상세 조회
  public async getEmployee(id: number): Promise<EmployeeSearch> {
    const response = await this.httpRepository.get({
      path: `/api/v1/employees/${id}`,
    });

    console.log('백엔드에서 받은 구성원 데이터:', response);
    console.log('구성원 필드 확인 - phone:', response.phone, 'birthDate:', response.birthDate);
    console.log('부서 정보 - department:', response.department, 'departmentId:', response.department?.id, 'teamName:', response.department?.name);

    return EmployeeSearch.fromResponse(response);
  }
}
