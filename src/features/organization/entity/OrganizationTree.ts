/**
 * 조직도 트리 노드 타입
 * 백엔드 TreeViewResponse와 매핑
 */
export interface OrganizationTreeNode {
  /** 부서 ID */
  departmentId?: number;
  
  /** 직원 ID (직원 노드인 경우) */
  employeeId?: number;
  
  /** 부서명 또는 직원명 */
  name: string;
  
  /** 하위 조직/구성원들 */
  children?: OrganizationTreeNode[];
  
  /** UI 상태 관리용 필드들 */
  expanded?: boolean;
  selected?: boolean;
  level?: number;
}

/**
 * 조직도 선택 이벤트 타입
 */
export interface OrganizationSelectEvent {
  node: OrganizationTreeNode;
  type: 'department' | 'employee';
  departmentId?: number;
  employeeId?: number;
}

/**
 * 조직도 필터 조건
 */
export interface OrganizationFilter {
  /** 부서명으로 필터링 */
  departmentName?: string;
  
  /** 직원명으로 필터링 */
  employeeName?: string;
  
  /** 특정 부서만 표시 */
  departmentId?: number;
  
  /** 빈 부서 포함 여부 */
  includeEmptyDepartments?: boolean;
}

/**
 * 조직도 옵션
 */
export interface OrganizationTreeOptions {
  /** 멤버 포함 여부 */
  withMembers?: boolean;
  
  /** 확장 가능 여부 */
  expandable?: boolean;
  
  /** 선택 가능 여부 */
  selectable?: boolean;
  
  /** 다중 선택 가능 여부 */
  multiSelect?: boolean;
  
  /** 검색 가능 여부 */
  searchable?: boolean;
  
  /** 드래그 앤 드롭 가능 여부 */
  draggable?: boolean;
  
  /** 컴팩트 모드 (작은 크기) */
  compact?: boolean;
}