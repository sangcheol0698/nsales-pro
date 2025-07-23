<template>
  <div class="space-y-4">
    <!-- 제목 섹션 -->
    <div class="flex items-center gap-3 text-sm font-medium">
      <div class="relative">
        <Calendar class="h-5 w-5 text-blue-500" />
        <div class="absolute -inset-1 bg-blue-500/20 rounded-full animate-pulse"></div>
      </div>
      <span class="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent font-semibold text-gradient">
        {{ title }}
      </span>
      <div class="h-px bg-gradient-to-r from-blue-500/50 to-transparent flex-1"></div>
      <Badge v-if="events.length > 0" class="bg-blue-50 text-blue-700 border-blue-200 animate-bounce-gentle">
        {{ events.length }}개
      </Badge>
    </div>
    
    <!-- 빈 상태 -->
    <div v-if="events.length === 0" class="text-center py-8">
      <div class="relative">
        <CalendarX class="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
        <div class="absolute inset-0 bg-gradient-to-b from-blue-500/10 to-transparent rounded-full animate-pulse"></div>
      </div>
      <p class="text-sm text-muted-foreground">일정이 없습니다</p>
    </div>
    
    <!-- Magic UI Animated List -->
    <AnimatedList
      v-else
      :items="displayEvents"
      :delay="150"
      class="space-y-3"
    >
      <template #default="{ item: event, index }">
        <MagicCard
          class="group relative overflow-hidden bg-gradient-to-br from-background/80 to-background/40 backdrop-blur-sm transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10"
          :gradient-color="'#3b82f6'"
          :gradient-opacity="0.1"
        >
          <!-- 카드 콘텐츠 -->
          <div class="relative z-10">
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <!-- 이벤트 제목 -->
                <h4 class="font-semibold text-sm text-foreground truncate group-hover:text-blue-600 transition-colors duration-300">
                  {{ event.summary || '제목 없음' }}
                </h4>
                
                <!-- 시간 정보 -->
                <div class="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                  <div class="flex items-center gap-1">
                    <Clock class="h-3 w-3 flex-shrink-0" />
                    <span>{{ formatEventTime(event) }}</span>
                  </div>
                  
                  <!-- 상태 인디케이터 -->
                  <div class="flex items-center gap-1">
                    <div 
                      class="h-2 w-2 rounded-full animate-pulse"
                      :class="getEventStatusColor(event)"
                    />
                    <span class="text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-600">
                      {{ getEventStatus(event) }}
                    </span>
                  </div>
                </div>
                
                <!-- 위치 정보 -->
                <div v-if="event.location" class="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                  <MapPin class="h-3 w-3 flex-shrink-0" />
                  <span class="truncate">{{ event.location }}</span>
                </div>
              </div>
              
              <!-- 우측 액션 영역 -->
              <div class="flex flex-col items-end gap-2">
                <!-- 오늘 배지 -->
                <Badge
                  v-if="isToday(event)"
                  class="text-[10px] px-2 py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white border-0 shadow-lg animate-pulse"
                >
                  오늘
                </Badge>
                
                <!-- 액션 버튼 -->
                <div class="opacity-0 group-hover:opacity-100 transition-all duration-300 transform group-hover:scale-105">
                  <ShimmerButton
                    v-if="event.htmlLink"
                    @click="openEvent(event.htmlLink)"
                    class="h-8 w-8 p-0"
                    :shimmer-color="'#3b82f6'"
                    :background="'linear-gradient(45deg, #3b82f6, #8b5cf6)'"
                    border-radius="50%"
                    title="Google 캘린더에서 열기"
                  >
                    <ExternalLink class="h-3 w-3" />
                  </ShimmerButton>
                </div>
              </div>
            </div>
            
            <!-- 설명 -->
            <div 
              v-if="event.description" 
              class="mt-3 text-xs text-muted-foreground line-clamp-2 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0"
            >
              {{ event.description }}
            </div>
            
            <!-- 참석자 정보 -->
            <div 
              v-if="event.attendees && event.attendees.length > 0" 
              class="mt-3 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0"
            >
              <div class="flex -space-x-1">
                <div
                  v-for="(attendee, idx) in event.attendees.slice(0, 3)"
                  :key="idx"
                  class="h-5 w-5 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-[8px] font-bold text-white border border-background animate-bounce-subtle"
                  :style="{ animationDelay: `${idx * 100}ms` }"
                >
                  {{ getInitials(attendee.displayName || attendee.email) }}
                </div>
              </div>
              <span class="text-xs text-muted-foreground">
                {{ event.attendees.length }}명 참석
              </span>
            </div>
          </div>
        </MagicCard>
      </template>
    </AnimatedList>
    
    <!-- 더보기 버튼 -->
    <div v-if="events.length > 5" class="text-center pt-4">
      <ShimmerButton
        @click="showAllEvents = !showAllEvents"
        class="text-xs px-6 py-3"
        :shimmer-color="'#3b82f6'"
        :background="'linear-gradient(45deg, #3b82f6, #8b5cf6)'"
      >
        {{ showAllEvents ? '접기' : `${events.length - 5}개 더보기` }}
        <ChevronDown class="h-3 w-3 ml-2 transition-transform duration-300" :class="{ 'rotate-180': showAllEvents }" />
      </ShimmerButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Calendar, CalendarX, Clock, MapPin, ExternalLink, ChevronDown } from 'lucide-vue-next'
import { Badge } from '@/core/components/ui/badge'
import AnimatedList from '@/core/components/ui/magic/animated-list.vue'
import ShimmerButton from '@/core/components/ui/magic/shimmer-button.vue'
import MagicCard from '@/core/components/ui/magic/magic-card.vue'

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
      const isSameDay = startDate.toDateString() === endDate.toDateString()
      
      if (isSameDay) {
        const endTime = new Intl.DateTimeFormat('ko-KR', {
          timeZone: 'Asia/Seoul',
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        }).format(endDate)
        
        return `${startStr} - ${endTime}`
      } else {
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
    
    const eventDateKST = new Date(eventDate.getTime() + (9 * 60 * 60 * 1000))
    const todayKST = new Date(today.getTime() + (9 * 60 * 60 * 1000))
    
    return eventDateKST.toDateString() === todayKST.toDateString()
  } catch {
    return false
  }
}

const getEventStatus = (event: CalendarEvent) => {
  const now = new Date()
  
  if (!event.start) return '미정'
  
  try {
    const startTime = new Date(event.start)
    const endTime = event.end ? new Date(event.end) : new Date(startTime.getTime() + 60 * 60 * 1000)
    
    if (now >= startTime && now <= endTime) {
      return '진행중'
    } else if (now < startTime) {
      return '예정'
    } else {
      return '완료'
    }
  } catch {
    return '미정'
  }
}

const getEventStatusColor = (event: CalendarEvent) => {
  const status = getEventStatus(event)
  
  switch (status) {
    case '진행중':
      return 'bg-green-500'
    case '예정':
      return 'bg-blue-500'
    case '완료':
      return 'bg-gray-400'
    default:
      return 'bg-gray-400'
  }
}

const getInitials = (name?: string) => {
  if (!name) return '?'
  
  if (/[가-힣]/.test(name)) {
    return name.charAt(0)
  } else {
    return name.slice(0, 2).toUpperCase()
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

.text-gradient {
  background-size: 200% 200%;
  animation: gradient 3s ease-in-out infinite;
}

@keyframes gradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes bounce-gentle {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

@keyframes bounce-subtle {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-1px) scale(1.05);
  }
}

.animate-bounce-gentle {
  animation: bounce-gentle 2s ease-in-out infinite;
}

.animate-bounce-subtle {
  animation: bounce-subtle 1.5s ease-in-out infinite;
}
</style>