export default class PageResponse<T> {
  page: number;
  size: number;
  totalPages: number;
  totalElements: number;
  content: T[];

  constructor(data: {
    page: number;
    size: number;
    totalPages: number;
    totalElements: number;
    content: T[];
  }) {
    this.page = data.page;
    this.size = data.size;
    this.totalPages = data.totalPages;
    this.totalElements = data.totalElements;
    this.content = data.content;
  }

  static fromResponse<T>(response: any): PageResponse<T> {
    return new PageResponse<T>({
      page: response.page || 1,
      size: response.size || 10,
      totalPages: response.totalPages || 0,
      totalElements: response.totalElements || 0,
      content: response.content || [],
    });
  }
}