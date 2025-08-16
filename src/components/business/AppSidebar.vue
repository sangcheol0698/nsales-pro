<template>
  <Sidebar v-bind="props" variant="floating" class="border-none">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" asChild>
            <router-link to="/" class="flex items-center gap-3">
              <div
                class="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-sidebar-primary-foreground transition-all duration-300"
              >
                <img src="@/assets/main_logo.png" alt="ABACUS Logo" class="size-8" />
              </div>
              <div
                class="flex flex-col gap-0.5 leading-none transition-all duration-300 ease-in-out group-data-[collapsible=icon]:opacity-0 group-data-[collapsible=icon]:w-0 group-data-[collapsible=icon]:overflow-hidden"
              >
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
    </SidebarContent>

    <SidebarFooter>
      <NavUser :user="data.user" :onOpenProfileDialog="openProfileDialog" />
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
import { Building2, FileText, GalleryVerticalEnd, LayoutDashboard, Users, Wallet } from 'lucide-vue-next';
import NavMain from './NavMain.vue';
import NavUser from './NavUser.vue';

const props = withDefaults(defineProps<SidebarProps & {
  onOpenProfileDialog?: () => void;
}>(), {
  collapsible: 'icon',
  onOpenProfileDialog: () => {
  },
});

// This is sample data.
const data = {
  user: {
    name: 'Admin',
    email: 'admin@abacus.com',
    avatar: '/avatars/admin.jpg',
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

// 프로필 다이얼로그 열기
function openProfileDialog() {
  props.onOpenProfileDialog();
}
</script>