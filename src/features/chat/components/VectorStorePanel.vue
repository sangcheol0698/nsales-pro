<template>
  <div class="bg-card border border-border rounded-lg p-4">
    <!-- 헤더 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <Database class="h-5 w-5 text-primary" />
        <h3 class="font-semibold text-sm">지식 베이스</h3>
        <Badge v-if="vectorStore" variant="secondary" class="text-xs">
          {{ vectorStore.file_counts?.total || 0 }}개 문서
        </Badge>
      </div>
      <Button
        variant="ghost"
        size="sm"
        @click="refreshVectorStore"
        :disabled="isLoading"
        class="h-8 w-8 p-0"
      >
        <RotateCcw class="h-3 w-3" :class="{ 'animate-spin': isLoading }" />
      </Button>
    </div>

    <!-- 벡터 스토어 상태 -->
    <div v-if="!vectorStore && !isLoading" class="text-center py-6">
      <FileSearch class="h-8 w-8 mx-auto text-muted-foreground mb-2" />
      <p class="text-sm text-muted-foreground mb-3">
        아직 업로드된 문서가 없습니다
      </p>
      <p class="text-xs text-muted-foreground">
        파일을 업로드하면 자동으로 지식 베이스에 추가됩니다
      </p>
    </div>

    <!-- 벡터 스토어 정보 -->
    <div v-else-if="vectorStore" class="space-y-4">
      <!-- 기본 정보 -->
      <div class="grid grid-cols-2 gap-3">
        <div class="p-3 bg-muted/50 rounded-lg">
          <div class="text-xs text-muted-foreground mb-1">전체 문서</div>
          <div class="text-lg font-semibold">
            {{ vectorStore.file_counts?.total || 0 }}
          </div>
        </div>
        <div class="p-3 bg-muted/50 rounded-lg">
          <div class="text-xs text-muted-foreground mb-1">처리 완료</div>
          <div class="text-lg font-semibold text-green-600">
            {{ vectorStore.file_counts?.completed || 0 }}
          </div>
        </div>
      </div>

      <!-- 검색 기능 -->
      <div class="space-y-2">
        <Label class="text-xs font-medium">문서 검색</Label>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-3 w-3 text-muted-foreground" />
          <Input
            v-model="searchQuery"
            placeholder="문서 내용 검색..."
            class="pl-9 h-8 text-xs"
            @keydown.enter="performSearch"
          />
          <Button
            v-if="searchQuery"
            variant="ghost"
            size="sm"
            @click="clearSearch"
            class="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
          >
            <X class="h-3 w-3" />
          </Button>
        </div>
        <Button
          @click="performSearch"
          :disabled="!searchQuery.trim() || isSearching"
          size="sm"
          class="w-full h-7 text-xs"
        >
          <Search v-if="!isSearching" class="h-3 w-3 mr-1" />
          <Loader v-else class="h-3 w-3 mr-1 animate-spin" />
          검색
        </Button>
      </div>

      <!-- 검색 결과 -->
      <div v-if="searchResults.length > 0" class="space-y-2">
        <div class="flex items-center justify-between">
          <Label class="text-xs font-medium">검색 결과</Label>
          <Badge variant="outline" class="text-xs">
            {{ searchResults.length }}건
          </Badge>
        </div>
        <div class="space-y-1 max-h-40 overflow-y-auto">
          <div
            v-for="(result, index) in searchResults"
            :key="index"
            class="p-2 bg-muted/30 rounded border cursor-pointer hover:bg-muted/50 transition-colors"
            @click="selectSearchResult(result)"
          >
            <div class="text-xs font-medium mb-1 truncate">
              유사도: {{ Math.round(result.score * 100) }}%
            </div>
            <div class="text-xs text-muted-foreground line-clamp-2">
              {{ result.content }}
            </div>
          </div>
        </div>
      </div>

      <!-- 최근 업로드된 파일 -->
      <div v-if="recentFiles.length > 0" class="space-y-2">
        <Label class="text-xs font-medium">최근 문서</Label>
        <div class="space-y-1">
          <div
            v-for="file in recentFiles"
            :key="file.id"
            class="flex items-center gap-2 p-2 bg-muted/30 rounded"
          >
            <FileText class="h-3 w-3 text-muted-foreground flex-shrink-0" />
            <span class="text-xs truncate flex-1">{{ file.name }}</span>
            <Badge
              :variant="file.status === 'completed' ? 'default' : 'secondary'"
              class="text-xs px-1 h-4"
            >
              {{ file.status }}
            </Badge>
          </div>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <Loader class="h-6 w-6 animate-spin text-primary" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { 
  Database, 
  RotateCcw, 
  FileSearch, 
  Search, 
  X, 
  Loader,
  FileText
} from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Input } from '@/core/components/ui/input'
import { Label } from '@/core/components/ui/label'
import { Badge } from '@/core/components/ui/badge'
import { useToast } from '@/core/composables'

interface Props {
  sessionId: string
}

interface VectorStore {
  id: string
  name: string
  file_counts: {
    total: number
    completed: number
    in_progress: number
    failed: number
  }
  created_at: string
}

interface SearchResult {
  content: string
  score: number
  file_id: string
  metadata: Record<string, any>
}

interface FileInfo {
  id: string
  name: string
  status: 'completed' | 'in_progress' | 'failed'
  created_at: string
}

const props = defineProps<Props>()
const toast = useToast()

// 상태
const vectorStore = ref<VectorStore | null>(null)
const isLoading = ref(false)
const isSearching = ref(false)
const searchQuery = ref('')
const searchResults = ref<SearchResult[]>([])
const recentFiles = ref<FileInfo[]>([])

// API 호출 함수들
const loadVectorStore = async () => {
  if (!props.sessionId) return
  
  try {
    isLoading.value = true
    const response = await fetch(`/api/v1/sessions/${props.sessionId}/vector-store`)
    
    if (response.ok) {
      const data = await response.json()
      vectorStore.value = data.vector_store || null
    } else if (response.status === 404) {
      // 벡터 스토어가 없는 경우
      vectorStore.value = null
    }
  } catch (error) {
    console.error('Failed to load vector store:', error)
  } finally {
    isLoading.value = false
  }
}

const performSearch = async () => {
  if (!searchQuery.value.trim() || !props.sessionId) return
  
  try {
    isSearching.value = true
    const response = await fetch(
      `/api/v1/sessions/${props.sessionId}/vector-store/search`, 
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery.value,
          limit: 5
        })
      }
    )
    
    if (response.ok) {
      const data = await response.json()
      searchResults.value = data.results || []
      
      if (searchResults.value.length === 0) {
        toast.info('검색 결과 없음', {
          description: '검색어와 일치하는 문서를 찾을 수 없습니다.'
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

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
}

const selectSearchResult = (result: SearchResult) => {
  // 검색 결과를 클릭했을 때의 동작 (예: 하이라이트, 스크롤 등)
  toast.success('관련 문서', {
    description: `유사도 ${Math.round(result.score * 100)}%의 문서를 찾았습니다.`
  })
}

const refreshVectorStore = () => {
  loadVectorStore()
}

const createVectorStore = async () => {
  if (!props.sessionId) return
  
  try {
    isLoading.value = true
    const response = await fetch(`/api/v1/sessions/${props.sessionId}/vector-store`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: `Session ${props.sessionId.substring(0, 8)} Knowledge Base`
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      await loadVectorStore()
      toast.success('지식 베이스 생성됨', {
        description: '새로운 지식 베이스가 생성되었습니다.'
      })
    }
  } catch (error) {
    console.error('Failed to create vector store:', error)
    toast.error('생성 실패', {
      description: '지식 베이스 생성 중 오류가 발생했습니다.'
    })
  } finally {
    isLoading.value = false
  }
}

// 세션 ID 변경 시 벡터 스토어 다시 로드
watch(() => props.sessionId, () => {
  if (props.sessionId) {
    loadVectorStore()
  }
}, { immediate: true })

onMounted(() => {
  if (props.sessionId) {
    loadVectorStore()
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>