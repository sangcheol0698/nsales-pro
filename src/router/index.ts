import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
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
    component: () => import('@/views/auth/SetPasswordView.vue'),
  },
  {
    path: '/auths/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
  },
  {
    path: '/auths/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
  },
  {
    path: '/auths/forgot-password',
    name: 'findPassword',
    component: () => import('@/views/auth/ForgotPasswordView.vue'),
  },
  {
    path: '/projects',
    name: 'projects',
    component: () => import('@/views/project/ProjectView.vue'),
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
          disabled: false,
        },
      ],
    },
  },
  // {
  //   path: '/projects/:id',
  //   name: 'projectDetail',
  //   component: () => import('@/views/project/ProjectDetailView.vue'),
  //   meta: {
  //     menu: false,
  //     activeIndex: 0,
  //     title: '프로젝트 관리',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '프로젝트 관리',
  //         disabled: false,
  //         to: {
  //           name: 'projects',
  //         },
  //       },
  //       {
  //         title: '프로젝트 상세',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/employees',
  //   name: 'employees',
  //   component: () => import('@/views/employee/EmployeeView.vue'),
  //   meta: {
  //     menu: true,
  //     activeIndex: 1,
  //     title: '구성원 관리',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '구성원 관리',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/partners',
  //   name: 'partners',
  //   component: () => import('@/views/partners/PartnersView.vue'),
  //   meta: {
  //     menu: true,
  //     activeIndex: 2,
  //     title: '협력사 관리',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '협력사 관리',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/partners/:id',
  //   name: 'partnersDetail',
  //   component: () => import('@/views/partners/PartnersDetailView.vue'),
  //   meta: {
  //     activeIndex: 2,
  //     title: '협력사 상세',
  //     breadcrumbs: [
  //       { title: '홈', disabled: false, to: { name: 'home' } },
  //       { title: '협력사 관리', disabled: false, to: { name: 'partners' } },
  //       { title: '협력사 상세', disabled: true },
  //     ],
  //   },
  // },
  // {
  //   path: '/sales',
  //   name: 'sales',
  //   component: () => import('@/views/SalesView.vue'),
  //   meta: {
  //     menu: true,
  //     activeIndex: 3,
  //     title: '매출 관리',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '매출 관리',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/permissions',
  //   name: 'permissions',
  //   component: () => import('@/views/PermissionView.vue'),
  //   meta: {
  //     menu: true,
  //     activeIndex: 4,
  //     title: '권한 관리',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '권한 관리',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/profiles',
  //   name: 'profiles',
  //   component: () => import('@/views/ProfileView.vue'),
  //   meta: {
  //     activeIndex: 5,
  //     title: '마이페이지',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '마이페이지',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/projects/detail/contracts/detail',
  //   name: 'contracts',
  //   component: () => import('@/views/project/ContractDetailView.vue'),
  //   meta: {
  //     activeIndex: 0,
  //     title: '계약 상세',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '프로젝트 관리',
  //         disabled: false,
  //         to: {
  //           name: 'projects',
  //         },
  //       },
  //       {
  //         title: '프로젝트 상세',
  //         disabled: false,
  //         to: {
  //           name: 'projects',
  //         },
  //       },
  //       {
  //         title: '계약 상세',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/employees/:id',
  //   name: 'employeeDetail',
  //   component: () => import('@/views/employee/EmployeeDetailView.vue'),
  //   meta: {
  //     activeIndex: 1,
  //     title: '구성원 상세',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '구성원 관리',
  //         disabled: false,
  //         to: {
  //           name: 'employees',
  //         },
  //       },
  //       {
  //         title: '구성원 상세',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/memberCreate',
  //   name: 'memberCreate',
  //   component: () => import('@/views/employee/EmployeeCreatePopup.vue'),
  //   meta: {
  //     activeIndex: 1,
  //     title: '구성원 추가',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '구성원 관리',
  //         disabled: false,
  //         to: {
  //           name: 'employees',
  //         },
  //       },
  //       {
  //         title: '구성원 추가',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
  // {
  //   path: '/employeeSalaryUpdate',
  //   name: 'employeeSalaryUpdate',
  //   component: () => import('@/views/employee/EmployeeSalaryView.vue'),
  //   meta: {
  //     activeIndex: 1,
  //     title: '구성원 연봉 관리',
  //     breadcrumbs: [
  //       {
  //         title: '홈',
  //         disabled: false,
  //         to: {
  //           name: 'home',
  //         },
  //       },
  //       {
  //         title: '구성원 관리',
  //         disabled: false,
  //         to: {
  //           name: 'employees',
  //         },
  //       },
  //       {
  //         title: '구성원 연봉 관리',
  //         disabled: true,
  //       },
  //     ],
  //   },
  // },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  // if (memberStore.isAuthenticated === null && !to.fullPath.startsWith('/auths')) {
  //   next({ name: 'login' });
  // }
  next();
});

export default router;
