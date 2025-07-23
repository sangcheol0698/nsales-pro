<template>
  <div class="p-6 space-y-8">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
        Enhanced UI Components Demo
      </h1>
      <p class="text-muted-foreground mt-2">
        Magic UI를 활용한 구글 서비스 UI 개선 데모
      </p>
    </div>

    <div class="grid md:grid-cols-2 gap-8">
      <!-- 기존 vs 개선된 캘린더 -->
      <div class="space-y-4">
        <h2 class="text-xl font-semibold flex items-center gap-2">
          <Calendar class="h-5 w-5 text-blue-500" />
          Google Calendar
        </h2>
        
        <div class="space-y-6">
          <!-- 기존 컴포넌트 -->
          <div>
            <h3 class="text-sm font-medium text-muted-foreground mb-3">기존 UI</h3>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 bg-gray-50">
              <GoogleCalendarCard
                title="오늘의 일정"
                :events="sampleCalendarEvents"
              />
            </div>
          </div>
          
          <!-- 개선된 컴포넌트 -->
          <div>
            <h3 class="text-sm font-medium text-muted-foreground mb-3">개선된 UI ✨</h3>
            <div class="border-2 border-dashed border-blue-300 rounded-lg p-4 bg-blue-50/30">
              <EnhancedGoogleCalendarCard
                title="오늘의 일정"
                :events="sampleCalendarEvents"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 기존 vs 개선된 메일 -->
      <div class="space-y-4">
        <h2 class="text-xl font-semibold flex items-center gap-2">
          <Mail class="h-5 w-5 text-emerald-500" />
          Gmail
        </h2>
        
        <div class="space-y-6">
          <!-- 기존 컴포넌트 -->
          <div>
            <h3 class="text-sm font-medium text-muted-foreground mb-3">기존 UI</h3>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 bg-gray-50">
              <GmailCard
                title="최근 메일"
                :emails="sampleEmails"
              />
            </div>
          </div>
          
          <!-- 개선된 컴포넌트 -->
          <div>
            <h3 class="text-sm font-medium text-muted-foreground mb-3">개선된 UI ✨</h3>
            <div class="border-2 border-dashed border-emerald-300 rounded-lg p-4 bg-emerald-50/30">
              <EnhancedGmailCard
                title="최근 메일"
                :emails="sampleEmails"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 개선사항 설명 -->
    <div class="mt-12 p-6 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border border-purple-200">
      <h3 class="text-lg font-semibold mb-4 text-purple-800">🎨 주요 개선사항</h3>
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="flex items-start gap-3">
          <div class="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
            <Sparkles class="h-4 w-4 text-purple-600" />
          </div>
          <div>
            <h4 class="font-medium text-purple-800">Magic Card</h4>
            <p class="text-sm text-purple-600">마우스 팔로우 테두리 효과</p>
          </div>
        </div>
        
        <div class="flex items-start gap-3">
          <div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
            <Zap class="h-4 w-4 text-blue-600" />
          </div>
          <div>
            <h4 class="font-medium text-blue-800">Shimmer Button</h4>
            <p class="text-sm text-blue-600">시머 애니메이션 버튼</p>
          </div>
        </div>
        
        <div class="flex items-start gap-3">
          <div class="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
            <List class="h-4 w-4 text-emerald-600" />
          </div>
          <div>
            <h4 class="font-medium text-emerald-800">Animated List</h4>
            <p class="text-sm text-emerald-600">순차적 애니메이션</p>
          </div>
        </div>
        
        <div class="flex items-start gap-3">
          <div class="h-8 w-8 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
            <Palette class="h-4 w-4 text-amber-600" />
          </div>
          <div>
            <h4 class="font-medium text-amber-800">Gradient Text</h4>
            <p class="text-sm text-amber-600">그라데이션 제목 애니메이션</p>
          </div>
        </div>
        
        <div class="flex items-start gap-3">
          <div class="h-8 w-8 rounded-full bg-pink-100 flex items-center justify-center flex-shrink-0">
            <MousePointer class="h-4 w-4 text-pink-600" />
          </div>
          <div>
            <h4 class="font-medium text-pink-800">Hover Effects</h4>
            <p class="text-sm text-pink-600">다양한 호버 효과</p>
          </div>
        </div>
        
        <div class="flex items-start gap-3">
          <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
            <Activity class="h-4 w-4 text-indigo-600" />
          </div>
          <div>
            <h4 class="font-medium text-indigo-800">Status Indicators</h4>
            <p class="text-sm text-indigo-600">실시간 상태 표시</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 마이그레이션 가이드 -->
    <div class="mt-8 p-6 bg-gray-50 rounded-xl border">
      <h3 class="text-lg font-semibold mb-4">🔄 마이그레이션 가이드</h3>
      <div class="space-y-4">
        <div>
          <h4 class="font-medium mb-2">1. 기존 컴포넌트 교체</h4>
          <div class="bg-white rounded-lg p-4 font-mono text-sm border">
            <div class="text-red-600 mb-2">// 기존</div>
            <div class="text-gray-600">import GoogleCalendarCard from '@/features/chat/components/GoogleCalendarCard.vue'</div>
            <div class="text-green-600 mt-2 mb-2">// 개선</div>
            <div class="text-gray-600">import EnhancedGoogleCalendarCard from '@/features/chat/components/enhanced/EnhancedGoogleCalendarCard.vue'</div>
          </div>
        </div>
        
        <div>
          <h4 class="font-medium mb-2">2. 프롭스는 동일하게 유지</h4>
          <div class="bg-white rounded-lg p-4 font-mono text-sm border">
            <div class="text-gray-600">&lt;EnhancedGoogleCalendarCard</div>
            <div class="text-gray-600 ml-4">title="일정"</div>
            <div class="text-gray-600 ml-4">:events="events"</div>
            <div class="text-gray-600">/&gt;</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Calendar, Mail, Sparkles, Zap, List, Palette, MousePointer, Activity } from 'lucide-vue-next'

// 기존 컴포넌트들
import GoogleCalendarCard from '../GoogleCalendarCard.vue'
import GmailCard from '../GmailCard.vue'

// 개선된 컴포넌트들
import EnhancedGoogleCalendarCard from './EnhancedGoogleCalendarCard.vue'
import EnhancedGmailCard from './EnhancedGmailCard.vue'

// 샘플 데이터
const sampleCalendarEvents = ref([
  {
    id: '1',
    summary: '팀 스탠드업 미팅',
    description: '일일 진행 상황 공유 및 이슈 논의',
    start: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2시간 후
    end: new Date(Date.now() + 2.5 * 60 * 60 * 1000).toISOString(),
    location: '회의실 A',
    attendees: [
      { email: 'john@example.com', displayName: '김철수' },
      { email: 'jane@example.com', displayName: '이영희' },
      { email: 'bob@example.com', displayName: '박민수' }
    ],
    htmlLink: 'https://calendar.google.com/event?eid=example'
  },
  {
    id: '2', 
    summary: '고객사 프레젠테이션',
    description: 'Q1 성과 발표 및 향후 계획 공유',
    start: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), // 4시간 후
    end: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(),
    location: '본사 대회의실',
    attendees: [
      { email: 'ceo@example.com', displayName: '홍길동' },
      { email: 'cto@example.com', displayName: '김기술' }
    ],
    htmlLink: 'https://calendar.google.com/event?eid=example2'
  }
])

const sampleEmails = ref([
  {
    id: '1',
    subject: '프로젝트 마일스톤 달성 축하합니다! 🎉',
    from: '프로젝트 매니저 <pm@example.com>',
    to: 'team@example.com',
    date: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30분 전
    snippet: '안녕하세요! 드디어 1차 마일스톤을 성공적으로 달성했습니다. 팀원 모두의 노고에 감사드리며...',
    body: `안녕하세요! 드디어 1차 마일스톤을 성공적으로 달성했습니다.

팀원 모두의 노고에 감사드리며, 다음 단계 준비를 위한 회의를 내일 오전 10시에 예정하고 있습니다.

감사합니다.`,
    isRead: false,
    isImportant: true,
    hasAttachments: true,
    labels: ['INBOX', 'IMPORTANT'],
    webLink: 'https://mail.google.com/mail/u/0/#inbox/example1'
  },
  {
    id: '2',
    subject: '코드 리뷰 요청',
    from: '개발자 <dev@example.com>',
    to: 'tech-team@example.com',
    date: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2시간 전
    snippet: 'PR #123에 대한 코드 리뷰를 요청드립니다. 새로운 사용자 인증 기능이 구현되었습니다...',
    body: `PR #123에 대한 코드 리뷰를 요청드립니다.

새로운 사용자 인증 기능이 구현되었으며, 보안 강화 및 UX 개선이 포함되어 있습니다.

리뷰 부탁드립니다.`,
    isRead: true,
    isImportant: false,
    hasAttachments: false,
    labels: ['INBOX'],
    webLink: 'https://mail.google.com/mail/u/0/#inbox/example2'
  }
])
</script>

<style scoped>
/* 커스텀 스타일이 필요한 경우 여기에 추가 */
</style>