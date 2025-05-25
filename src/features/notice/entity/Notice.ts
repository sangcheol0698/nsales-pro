export interface Notice {
  id: string;
  title: string;
  content: string;
  author: string;
  createdAt: string;
  updatedAt: string;
}

export interface NoticeSearch extends Notice {
  // Additional fields for search results if needed
}