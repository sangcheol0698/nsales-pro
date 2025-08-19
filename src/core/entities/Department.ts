export default class Department {
  id: number;
  name: string;

  constructor(data: {
    id: number;
    name: string;
  }) {
    this.id = data.id;
    this.name = data.name;
  }

  static fromResponse(response: any): Department {
    return new Department({
      id: response.id,
      name: response.name || '',
    });
  }
}