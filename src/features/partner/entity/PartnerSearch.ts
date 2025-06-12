export interface PartnerSearch {
  id: number;
  name: string;
  ceoName: string;
  salesRepName: string;
  salesRepPhone: string;
  salesRepEmail: string;
  grade: 'A' | 'B' | 'C' | 'D' | 'E';
  address: string;
  createdAt: string;
  updatedAt: string;
}