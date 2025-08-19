export default class EmployeeUpdate {
  id: number;
  name: string;
  email: string;
  phone: string;
  departmentId: number;
  rank: string;
  grade: string;
  type: string;
  status: string;
  birthDate: string;
  joinDate: string;
  leaveDate?: string;
  comment?: string;
  modifiedDateTime: string;

  constructor(data: {
    id: number;
    name: string;
    email: string;
    phone: string;
    departmentId: number;
    rank: string;
    grade: string;
    type: string;
    status: string;
    birthDate: string;
    joinDate: string;
    leaveDate?: string;
    comment?: string;
    modifiedDateTime: string;
  }) {
    this.id = data.id;
    this.name = data.name;
    this.email = data.email;
    this.phone = data.phone;
    this.departmentId = data.departmentId;
    this.rank = data.rank;
    this.grade = data.grade;
    this.type = data.type;
    this.status = data.status;
    this.birthDate = data.birthDate;
    this.joinDate = data.joinDate;
    this.leaveDate = data.leaveDate;
    this.comment = data.comment;
    this.modifiedDateTime = data.modifiedDateTime;
  }

  static fromEmployee(employee: any): EmployeeUpdate {
    return new EmployeeUpdate({
      id: employee.id,
      name: employee.name || '',
      email: employee.email || '',
      phone: employee.phone || '',
      departmentId: employee.departmentId || 0,
      rank: employee.rank || '',
      grade: employee.grade || '',
      type: employee.type || '',
      status: employee.status || '재직',
      birthDate: employee.birthDate || '',
      joinDate: employee.joinDate || '',
      leaveDate: employee.leaveDate,
      comment: employee.comment || '',
      modifiedDateTime: employee.modifiedDateTime || employee.updatedAt || '',
    });
  }

  static fromFormData(formData: any): EmployeeUpdate {
    return new EmployeeUpdate({
      id: formData.id,
      name: formData.name,
      email: formData.email,
      phone: formData.phone,
      departmentId: formData.departmentId,
      rank: formData.rank,
      grade: formData.grade,
      type: formData.type,
      status: formData.status,
      birthDate: formData.birthDate,
      joinDate: formData.joinDate,
      leaveDate: formData.leaveDate,
      comment: formData.comment,
      modifiedDateTime: formData.modifiedDateTime,
    });
  }
}