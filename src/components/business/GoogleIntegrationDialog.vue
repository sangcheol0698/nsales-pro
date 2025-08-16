<template>
  <div class="space-y-4">
    <!-- 상태 카드 -->
    <div class="bg-card border rounded-xl p-4">
      <div class="flex items-start gap-3">
        <div
          class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white text-lg">
          {{ statusIcon }}
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="text-base font-semibold text-foreground mb-1">Google 연동 상태</h3>
          <p class="text-sm" :class="statusColor">{{ statusText }}</p>
          <div class="mt-2 text-xs text-muted-foreground flex items-center gap-2">
            <span>서비스: </span>
            <span :class="servicesAvailable ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ servicesAvailable ? '사용 가능' : '사용 불가' }}
            </span>
            <span class="opacity-50">•</span>
            <span>마지막 확인: {{ lastChecked ? formatDateTime(lastChecked) : '—' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 액션 -->
    <div class="flex flex-wrap items-center gap-2">
      <Button
        v-if="!isAuthenticated"
        :disabled="isLoading || !servicesAvailable"
        @click="startAuth()"
      >
        <Plug2 class="h-4 w-4 mr-2" />
        Google 계정 연결
      </Button>

      <Button
        v-else
        variant="destructive"
        :disabled="isLoading"
        @click="disconnect()"
      >
        연결 해제
      </Button>

      <Button
        variant="outline"
        :disabled="isLoading"
        @click="checkAuthStatus()"
      >
        상태 새로고침
      </Button>
    </div>

    <!-- 도움말 섹션 -->
    <div class="bg-muted/40 border rounded-xl p-4 space-y-2 text-sm">
      <p class="text-foreground font-medium">도움말</p>
      <ul class="list-disc pl-5 space-y-1 text-muted-foreground">
        <li>첫 연결 시 Google 로그인 팝업이 열립니다. 팝업이 차단되지 않았는지 확인하세요.</li>
        <li>인증이 완료되면 이 창이 자동으로 상태를 갱신합니다.</li>
        <li>문제가 지속되면 브라우저 캐시/쿠키를 지우고 다시 시도하세요.</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Plug2 } from 'lucide-vue-next';
import { useGoogleAuth } from '@/core/composables/useGoogleAuth';

const {
  isAuthenticated,
  isLoading,
  servicesAvailable,
  lastChecked,
  statusColor,
  statusText,
  statusIcon,
  checkAuthStatus,
  startAuth,
  disconnect,
} = useGoogleAuth();

const formatDateTime = (d: Date) => {
  const date = new Date(d);
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  }).format(date);
};
</script>

