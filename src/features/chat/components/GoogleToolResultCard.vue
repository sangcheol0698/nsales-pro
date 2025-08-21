<template>
  <div class="space-y-3">
    <!-- 캘린더 이벤트 결과 -->
    <div v-if="isCalendarTool" class="space-y-3">
      <div class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Calendar class="h-4 w-4 text-primary" />
        <span>검색된 일정</span>
        <div class="h-px bg-border flex-1"></div>
        <span class="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
          {{ calendarEvents.length }}개
        </span>
      </div>
      
      <div class="grid gap-3">
        <div
          v-for="event in calendarEvents.slice(0, 5)"
          :key="event.id"
          class="group relative overflow-hidden rounded-xl border border-border/50 bg-card/50 p-4 backdrop-blur-sm transition-all duration-200 hover:border-border hover:bg-card/80 hover:shadow-md"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-sm text-card-foreground truncate group-hover:text-foreground transition-colors">
                {{ event.summary || '제목 없음' }}
              </h4>
              <p class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                <span class="inline-flex h-1.5 w-1.5 rounded-full bg-primary"></span>
                {{ formatEventDate(event) }}
              </p>
              <p v-if="event.location" class="text-xs text-muted-foreground mt-1 opacity-75">
                📍 {{ event.location }}
              </p>
            </div>
            <div class="flex items-center gap-1">
              <div class="h-8 w-1 rounded-full bg-gradient-to-b from-primary to-primary/80"></div>
              <span class="text-[10px] font-medium text-primary bg-primary/10 px-2 py-1 rounded-full">
                EVENT
              </span>
            </div>
          </div>
          
          <!-- 호버시 상세 정보 -->
          <div class="mt-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div v-if="event.description" class="text-xs text-muted-foreground line-clamp-2">
              {{ event.description }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 메일 결과 -->
    <div v-else-if="isEmailTool" class="space-y-3">
      <div class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Mail class="h-4 w-4 text-emerald-500" />
        <span>검색된 메일</span>
        <div class="h-px bg-border flex-1"></div>
        <span class="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full dark:bg-emerald-950/50 dark:text-emerald-300">
          {{ emails.length }}개
        </span>
      </div>
      
      <div class="grid gap-3">
        <div
          v-for="email in emails.slice(0, 5)"
          :key="email.id"
          class="group relative overflow-hidden rounded-xl border border-border/50 bg-card/50 p-4 backdrop-blur-sm transition-all duration-200 hover:border-border hover:bg-card/80 hover:shadow-md"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-sm text-card-foreground truncate group-hover:text-foreground transition-colors">
                {{ email.subject || '제목 없음' }}
              </h4>
              <p class="text-xs text-muted-foreground mt-1">
                <span class="font-medium">{{ email.from }}</span>
              </p>
              <p class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                <span class="inline-flex h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                {{ formatEmailDate(email.date) }}
              </p>
            </div>
            <div class="flex items-center gap-1">
              <div class="h-8 w-1 rounded-full bg-gradient-to-b from-emerald-500 to-emerald-400"></div>
              <span class="text-[10px] font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full dark:bg-emerald-950/50 dark:text-emerald-300">
                EMAIL
              </span>
            </div>
          </div>
          
          <!-- 호버시 미리보기 -->
          <div class="mt-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div v-if="email.snippet" class="text-xs text-muted-foreground line-clamp-2">
              {{ email.snippet }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Calendar, Mail } from 'lucide-vue-next'

interface Props {
  toolName?: string
  result?: any
}

const props = defineProps<Props>()

// 디버깅을 위한 로그
console.log('GoogleToolResultCard props:', {
  toolName: props.toolName,
  result: props.result
})

// 캘린더 도구인지 확인
const isCalendarTool = computed(() => {
  const calendarTools = ['get_calendar_events', 'create_calendar_event', 'find_free_time']
  return calendarTools.includes(props.toolName || '')
})

// 이메일 도구인지 확인
const isEmailTool = computed(() => {
  const emailTools = ['get_emails', 'send_email']
  return emailTools.includes(props.toolName || '')
})

// 캘린더 이벤트 목록
const calendarEvents = computed(() => {
  if (!isCalendarTool.value || !props.result) return []
  
  // result가 배열인 경우와 객체인 경우 모두 처리
  if (Array.isArray(props.result)) {
    return props.result
  }
  if (props.result.events && Array.isArray(props.result.events)) {
    return props.result.events
  }
  if (props.result.items && Array.isArray(props.result.items)) {
    return props.result.items
  }
  return []
})

// 이메일 목록
const emails = computed(() => {
  if (!isEmailTool.value || !props.result) return []
  
  // result가 배열인 경우와 객체인 경우 모두 처리
  if (Array.isArray(props.result)) {
    return props.result
  }
  if (props.result.messages && Array.isArray(props.result.messages)) {
    return props.result.messages
  }
  if (props.result.emails && Array.isArray(props.result.emails)) {
    return props.result.emails
  }
  return []
})

// 이벤트 날짜 포맷팅
const formatEventDate = (event: any) => {
  try {
    const start = event.start?.dateTime || event.start?.date
    if (!start) return '시간 정보 없음'
    
    const date = new Date(start)
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const eventDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
    
    const diffDays = Math.floor((eventDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return `오늘 ${date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}`
    } else if (diffDays === 1) {
      return `내일 ${date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}`
    } else if (diffDays === -1) {
      return `어제 ${date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}`
    } else {
      return date.toLocaleDateString('ko-KR', { 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit', 
        minute: '2-digit'
      })
    }
  } catch (error) {
    return '시간 정보 오류'
  }
}

// 이메일 날짜 포맷팅
const formatEmailDate = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      if (diffHours === 0) {
        const diffMinutes = Math.floor(diffMs / (1000 * 60))
        return `${diffMinutes}분 전`
      }
      return `${diffHours}시간 전`
    } else if (diffDays === 1) {
      return '어제'
    } else if (diffDays < 7) {
      return `${diffDays}일 전`
    } else {
      return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
    }
  } catch (error) {
    return '날짜 정보 오류'
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>