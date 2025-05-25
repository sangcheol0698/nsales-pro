<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header
        class="flex h-16 shrink-0 items-center gap-2 border-b dark:border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 transition-all duration-300 ease-in-out sticky top-0 z-10"
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
          <SearchComponent />

          <Button variant="outline" size="icon">
            <Bell class="h-5 w-5" />
            <span class="sr-only">Notifications</span>
          </Button>
          <ThemeToggle />
        </div>
      </header>
      <main class="flex-1 p-4 transition-all duration-300 ease-in-out">
        <slot></slot>
      </main>
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
import { Bell } from 'lucide-vue-next';
import AppSidebar from '@/shared/components/sidebar/AppSidebar.vue';
import { ThemeToggle } from '@/core/components/theme';
import { useRoute } from 'vue-router';
import { computed } from 'vue';
import SearchComponent from '@/shared/components/search/SearchComponent.vue';
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

</script>
