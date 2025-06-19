import { formatPhoneNumber } from '@/core/utils/PhoneUtils.ts';

export default class PartnerSearch {
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

  constructor(data: {
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
  }) {
    this.id = data.id;
    this.name = data.name;
    this.ceoName = data.ceoName;
    this.salesRepName = data.salesRepName;
    this.salesRepPhone = data.salesRepPhone;
    this.salesRepEmail = data.salesRepEmail;
    this.grade = data.grade;
    this.address = data.address;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
  }

  static fromResponse(response: any): PartnerSearch {
    return new PartnerSearch({
      id: response.id,
      name: response.name || '',
      ceoName: response.ceoName || '',
      salesRepName: response.salesRepName || '',
      salesRepPhone: formatPhoneNumber(response.salesRepPhone),
      salesRepEmail: response.salesRepEmail || '',
      grade: response.grade || 'C',
      address: response.address || '',
      createdAt: response.createdAt || '',
      updatedAt: response.updatedAt || '',
    });
  }
}
