/**
 * 엑셀 파일 처리를 위한 유틸리티 함수들
 */

/**
 * 파일을 다운로드하는 유틸리티 함수
 * @param blob - 다운로드할 Blob 객체
 * @param filename - 저장할 파일명
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * 현재 날짜를 기반으로 파일명을 생성하는 함수
 * @param prefix - 파일명 접두사
 * @param extension - 파일 확장자 (기본값: 'xlsx')
 * @returns 생성된 파일명
 */
export function generateExcelFilename(prefix: string, extension: string = 'xlsx'): string {
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
  const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '');
  return `${prefix}_${dateStr}_${timeStr}.${extension}`;
}

/**
 * 엑셀 업로드를 위한 FormData 생성
 * @param file - 업로드할 파일
 * @param additionalData - 추가 데이터 (선택사항)
 * @returns FormData 객체
 */
export function createExcelFormData(file: File, additionalData?: Record<string, string>): FormData {
  const formData = new FormData();
  formData.append('file', file);
  
  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, value);
    });
  }
  
  return formData;
}

/**
 * 파일 크기를 포맷팅하는 함수
 * @param bytes - 바이트 크기
 * @returns 포맷된 파일 크기 문자열
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 엑셀 파일 형식 검증
 * @param file - 검증할 파일
 * @returns 유효한 엑셀 파일인지 여부
 */
export function validateExcelFile(file: File): { isValid: boolean; message?: string } {
  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel'
  ];
  
  if (!allowedTypes.includes(file.type)) {
    return {
      isValid: false,
      message: '엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.'
    };
  }

  // 파일 크기 제한 (10MB)
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    return {
      isValid: false,
      message: '파일 크기는 10MB를 초과할 수 없습니다.'
    };
  }

  return { isValid: true };
}

/**
 * HTTP 응답에서 Content-Disposition 헤더를 파싱하여 파일명 추출
 * @param response - HTTP 응답 객체
 * @returns 파일명 또는 기본값
 */
export function extractFilenameFromResponse(response: Response, fallback: string = 'download.xlsx'): string {
  const contentDisposition = response.headers.get('Content-Disposition');
  
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    if (filenameMatch && filenameMatch[1]) {
      return filenameMatch[1].replace(/['"]/g, '');
    }
  }
  
  return fallback;
}

/**
 * 엑셀 다운로드 에러 메시지 생성
 * @param error - 에러 객체
 * @returns 사용자 친화적인 에러 메시지
 */
export function getExcelErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    if (error.message.includes('Network')) {
      return '네트워크 연결을 확인해주세요.';
    }
    if (error.message.includes('404')) {
      return '요청하신 데이터를 찾을 수 없습니다.';
    }
    if (error.message.includes('403')) {
      return '해당 작업에 대한 권한이 없습니다.';
    }
    if (error.message.includes('500')) {
      return '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    }
    return error.message;
  }
  
  return '알 수 없는 오류가 발생했습니다.';
}

/**
 * 업로드 진행률을 계산하는 함수
 * @param loaded - 업로드된 바이트
 * @param total - 전체 바이트
 * @returns 진행률 (0-100)
 */
export function calculateUploadProgress(loaded: number, total: number): number {
  return total > 0 ? Math.round((loaded / total) * 100) : 0;
}