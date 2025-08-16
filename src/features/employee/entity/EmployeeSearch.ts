export default class EmployeeSearch {
  id: number;
  code: string;
  name: string;
  email: string;
  teamName: string;
  rank: string;
  joinDate: string;
  status: '재직' | '휴직' | '퇴사';
  createdAt: string;
  updatedAt: string;

  constructor(data: {
    id: number;
    code: string;
    name: string;
    email: string;
    teamName: string;
    rank: string;
    joinDate: string;
    status: '재직' | '휴직' | '퇴사';
    createdAt: string;
    updatedAt: string;
  }) {
    this.id = data.id;
    this.code = data.code;
    this.name = data.name;
    this.email = data.email;
    this.teamName = data.teamName;
    this.rank = data.rank;
    this.joinDate = data.joinDate;
    this.status = data.status;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
  }

  static fromResponse(response: any): EmployeeSearch {
    return new EmployeeSearch({
      id: response.id,
      code: response.code || '',
      name: response.name || '',
      email: response.email || '',
      teamName: response.teamName || '',
      rank: response.rank || '',
      joinDate: response.joinDate || '',
      status: response.status || '재직',
      createdAt: response.createdAt || '',
      updatedAt: response.updatedAt || '',
    });
  }
}
