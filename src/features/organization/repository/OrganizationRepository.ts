import { inject, singleton } from 'tsyringe';
import HttpRepository from '@/core/http/HttpRepository.ts';
import type { OrganizationTreeNode } from '../entity/OrganizationTree';

/**
 * 조직도 API Repository
 */
@singleton()
export default class OrganizationRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}
  
  /**
   * 팀 목록 조회
   */
  async getTeams(): Promise<Array<{ id: number; name: string }>> {
    const response = await this.httpRepository.get({
      path: '/api/v1/teams'
    });
    return response;
  }

  /**
   * 부서 목록 조회  
   */
  async getDepartments(): Promise<Array<{ id: number; name: string }>> {
    const response = await this.httpRepository.get({
      path: '/api/v1/departments'
    });
    return response;
  }

  /**
   * 조직도 트리뷰 조회 (멤버 제외)
   */
  async getOrganizationTree(): Promise<OrganizationTreeNode[]> {
    const response = await this.httpRepository.get({
      path: '/api/v1/teams/tree'
    });
    return this.transformTreeData(response);
  }

  /**
   * 조직도 트리뷰 조회 (멤버 포함)
   */
  async getOrganizationTreeWithMembers(): Promise<OrganizationTreeNode[]> {
    const response = await this.httpRepository.get({
      path: '/api/v1/teams/tree/member'
    });
    return this.transformTreeData(response);
  }

  /**
   * 백엔드 TreeViewResponse를 프론트엔드 OrganizationTreeNode로 변환
   */
  private transformTreeData(data: any[]): OrganizationTreeNode[] {
    return data.map(item => this.transformTreeNode(item, 0));
  }

  /**
   * 개별 트리 노드 변환
   */
  private transformTreeNode(item: any, level: number): OrganizationTreeNode {
    return {
      departmentId: item.departmentId,
      employeeId: item.employeeId,
      name: item.name,
      children: item.children?.map((child: any) => this.transformTreeNode(child, level + 1)) || [],
      expanded: level < 2, // 기본적으로 2레벨까지만 확장
      selected: false,
      level
    };
  }
}