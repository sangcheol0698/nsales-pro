export default class ProjectUpdate {
  id: number;
  code: string;
  name: string;
  type: 'SI' | 'SM';
  contractDate: string;
  departmentId: number;
  mainCompany: string;
  clientCompany: string;
  expectedAmount?: number;
  contractAmount?: number;
  pmName?: string;
  pmPhone?: string;
  startDate?: string;
  endDate?: string;
  mainCompanyRep?: string;
  mainCompanyRepPhone?: string;
  clientCompanyRep?: string;
  clientCompanyRepPhone?: string;
  modifiedDateTime: string; // 낙관적 동시성 제어용

  constructor(data: {
    id: number;
    code: string;
    name: string;
    type: 'SI' | 'SM';
    contractDate: string;
    departmentId: number;
    mainCompany: string;
    clientCompany: string;
    expectedAmount?: number;
    contractAmount?: number;
    pmName?: string;
    pmPhone?: string;
    startDate?: string;
    endDate?: string;
    mainCompanyRep?: string;
    mainCompanyRepPhone?: string;
    clientCompanyRep?: string;
    clientCompanyRepPhone?: string;
    modifiedDateTime: string;
  }) {
    this.id = data.id;
    this.code = data.code;
    this.name = data.name;
    this.type = data.type;
    this.contractDate = data.contractDate;
    this.departmentId = data.departmentId;
    this.mainCompany = data.mainCompany;
    this.clientCompany = data.clientCompany;
    this.expectedAmount = data.expectedAmount;
    this.contractAmount = data.contractAmount;
    this.pmName = data.pmName;
    this.pmPhone = data.pmPhone;
    this.startDate = data.startDate;
    this.endDate = data.endDate;
    this.mainCompanyRep = data.mainCompanyRep;
    this.mainCompanyRepPhone = data.mainCompanyRepPhone;
    this.clientCompanyRep = data.clientCompanyRep;
    this.clientCompanyRepPhone = data.clientCompanyRepPhone;
    this.modifiedDateTime = data.modifiedDateTime;
  }

  static fromFormData(formData: any): ProjectUpdate {
    return new ProjectUpdate({
      id: formData.id,
      code: formData.code,
      name: formData.name,
      type: formData.type,
      contractDate: formData.contractDate,
      departmentId: formData.departmentId,
      mainCompany: formData.mainCompany,
      clientCompany: formData.clientCompany,
      expectedAmount: formData.expectedAmount || undefined,
      contractAmount: formData.contractAmount || undefined,
      pmName: formData.pmName || undefined,
      pmPhone: formData.pmPhone || undefined,
      startDate: formData.startDate || undefined,
      endDate: formData.endDate || undefined,
      mainCompanyRep: formData.mainCompanyRep || undefined,
      mainCompanyRepPhone: formData.mainCompanyRepPhone || undefined,
      clientCompanyRep: formData.clientCompanyRep || undefined,
      clientCompanyRepPhone: formData.clientCompanyRepPhone || undefined,
      modifiedDateTime: formData.modifiedDateTime,
    });
  }
}