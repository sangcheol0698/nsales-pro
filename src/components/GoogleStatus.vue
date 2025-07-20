<template>
  <div class="google-status-wrapper">
    <!-- Google 연동 상태 카드 -->
    <div class="bg-card border rounded-lg p-4 space-y-4">
      <!-- 헤더 -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
          </div>
          <div>
            <h3 class="font-semibold text-foreground">Google 서비스 연동</h3>
            <p class="text-sm text-muted-foreground">캘린더 및 Gmail 연동 상태</p>
          </div>
        </div>
        
        <!-- 새로고침 버튼 -->
        <button
          @click="refresh"
          :disabled="isLoading"
          class="p-2 rounded-lg hover:bg-accent transition-colors"
          :class="{ 'animate-spin': isLoading }"
        >
          <svg class="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <!-- 상태 표시 -->
      <div class="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
        <div class="flex items-center gap-3">
          <div class="text-2xl" v-html="statusIcon"></div>
          <div>
            <div class="font-medium" :class="statusColor">{{ statusText }}</div>
            <div v-if="lastChecked" class="text-xs text-muted-foreground">
              마지막 확인: {{ formatLastChecked }}
            </div>
          </div>
        </div>
        
        <!-- 액션 버튼 -->
        <div class="flex gap-2">
          <button
            v-if="!isAuthenticated && servicesAvailable"
            @click="connect"
            :disabled="isLoading"
            class="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>{{ isLoading ? '연결 중...' : '연결하기' }}</span>
          </button>
          
          <button
            v-if="isAuthenticated"
            @click="disconnect"
            class="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>연결 해제</span>
          </button>
        </div>
      </div>

      <!-- 에러 메시지 -->
      <div v-if="error" class="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
        <div class="flex items-start gap-2">
          <svg class="w-4 h-4 text-destructive mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <div>
            <div class="font-medium text-destructive">연결 오류</div>
            <div class="text-sm text-destructive/80">{{ error }}</div>
          </div>
        </div>
      </div>

      <!-- 사용 가능한 기능 -->
      <div v-if="isAuthenticated" class="space-y-3">
        <div class="text-sm font-medium text-foreground">사용 가능한 기능</div>
        <div class="grid grid-cols-2 gap-3">
          <div class="flex items-center gap-2 p-2 bg-green-50 dark:bg-green-950/20 rounded-lg">
            <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
            </svg>
            <span class="text-sm text-green-700 dark:text-green-300">캘린더</span>
          </div>
          <div class="flex items-center gap-2 p-2 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
            <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
            </svg>
            <span class="text-sm text-blue-700 dark:text-blue-300">Gmail</span>
          </div>
        </div>
      </div>

      <!-- AI 사용 예시 -->
      <div v-if="isAuthenticated" class="space-y-3">
        <div class="text-sm font-medium text-foreground">AI 명령어 예시</div>
        <div class="space-y-2">
          <div class="p-2 bg-muted/50 rounded text-xs font-mono">
            "오늘 일정 확인해줘"
          </div>
          <div class="p-2 bg-muted/50 rounded text-xs font-mono">
            "내일 오후 3시에 팀 미팅 일정 잡아줘"
          </div>
          <div class="p-2 bg-muted/50 rounded text-xs font-mono">
            "김과장님께 회의 일정 메일 보내줘"
          </div>
        </div>
      </div>
    </div>
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
  error,
  lastChecked,
  statusColor,
  statusText,
  statusIcon,
  checkAuthStatus,
  startAuth,
  disconnect
} = useGoogleAuth()

// 마지막 확인 시간 포맷팅
const formatLastChecked = computed(() => {
  if (!lastChecked.value) return ''
  
  const now = new Date()
  const diff = now.getTime() - lastChecked.value.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days}일 전`
  if (hours > 0) return `${hours}시간 전`
  if (minutes > 0) return `${minutes}분 전`
  return '방금 전'
})

// 새로고침
const refresh = () => {
  checkAuthStatus()
}

// 연결하기
const connect = () => {
  startAuth()
}
</script>

<style scoped>
.google-status-wrapper {
  width: 100%;
}
</style>