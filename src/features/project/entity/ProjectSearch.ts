export default class ProjectSearch {
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
  departmentId?: number;
  departmentName?: string;
  pmName?: string;
  pmPhone?: string;
  expectedAmount?: number;
  mainCompanyRep?: string;
  mainCompanyRepPhone?: string;
  clientCompanyRep?: string;
  clientCompanyRepPhone?: string;
  createdAt: string;
  updatedAt: string;
  modifiedDateTime: string;

  constructor(data: {
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
    departmentId?: number;
    departmentName?: string;
    pmName?: string;
    pmPhone?: string;
    expectedAmount?: number;
    mainCompanyRep?: string;
    mainCompanyRepPhone?: string;
    clientCompanyRep?: string;
    clientCompanyRepPhone?: string;
    createdAt: string;
    updatedAt: string;
    modifiedDateTime: string;
  }) {
    this.id = data.id;
    this.code = data.code;
    this.name = data.name;
    this.type = data.type;
    this.startDate = data.startDate;
    this.endDate = data.endDate;
    this.contractDate = data.contractDate;
    this.contractAmount = data.contractAmount;
    this.mainCompany = data.mainCompany;
    this.clientCompany = data.clientCompany;
    this.status = data.status;
    this.departmentId = data.departmentId;
    this.departmentName = data.departmentName;
    this.pmName = data.pmName;
    this.pmPhone = data.pmPhone;
    this.expectedAmount = data.expectedAmount;
    this.mainCompanyRep = data.mainCompanyRep;
    this.mainCompanyRepPhone = data.mainCompanyRepPhone;
    this.clientCompanyRep = data.clientCompanyRep;
    this.clientCompanyRepPhone = data.clientCompanyRepPhone;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
    this.modifiedDateTime = data.modifiedDateTime;
  }

  static fromResponse(response: any): ProjectSearch {
    console.log('ProjectSearch.fromResponse - 서버 응답:', response);
    
    return new ProjectSearch({
      id: response.id,
      code: response.code || '',
      name: response.name || '',
      type: response.type || '',
      startDate: response.startDate || '',
      endDate: response.endDate || '',
      contractDate: response.contractDate || '',
      contractAmount: response.contractAmount || 0,
      mainCompany: response.mainCompany || '',
      clientCompany: response.clientCompany || '',
      status: response.status || '진행중',
      departmentId: response.departmentId || response.department?.id,
      departmentName: response.departmentName || response.department?.name,
      pmName: response.pmName,
      pmPhone: response.pmPhone,
      expectedAmount: response.expectedAmount,
      mainCompanyRep: response.mainCompanyRep,
      mainCompanyRepPhone: response.mainCompanyRepPhone,
      clientCompanyRep: response.clientCompanyRep,
      clientCompanyRepPhone: response.clientCompanyRepPhone,
      createdAt: response.createdAt || '',
      updatedAt: response.updatedAt || '',
      modifiedDateTime: response.modifiedDateTime || '',
    });
  }
}
