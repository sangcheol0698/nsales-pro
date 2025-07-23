<template>
  <div class="space-y-4">
    <!-- 제목 섹션 -->
    <div class="flex items-center gap-3 text-sm font-medium">
      <div class="relative">
        <Mail class="h-5 w-5 text-emerald-500" />
        <div class="absolute -inset-1 bg-emerald-500/20 rounded-full animate-pulse"></div>
      </div>
      <span class="bg-gradient-to-r from-emerald-600 via-blue-600 to-emerald-800 bg-clip-text text-transparent font-semibold text-gradient">
        {{ title }}
      </span>
      <div class="h-px bg-gradient-to-r from-emerald-500/50 to-transparent flex-1"></div>
      <Badge v-if="emails.length > 0" class="bg-emerald-50 text-emerald-700 border-emerald-200 animate-bounce-gentle">
        {{ emails.length }}개
      </Badge>
    </div>
    
    <!-- 빈 상태 -->
    <div v-if="emails.length === 0" class="text-center py-8">
      <div class="relative">
        <MailX class="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
        <div class="absolute inset-0 bg-gradient-to-b from-emerald-500/10 to-transparent rounded-full animate-pulse"></div>
      </div>
      <p class="text-sm text-muted-foreground">메일이 없습니다</p>
    </div>
    
    <!-- Magic UI Animated List -->
    <AnimatedList
      v-else
      :items="displayEmails"
      :delay="150"
      class="space-y-3"
    >
      <template #default="{ item: email, index }">
        <MagicCard
          class="group relative overflow-hidden bg-gradient-to-br from-background/80 to-background/40 backdrop-blur-sm transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/10"
          :gradient-color="'#10b981'"
          :gradient-opacity="0.1"
        >
          <!-- 카드 콘텐츠 -->
          <div class="relative z-10">
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <!-- 발신자 정보 -->
                <div class="flex items-center gap-3 mb-2">
                  <div class="relative">
                    <div class="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center flex-shrink-0 shadow-sm">
                      <span class="text-xs font-bold text-white">
                        {{ getInitials(email.from) }}
                      </span>
                    </div>
                    <!-- 읽음 상태 인디케이터 -->
                    <div 
                      class="absolute -bottom-1 -right-1 h-3 w-3 rounded-full border-2 border-background"
                      :class="email.isRead ? 'bg-gray-400' : 'bg-emerald-500 animate-pulse'"
                    />
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-foreground truncate group-hover:text-emerald-600 transition-colors">
                      {{ getDisplayName(email.from) }}
                    </p>
                    <p class="text-xs text-muted-foreground truncate">
                      {{ getEmailAddress(email.from) }}
                    </p>
                  </div>
                </div>
                
                <!-- 제목 -->
                <h4 class="font-semibold text-sm text-foreground line-clamp-1 group-hover:text-emerald-600 transition-colors mb-2">
                  {{ email.subject || '제목 없음' }}
                </h4>
                
                <!-- 메타 정보 -->
                <div class="flex items-center gap-3 text-xs text-muted-foreground">
                  <div class="flex items-center gap-1">
                    <Clock class="h-3 w-3 flex-shrink-0" />
                    <span>{{ formatEmailTime(email.date) }}</span>
                  </div>
                  
                  <!-- 첨부파일 -->
                  <div v-if="email.hasAttachments" class="flex items-center gap-1">
                    <Paperclip class="h-3 w-3" />
                    <span>첨부</span>
                  </div>
                  
                  <!-- 중요 표시 -->
                  <Star 
                    v-if="email.isImportant"
                    class="h-3 w-3 text-amber-500 fill-amber-500 animate-pulse"
                  />
                </div>
              </div>
              
              <!-- 우측 액션 영역 -->
              <div class="flex flex-col items-end gap-2">
                <!-- 오늘 배지 -->
                <Badge
                  v-if="isToday(email.date)"
                  class="text-[10px] px-2 py-1 bg-gradient-to-r from-emerald-500 to-blue-500 text-white border-0 shadow-lg animate-pulse"
                >
                  오늘
                </Badge>
                
                <!-- 액션 버튼들 -->
                <div class="flex items-center gap-2 opacity-60 group-hover:opacity-100 transition-all duration-300">
                  <button
                    v-if="email.webLink"
                    @click="openEmail(email.webLink)"
                    class="flex items-center gap-1 px-3 py-1.5 text-xs bg-gradient-to-r from-emerald-50 to-blue-50 hover:from-emerald-100 hover:to-blue-100 text-emerald-700 hover:text-emerald-800 rounded-full border border-emerald-200 hover:border-emerald-300 transition-all duration-200 hover:scale-105 hover:shadow-sm"
                    title="Gmail에서 열기"
                  >
                    <ExternalLink class="h-3 w-3" />
                    <span>열기</span>
                  </button>
                  
                  <button
                    @click="toggleEmailExpanded(email.id)"
                    class="flex items-center gap-1 px-3 py-1.5 text-xs bg-gradient-to-r from-blue-50 to-emerald-50 hover:from-blue-100 hover:to-emerald-100 text-blue-700 hover:text-blue-800 rounded-full border border-blue-200 hover:border-blue-300 transition-all duration-200 hover:scale-105 hover:shadow-sm"
                    :title="expandedEmails.has(email.id) ? '접기' : '자세히 보기'"
                  >
                    <ChevronDown class="h-3 w-3 transition-transform duration-300" :class="{ 'rotate-180': expandedEmails.has(email.id) }" />
                    <span>{{ expandedEmails.has(email.id) ? '접기' : '더보기' }}</span>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 미리보기 내용 -->
            <div 
              v-if="email.snippet" 
              class="mt-3 text-xs text-muted-foreground line-clamp-2 opacity-70 group-hover:opacity-100 transition-all duration-300"
            >
              {{ email.snippet }}
            </div>
            
            <!-- 라벨 표시 -->
            <AnimatedList
              v-if="email.labels && email.labels.length > 0"
              :items="email.labels.slice(0, 3).map((label, idx) => ({ id: idx, label }))"
              :delay="50"
              class="mt-3 flex flex-wrap gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0"
            >
              <template #default="{ item }">
                <Badge class="text-[10px] px-2 py-1 bg-gradient-to-r from-emerald-100 to-blue-100 text-emerald-700 border-emerald-200">
                  {{ formatLabel(item.label) }}
                </Badge>
              </template>
            </AnimatedList>
            
            <span v-if="email.labels && email.labels.length > 3" class="text-[10px] text-muted-foreground ml-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              +{{ email.labels.length - 3 }}
            </span>
            
            <!-- 확장된 내용 -->
            <div 
              v-if="expandedEmails.has(email.id)" 
              class="mt-4 pt-4 border-t border-gradient-to-r from-emerald-200/50 to-blue-200/50 animate-in fade-in slide-in-from-top-2 duration-300"
            >
              <!-- 수신자 정보 -->
              <div v-if="email.to" class="text-xs text-muted-foreground mb-3 p-3 bg-gradient-to-r from-emerald-50/50 to-blue-50/50 rounded-lg border border-emerald-200/30">
                <span class="font-semibold text-emerald-700">받는 사람:</span>
                <span class="ml-2">{{ email.to }}</span>
              </div>
              
              <!-- 전체 내용 -->
              <div 
                v-if="email.body" 
                class="text-xs text-foreground whitespace-pre-wrap max-h-40 overflow-y-auto p-3 bg-gradient-to-br from-emerald-50/30 to-blue-50/30 rounded-lg border border-emerald-200/50 backdrop-blur-sm"
              >
                {{ email.body }}
              </div>
            </div>
          </div>
        </MagicCard>
      </template>
    </AnimatedList>
    
    <!-- 더보기 버튼 -->
    <div v-if="emails.length > 5" class="text-center pt-4">
      <ShimmerButton
        @click="showAllEmails = !showAllEmails"
        class="text-xs px-6 py-3"
        :shimmer-color="'#10b981'"
        :background="'linear-gradient(45deg, #10b981, #3b82f6)'"
      >
        {{ showAllEmails ? '접기' : `${emails.length - 5}개 더보기` }}
        <ChevronDown class="h-3 w-3 ml-2 transition-transform duration-300" :class="{ 'rotate-180': showAllEmails }" />
      </ShimmerButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Mail, MailX, Clock, Paperclip, Star, ExternalLink, ChevronDown } from 'lucide-vue-next'
import { Badge } from '@/core/components/ui/badge'
import AnimatedList from '@/core/components/ui/magic/animated-list.vue'
import ShimmerButton from '@/core/components/ui/magic/shimmer-button.vue'
import MagicCard from '@/core/components/ui/magic/magic-card.vue'

interface EmailMessage {
  id: string
  subject?: string
  from?: string
  to?: string
  date?: string
  snippet?: string
  body?: string
  isRead?: boolean
  isImportant?: boolean
  hasAttachments?: boolean
  labels?: string[]
  webLink?: string
}

interface Props {
  title: string
  emails: EmailMessage[]
}

const props = defineProps<Props>()
const showAllEmails = ref(false)
const expandedEmails = ref<Set<string>>(new Set())

const displayEmails = computed(() => {
  if (showAllEmails.value || props.emails.length <= 5) {
    return props.emails
  }
  return props.emails.slice(0, 5)
})

const getInitials = (from?: string) => {
  if (!from) return '?'
  
  const nameMatch = from.match(/^(.+?)\s*</)
  const name = nameMatch ? nameMatch[1].trim() : from.split('@')[0]
  
  if (/[가-힣]/.test(name)) {
    return name.charAt(0)
  } else {
    return name.slice(0, 2).toUpperCase()
  }
}

const getDisplayName = (from?: string) => {
  if (!from) return '알 수 없음'
  
  const nameMatch = from.match(/^(.+?)\s*</)
  return nameMatch ? nameMatch[1].trim() : from.split('@')[0]
}

const getEmailAddress = (from?: string) => {
  if (!from) return ''
  
  const emailMatch = from.match(/<(.+?)>/)
  return emailMatch ? emailMatch[1] : from
}

const formatEmailTime = (date?: string) => {
  if (!date) return '날짜 미상'
  
  try {
    const emailDate = new Date(date)
    const now = new Date()
    
    const emailDateKST = new Date(emailDate.getTime() + (9 * 60 * 60 * 1000))
    const nowKST = new Date(now.getTime() + (9 * 60 * 60 * 1000))
    
    const diffMs = nowKST.getTime() - emailDateKST.getTime()
    const diffHours = diffMs / (1000 * 60 * 60)
    const diffDays = diffMs / (1000 * 60 * 60 * 24)
    
    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return `${diffMinutes}분 전`
    } else if (diffHours < 24) {
      return `${Math.floor(diffHours)}시간 전`
    } else if (diffDays < 7) {
      return `${Math.floor(diffDays)}일 전`
    } else {
      return new Intl.DateTimeFormat('ko-KR', {
        timeZone: 'Asia/Seoul',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(emailDateKST)
    }
  } catch (error) {
    console.warn('Failed to format email time:', error)
    return date
  }
}

const isToday = (date?: string) => {
  if (!date) return false
  
  try {
    const emailDate = new Date(date)
    const today = new Date()
    
    const emailDateKST = new Date(emailDate.getTime() + (9 * 60 * 60 * 1000))
    const todayKST = new Date(today.getTime() + (9 * 60 * 60 * 1000))
    
    return emailDateKST.toDateString() === todayKST.toDateString()
  } catch {
    return false
  }
}

const formatLabel = (label: string) => {
  const labelMap: Record<string, string> = {
    'INBOX': '받은편지함',
    'SENT': '보낸편지함',
    'DRAFT': '임시보관함',
    'SPAM': '스팸',
    'TRASH': '휴지통',
    'IMPORTANT': '중요',
    'STARRED': '별표',
    'UNREAD': '읽지 않음'
  }
  
  return labelMap[label] || label
}

const toggleEmailExpanded = (emailId: string) => {
  if (expandedEmails.value.has(emailId)) {
    expandedEmails.value.delete(emailId)
  } else {
    expandedEmails.value.add(emailId)
  }
}

const openEmail = (webLink: string) => {
  window.open(webLink, '_blank', 'noopener,noreferrer')
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

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

.animate-bounce-gentle {
  animation: bounce-gentle 2s ease-in-out infinite;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-in-from-top {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation-fill-mode: both;
}

.fade-in {
  animation: fade-in 0.3s ease-out;
}

.slide-in-from-top-2 {
  animation: slide-in-from-top 0.3s ease-out;
}

.duration-300 {
  animation-duration: 300ms;
}
</style>