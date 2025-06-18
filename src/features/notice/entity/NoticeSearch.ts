import { Notice } from './Notice';

export default class NoticeSearch extends Notice {
  // Additional fields for search results if needed

  constructor(data: {
    id: string;
    title: string;
    content: string;
    author: string;
    createdAt: string;
    updatedAt: string;
  }) {
    super(data);
    // Initialize additional fields if needed
  }

  static fromResponse(response: any): NoticeSearch {
    return new NoticeSearch({
      id: response.id || '',
      title: response.title || '',
      content: response.content || '',
      author: response.author || '',
      createdAt: response.createdAt || '',
      updatedAt: response.updatedAt || '',
    });
  }
}