<template>
  <div class="flex min-h-svh w-full">
    <AppSidebar :onOpenProfileDialog="openProfileDialog" />
    <SidebarInset>
      <!-- Header -->
      <header class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div class="flex items-center gap-2 px-4">
          <SidebarTrigger class="-ml-1" />
          <Separator orientation="vertical" class="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <template v-for="(crumb, index) in breadcrumbs" :key="index">
                <BreadcrumbItem class="hidden md:block">
                  <template v-if="crumb.disabled">
                    <BreadcrumbPage>{{ crumb.title }}</BreadcrumbPage>
                  </template>
                  <template v-else-if="crumb.to">
                    <BreadcrumbLink as-child>
                      <router-link :to="crumb.to">{{ crumb.title }}</router-link>
                    </BreadcrumbLink>
                  </template>
                  <template v-else>
                    <BreadcrumbPage>{{ crumb.title }}</BreadcrumbPage>
                  </template>
                </BreadcrumbItem>
                <BreadcrumbSeparator
                  v-if="index < breadcrumbs.length - 1"
                  class="hidden md:block"
                />
              </template>
            </BreadcrumbList>
          </Breadcrumb>
        </div>
        
        <div class="ml-auto flex items-center gap-2 px-4">
          <!-- Search Command Palette -->
          <Button variant="outline" size="sm" @click="openCommandPalette" class="relative h-8 w-40 justify-start text-sm font-normal text-muted-foreground shadow-none">
            <Search class="mr-2 h-4 w-4" />
            <span class="hidden lg:inline-flex">검색...</span>
            <span class="inline-flex lg:hidden">검색</span>
            <kbd class="pointer-events-none absolute right-1.5 top-1.5 hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
              <span class="text-xs">⌘</span>K
            </kbd>
          </Button>
          
          <!-- Notifications -->
          <Button variant="outline" size="sm" @click="openNotifications" class="relative h-8 w-8 px-0">
            <Bell class="h-4 w-4"/>
            <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 h-4 w-4 bg-destructive text-destructive-foreground text-xs rounded-full flex items-center justify-center">
              {{ unreadCount > 9 ? '9+' : unreadCount }}
            </span>
          </Button>
          
          <!-- Theme toggle -->
          <ThemeToggle />
        </div>
      </header>

      <!-- Main content area -->
      <main class="flex-1 p-4 transition-all duration-300 ease-in-out">
        <slot/>
      </main>
    </SidebarInset>

    <!-- Profile Dialog -->
    <ProfileDialog 
      :open="isProfileDialogOpen" 
      @update:open="isProfileDialogOpen = $event" 
    />

    <!-- Command Palette -->
    <CommandPalette
      :open="isCommandPaletteOpen"
      @update:open="isCommandPaletteOpen = $event"
      :onOpenSettings="openSettingsDialog"
    />

    <!-- Settings Dialog -->
    <SettingsDialog
      :open="isSettingsDialogOpen"
      @update:open="isSettingsDialogOpen = $event"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { Search, Bell } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import {
  SidebarInset,
  SidebarTrigger,
} from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import ThemeToggle from '@/core/theme/ThemeToggle.vue';
import { ProfileDialog, SettingsDialog } from '@/components/business';
import AppSidebar from '@/components/business/AppSidebar.vue';
import CommandPalette from '@/components/business/CommandPalette.vue';

const route = useRoute();
const isProfileDialogOpen = ref(false);
const isCommandPaletteOpen = ref(false);
const isSettingsDialogOpen = ref(false);
const unreadCount = ref(3); // 임시로 3개의 읽지 않은 알림

// Get the current route's title
const pageTitle = computed(() => {
  return (route.meta.title as string) || 'NSales Pro';
});

// Breadcrumb type definition
type BreadcrumbItem = {
  title: string;
  to?: string;
  disabled?: boolean;
};

// Get breadcrumbs from route meta
const breadcrumbs = computed(() => {
  return (route.meta.breadcrumbs || []) as BreadcrumbItem[];
});

function openProfileDialog() {
  isProfileDialogOpen.value = true;
}

function openCommandPalette() {
  isCommandPaletteOpen.value = true;
}

function openNotifications() {
  // 알림 패널 열기 (나중에 구현)
  console.log('알림 패널 열기');
}

function openSettingsDialog() {
  isSettingsDialogOpen.value = true;
}

// Command + K 단축키 처리
function handleKeydown(event: KeyboardEvent) {
  if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
    event.preventDefault();
    openCommandPalette();
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});
</script>
