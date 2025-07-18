import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/features/dashboard/views/HomeView.vue'),
    meta: {
      title: '대시보드',
      breadcrumbs: [
        {
          title: '홈',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/my-page',
    name: 'myPage',
    component: () => import('@/features/member/views/MyPageParentView.vue'),
    redirect: '/my-page/profile',
    meta: {
      menu: false,
      title: '내 프로필',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '내 프로필',
          disabled: true,
        },
      ],
    },
    children: [
      {
        path: 'profile',
        name: 'myPageProfile',
        component: () => import('@/features/member/views/ProfileView.vue'),
        meta: {
          title: '프로필',
        },
      },
      {
        path: 'account',
        name: 'myPageAccount',
        component: () => import('@/features/member/views/AccountView.vue'),
        meta: {
          title: '계정 정보',
        },
      },
      {
        path: 'appearance',
        name: 'myPageAppearance',
        component: () => import('@/features/member/views/AppearanceView.vue'),
        meta: {
          title: '화면 설정',
        },
      },
      {
        path: 'security',
        name: 'myPageSecurity',
        component: () => import('@/features/member/views/SecurityView.vue'),
        meta: {
          title: '보안 설정',
        },
      },
      {
        path: 'activity',
        name: 'myPageActivity',
        component: () => import('@/features/member/views/ActivityView.vue'),
        meta: {
          title: '활동 내역',
        },
      },
    ],
  },
  {
    path: '/notices',
    name: 'notices',
    component: () => import('@/features/notice/views/NoticeView.vue'),
    meta: {
      menu: true,
      activeIndex: 5,
      title: '공지사항',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '공지사항',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/notices/new',
    name: 'noticeCreate',
    component: () => import('@/features/notice/views/NoticeFormView.vue'),
    meta: {
      menu: false,
      activeIndex: 5,
      title: '공지사항 등록',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '공지사항',
          disabled: false,
          to: '/notices',
        },
        {
          title: '공지사항 등록',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/notices/:id',
    name: 'noticeDetail',
    component: () => import('@/features/notice/views/NoticeDetailView.vue'),
    meta: {
      menu: false,
      activeIndex: 5,
      title: '공지사항 상세',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '공지사항',
          disabled: false,
          to: '/notices',
        },
        {
          title: '공지사항 상세',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/notices/:id/edit',
    name: 'noticeEdit',
    component: () => import('@/features/notice/views/NoticeFormView.vue'),
    meta: {
      menu: false,
      activeIndex: 5,
      title: '공지사항 수정',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '공지사항',
          disabled: false,
          to: '/notices',
        },
        {
          title: '공지사항 상세',
          disabled: false,
          to: (route: { params: { id: string | number } }) => `/notices/${route.params.id}`,
        },
        {
          title: '공지사항 수정',

          disabled: true,
        },
      ],
    },
  },
  {
    path: '/auths/initialize',
    name: 'initialize',
    component: () => import('@/features/auth/views/SetPasswordView.vue'),
  },
  {
    path: '/auths/register',
    name: 'register',
    component: () => import('@/features/auth/views/RegisterView.vue'),
  },
  {
    path: '/auths/login',
    name: 'login',
    component: () => import('@/features/auth/views/LoginView.vue'),
  },
  {
    path: '/auths/forgot-password',
    name: 'findPassword',
    component: () => import('@/features/auth/views/ForgotPasswordView.vue'),
  },
  {
    path: '/projects',
    name: 'projects',
    component: () => import('@/features/project/views/ProjectView.vue'),
    meta: {
      menu: true,
      activeIndex: 0,
      title: '프로젝트 관리',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '프로젝트 관리',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/employees',
    name: 'employees',
    component: () => import('@/features/employee/views/EmployeeView.vue'),
    meta: {
      menu: true,
      activeIndex: 1,
      title: '구성원 관리',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '구성원 관리',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/partners',
    name: 'partners',
    component: () => import('@/features/partner/views/PartnerView.vue'),
    meta: {
      menu: true,
      activeIndex: 2,
      title: '협력사 관리',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '협력사 관리',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/sales',
    name: 'sales',
    component: () => import('@/features/sales/views/SalesView.vue'),
    meta: {
      menu: true,
      activeIndex: 3,
      title: '매출 관리',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '매출 관리',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/projects/:id',
    name: 'projectDetail',
    component: () => import('@/features/project/views/ProjectDetailView.vue'),
    meta: {
      menu: false,
      activeIndex: 0,
      title: '프로젝트 상세',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: '프로젝트 관리',
          disabled: false,
          to: '/projects',
        },
        {
          title: '프로젝트 상세',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/features/chat/views/ChatView.vue'),
    meta: {
      menu: true,
      activeIndex: 4,
      title: 'AI Assistant',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: 'AI Assistant',
          disabled: true,
        },
      ],
    },
  },
  {
    path: '/chat/:sessionId',
    name: 'chatSession',
    component: () => import('@/features/chat/views/ChatView.vue'),
    meta: {
      menu: false,
      activeIndex: 4,
      title: 'AI Assistant',
      breadcrumbs: [
        {
          title: '홈',
          disabled: false,
          to: '/',
        },
        {
          title: 'AI Assistant',
          disabled: false,
          to: '/chat',
        },
        {
          title: '채팅 세션',
          disabled: true,
        },
      ],
    },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  // 인증이 필요하지 않은 경로 목록
  const publicPaths = ['/auths/login', '/auths/register', '/auths/forgot-password', '/auths/initialize'];

  // localStorage에서 사용자 정보 가져오기
  const userStr = localStorage.getItem('user');

  // 로그인이 필요한 페이지에 접근하려고 하는데 사용자 정보가 없는 경우
  if (!userStr && !publicPaths.includes(to.path)) {
    // 로그인 페이지로 리다이렉트
    next({ name: 'login' });
  } else {
    // 그 외의 경우 정상적으로 라우팅
    next();
  }
});

export default router;
