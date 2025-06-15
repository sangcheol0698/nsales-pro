export default interface Member {
  name: string;
  username: string;

  // 추가 정보 (옵션)
  phone?: string;
  birthDate?: string;
  departmentName?: string;
  departmentId?: number;
  rank?: string;
  grade?: string;
  type?: string;
  joinDate?: string;
  annualSalary?: number;
  hrStatus?: string;
}
