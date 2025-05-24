export interface ProjectSearch {
  id: number;
  code: string;
  name: string;
  type: string;
  startDate: string;
  endDate: string;
  contractDate: string;
  contractAmount: number;
  mainCompany: string;
  clientCompany: string;
  status: '진행중' | '완료' | '예약';
  createdAt: string;
  updatedAt: string;
}