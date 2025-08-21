// 개발환경용 인증 유틸리티
// 브라우저 콘솔에서 setAdminUser(), setRegularUser() 함수를 사용하여 권한을 변경할 수 있습니다.

export const setAdminUser = () => {
  const adminUser = {
    name: '관리자',
    username: 'admin',
    role: 'ADMIN'
  };
  
  localStorage.setItem('user', JSON.stringify(adminUser));
  console.log('✅ 관리자 권한으로 설정되었습니다.');
  console.log('페이지를 새로고침하세요.');
};

export const setRegularUser = () => {
  const regularUser = {
    name: '일반사용자',
    username: 'user',
    role: 'USER'
  };
  
  localStorage.setItem('user', JSON.stringify(regularUser));
  console.log('✅ 일반사용자 권한으로 설정되었습니다.');
  console.log('페이지를 새로고침하세요.');
};

export const getCurrentAuthInfo = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    const user = JSON.parse(userStr);
    console.log('현재 사용자 정보:', user);
    console.log(`권한: ${user.role === 'ADMIN' ? '관리자' : '일반사용자'}`);
  } else {
    console.log('로그인된 사용자가 없습니다.');
  }
};

// 전역 함수로 등록하여 브라우저 콘솔에서 사용 가능하도록 함
if (typeof window !== 'undefined') {
  (window as any).setAdminUser = setAdminUser;
  (window as any).setRegularUser = setRegularUser;
  (window as any).getCurrentAuthInfo = getCurrentAuthInfo;
}