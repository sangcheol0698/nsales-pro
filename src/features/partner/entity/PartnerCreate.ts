export default class PartnerCreate {
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

  constructor(data: {
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
  }) {
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
  }

  static fromFormData(formData: any): PartnerCreate {
    return new PartnerCreate({
      name: formData.name,
      ceoName: formData.ceoName,
      salesRepName: formData.salesRepName,
      salesRepPhone: formData.salesRepPhone,
      salesRepEmail: formData.salesRepEmail,
      commissionRate: formData.commissionRate,
      street: formData.street,
      detail: formData.detail,
      zipcode: formData.zipcode,
      grade: formData.grade,
      comment: formData.comment,
    });
  }
}