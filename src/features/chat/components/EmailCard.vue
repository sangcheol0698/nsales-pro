<template>
  <div class="relative group">
    <!-- Card with gradient border animation -->
    <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-emerald-600/20 via-teal-600/20 to-cyan-600/20 p-px opacity-75 group-hover:opacity-100 transition-all duration-500">
      <div class="h-full w-full rounded-xl bg-background/95 backdrop-blur-sm">
        <!-- Shimmer overlay -->
        <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-transparent via-emerald-500/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
      </div>
    </div>
    
    <!-- Main content -->
    <div class="relative bg-background/95 backdrop-blur-sm rounded-xl p-4 border border-border/50 hover:border-border/80 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-emerald-500/10">
      <!-- Header with priority indicator -->
      <div class="flex items-start justify-between mb-3">
        <div class="flex items-center flex-1 min-w-0">
          <div class="flex-shrink-0 mr-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-white font-bold text-sm">
              {{ getInitials(email.sender) }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-foreground truncate group-hover:text-emerald-600 transition-colors duration-300">
              {{ email.subject }}
            </h3>
            <p class="text-sm text-muted-foreground truncate">
              {{ email.sender }}
            </p>
          </div>
        </div>
        <div class="ml-3 flex items-center space-x-2">
          <!-- Read status -->
          <div v-if="email.isUnread" class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
          <!-- Priority indicator -->
          <div v-if="email.priority === 'high'" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-600 ring-1 ring-red-500/20">
            <Zap class="w-3 h-3 mr-1" />
            높음
          </div>
          <!-- Date -->
          <div class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-600 ring-1 ring-emerald-500/20">
            <Mail class="w-3 h-3 mr-1" />
            {{ formatDate(email.date) }}
          </div>
        </div>
      </div>
      
      <!-- Email preview -->
      <div class="mb-4 text-sm text-muted-foreground/80">
        <div class="line-clamp-3 group-hover:line-clamp-4 transition-all duration-300">
          {{ email.snippet }}
        </div>
      </div>
      
      <!-- Attachments -->
      <div v-if="email.attachments && email.attachments.length > 0" class="mb-3">
        <div class="flex items-center text-sm text-muted-foreground mb-2">
          <Paperclip class="w-4 h-4 mr-2 text-orange-500" />
          {{ email.attachments.length }}개 첨부파일
        </div>
        <div class="flex flex-wrap gap-2">
          <div v-for="(attachment, index) in email.attachments.slice(0, 3)" 
               :key="index" 
               class="inline-flex items-center px-2 py-1 rounded-md bg-muted/50 text-xs">
            <FileText class="w-3 h-3 mr-1 text-orange-500" />
            {{ attachment.name }}
          </div>
          <div v-if="email.attachments.length > 3" 
               class="inline-flex items-center px-2 py-1 rounded-md bg-muted/50 text-xs">
            +{{ email.attachments.length - 3 }} 더보기
          </div>
        </div>
      </div>
      
      <!-- Tags/Labels -->
      <div v-if="email.labels && email.labels.length > 0" class="flex flex-wrap gap-1 mb-3">
        <span v-for="label in email.labels.slice(0, 4)" 
              :key="label" 
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="getLabelStyle(label)">
          <Tag class="w-3 h-3 mr-1" />
          {{ label }}
        </span>
      </div>
      
      <!-- Action buttons -->
      <div class="flex items-center justify-between pt-3 border-t border-border/50 opacity-0 group-hover:opacity-100 transition-all duration-300">
        <div class="flex space-x-2">
          <button class="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-200 hover:scale-105">
            <Eye class="w-3 h-3 mr-1" />
            읽기
          </button>
          <button class="inline-flex items-center px-3 py-1.5 rounded-md text-xs font-medium bg-blue-500/10 hover:bg-blue-500/20 text-blue-600 border border-blue-500/20 hover:border-blue-500/40 transition-all duration-200 hover:scale-105">
            <Reply class="w-3 h-3 mr-1" />
            답장
          </button>
        </div>
        <div class="text-xs text-muted-foreground">
          {{ formatTimeAgo(email.date) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Mail, Zap, Paperclip, FileText, Tag, Eye, Reply } from 'lucide-vue-next'

interface EmailAttachment {
  name: string
  size?: string
}

interface Email {
  id: string
  sender: string
  subject: string
  snippet: string
  date: string
  isUnread?: boolean
  priority?: 'high' | 'normal' | 'low'
  attachments?: EmailAttachment[]
  labels?: string[]
}

interface Props {
  email: Email
}

defineProps<Props>()

const getInitials = (name: string) => {
  // Extract name from email format "Name <email@domain.com>"
  const nameMatch = name.match(/^([^<]+)/)
  const displayName = nameMatch ? nameMatch[1].trim() : name
  return displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) {
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '어제'
  } else {
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
  }
}

const formatTimeAgo = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffHours < 1) {
    return '방금 전'
  } else if (diffHours < 24) {
    return `${diffHours}시간 전`
  } else {
    return `${diffDays}일 전`
  }
}

const getLabelStyle = (label: string) => {
  const styles = {
    'IMPORTANT': 'bg-red-500/10 text-red-600 ring-1 ring-red-500/20',
    'WORK': 'bg-blue-500/10 text-blue-600 ring-1 ring-blue-500/20',
    'PERSONAL': 'bg-green-500/10 text-green-600 ring-1 ring-green-500/20',
    'PROMOTION': 'bg-purple-500/10 text-purple-600 ring-1 ring-purple-500/20',
    'SOCIAL': 'bg-pink-500/10 text-pink-600 ring-1 ring-pink-500/20'
  } as Record<string, string>
  
  return styles[label.toUpperCase()] || 'bg-muted/50 text-muted-foreground'
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>