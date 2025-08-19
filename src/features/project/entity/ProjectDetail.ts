export default class ProjectDetail {
  id: number;
  code: string;
  name: string;
  type: 'SI' | 'SM';
  status: '진행중' | '완료' | '예약';
  contractDate: string;
  department: {
    id: number;
    name: string;
  };
  startDate?: string;
  endDate?: string;
  pmName?: string;
  pmPhone?: string;
  mainCompany: string;
  mainCompanyRep?: string;
  mainCompanyRepPhone?: string;
  clientCompany: string;
  clientCompanyRep?: string;
  clientCompanyRepPhone?: string;
  expectedAmount?: number;
  contractAmount?: number;
  modifiedDateTime: string;

  constructor(data: {
    id: number;
    code: string;
    name: string;
    type: 'SI' | 'SM';
    status: '진행중' | '완료' | '예약';
    contractDate: string;
    department: {
      id: number;
      name: string;
    };
    startDate?: string;
    endDate?: string;
    pmName?: string;
    pmPhone?: string;
    mainCompany: string;
    mainCompanyRep?: string;
    mainCompanyRepPhone?: string;
    clientCompany: string;
    clientCompanyRep?: string;
    clientCompanyRepPhone?: string;
    expectedAmount?: number;
    contractAmount?: number;
    modifiedDateTime: string;
  }) {
    this.id = data.id;
    this.code = data.code;
    this.name = data.name;
    this.type = data.type;
    this.status = data.status;
    this.contractDate = data.contractDate;
    this.department = data.department;
    this.startDate = data.startDate;
    this.endDate = data.endDate;
    this.pmName = data.pmName;
    this.pmPhone = data.pmPhone;
    this.mainCompany = data.mainCompany;
    this.mainCompanyRep = data.mainCompanyRep;
    this.mainCompanyRepPhone = data.mainCompanyRepPhone;
    this.clientCompany = data.clientCompany;
    this.clientCompanyRep = data.clientCompanyRep;
    this.clientCompanyRepPhone = data.clientCompanyRepPhone;
    this.expectedAmount = data.expectedAmount;
    this.contractAmount = data.contractAmount;
    this.modifiedDateTime = data.modifiedDateTime;
  }

  static fromResponse(response: any): ProjectDetail {
    console.log('ProjectDetail.fromResponse - 서버 응답:', response);
    
    return new ProjectDetail({
      id: response.id,
      code: response.code,
      name: response.name,
      type: response.type,
      status: response.status,
      contractDate: response.contractDate,
      department: response.department,
      startDate: response.startDate,
      endDate: response.endDate,
      pmName: response.pmName,
      pmPhone: response.pmPhone,
      mainCompany: response.mainCompany,
      mainCompanyRep: response.mainCompanyRep,
      mainCompanyRepPhone: response.mainCompanyRepPhone,
      clientCompany: response.clientCompany,
      clientCompanyRep: response.clientCompanyRep,
      clientCompanyRepPhone: response.clientCompanyRepPhone,
      expectedAmount: response.expectedAmount,
      contractAmount: response.contractAmount,
      modifiedDateTime: response.modifiedDateTime,
    });
  }
}