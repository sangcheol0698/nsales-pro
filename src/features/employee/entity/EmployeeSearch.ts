export interface EmployeeSearch {
  id: number;
  code: string;
  name: string;
  email: string;
  department: string;
  position: string;
  joinDate: string;
  status: '재직중' | '휴직' | '퇴사';
  createdAt: string;
  updatedAt: string;
}