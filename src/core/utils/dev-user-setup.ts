// 개발환경용 사용자 정보 설정 유틸리티

export interface MockUser {
  name: string;
  username: string;
  email?: string;
  role: 'ADMIN' | 'USER';
  avatarUrl?: string;
}

export interface MockEmployee {
  id: number;
  name: string;
  email: string;
  phone?: string;
  birthDate?: string;
  joinDate?: string;
  teamName?: string;
  status: string;
  rank?: string;
  grade?: string;
}

// 목 사용자 데이터
const mockUsers: MockUser[] = [
  {
    name: '김철수',
    username: 'kimcs@abacus.com',
    email: 'kimcs@abacus.com',
    role: 'ADMIN',
    avatarUrl: '',
  },
  {
    name: '이영희',
    username: 'leeyh@abacus.com', 
    email: 'leeyh@abacus.com',
    role: 'USER',
    avatarUrl: '',
  },
  {
    name: 'John Smith',
    username: 'john@abacus.com',
    email: 'john@abacus.com', 
    role: 'USER',
    avatarUrl: '',
  },
];

const mockEmployees: MockEmployee[] = [
  {
    id: 1,
    name: '김철수',
    email: 'kimcs@abacus.com',
    phone: '010-1234-5678',
    birthDate: '1985-03-15',
    joinDate: '2020-01-01',
    teamName: '개발팀',
    status: 'ACTIVE',
    rank: '책임',
    grade: '5급',
  },
  {
    id: 2,
    name: '이영희',
    email: 'leeyh@abacus.com',
    phone: '010-9876-5432',
    birthDate: '1990-08-22',
    joinDate: '2021-03-15',
    teamName: '마케팅팀',
    status: 'ACTIVE',
    rank: '주임',
    grade: '6급',
  },
  {
    id: 3,
    name: 'John Smith',
    email: 'john@abacus.com', 
    phone: '010-5555-1234',
    birthDate: '1988-11-10',
    joinDate: '2019-06-01',
    teamName: '영업팀',
    status: 'ACTIVE',
    rank: '과장',
    grade: '4급',
  },
];

/**
 * 개발환경용 사용자 정보를 localStorage에 설정
 */
export function setupDevUser(userIndex: number = 0): void {
  const user = mockUsers[userIndex] || mockUsers[0];
  const employee = mockEmployees[userIndex] || mockEmployees[0];
  
  // localStorage에 사용자 정보 저장
  localStorage.setItem('user', JSON.stringify(user));
  localStorage.setItem('employee', JSON.stringify(employee));
  
  console.log('✅ 개발환경 사용자 정보가 설정되었습니다:', {
    user: user.name,
    role: user.role,
    employee: employee.teamName,
  });
}

/**
 * 관리자 권한 사용자로 전환
 */
export function setAsAdmin(): void {
  setupDevUser(0); // 김철수 (ADMIN)
}

/**
 * 일반 사용자 권한으로 전환  
 */
export function setAsUser(): void {
  setupDevUser(1); // 이영희 (USER)
}

/**
 * 현재 설정된 사용자 정보 확인
 */
export function getCurrentDevUser(): { user: MockUser | null, employee: MockEmployee | null } {
  try {
    const userStr = localStorage.getItem('user');
    const employeeStr = localStorage.getItem('employee');
    
    return {
      user: userStr ? JSON.parse(userStr) : null,
      employee: employeeStr ? JSON.parse(employeeStr) : null,
    };
  } catch (error) {
    console.error('사용자 정보 파싱 실패:', error);
    return { user: null, employee: null };
  }
}

/**
 * 사용자 정보 초기화
 */
export function clearDevUser(): void {
  localStorage.removeItem('user');
  localStorage.removeItem('employee');
  console.log('✅ 사용자 정보가 초기화되었습니다.');
}

// 브라우저 콘솔에서 사용할 수 있도록 전역 함수로 등록
if (typeof window !== 'undefined') {
  (window as any).devUser = {
    setup: setupDevUser,
    setAsAdmin,
    setAsUser,
    getCurrent: getCurrentDevUser,
    clear: clearDevUser,
    mockUsers,
    mockEmployees,
  };
  
  console.log('🔧 개발환경 사용자 유틸리티가 로드되었습니다:');
  console.log('  - window.devUser.setAsAdmin() : 관리자로 전환');
  console.log('  - window.devUser.setAsUser()  : 일반 사용자로 전환');
  console.log('  - window.devUser.getCurrent() : 현재 사용자 확인');
  console.log('  - window.devUser.clear()      : 사용자 정보 초기화');
}

// 기본적으로 사용자 정보가 없으면 관리자로 설정
if (typeof window !== 'undefined') {
  const current = getCurrentDevUser();
  if (!current.user) {
    setupDevUser(0); // 기본값: 김철수 (ADMIN)
  }
}