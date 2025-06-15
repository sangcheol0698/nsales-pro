<template>
  <SidebarGroup>
    <SidebarGroupLabel>공지사항</SidebarGroupLabel>
    <SidebarMenu>
      <SidebarMenuItem v-for="item in items" :key="item.title">
        <SidebarMenuButton as-child :tooltip="item.title" :isActive="isActiveRoute(item.url)">
          <router-link :to="item.url" @click.prevent.stop="navigateTo(item.url)">
            <component :is="item.icon" v-if="item.icon" />
            <span>{{ item.title }}</span>
          </router-link>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  </SidebarGroup>
</template>

<script setup lang="ts">
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/core/components/ui/sidebar';
import { type LucideIcon } from 'lucide-vue-next';
import { useRoute, useRouter } from 'vue-router';

defineProps<{
  items: {
    title: string;
    url: string;
    icon?: LucideIcon;
    isActive?: boolean;
  }[];
}>();

const route = useRoute();
const router = useRouter();

// Check if the current route path matches the menu item's URL
const isActiveRoute = (url: string) => {
  return route.path === url || route.path.startsWith(`${url}/`);
};

// Function to navigate to a URL
const navigateTo = (url: string) => {
  router.push(url);
};
</script>
