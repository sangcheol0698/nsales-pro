export default class Member {
  name: string;
  username: string;

  constructor(data: {
    name: string;
    username: string;
  }) {
    this.name = data.name;
    this.username = data.username;
  }

  static fromResponse(response: any): Member {
    return new Member({
      name: response.name || '',
      username: response.username || '',
    });
  }
}
