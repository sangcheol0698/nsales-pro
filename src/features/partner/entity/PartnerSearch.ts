export interface PartnerSearch {
  id: number;
  code: string;
  name: string;
  businessNumber: string;
  representative: string;
  address: string;
  contactPerson: string;
  contactEmail: string;
  contactPhone: string;
  status: '활성' | '비활성';
  createdAt: string;
  updatedAt: string;
}