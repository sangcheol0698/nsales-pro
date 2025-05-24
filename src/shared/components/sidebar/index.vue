<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header
        class="flex h-16 shrink-0 items-center gap-2 border-b dark:border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12"
      >
        <div class="flex items-center gap-2 px-4">
          <SidebarTrigger class="-ml-1" />
          <Separator orientation="vertical" class="mr-2 h-4" />
          <div class="flex flex-col">
            <h1 class="text-lg font-semibold">{{ pageTitle }}</h1>
            <Breadcrumb>
              <BreadcrumbList>
                <template v-for="(crumb, index) in breadcrumbs" :key="index">
                  <BreadcrumbItem class="hidden md:block">
                    <template v-if="crumb.disabled">
                      <BreadcrumbPage>{{ crumb.title }}</BreadcrumbPage>
                    </template>
                    <template v-else>
                      <BreadcrumbLink as-child>
                        <router-link :to="crumb.to">{{ crumb.title }}</router-link>
                      </BreadcrumbLink>
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
        </div>
        <div class="ml-auto flex items-center gap-2 px-4">
          <CommandDialog modal :open="isCommandDialogOpen" @open-change="setIsCommandDialogOpen">
            <CommandInput placeholder="Type a command or search..." />
            <CommandList>
              <CommandEmpty>No results found.</CommandEmpty>
              <CommandGroup heading="Suggestions">
                <CommandItem>Calendar</CommandItem>
                <CommandItem>Search</CommandItem>
                <CommandItem>Projects</CommandItem>
                <CommandItem>Settings</CommandItem>
              </CommandGroup>
            </CommandList>
          </CommandDialog>
          <Button variant="outline" size="icon">
            <Bell class="h-5 w-5" />
            <span class="sr-only">Notifications</span>
          </Button>
          <Button variant="outline" size="icon" @click="isCommandDialogOpen = true">
            <Search class="h-5 w-5" />
            <span class="sr-only">Search</span>
          </Button>
          <ThemeToggle />
        </div>
      </header>
      <slot></slot>
    </SidebarInset>
  </SidebarProvider>
</template>

<script setup lang="ts">
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/core/components/ui/sidebar';
import { Separator } from '@/core/components/ui/separator';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/core/components/ui/breadcrumb';
import { Button } from '@/core/components/ui/button';
import { Bell, Search } from 'lucide-vue-next';
import AppSidebar from '@/shared/components/sidebar/AppSidebar.vue';
import { ThemeToggle } from '@/core/components/theme';
import { useRoute } from 'vue-router';
import { computed, ref } from 'vue';
import { useEventListener } from '@vueuse/core';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/core/components/ui/command';

const route = useRoute();

// Get the current route's title
const pageTitle = computed(() => {
  return route.meta.title || 'Dashboard';
});

type Breadcrumb = {
  title: string;
  disabled: boolean;
  to: string;
};

const breadcrumbs = computed(() => {
  return (route.meta.breadcrumbs || []) as Breadcrumb[];
});

// Command dialog state
const isCommandDialogOpen = ref(false);

const setIsCommandDialogOpen = (open: boolean) => {
  isCommandDialogOpen.value = open;
};

// Keyboard shortcut for command dialog (Cmd/Ctrl + K)
useEventListener('keydown', (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    isCommandDialogOpen.value = !isCommandDialogOpen.value;
  }
});
</script>