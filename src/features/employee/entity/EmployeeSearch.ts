export default class EmployeeSearch {
  id: number;
  code: string;
  name: string;
  email: string;
  phone?: string;
  teamName: string;
  rank: string;
  grade: string;
  type: string;
  status: '재직' | '휴직' | '퇴사';
  birthDate?: string;
  joinDate: string;
  leaveDate?: string;
  departmentId?: number;
  createdAt: string;
  updatedAt: string;
  modifiedDateTime?: string;

  constructor(data: {
    id: number;
    code: string;
    name: string;
    email: string;
    phone?: string;
    teamName: string;
    rank: string;
    grade: string;
    type: string;
    status: '재직' | '휴직' | '퇴사';
    birthDate?: string;
    joinDate: string;
    leaveDate?: string;
    departmentId?: number;
    createdAt: string;
    updatedAt: string;
    modifiedDateTime?: string;
  }) {
    this.id = data.id;
    this.code = data.code;
    this.name = data.name;
    this.email = data.email;
    this.phone = data.phone;
    this.teamName = data.teamName;
    this.rank = data.rank;
    this.grade = data.grade;
    this.type = data.type;
    this.status = data.status;
    this.birthDate = data.birthDate;
    this.joinDate = data.joinDate;
    this.leaveDate = data.leaveDate;
    this.departmentId = data.departmentId;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
    this.modifiedDateTime = data.modifiedDateTime;
  }

  static fromResponse(response: any): EmployeeSearch {
    return new EmployeeSearch({
      id: response.id,
      code: response.code || '',
      name: response.name || '',
      email: response.email || '',
      phone: response.phone || response.phoneNumber || '', // phone 또는 phoneNumber 필드 지원
      teamName: response.department?.name || response.teamName || '', // department.name 또는 teamName 사용
      rank: response.rank || '',
      grade: response.grade || '',
      type: response.type || '',
      status: response.status || '재직',
      birthDate: response.birthDate || '',
      joinDate: response.joinDate || '',
      leaveDate: response.leaveDate,
      departmentId: response.department?.id || response.departmentId, // department.id 또는 departmentId 사용
      createdAt: response.createdAt || response.modifiedDateTime || '', // modifiedDateTime도 지원
      updatedAt: response.updatedAt || response.modifiedDateTime || '', // modifiedDateTime도 지원
      modifiedDateTime: response.modifiedDateTime || '', // 낙관적 동시성 제어용
    });
  }
}
