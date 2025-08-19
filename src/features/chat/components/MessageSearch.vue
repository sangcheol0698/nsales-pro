<template>
  <div class="relative">
    <!-- 검색 트리거 버튼 -->
    <Button
      variant="ghost"
      size="sm"
      @click="toggleSearch"
      class="h-8 w-8 p-0"
      :aria-label="$t ? $t('chat.searchMessages') : '메시지 검색'"
    >
      <Search class="h-4 w-4" />
    </Button>

    <!-- 검색 패널 -->
    <div
      v-if="isSearchOpen"
      class="absolute top-full right-0 mt-2 w-80 bg-card border border-border rounded-lg shadow-lg p-4 z-50"
      role="dialog"
      :aria-label="$t ? $t('chat.messageSearchDialog') : '메시지 검색 다이얼로그'"
    >
      <div class="space-y-3">
        <!-- 검색 헤더 -->
        <div class="flex items-center justify-between">
          <h3 class="font-medium">메시지 검색</h3>
          <Button
            variant="ghost"
            size="sm"
            @click="toggleSearch"
            class="h-6 w-6 p-0"
          >
            <X class="h-3 w-3" />
          </Button>
        </div>

        <!-- 검색 입력 -->
        <div class="relative">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            ref="searchInputRef"
            v-model="searchQuery"
            placeholder="메시지 내용 검색..."
            class="pl-10"
            @keydown.enter="performSearch"
            @keydown.escape="toggleSearch"
          />
        </div>

        <!-- 검색 옵션 -->
        <div class="flex items-center gap-4 text-sm">
          <label class="flex items-center gap-2">
            <input
              v-model="searchOptions.caseSensitive"
              type="checkbox"
              class="rounded"
            />
            <span>대소문자 구분</span>
          </label>
          <label class="flex items-center gap-2">
            <input
              v-model="searchOptions.wholeWord"
              type="checkbox"
              class="rounded"
            />
            <span>완전한 단어</span>
          </label>
        </div>

        <!-- 검색 결과 -->
        <div v-if="searchResults.length > 0" class="max-h-60 overflow-y-auto space-y-2">
          <div class="text-sm text-muted-foreground mb-2">
            {{ searchResults.length }}개의 결과 발견
          </div>
          
          <div
            v-for="(result, index) in searchResults"
            :key="result.id"
            class="p-3 rounded border border-border hover:bg-muted/50 cursor-pointer"
            :class="{ 'bg-primary/10': index === selectedResultIndex }"
            @click="selectResult(result)"
          >
            <div class="flex items-start gap-2">
              <div class="flex-shrink-0 w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
                <span class="text-xs font-medium">
                  {{ result.role === 'user' ? 'U' : 'AI' }}
                </span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium truncate">
                  {{ result.role === 'user' ? '사용자' : 'AI Assistant' }}
                </div>
                <div class="text-sm text-muted-foreground mt-1" v-html="highlightSearchTerm(result.content)"></div>
                <div class="text-xs text-muted-foreground mt-1">
                  {{ formatTime(result.timestamp) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 검색 결과가 없을 때 -->
        <div v-else-if="searchQuery && hasSearched" class="text-center py-4 text-muted-foreground">
          <Search class="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>검색 결과가 없습니다</p>
        </div>

        <!-- 검색 안내 -->
        <div v-else-if="!searchQuery" class="text-center py-4 text-muted-foreground">
          <p>메시지 내용을 검색하세요</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { Search, X } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { ChatMessage } from '../entity/ChatMessage'

interface Props {
  messages: ChatMessage[]
}

interface Emits {
  selectMessage: [messageId: string]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isSearchOpen = ref(false)
const searchQuery = ref('')
const searchInputRef = ref<HTMLInputElement>()
const selectedResultIndex = ref(-1)
const hasSearched = ref(false)

const searchOptions = ref({
  caseSensitive: false,
  wholeWord: false
})

const searchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  
  const query = searchOptions.value.caseSensitive 
    ? searchQuery.value 
    : searchQuery.value.toLowerCase()
  
  return props.messages.filter(message => {
    const content = searchOptions.value.caseSensitive 
      ? message.content 
      : message.content.toLowerCase()
    
    if (searchOptions.value.wholeWord) {
      const regex = new RegExp(`\\b${query}\\b`, 'g')
      return regex.test(content)
    }
    
    return content.includes(query)
  })
})

const toggleSearch = () => {
  isSearchOpen.value = !isSearchOpen.value
  if (isSearchOpen.value) {
    nextTick(() => {
      searchInputRef.value?.focus()
    })
  } else {
    searchQuery.value = ''
    selectedResultIndex.value = -1
    hasSearched.value = false
  }
}

const performSearch = () => {
  hasSearched.value = true
  selectedResultIndex.value = searchResults.value.length > 0 ? 0 : -1
}

const selectResult = (result: ChatMessage) => {
  emit('selectMessage', result.id)
  toggleSearch()
}

const highlightSearchTerm = (content: string): string => {
  if (!searchQuery.value.trim()) return content
  
  const query = searchOptions.value.caseSensitive 
    ? searchQuery.value 
    : searchQuery.value.toLowerCase()
  
  const targetContent = searchOptions.value.caseSensitive 
    ? content 
    : content.toLowerCase()
  
  const regex = searchOptions.value.wholeWord 
    ? new RegExp(`\\b(${query})\\b`, 'gi')
    : new RegExp(`(${query})`, 'gi')
  
  return content.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800 rounded px-1">$1</mark>')
}

const formatTime = (timestamp: Date | string) => {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
  
  if (isNaN(date.getTime())) {
    return '시간 정보 없음'
  }
  
  return new Intl.DateTimeFormat('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

// 키보드 내비게이션
watch(searchQuery, () => {
  if (searchQuery.value.trim()) {
    performSearch()
  } else {
    hasSearched.value = false
  }
})
</script>

<style scoped>
/* 검색 결과 하이라이트 스타일 */
:deep(mark) {
  background-color: rgb(254 240 138);
  border-radius: 2px;
  padding: 0 2px;
}

:deep(.dark mark) {
  background-color: rgb(133 77 14);
}
</style>