export default class EmployeeCreate {
  partnersId?: number;
  departmentId: number;
  name: string;
  email: string;
  rank: string;
  grade: string;
  type: string;
  phone: string;
  birthDate: string;
  joinDate: string;
  comment?: string;
  status?: string;

  constructor(data: {
    partnersId?: number;
    departmentId: number;
    name: string;
    email: string;
    rank: string;
    grade: string;
    type: string;
    phone: string;
    birthDate: string;
    joinDate: string;
    comment?: string;
    status?: string;
  }) {
    this.partnersId = data.partnersId;
    this.departmentId = data.departmentId;
    this.name = data.name;
    this.email = data.email;
    this.rank = data.rank;
    this.grade = data.grade;
    this.type = data.type;
    this.phone = data.phone;
    this.birthDate = data.birthDate;
    this.joinDate = data.joinDate;
    this.comment = data.comment;
    this.status = data.status;
  }

  static fromFormData(formData: any): EmployeeCreate {
    return new EmployeeCreate({
      partnersId: formData.partnersId,
      departmentId: formData.departmentId,
      name: formData.name,
      email: formData.email,
      rank: formData.rank,
      grade: formData.grade,
      type: formData.type,
      phone: formData.phone,
      birthDate: formData.birthDate,
      joinDate: formData.joinDate,
      comment: formData.comment,
      status: formData.status,
    });
  }
}