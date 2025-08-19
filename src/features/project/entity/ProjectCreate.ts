export default class ProjectCreate {
  code: string;
  name: string;
  type: 'SI' | 'SM';
  contractDate: string;
  expectedAmount?: number;
  contractAmount?: number;
  departmentId: number;
  pmName?: string;
  pmPhone?: string;
  startDate?: string;
  endDate?: string;
  mainCompany: string;
  mainCompanyRep?: string;
  mainCompanyRepPhone?: string;
  clientCompany: string;
  clientCompanyRep?: string;
  clientCompanyRepPhone?: string;

  constructor(data: {
    code: string;
    name: string;
    type: 'SI' | 'SM';
    contractDate: string;
    expectedAmount?: number;
    contractAmount?: number;
    departmentId: number;
    pmName?: string;
    pmPhone?: string;
    startDate?: string;
    endDate?: string;
    mainCompany: string;
    mainCompanyRep?: string;
    mainCompanyRepPhone?: string;
    clientCompany: string;
    clientCompanyRep?: string;
    clientCompanyRepPhone?: string;
  }) {
    this.code = data.code;
    this.name = data.name;
    this.type = data.type;
    this.contractDate = data.contractDate;
    this.expectedAmount = data.expectedAmount;
    this.contractAmount = data.contractAmount;
    this.departmentId = data.departmentId;
    this.pmName = data.pmName;
    this.pmPhone = data.pmPhone;
    this.startDate = data.startDate;
    this.endDate = data.endDate;
    this.mainCompany = data.mainCompany;
    this.mainCompanyRep = data.mainCompanyRep;
    this.mainCompanyRepPhone = data.mainCompanyRepPhone;
    this.clientCompany = data.clientCompany;
    this.clientCompanyRep = data.clientCompanyRep;
    this.clientCompanyRepPhone = data.clientCompanyRepPhone;
  }

  static createDefault(): ProjectCreate {
    return new ProjectCreate({
      code: '',
      name: '',
      type: 'SI',
      contractDate: '',
      departmentId: 0,
      mainCompany: '',
      clientCompany: '',
    });
  }

  toRequest(): object {
    return {
      code: this.code,
      name: this.name,
      type: this.type,
      contractDate: this.contractDate,
      expectedAmount: this.expectedAmount || null,
      contractAmount: this.contractAmount || null,
      departmentId: this.departmentId,
      pmName: this.pmName || null,
      pmPhone: this.pmPhone || null,
      startDate: this.startDate || null,
      endDate: this.endDate || null,
      mainCompany: this.mainCompany,
      mainCompanyRep: this.mainCompanyRep || null,
      mainCompanyRepPhone: this.mainCompanyRepPhone || null,
      clientCompany: this.clientCompany,
      clientCompanyRep: this.clientCompanyRep || null,
      clientCompanyRepPhone: this.clientCompanyRepPhone || null,
    };
  }
}