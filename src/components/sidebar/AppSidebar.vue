<template>
  <Sidebar v-bind="props" variant="floating">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <a href="/">
              <div
                class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground"
              >
                <GalleryVerticalEnd class="size-4" />
              </div>
              <div class="flex flex-col gap-0.5 leading-none">
                <span class="font-semibold">Abacus - 매출 관리</span>
                <span class="text-xs text-muted-foreground"> Abacus Inc </span>
              </div>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
    <SidebarContent>
      <NavMain :items="data.navMain" />
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
} from '@/components/ui/sidebar';
import {
  Building2,
  FileText,
  GalleryVerticalEnd,
  LayoutDashboard,
  Users,
  Wallet,
} from 'lucide-vue-next';
import NavMain from './NavMain.vue';
import NavUser from './NavUser.vue';

const props = withDefaults(defineProps<SidebarProps>(), {
  collapsible: 'icon',
});

// This is sample data.
const data = {
  user: {
    name: 'shadcn',
    email: 'm@example.com',
    avatar: '/avatars/shadcnjpg.',
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
};
</script>
