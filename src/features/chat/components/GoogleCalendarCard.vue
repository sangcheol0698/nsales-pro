<template>
  <div class="space-y-3">
    <div class="flex items-center gap-2 text-sm font-medium text-primary">
      <Calendar class="h-4 w-4" />
      <span>{{ title }}</span>
      <Badge v-if="events.length > 0" variant="secondary" class="text-xs">
        {{ events.length }}개
      </Badge>
    </div>
    
    <div v-if="events.length === 0" class="text-center py-6 text-muted-foreground">
      <CalendarX class="h-8 w-8 mx-auto mb-2 opacity-50" />
      <p class="text-sm">일정이 없습니다</p>
    </div>
    
    <div v-else class="space-y-2">
      <div
        v-for="event in events"
        :key="event.id"
        class="group relative bg-background border border-border/60 rounded-lg p-3 hover:border-border transition-all duration-200 hover:shadow-sm"
      >
        <!-- 이벤트 상단 정보 -->
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <h4 class="font-medium text-sm text-foreground truncate group-hover:text-primary transition-colors">
              {{ event.summary || '제목 없음' }}
            </h4>
            
            <!-- 시간 정보 -->
            <div class="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
              <Clock class="h-3 w-3 flex-shrink-0" />
              <span>{{ formatEventTime(event) }}</span>
            </div>
            
            <!-- 위치 정보 -->
            <div v-if="event.location" class="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
              <MapPin class="h-3 w-3 flex-shrink-0" />
              <span class="truncate">{{ event.location }}</span>
            </div>
          </div>
          
          <!-- 이벤트 상태 표시 -->
          <div class="flex items-center gap-1">
            <div 
              class="h-2 w-2 rounded-full flex-shrink-0"
              :class="getEventStatusColor(event)"
            />
            <Badge
              v-if="isToday(event)"
              variant="default"
              class="text-[10px] px-1.5 py-0.5 h-auto"
            >
              오늘
            </Badge>
          </div>
        </div>
        
        <!-- 설명 -->
        <div v-if="event.description" class="mt-2 text-xs text-muted-foreground line-clamp-2">
          {{ event.description }}
        </div>
        
        <!-- 참석자 정보 -->
        <div v-if="event.attendees && event.attendees.length > 0" class="mt-2 flex items-center gap-1">
          <Users class="h-3 w-3 text-muted-foreground" />
          <span class="text-xs text-muted-foreground">
            {{ event.attendees.length }}명 참석
          </span>
        </div>
        
        <!-- 액션 버튼 (호버 시 표시) -->
        <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            v-if="event.htmlLink"
            variant="ghost"
            size="sm"
            class="h-6 w-6 p-0"
            @click="openEvent(event.htmlLink)"
            title="Google 캘린더에서 열기"
          >
            <ExternalLink class="h-3 w-3" />
          </Button>
        </div>
      </div>
    </div>
    
    <!-- 더보기 버튼 -->
    <div v-if="events.length > 5" class="text-center pt-2">
      <Button
        variant="outline"
        size="sm"
        class="text-xs"
        @click="showAllEvents = !showAllEvents"
      >
        {{ showAllEvents ? '접기' : `${events.length - 5}개 더보기` }}
        <ChevronDown class="h-3 w-3 ml-1" :class="{ 'rotate-180': showAllEvents }" />
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Calendar, CalendarX, Clock, MapPin, Users, ExternalLink, ChevronDown } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface CalendarEvent {
  id: string
  summary?: string
  description?: string
  start?: string
  end?: string
  location?: string
  attendees?: Array<{ email: string; displayName?: string }>
  htmlLink?: string
  status?: string
}

interface Props {
  title: string
  events: CalendarEvent[]
}

const props = defineProps<Props>()
const showAllEvents = ref(false)

const displayEvents = computed(() => {
  if (showAllEvents.value || props.events.length <= 5) {
    return props.events
  }
  return props.events.slice(0, 5)
})

const formatEventTime = (event: CalendarEvent) => {
  if (!event.start) return '시간 미정'
  
  try {
    const startDate = new Date(event.start)
    const endDate = event.end ? new Date(event.end) : null
    
    // 한국 시간으로 변환
    const formatter = new Intl.DateTimeFormat('ko-KR', {
      timeZone: 'Asia/Seoul',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
    
    const startStr = formatter.format(startDate)
    
    if (endDate) {
      // 같은 날인지 확인
      const isSameDay = startDate.toDateString() === endDate.toDateString()
      
      if (isSameDay) {
        // 같은 날이면 시간만 표시
        const endTime = new Intl.DateTimeFormat('ko-KR', {
          timeZone: 'Asia/Seoul',
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        }).format(endDate)
        
        return `${startStr} - ${endTime}`
      } else {
        // 다른 날이면 전체 날짜 표시
        const endStr = formatter.format(endDate)
        return `${startStr} - ${endStr}`
      }
    }
    
    return startStr
  } catch (error) {
    console.warn('Failed to format event time:', error)
    return event.start
  }
}

const isToday = (event: CalendarEvent) => {
  if (!event.start) return false
  
  try {
    const eventDate = new Date(event.start)
    const today = new Date()
    
    // 한국 시간 기준으로 오늘인지 확인
    const eventDateKST = new Date(eventDate.getTime() + (9 * 60 * 60 * 1000))
    const todayKST = new Date(today.getTime() + (9 * 60 * 60 * 1000))
    
    return eventDateKST.toDateString() === todayKST.toDateString()
  } catch {
    return false
  }
}

const getEventStatusColor = (event: CalendarEvent) => {
  const now = new Date()
  
  if (!event.start) return 'bg-gray-400'
  
  try {
    const startTime = new Date(event.start)
    const endTime = event.end ? new Date(event.end) : new Date(startTime.getTime() + 60 * 60 * 1000) // 1시간 기본
    
    if (now >= startTime && now <= endTime) {
      return 'bg-green-500' // 진행 중
    } else if (now < startTime) {
      return 'bg-blue-500' // 예정
    } else {
      return 'bg-gray-400' // 완료
    }
  } catch {
    return 'bg-gray-400'
  }
}

const openEvent = (htmlLink: string) => {
  window.open(htmlLink, '_blank', 'noopener,noreferrer')
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