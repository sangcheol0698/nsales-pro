<template>
  <SidebarGroup>
    <SidebarGroupLabel class="px-2 text-xs font-semibold text-muted-foreground group-data-[collapsible=icon]:hidden">설정</SidebarGroupLabel>
    <SidebarMenu>
      <SidebarMenuItem v-for="item in items" :key="item.title">
        <SidebarMenuButton as-child :tooltip="item.title" :isActive="isActiveRoute(item.url)">
          <router-link
            :to="item.url"
            @click.prevent.stop="navigateTo(item.url)"
            class="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-all duration-300 ease-in-out hover:bg-accent hover:text-accent-foreground"
            :class="[
              isActiveRoute(item.url) 
                ? 'bg-accent text-accent-foreground' 
                : 'text-muted-foreground'
            ]"
          >
            <component 
              :is="item.icon" 
              v-if="item.icon" 
              class="size-4 transition-all duration-300 ease-in-out" 
              :class="[
                isActiveRoute(item.url) 
                  ? 'text-primary' 
                  : 'text-muted-foreground'
              ]"
            />
            <span class="group-data-[collapsible=icon]:hidden transition-all duration-300 ease-in-out">{{ item.title }}</span>
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
