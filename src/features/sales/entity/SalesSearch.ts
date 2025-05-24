export interface SalesSearch {
  id: number;
  code: string;
  projectId: number;
  projectName: string;
  partnerId: number;
  partnerName: string;
  amount: number;
  taxAmount: number;
  totalAmount: number;
  issueDate: string;
  dueDate: string;
  paymentDate: string;
  status: '미수금' | '수금완료' | '취소';
  createdAt: string;
  updatedAt: string;
}