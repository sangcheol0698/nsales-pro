export default class SalesStats {
  public readonly totalRevenue: number;
  public readonly collectedRevenue: number;
  public readonly outstandingAmount: number;
  public readonly averageCollectionPeriod: number;

  constructor(data: {
    totalRevenue: number;
    collectedRevenue: number;
    outstandingAmount: number;
    averageCollectionPeriod: number;
  }) {
    this.totalRevenue = data.totalRevenue;
    this.collectedRevenue = data.collectedRevenue;
    this.outstandingAmount = data.outstandingAmount;
    this.averageCollectionPeriod = data.averageCollectionPeriod;
  }

  public static fromResponse(response: any): SalesStats {
    return new SalesStats({
      totalRevenue: response.totalRevenue || 0,
      collectedRevenue: response.collectedRevenue || 0,
      outstandingAmount: response.outstandingAmount || 0,
      averageCollectionPeriod: response.averageCollectionPeriod || 0,
    });
  }
}