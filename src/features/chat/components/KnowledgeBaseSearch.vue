<template>
  <div class="relative">
    <!-- 검색 헤더 -->
    <div class="flex items-center gap-2 mb-3">
      <Search class="h-4 w-4 text-primary" />
      <h3 class="font-semibold text-sm">지식 베이스 검색</h3>
      <Badge v-if="lastSearchResults.length > 0" variant="secondary" class="text-xs">
        {{ lastSearchResults.length }}건 발견
      </Badge>
    </div>

    <!-- 검색 입력 -->
    <div class="relative mb-4">
      <div class="relative">
        <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          v-model="searchQuery"
          placeholder="문서 내용을 검색하세요..."
          class="pl-10 pr-24"
          @keydown.enter="performSearch"
          @input="onSearchInput"
        />
        <div class="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
          <Button
            v-if="searchQuery"
            variant="ghost"
            size="sm"
            @click="clearSearch"
            class="h-6 w-6 p-0"
          >
            <X class="h-3 w-3" />
          </Button>
          <Button
            @click="performSearch"
            :disabled="!searchQuery.trim() || isSearching"
            size="sm"
            class="h-6 px-2 text-xs"
          >
            <Loader v-if="isSearching" class="h-3 w-3 animate-spin" />
            <Search v-else class="h-3 w-3" />
          </Button>
        </div>
      </div>
    </div>

    <!-- 검색 옵션 -->
    <div class="mb-4 space-y-2">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <Label for="search-limit" class="text-xs">결과 수:</Label>
          <select
            id="search-limit"
            v-model="searchLimit"
            class="text-xs border rounded px-2 py-1 bg-background"
          >
            <option value="3">3개</option>
            <option value="5">5개</option>
            <option value="10">10개</option>
            <option value="20">20개</option>
          </select>
        </div>
        
        <div class="flex items-center gap-2">
          <Switch
            v-model:checked="autoSearch"
            id="auto-search"
          />
          <Label for="auto-search" class="text-xs">실시간 검색</Label>
        </div>
      </div>
    </div>

    <!-- 빠른 검색 태그 -->
    <div class="mb-4">
      <Label class="text-xs text-muted-foreground mb-2 block">빠른 검색</Label>
      <div class="flex flex-wrap gap-1">
        <Button
          v-for="tag in quickSearchTags"
          :key="tag"
          variant="outline"
          size="sm"
          @click="setQuickSearch(tag)"
          class="h-6 px-2 text-xs"
        >
          {{ tag }}
        </Button>
      </div>
    </div>

    <!-- 검색 결과 -->
    <div v-if="searchResults.length > 0 || isSearching" class="space-y-3">
      <div class="flex items-center justify-between">
        <Label class="text-sm font-medium">검색 결과</Label>
        <div class="flex items-center gap-2">
          <Badge variant="outline" class="text-xs">
            {{ searchResults.length }}건
          </Badge>
          <Button
            v-if="searchResults.length > 0"
            variant="ghost"
            size="sm"
            @click="insertAllToChat"
            class="h-6 text-xs"
          >
            <MessageSquare class="h-3 w-3 mr-1" />
            채팅에 추가
          </Button>
        </div>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="isSearching" class="flex items-center justify-center py-4">
        <div class="text-center space-y-2">
          <Loader class="h-6 w-6 animate-spin mx-auto text-primary" />
          <p class="text-xs text-muted-foreground">검색 중...</p>
        </div>
      </div>

      <!-- 검색 결과 목록 -->
      <div v-else class="space-y-2 max-h-80 overflow-y-auto">
        <div
          v-for="(result, index) in searchResults"
          :key="index"
          class="group border rounded-lg p-3 hover:shadow-sm transition-all duration-200 cursor-pointer"
          :class="{
            'border-primary/30 bg-primary/5': selectedResults.has(index),
            'border-border hover:border-primary/50': !selectedResults.has(index)
          }"
          @click="toggleResultSelection(index)"
        >
          <!-- 결과 헤더 -->
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2 flex-1">
              <div class="w-2 h-2 rounded-full bg-primary"></div>
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-xs font-medium">
                    유사도: {{ Math.round(result.score * 100) }}%
                  </span>
                  <Badge
                    :variant="result.score > 0.8 ? 'default' : result.score > 0.6 ? 'secondary' : 'outline'"
                    class="text-xs h-4 px-1"
                  >
                    {{ result.score > 0.8 ? '높음' : result.score > 0.6 ? '보통' : '낮음' }}
                  </Badge>
                </div>
                <div v-if="result.metadata?.filename" class="text-xs text-muted-foreground">
                  📄 {{ result.metadata.filename }}
                </div>
              </div>
            </div>
            
            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button
                variant="ghost"
                size="sm"
                @click.stop="insertSingleToChat(result, index)"
                class="h-6 w-6 p-0"
              >
                <Plus class="h-3 w-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click.stop="copyToClipboard(result.content)"
                class="h-6 w-6 p-0"
              >
                <Copy class="h-3 w-3" />
              </Button>
            </div>
          </div>

          <!-- 결과 내용 -->
          <div class="space-y-2">
            <div class="text-sm text-foreground/90 leading-relaxed">
              <div class="line-clamp-3" v-html="highlightSearchTerms(result.content)"></div>
            </div>
            
            <!-- 확장 버튼 -->
            <Button
              v-if="result.content.length > 150"
              variant="ghost"
              size="sm"
              @click.stop="toggleExpanded(index)"
              class="h-5 text-xs text-muted-foreground hover:text-foreground p-0"
            >
              {{ expandedResults.has(index) ? '접기' : '더보기' }}
              <ChevronDown 
                class="h-3 w-3 ml-1 transition-transform" 
                :class="{ 'rotate-180': expandedResults.has(index) }"
              />
            </Button>
          </div>

          <!-- 확장된 내용 -->
          <div v-if="expandedResults.has(index)" class="mt-3 pt-3 border-t border-border">
            <div class="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">
              {{ result.content }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 빈 상태 -->
    <div v-else-if="hasSearched && searchResults.length === 0" class="text-center py-8">
      <FileSearch class="h-8 w-8 mx-auto text-muted-foreground mb-2" />
      <p class="text-sm text-muted-foreground mb-1">검색 결과를 찾을 수 없습니다</p>
      <p class="text-xs text-muted-foreground">다른 키워드로 검색해보세요</p>
    </div>

    <!-- 초기 상태 -->
    <div v-else class="text-center py-6">
      <Search class="h-6 w-6 mx-auto text-muted-foreground mb-2" />
      <p class="text-sm text-muted-foreground">문서 내용을 검색해보세요</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  Search, 
  X, 
  Loader, 
  FileSearch, 
  Plus, 
  Copy,
  MessageSquare,
  ChevronDown
} from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Input } from '@/core/components/ui/input'
import { Label } from '@/core/components/ui/label'
import { Badge } from '@/core/components/ui/badge'
import { Switch } from '@/core/components/ui/switch'
import { useToast } from '@/core/composables'

interface Props {
  sessionId: string
}

interface SearchResult {
  content: string
  score: number
  file_id: string
  metadata: Record<string, any>
}

interface Emits {
  insertToChat: [content: string]
  resultSelected: [result: SearchResult]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const toast = useToast()

// 상태
const searchQuery = ref('')
const searchLimit = ref(5)
const autoSearch = ref(false)
const isSearching = ref(false)
const hasSearched = ref(false)
const searchResults = ref<SearchResult[]>([])
const lastSearchResults = ref<SearchResult[]>([])
const selectedResults = ref(new Set<number>())
const expandedResults = ref(new Set<number>())

// 빠른 검색 태그
const quickSearchTags = ref([
  '계약서', '가격', '일정', '연락처', '회의록', 
  '제안서', '견적서', '납기일', '결제', '조건'
])

// 검색 함수
const performSearch = async () => {
  if (!searchQuery.value.trim() || !props.sessionId) return
  
  try {
    isSearching.value = true
    hasSearched.value = true
    
    const response = await fetch(
      `/api/v1/sessions/${props.sessionId}/vector-store/search`, 
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery.value,
          limit: parseInt(searchLimit.value.toString())
        })
      }
    )
    
    if (response.ok) {
      const data = await response.json()
      searchResults.value = data.results || []
      lastSearchResults.value = [...searchResults.value]
      selectedResults.value.clear()
      expandedResults.value.clear()
      
      if (searchResults.value.length === 0) {
        toast.info('검색 결과 없음', {
          description: '검색어와 일치하는 문서를 찾을 수 없습니다.'
        })
      } else {
        toast.success('검색 완료', {
          description: `${searchResults.value.length}개의 관련 문서를 찾았습니다.`
        })
      }
    } else {
      throw new Error('Search failed')
    }
  } catch (error) {
    console.error('Search error:', error)
    toast.error('검색 실패', {
      description: '문서 검색 중 오류가 발생했습니다.'
    })
  } finally {
    isSearching.value = false
  }
}

// 실시간 검색
let searchTimeout: NodeJS.Timeout
const onSearchInput = () => {
  if (!autoSearch.value) return
  
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (searchQuery.value.trim()) {
      performSearch()
    }
  }, 500)
}

// 유틸리티 함수들
const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  hasSearched.value = false
  selectedResults.value.clear()
  expandedResults.value.clear()
}

const setQuickSearch = (tag: string) => {
  searchQuery.value = tag
  if (autoSearch.value) {
    performSearch()
  }
}

const highlightSearchTerms = (content: string): string => {
  if (!searchQuery.value) return content
  
  const query = searchQuery.value.trim()
  const regex = new RegExp(`(${query})`, 'gi')
  return content.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800">$1</mark>')
}

const toggleResultSelection = (index: number) => {
  if (selectedResults.value.has(index)) {
    selectedResults.value.delete(index)
  } else {
    selectedResults.value.add(index)
  }
}

const toggleExpanded = (index: number) => {
  if (expandedResults.value.has(index)) {
    expandedResults.value.delete(index)
  } else {
    expandedResults.value.add(index)
  }
}

const insertSingleToChat = (result: SearchResult, index: number) => {
  const content = `**검색 결과** (유사도: ${Math.round(result.score * 100)}%)\n\n${result.content}`
  emit('insertToChat', content)
  emit('resultSelected', result)
  
  toast.success('채팅에 추가됨', {
    description: '검색 결과가 채팅에 추가되었습니다.'
  })
}

const insertAllToChat = () => {
  const content = searchResults.value
    .map((result, index) => 
      `**문서 ${index + 1}** (유사도: ${Math.round(result.score * 100)}%)\n${result.content}`
    )
    .join('\n\n---\n\n')
  
  emit('insertToChat', `**검색 결과 요약**\n\n${content}`)
  
  toast.success('모든 결과 추가됨', {
    description: `${searchResults.value.length}개의 검색 결과가 채팅에 추가되었습니다.`
  })
}

const copyToClipboard = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    toast.success('복사됨', {
      description: '내용이 클립보드에 복사되었습니다.'
    })
  } catch (error) {
    toast.error('복사 실패', {
      description: '클립보드 복사 중 오류가 발생했습니다.'
    })
  }
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

mark {
  background-color: #fef3c7;
  padding: 0 2px;
  border-radius: 2px;
}

.dark mark {
  background-color: #92400e;
  color: #fef3c7;
}
</style>