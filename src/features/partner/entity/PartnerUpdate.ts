export default class PartnerUpdate {
  id: number;
  name: string;
  ceoName: string;
  salesRepName: string;
  salesRepPhone: string;
  salesRepEmail?: string;
  commissionRate?: number;
  street?: string;
  detail?: string;
  zipcode?: string;
  grade?: string;
  comment?: string;
  modifiedDateTime: string; // 낙관적 동시성 제어용

  constructor(data: {
    id: number;
    name: string;
    ceoName: string;
    salesRepName: string;
    salesRepPhone: string;
    salesRepEmail?: string;
    commissionRate?: number;
    street?: string;
    detail?: string;
    zipcode?: string;
    grade?: string;
    comment?: string;
    modifiedDateTime: string;
  }) {
    this.id = data.id;
    this.name = data.name;
    this.ceoName = data.ceoName;
    this.salesRepName = data.salesRepName;
    this.salesRepPhone = data.salesRepPhone;
    this.salesRepEmail = data.salesRepEmail;
    this.commissionRate = data.commissionRate;
    this.street = data.street;
    this.detail = data.detail;
    this.zipcode = data.zipcode;
    this.grade = data.grade;
    this.comment = data.comment;
    this.modifiedDateTime = data.modifiedDateTime;
  }

  static fromFormData(formData: any): PartnerUpdate {
    return new PartnerUpdate({
      id: formData.id,
      name: formData.name,
      ceoName: formData.ceoName,
      salesRepName: formData.salesRepName,
      salesRepPhone: formData.salesRepPhone,
      salesRepEmail: formData.salesRepEmail || undefined,
      commissionRate: formData.commissionRate || undefined,
      street: formData.street || undefined,
      detail: formData.detail || undefined,
      zipcode: formData.zipcode || undefined,
      grade: formData.grade || undefined,
      comment: formData.comment || undefined,
      modifiedDateTime: formData.modifiedDateTime,
    });
  }
}