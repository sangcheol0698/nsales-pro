<template>
  <Sidebar v-bind="props" variant="floating">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <router-link to="/">
              <div
                class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground"
              >
                <GalleryVerticalEnd class="size-4" />
              </div>
              <div class="flex flex-col gap-0.5 leading-none">
                <span class="font-semibold">ABACUS</span>
                <span class="text-xs text-muted-foreground"> Abacus Inc </span>
              </div>
            </router-link>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
    <SidebarContent>
      <NavMain :items="data.navMain" />
      <NavSettings :items="data.navSettings" />
    </SidebarContent>
    <SidebarFooter>
      <NavUser :user="data.user" />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>

<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  type SidebarProps,
  SidebarRail,
} from '@/core/components/ui/sidebar';
import {
  BadgeCheck,
  Bell,
  Building2,
  Clock,
  CreditCard,
  FileText,
  GalleryVerticalEnd,
  LayoutDashboard,
  Shield,
  Sun,
  Users,
  Wallet,
} from 'lucide-vue-next';
import NavMain from '@/shared/components/sidebar/NavMain.vue';
import NavSettings from '@/shared/components/sidebar/NavSettings.vue';
import NavUser from '@/shared/components/sidebar/NavUser.vue';

const props = withDefaults(defineProps<SidebarProps>(), {
  collapsible: 'icon',
});

const data = {
  user: {
    name: 'shadcn',
    email: 'm@example.com',
    avatar: '/avatars/shadcn.jpg',
  },
  teams: [
    {
      name: 'Abacus Inc',
      logo: GalleryVerticalEnd,
      plan: 'Enterprise',
    },
  ],
  navMain: [
    {
      title: '대시보드',
      url: '/',
      icon: LayoutDashboard,
    },
    {
      title: '프로젝트',
      url: '/projects',
      icon: FileText,
    },
    {
      title: '구성원',
      url: '/employees',
      icon: Users,
    },
    {
      title: '협력사',
      url: '/partners',
      icon: Building2,
    },
    {
      title: '매출',
      url: '/sales',
      icon: Wallet,
    },
  ],
  navNotices: [
    {
      title: '공지사항',
      url: '/notices',
      icon: Bell,
    },
  ],
  navSettings: [
    {
      title: '프로필',
      url: '/my-page/profile',
      icon: BadgeCheck,
    },
    {
      title: '계정 정보',
      url: '/my-page/account',
      icon: CreditCard,
    },
    {
      title: '화면 설정',
      url: '/my-page/appearance',
      icon: Sun,
    },
    {
      title: '보안 설정',
      url: '/my-page/security',
      icon: Shield,
    },
    {
      title: '활동 내역',
      url: '/my-page/activity',
      icon: Clock,
    },
  ],
};
</script>
