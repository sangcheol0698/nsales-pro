<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <div class="mb-6">
          <h1 class="text-xl font-semibold">설정</h1>
          <p class="text-sm text-muted-foreground">계정 설정 및 이메일 환경설정을 관리합니다.</p>
        </div>
        <div v-if="loading" class="flex justify-center items-center p-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        <div v-else class="flex flex-col md:flex-row gap-4 md:gap-8">
          <aside class="w-full md:w-48 flex-shrink-0">
            <nav class="space-y-1">
              <router-link
                to="/my-page/profile"
                class="block rounded-md px-3 py-2 text-sm font-medium"
                :class="[
                  $route.path === '/my-page/profile'
                    ? 'bg-secondary text-secondary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                ]"
              >
                프로필
              </router-link>
              <router-link
                to="/my-page/account"
                class="block rounded-md px-3 py-2 text-sm font-medium"
                :class="[
                  $route.path === '/my-page/account'
                    ? 'bg-secondary text-secondary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                ]"
              >
                내 계정 정보
              </router-link>
              <router-link
                to="/my-page/appearance"
                class="block rounded-md px-3 py-2 text-sm font-medium"
                :class="[
                  $route.path === '/my-page/appearance'
                    ? 'bg-secondary text-secondary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                ]"
              >
                환경 설정
              </router-link>
              <router-link
                to="/my-page/security"
                class="block rounded-md px-3 py-2 text-sm font-medium"
                :class="[
                  $route.path === '/my-page/security'
                    ? 'bg-secondary text-secondary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                ]"
              >
                보안설정
              </router-link>
              <router-link
                to="/my-page/activity"
                class="block rounded-md px-3 py-2 text-sm font-medium"
                :class="[
                  $route.path === '/my-page/activity'
                    ? 'bg-secondary text-secondary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                ]"
              >
                활동 내역
              </router-link>
            </nav>
          </aside>

          <div class="flex-1">
            <slot></slot>
          </div>
        </div>
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { SidebarLayout } from '@/shared/components/sidebar';

const props = defineProps<{
  loading?: boolean;
}>();

const loading = ref(props.loading || false);
</script>

<style scoped></style>
