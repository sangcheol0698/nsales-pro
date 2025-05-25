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
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// router.beforeEach((to, from, next) => {
//   // if (memberStore.isAuthenticated === null && !to.fullPath.startsWith('/auths')) {
//   //   next({ name: 'login' });
//   // }
//   next();
// });

export default router;
