<template>
  <Sidebar v-bind="props" variant="floating">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <router-link to="/" class="flex items-center gap-3">
              <div
                class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground transition-all duration-300"
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
  Bot,
  Building2,
  FileText,
  GalleryVerticalEnd,
  LayoutDashboard,
  Users,
  Wallet,
  Smartphone,
} from 'lucide-vue-next';
import NavMain from '@/shared/components/sidebar/NavMain.vue';
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
    {
      title: 'AI Assistant',
      url: '/chat',
      icon: Bot,
    },
    {
      title: 'Google 연동',
      url: '/google-integration',
      icon: Smartphone,
    },
  ],
};
</script>
