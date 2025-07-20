<template>
  <div class="google-status-badge">
    <Transition name="fade" mode="out-in">
      <div
        v-if="!isLoading"
        :class="[
          'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-colors',
          badgeClass
        ]"
      >
        <div class="text-sm" v-html="statusIcon"></div>
        <span>{{ badgeText }}</span>
        <button
          v-if="!isAuthenticated && servicesAvailable"
          @click="connect"
          class="ml-1 text-xs underline hover:no-underline"
        >
          연결
        </button>
      </div>
      
      <div
        v-else
        class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium bg-muted text-muted-foreground"
      >
        <div class="w-3 h-3 animate-spin rounded-full border border-current border-t-transparent"></div>
        <span>확인 중...</span>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useGoogleAuth } from '@/core/composables/useGoogleAuth'

// Google 인증 상태 관리
const {
  isAuthenticated,
  isLoading,
  servicesAvailable,
  statusIcon,
  startAuth
} = useGoogleAuth()

// 배지 스타일 클래스
const badgeClass = computed(() => {
  if (isAuthenticated.value) {
    return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
  }
  if (!servicesAvailable.value) {
    return 'bg-gray-100 text-gray-600 dark:bg-gray-900/20 dark:text-gray-400'
  }
  return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300'
})

// 배지 텍스트
const badgeText = computed(() => {
  if (isAuthenticated.value) return 'Google 연결됨'
  if (!servicesAvailable.value) return 'Google 서비스 없음'
  return 'Google 연결 필요'
})

// 연결하기
const connect = () => {
  startAuth()
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>