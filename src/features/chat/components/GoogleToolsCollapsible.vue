<template>
  <div class="space-y-3">
    <!-- Gmail 섹션 -->
    <div v-if="gmailResult" class="group">
      <Collapsible v-model:open="isGmailOpen">
        <CollapsibleTrigger class="w-full">
          <div class="flex items-center justify-between p-3 rounded-lg border border-emerald-200/50 bg-gradient-to-r from-emerald-50/50 to-blue-50/50 hover:from-emerald-100/70 hover:to-blue-100/70 transition-all duration-300 hover:shadow-md hover:shadow-emerald-500/10 group-hover:border-emerald-300/70">
            <div class="flex items-center gap-3">
              <div class="relative">
                <Mail class="h-5 w-5 text-emerald-600" />
                <div class="absolute -inset-1 bg-emerald-500/20 rounded-full animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div class="text-left">
                <h3 class="font-semibold text-sm text-emerald-800 bg-gradient-to-r from-emerald-700 to-blue-700 bg-clip-text text-transparent">
                  {{ gmailResult.title }}
                </h3>
                <p class="text-xs text-emerald-600/70">
                  {{ Array.isArray(gmailResult.data) ? `${gmailResult.data.length}개의 메일` : '메일 정보' }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <Badge class="bg-emerald-100 text-emerald-700 border-emerald-200 text-xs px-2 py-1">
                새로운
              </Badge>
              <ChevronDown 
                class="h-4 w-4 text-emerald-600 transition-transform duration-300 group-hover:text-emerald-700"
                :class="{ 'rotate-180': isGmailOpen }"
              />
            </div>
          </div>
        </CollapsibleTrigger>
        
        <CollapsibleContent>
          <div class="mt-3 animate-in slide-in-from-top-2 fade-in duration-300">
            <EnhancedGmailCard
              :title="gmailResult.title"
              :emails="gmailResult.data as EmailMessage[]"
            />
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>

    <!-- 캘린더 섹션 -->
    <div v-if="calendarResult" class="group">
      <Collapsible v-model:open="isCalendarOpen">
        <CollapsibleTrigger class="w-full">
          <div class="flex items-center justify-between p-3 rounded-lg border border-blue-200/50 bg-gradient-to-r from-blue-50/50 to-purple-50/50 hover:from-blue-100/70 hover:to-purple-100/70 transition-all duration-300 hover:shadow-md hover:shadow-blue-500/10 group-hover:border-blue-300/70">
            <div class="flex items-center gap-3">
              <div class="relative">
                <Calendar class="h-5 w-5 text-blue-600" />
                <div class="absolute -inset-1 bg-blue-500/20 rounded-full animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
              <div class="text-left">
                <h3 class="font-semibold text-sm text-blue-800 bg-gradient-to-r from-blue-700 to-purple-700 bg-clip-text text-transparent">
                  {{ calendarResult.title }}
                </h3>
                <p class="text-xs text-blue-600/70">
                  {{ Array.isArray(calendarResult.data) ? `${calendarResult.data.length}개의 일정` : '일정 정보' }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <Badge class="bg-blue-100 text-blue-700 border-blue-200 text-xs px-2 py-1">
                {{ isToday() ? '오늘' : '예정' }}
              </Badge>
              <ChevronDown 
                class="h-4 w-4 text-blue-600 transition-transform duration-300 group-hover:text-blue-700"
                :class="{ 'rotate-180': isCalendarOpen }"
              />
            </div>
          </div>
        </CollapsibleTrigger>
        
        <CollapsibleContent>
          <div class="mt-3 animate-in slide-in-from-top-2 fade-in duration-300">
            <EnhancedGoogleCalendarCard
              :title="calendarResult.title"
              :events="calendarResult.data as CalendarEvent[]"
            />
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Calendar, Mail, ChevronDown } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import EnhancedGmailCard from './enhanced/EnhancedGmailCard.vue'
import EnhancedGoogleCalendarCard from './enhanced/EnhancedGoogleCalendarCard.vue'
import type { CalendarEvent, EmailMessage } from '../utils/googleToolsParser'

interface GoogleToolResult {
  type: 'calendar' | 'gmail' | 'text'
  title: string
  data?: CalendarEvent[] | EmailMessage[]
  rawContent?: string
}

interface Props {
  googleToolResult: GoogleToolResult | null
}

const props = defineProps<Props>()

// 각 섹션의 열림/닫힘 상태
const isGmailOpen = ref(false)
const isCalendarOpen = ref(false)

// Gmail과 Calendar 결과 분리
const gmailResult = computed(() => {
  return props.googleToolResult?.type === 'gmail' ? props.googleToolResult : null
})

const calendarResult = computed(() => {
  return props.googleToolResult?.type === 'calendar' ? props.googleToolResult : null
})

const isToday = () => {
  const today = new Date()
  return today.getDay() !== 0 && today.getDay() !== 6 // 주말이 아닌 경우 '오늘'로 표시
}
</script>

<style scoped>
.animate-in {
  animation-fill-mode: both;
}

.slide-in-from-top-2 {
  animation: slide-in-from-top-2 0.3s ease-out;
}

.fade-in {
  animation: fade-in 0.3s ease-out;
}

@keyframes slide-in-from-top-2 {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 그라데이션 텍스트 애니메이션 */
.text-transparent {
  background-size: 200% 200%;
  animation: gradient-flow 3s ease-in-out infinite;
}

@keyframes gradient-flow {
  0%, 100% { 
    background-position: 0% 50%; 
  }
  50% { 
    background-position: 100% 50%; 
  }
}
</style>