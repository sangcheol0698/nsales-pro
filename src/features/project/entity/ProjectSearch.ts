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
  createdAt: string;
  updatedAt: string;

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
    createdAt: string;
    updatedAt: string;
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
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
  }

  static fromResponse(response: any): ProjectSearch {
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
      createdAt: response.createdAt || '',
      updatedAt: response.updatedAt || '',
    });
  }
}
