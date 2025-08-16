export default class EmployeeStats {
  public readonly totalEmployees: number;
  public readonly activeEmployees: number;
  public readonly newHires: number;
  public readonly averageTenure: number;

  constructor(data: {
    totalEmployees: number;
    activeEmployees: number;
    newHires: number;
    averageTenure: number;
  }) {
    this.totalEmployees = data.totalEmployees;
    this.activeEmployees = data.activeEmployees;
    this.newHires = data.newHires;
    this.averageTenure = data.averageTenure;
  }

  public static fromResponse(response: any): EmployeeStats {
    return new EmployeeStats({
      totalEmployees: response.totalEmployees || 0,
      activeEmployees: response.activeEmployees || 0,
      newHires: response.newHires || 0,
      averageTenure: response.averageTenure || 0,
    });
  }
}