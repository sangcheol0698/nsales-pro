# Enhanced Google Services UI Components

Magic UI를 활용한 구글 메일과 캘린더의 개선된 UI 컴포넌트입니다.

## 📋 개요

기존의 기본적인 카드 UI를 Magic UI의 특별한 효과들로 개선하여 더욱 인터랙티브하고 매력적인 사용자 경험을 제공합니다.

## ✨ 주요 개선사항

### 🎨 시각적 개선
- **그라데이션 애니메이션**: 제목에 동적 그라데이션 효과
- **Magic Card**: 마우스 팔로우 테두리 효과
- **Shimmer Button**: 액션 버튼에 시머 애니메이션
- **블러 백드롭**: 카드 배경에 블러 효과

### 🎭 애니메이션 효과
- **Animated List**: 순차적으로 나타나는 리스트 애니메이션
- **Bounce Animation**: 부드러운 바운스 효과
- **Fade & Slide**: 페이드인/슬라이드 전환 효과
- **Pulse Effects**: 중요 정보에 펄스 애니메이션

### 🔄 인터랙션 개선
- **호버 효과**: 카드 호버 시 추가 정보 표시
- **상태 인디케이터**: 실시간 상태 표시 (진행중/예정/완료)
- **스케일 애니메이션**: 버튼 호버 시 스케일 효과
- **부드러운 전환**: 모든 상태 변화에 부드러운 전환

## 🚀 사용법

### 캘린더 컴포넌트

```vue
<template>
  <EnhancedGoogleCalendarCard
    title="오늘의 일정"
    :events="calendarEvents"
  />
</template>

<script setup lang="ts">
import EnhancedGoogleCalendarCard from '@/features/chat/components/enhanced/EnhancedGoogleCalendarCard.vue'

const calendarEvents = [
  {
    id: '1',
    summary: '팀 미팅',
    description: '주간 계획 회의',
    start: '2024-01-15T10:00:00Z',
    end: '2024-01-15T11:00:00Z',
    location: '회의실 A',
    attendees: [
      { email: 'user1@example.com', displayName: '홍길동' },
      { email: 'user2@example.com', displayName: '김철수' }
    ],
    htmlLink: 'https://calendar.google.com/event?eid=...'
  }
]
</script>
```

### 메일 컴포넌트

```vue
<template>
  <EnhancedGmailCard
    title="최근 메일"
    :emails="emailMessages"
  />
</template>

<script setup lang="ts">
import EnhancedGmailCard from '@/features/chat/components/enhanced/EnhancedGmailCard.vue'

const emailMessages = [
  {
    id: '1',
    subject: '프로젝트 진행 상황',
    from: '홍길동 <hong@example.com>',
    to: 'team@example.com',
    date: '2024-01-15T09:30:00Z',
    snippet: '안녕하세요. 프로젝트 진행 상황을 공유드립니다...',
    body: '전체 메일 내용...',
    isRead: false,
    isImportant: true,
    hasAttachments: true,
    labels: ['INBOX', 'IMPORTANT'],
    webLink: 'https://mail.google.com/mail/u/0/#inbox/...'
  }
]
</script>
```

## 🎯 컴포넌트 특징

### EnhancedGoogleCalendarCard

**Props:**
- `title` (string): 카드 제목
- `events` (CalendarEvent[]): 캘린더 이벤트 배열

**주요 기능:**
- 📅 이벤트 상태 실시간 표시 (진행중/예정/완료)
- 👥 참석자 아바타 표시
- 📍 위치 정보 표시  
- 🔗 Google 캘린더 연결
- 🎨 Magic Card 마우스 팔로우 효과

### EnhancedGmailCard

**Props:**
- `title` (string): 카드 제목
- `emails` (EmailMessage[]): 이메일 메시지 배열

**주요 기능:**
- 📧 읽음/안읽음 상태 표시
- ⭐ 중요 메일 표시
- 📎 첨부파일 아이콘
- 🏷️ 라벨 애니메이션 표시
- 📖 확장/접기 기능
- 🔗 Gmail 연결

## 🎨 스타일 가이드

### 색상 팔레트
- **캘린더**: 파란색 계열 (`#3b82f6` ~ `#8b5cf6`)
- **메일**: 초록색 계열 (`#10b981` ~ `#3b82f6`)

### 애니메이션 타이밍
- **기본 전환**: 300ms ease-out
- **리스트 애니메이션**: 150ms 지연
- **라벨 애니메이션**: 50ms 지연

### 호버 효과
- **카드**: 그림자 + 테두리 글로우
- **버튼**: 스케일 1.05 + 시머 효과
- **텍스트**: 색상 변경 (파란색/초록색)

## 📦 의존성

```json
{
  "dependencies": {
    "lucide-vue-next": "^0.xxx.x",
    "@/core/components/ui/badge": "내부 컴포넌트"
  },
  "magicComponents": [
    "AnimatedList",
    "ShimmerButton", 
    "MagicCard"
  ]
}
```

## 🔧 커스터마이징

### 색상 변경
각 컴포넌트의 그라데이션 색상은 props로 커스터마이징 가능합니다:

```vue
<MagicCard
  :gradient-color="'#ff6b6b'"  <!-- 빨간색으로 변경 -->
  :gradient-opacity="0.2"      <!-- 투명도 조정 -->
>
```

### 애니메이션 속도 조정
CSS 변수를 통해 애니메이션 속도를 조정할 수 있습니다:

```css
.custom-timing {
  --animation-duration: 500ms;
  --shimmer-speed: 2s;
}
```

## 📱 반응형 지원

모든 컴포넌트는 반응형으로 설계되어 다양한 화면 크기에서 최적화된 경험을 제공합니다:

- **데스크톱**: 풀 기능 표시
- **태블릿**: 적절한 간격 조정
- **모바일**: 컴팩트한 레이아웃

## 🚨 브라우저 지원

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 📄 라이선스

이 컴포넌트들은 프로젝트의 라이선스를 따릅니다.