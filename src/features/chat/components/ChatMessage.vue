<template>
  <div
    class="flex mb-4"
    :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
  >
    <div class="flex gap-3 max-w-[80%]">
      <Avatar
        v-if="message.role === 'assistant'"
        class="h-8 w-8 flex-shrink-0"
      >
        <AvatarFallback class="bg-primary text-primary-foreground">
          AI
        </AvatarFallback>
      </Avatar>

      <div
        class="rounded-lg p-3 break-words"
        :class="[
          message.role === 'user'
            ? 'bg-primary text-primary-foreground ml-auto'
            : 'bg-card text-card-foreground',
        ]"
      >
        <div
          v-if="message.role === 'assistant'"
          class="prose prose-sm max-w-none dark:prose-invert"
          v-html="formattedContent"
        />
        <div v-else class="whitespace-pre-wrap">
          {{ message.content }}
        </div>

        <div
          class="text-xs mt-2 opacity-70"
          :class="
            message.role === 'user'
              ? 'text-primary-foreground/70'
              : 'text-foreground/70'
          "
        >
          {{ formatTime(message.timestamp) }}
        </div>
      </div>

      <Avatar
        v-if="message.role === 'user'"
        class="h-8 w-8 flex-shrink-0"
      >
        <AvatarFallback class="bg-card text-card-foreground">
          U
        </AvatarFallback>
      </Avatar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { Avatar, AvatarFallback } from '@/core/components/ui/avatar'
import type { ChatMessage } from '../entity/ChatMessage'

interface Props {
  message: ChatMessage
}

const props = defineProps<Props>()

// Configure marked with highlight.js
marked.setOptions({
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.warn('Highlight.js error:', err)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

const formattedContent = computed(() => {
  if (props.message.role === 'assistant') {
    return marked(props.message.content)
  }
  return props.message.content
})

const formatTime = (timestamp: Date | string) => {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
  
  // 유효한 날짜인지 확인
  if (isNaN(date.getTime())) {
    return '시간 정보 없음'
  }
  
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}
</script>

<style>
/* Highlight.js 스타일을 위한 CSS */
.prose pre {
  background-color: #1f2937;
  color: #f9fafb;
  padding: 1rem;
  border-radius: 0.375rem;
  overflow-x: auto;
}

.prose code {
  background-color: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.dark .prose code {
  background-color: #374151;
  color: #f9fafb;
}

.prose pre code {
  background-color: transparent;
  padding: 0;
}
</style>