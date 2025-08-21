export type UserRole = 'ADMIN' | 'USER';

export default class Member {
  name: string;
  username: string;
  role: UserRole;

  constructor(data: {
    name: string;
    username: string;
    role: UserRole;
  }) {
    this.name = data.name;
    this.username = data.username;
    this.role = data.role;
  }

  static fromResponse(response: any): Member {
    return new Member({
      name: response.name || '',
      username: response.username || '',
      role: response.role || 'USER',
    });
  }

  isAdmin(): boolean {
    return this.role === 'ADMIN';
  }

  isUser(): boolean {
    return this.role === 'USER';
  }
}
