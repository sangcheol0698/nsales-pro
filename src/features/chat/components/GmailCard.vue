<template>
  <div class="space-y-3">
    <div class="flex items-center gap-2 text-sm font-medium text-primary">
      <Mail class="h-4 w-4" />
      <span>{{ title }}</span>
      <Badge v-if="emails.length > 0" variant="secondary" class="text-xs">
        {{ emails.length }}개
      </Badge>
    </div>
    
    <div v-if="emails.length === 0" class="text-center py-6 text-muted-foreground">
      <MailX class="h-8 w-8 mx-auto mb-2 opacity-50" />
      <p class="text-sm">메일이 없습니다</p>
    </div>
    
    <div v-else class="space-y-2">
      <div
        v-for="email in displayEmails"
        :key="email.id"
        class="group relative bg-background border border-border/60 rounded-lg p-3 hover:border-border transition-all duration-200 hover:shadow-sm"
      >
        <!-- 메일 헤더 -->
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <!-- 발신자 정보 -->
            <div class="flex items-center gap-2 mb-1">
              <div class="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <span class="text-xs font-medium text-primary">
                  {{ getInitials(email.from) }}
                </span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-medium text-foreground truncate">
                  {{ getDisplayName(email.from) }}
                </p>
                <p class="text-[10px] text-muted-foreground truncate">
                  {{ getEmailAddress(email.from) }}
                </p>
              </div>
            </div>
            
            <!-- 제목 -->
            <h4 class="font-medium text-sm text-foreground line-clamp-1 group-hover:text-primary transition-colors mb-1">
              {{ email.subject || '제목 없음' }}
            </h4>
            
            <!-- 시간 정보 -->
            <div class="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock class="h-3 w-3 flex-shrink-0" />
              <span>{{ formatEmailTime(email.date) }}</span>
              
              <!-- 첨부파일 표시 -->
              <div v-if="email.hasAttachments" class="flex items-center gap-1 ml-2">
                <Paperclip class="h-3 w-3" />
                <span>첨부</span>
              </div>
            </div>
          </div>
          
          <!-- 메일 상태 및 우선순위 -->
          <div class="flex items-center gap-1">
            <!-- 읽음 상태 -->
            <div 
              class="h-2 w-2 rounded-full flex-shrink-0"
              :class="email.isRead ? 'bg-gray-400' : 'bg-blue-500'"
              :title="email.isRead ? '읽음' : '읽지 않음'"
            />
            
            <!-- 중요 표시 -->
            <Star 
              v-if="email.isImportant"
              class="h-3 w-3 text-yellow-500 fill-yellow-500"
              title="중요"
            />
            
            <!-- 오늘 메일 -->
            <Badge
              v-if="isToday(email.date)"
              variant="default"
              class="text-[10px] px-1.5 py-0.5 h-auto"
            >
              오늘
            </Badge>
          </div>
        </div>
        
        <!-- 미리보기 내용 -->
        <div v-if="email.snippet" class="mt-2 text-xs text-muted-foreground line-clamp-2 pl-8">
          {{ email.snippet }}
        </div>
        
        <!-- 라벨 표시 -->
        <div v-if="email.labels && email.labels.length > 0" class="mt-2 flex flex-wrap gap-1 pl-8">
          <Badge
            v-for="label in email.labels.slice(0, 3)"
            :key="label"
            variant="outline"
            class="text-[10px] px-1.5 py-0.5 h-auto"
          >
            {{ formatLabel(label) }}
          </Badge>
          <span v-if="email.labels.length > 3" class="text-[10px] text-muted-foreground">
            +{{ email.labels.length - 3 }}
          </span>
        </div>
        
        <!-- 액션 버튼 (호버 시 표시) -->
        <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <div class="flex items-center gap-1">
            <Button
              v-if="email.webLink"
              variant="ghost"
              size="sm"
              class="h-6 w-6 p-0"
              @click="openEmail(email.webLink)"
              title="Gmail에서 열기"
            >
              <ExternalLink class="h-3 w-3" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              class="h-6 w-6 p-0"
              @click="toggleEmailExpanded(email.id)"
              :title="expandedEmails.has(email.id) ? '접기' : '전체 내용 보기'"
            >
              <ChevronDown class="h-3 w-3" :class="{ 'rotate-180': expandedEmails.has(email.id) }" />
            </Button>
          </div>
        </div>
        
        <!-- 확장된 내용 -->
        <div v-if="expandedEmails.has(email.id)" class="mt-3 pt-3 border-t border-border/60">
          <!-- 수신자 정보 -->
          <div v-if="email.to" class="text-xs text-muted-foreground mb-2">
            <span class="font-medium">받는 사람:</span> {{ email.to }}
          </div>
          
          <!-- 전체 내용 -->
          <div v-if="email.body" class="text-xs text-foreground whitespace-pre-wrap max-h-40 overflow-y-auto">
            {{ email.body }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 더보기 버튼 -->
    <div v-if="emails.length > 5" class="text-center pt-2">
      <Button
        variant="outline"
        size="sm"
        class="text-xs"
        @click="showAllEmails = !showAllEmails"
      >
        {{ showAllEmails ? '접기' : `${emails.length - 5}개 더보기` }}
        <ChevronDown class="h-3 w-3 ml-1" :class="{ 'rotate-180': showAllEmails }" />
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Mail, MailX, Clock, Paperclip, Star, ExternalLink, ChevronDown } from 'lucide-vue-next'
import { Badge } from '@/core/components/ui/badge'
import { Button } from '@/core/components/ui/button'

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
  
  // 이름 부분 추출 (예: "홍길동 <hong@example.com>" -> "홍길동")
  const nameMatch = from.match(/^(.+?)\s*</)
  const name = nameMatch ? nameMatch[1].trim() : from.split('@')[0]
  
  // 한글 이름의 경우 첫 글자, 영문의 경우 첫 두 글자
  if (/[가-힣]/.test(name)) {
    return name.charAt(0)
  } else {
    return name.slice(0, 2).toUpperCase()
  }
}

const getDisplayName = (from?: string) => {
  if (!from) return '알 수 없음'
  
  // 이름 부분 추출
  const nameMatch = from.match(/^(.+?)\s*</)
  return nameMatch ? nameMatch[1].trim() : from.split('@')[0]
}

const getEmailAddress = (from?: string) => {
  if (!from) return ''
  
  // 이메일 주소 부분 추출
  const emailMatch = from.match(/<(.+?)>/)
  return emailMatch ? emailMatch[1] : from
}

const formatEmailTime = (date?: string) => {
  if (!date) return '날짜 미상'
  
  try {
    const emailDate = new Date(date)
    const now = new Date()
    
    // 한국 시간으로 변환
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
    
    // 한국 시간 기준으로 오늘인지 확인
    const emailDateKST = new Date(emailDate.getTime() + (9 * 60 * 60 * 1000))
    const todayKST = new Date(today.getTime() + (9 * 60 * 60 * 1000))
    
    return emailDateKST.toDateString() === todayKST.toDateString()
  } catch {
    return false
  }
}

const formatLabel = (label: string) => {
  // Gmail 기본 라벨 한국어 변환
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
</style>