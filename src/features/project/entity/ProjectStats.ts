export default class ProjectStats {
  public readonly totalProjects: number;
  public readonly activeProjects: number;
  public readonly totalValue: number;
  public readonly completionRate: number;

  constructor(data: {
    totalProjects: number;
    activeProjects: number;
    totalValue: number;
    completionRate: number;
  }) {
    this.totalProjects = data.totalProjects;
    this.activeProjects = data.activeProjects;
    this.totalValue = data.totalValue;
    this.completionRate = data.completionRate;
  }

  public static fromResponse(response: any): ProjectStats {
    return new ProjectStats({
      totalProjects: response.totalProjects || 0,
      activeProjects: response.activeProjects || 0,
      totalValue: response.totalValue || 0,
      completionRate: response.completionRate || 0,
    });
  }
}