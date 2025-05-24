<template>
  <SidebarGroup>
    <SidebarGroupLabel>메뉴</SidebarGroupLabel>
    <SidebarMenu>
      <SidebarMenuItem v-for="item in items" :key="item.title">
        <SidebarMenuButton as-child :tooltip="item.title" :isActive="isActiveRoute(item.url)">
          <a :href="item.url">
            <component :is="item.icon" v-if="item.icon" />
            <span>{{ item.title }}</span>
          </a>
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
} from '@/components/ui/sidebar';
import { type LucideIcon } from 'lucide-vue-next';
import { useRoute } from 'vue-router';

defineProps<{
  items: {
    title: string;
    url: string;
    icon?: LucideIcon;
    isActive?: boolean;
  }[];
}>();

const route = useRoute();

// Check if the current route path matches the menu item's URL
const isActiveRoute = (url: string) => {
  return route.path === url;
};
</script>
