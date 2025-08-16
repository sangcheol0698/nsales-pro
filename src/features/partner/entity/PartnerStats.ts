export default class PartnerStats {
  public readonly totalPartners: number;
  public readonly activePartners: number;
  public readonly averageGrade: string;
  public readonly revenueContribution: number;

  constructor(data: {
    totalPartners: number;
    activePartners: number;
    averageGrade: string;
    revenueContribution: number;
  }) {
    this.totalPartners = data.totalPartners;
    this.activePartners = data.activePartners;
    this.averageGrade = data.averageGrade;
    this.revenueContribution = data.revenueContribution;
  }

  public static fromResponse(response: any): PartnerStats {
    return new PartnerStats({
      totalPartners: response.totalPartners || 0,
      activePartners: response.activePartners || 0,
      averageGrade: response.averageGrade || 'N/A',
      revenueContribution: response.revenueContribution || 0,
    });
  }
}