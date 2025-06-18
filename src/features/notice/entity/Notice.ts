export default class Notice {
  id: string;
  title: string;
  content: string;
  author: string;
  createdAt: string;
  updatedAt: string;

  constructor(data: {
    id: string;
    title: string;
    content: string;
    author: string;
    createdAt: string;
    updatedAt: string;
  }) {
    this.id = data.id;
    this.title = data.title;
    this.content = data.content;
    this.author = data.author;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
  }

  static fromResponse(response: any): Notice {
    return new Notice({
      id: response.id || '',
      title: response.title || '',
      content: response.content || '',
      author: response.author || '',
      createdAt: response.createdAt || '',
      updatedAt: response.updatedAt || '',
    });
  }
}
