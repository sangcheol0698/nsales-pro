export default class EmployeeSearch {
  id: number;
  code: string;
  name: string;
  email: string;
  teamName: string;
  rank: string;
  grade: string;
  type: string;
  status: '재직' | '휴직' | '퇴사';
  joinDate: string;
  leaveDate?: string;
  departmentId?: number;
  createdAt: string;
  updatedAt: string;

  constructor(data: {
    id: number;
    code: string;
    name: string;
    email: string;
    teamName: string;
    rank: string;
    grade: string;
    type: string;
    status: '재직' | '휴직' | '퇴사';
    joinDate: string;
    leaveDate?: string;
    departmentId?: number;
    createdAt: string;
    updatedAt: string;
  }) {
    this.id = data.id;
    this.code = data.code;
    this.name = data.name;
    this.email = data.email;
    this.teamName = data.teamName;
    this.rank = data.rank;
    this.grade = data.grade;
    this.type = data.type;
    this.status = data.status;
    this.joinDate = data.joinDate;
    this.leaveDate = data.leaveDate;
    this.departmentId = data.departmentId;
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
      grade: response.grade || '',
      type: response.type || '',
      status: response.status || '재직',
      joinDate: response.joinDate || '',
      leaveDate: response.leaveDate,
      departmentId: response.departmentId,
      createdAt: response.createdAt || '',
      updatedAt: response.updatedAt || '',
    });
  }
}
