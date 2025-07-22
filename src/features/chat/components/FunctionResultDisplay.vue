<template>
  <div class="function-result-container my-4">
    <!-- Function execution status -->
    <div v-if="isExecuting" class="mb-4">
      <div class="flex items-center p-3 rounded-lg bg-blue-500/5 border border-blue-500/20">
        <div class="mr-3">
          <div class="relative">
            <div class="w-6 h-6 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
        <div>
          <p class="text-sm font-medium text-blue-700 dark:text-blue-300">
            {{ functionName }} 실행 중...
          </p>
          <p class="text-xs text-blue-600/80 dark:text-blue-400/80">
            데이터를 가져오고 있습니다
          </p>
        </div>
      </div>
    </div>

    <!-- Function result content -->
    <div v-if="parsedResult" class="space-y-4">
      <!-- Header with function info -->
      <div class="flex items-center justify-between p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
        <div class="flex items-center">
          <div class="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center mr-3">
            <component :is="getFunctionIcon(functionName)" class="w-4 h-4 text-emerald-600" />
          </div>
          <div>
            <p class="text-sm font-medium text-emerald-700 dark:text-emerald-300">
              {{ getFunctionDisplayName(functionName) }}
            </p>
            <p class="text-xs text-emerald-600/80 dark:text-emerald-400/80">
              {{ parsedResult.message }}
            </p>
          </div>
        </div>
        <div class="text-xs text-emerald-600/60 dark:text-emerald-400/60">
          완료
        </div>
      </div>

      <!-- Calendar Events Display -->
      <div v-if="functionName === 'get_calendar_events' && parsedResult.events" class="space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-semibold text-foreground flex items-center">
            <Calendar class="w-4 h-4 mr-2 text-blue-500" />
            일정 목록
            <span class="ml-2 text-xs font-normal text-muted-foreground">
              ({{ parsedResult.events.length }}개)
            </span>
          </h4>
          <div class="text-xs text-muted-foreground">
            이번 달
          </div>
        </div>
        
        <div class="grid gap-3">
          <CalendarEventCard 
            v-for="event in parsedResult.events" 
            :key="event.id" 
            :event="event"
          />
        </div>
      </div>

      <!-- Email Display -->
      <div v-if="functionName === 'get_emails' && parsedResult.emails" class="space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-semibold text-foreground flex items-center">
            <Mail class="w-4 h-4 mr-2 text-emerald-500" />
            이메일 목록
            <span class="ml-2 text-xs font-normal text-muted-foreground">
              ({{ parsedResult.emails.length }}개)
            </span>
          </h4>
          <div class="text-xs text-muted-foreground">
            최근 메일
          </div>
        </div>
        
        <div class="space-y-3">
          <EmailCard 
            v-for="email in parsedResult.emails" 
            :key="email.id" 
            :email="email"
          />
        </div>
      </div>

      <!-- Other Function Results -->
      <div v-if="!parsedResult.events && !parsedResult.emails && parsedResult.data" class="space-y-3">
        <div class="p-4 rounded-lg bg-muted/30 border border-border/50">
          <pre class="text-sm text-foreground/80 whitespace-pre-wrap">{{ JSON.stringify(parsedResult.data, null, 2) }}</pre>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="flex items-center justify-end pt-3 space-x-2 opacity-70 hover:opacity-100 transition-opacity duration-300">
        <button class="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground border border-border/50 hover:border-border transition-all duration-200">
          <RefreshCw class="w-3 h-3 mr-1" />
          새로고침
        </button>
        <button class="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground border border-border/50 hover:border-border transition-all duration-200">
          <ExternalLink class="w-3 h-3 mr-1" />
          자세히 보기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Calendar, Mail, Clock, Users, RefreshCw, ExternalLink } from 'lucide-vue-next'
import CalendarEventCard from './CalendarEventCard.vue'
import EmailCard from './EmailCard.vue'

interface Props {
  functionName: string
  result?: string
  isExecuting?: boolean
}

const props = defineProps<Props>()

const parsedResult = computed(() => {
  if (!props.result) return null
  
  try {
    return JSON.parse(props.result)
  } catch (e) {
    // If it's not JSON, treat as plain text
    return { message: props.result }
  }
})

const getFunctionIcon = (functionName: string) => {
  const iconMap = {
    'get_calendar_events': Calendar,
    'create_calendar_event': Calendar,
    'update_calendar_event': Calendar,
    'delete_calendar_event': Calendar,
    'get_emails': Mail,
    'send_email': Mail,
    'find_free_time': Clock,
  } as Record<string, any>
  
  return iconMap[functionName] || Calendar
}

const getFunctionDisplayName = (functionName: string) => {
  const displayNames = {
    'get_calendar_events': '캘린더 일정 조회',
    'create_calendar_event': '일정 생성',
    'update_calendar_event': '일정 수정',
    'delete_calendar_event': '일정 삭제',
    'get_emails': '이메일 조회',
    'send_email': '이메일 전송',
    'find_free_time': '빈 시간 찾기',
  } as Record<string, string>
  
  return displayNames[functionName] || functionName
}
</script>

<style scoped>
.function-result-container {
  max-width: 100%;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}
</style>