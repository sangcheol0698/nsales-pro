<template>
  <div 
    class="flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all duration-200"
    :class="{
      'bg-green-50 border-green-200 dark:bg-green-950/30 dark:border-green-800': hasVectorStore && isActive,
      'bg-blue-50 border-blue-200 dark:bg-blue-950/30 dark:border-blue-800': hasVectorStore && !isActive,
      'bg-muted/50 border-muted-foreground/20': !hasVectorStore
    }"
  >
    <!-- 상태 아이콘 -->
    <div class="flex-shrink-0">
      <Database 
        v-if="hasVectorStore" 
        class="h-3 w-3"
        :class="{
          'text-green-600 dark:text-green-400': isActive,
          'text-blue-600 dark:text-blue-400': !isActive
        }"
      />
      <Zap 
        v-else 
        class="h-3 w-3 text-muted-foreground"
      />
    </div>

    <!-- 상태 정보 -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-1">
        <span 
          class="text-xs font-medium"
          :class="{
            'text-green-700 dark:text-green-300': hasVectorStore && isActive,
            'text-blue-700 dark:text-blue-300': hasVectorStore && !isActive,
            'text-muted-foreground': !hasVectorStore
          }"
        >
          {{ statusText }}
        </span>
        
        <!-- 파일 수 표시 -->
        <Badge 
          v-if="fileCount > 0" 
          variant="secondary" 
          class="text-xs h-3 px-1"
        >
          {{ fileCount }}
        </Badge>
        
        <!-- 활성 표시 -->
        <div 
          v-if="hasVectorStore && isActive"
          class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"
        ></div>
      </div>
      
      <!-- 세부 정보 (확장 시) -->
      <div v-if="expanded && hasVectorStore" class="text-xs text-muted-foreground mt-0.5">
        {{ detailText }}
      </div>
    </div>

    <!-- 액션 버튼 -->
    <div class="flex items-center gap-1">
      <!-- 토글 버튼 (확장/축소) -->
      <Button
        v-if="hasVectorStore"
        variant="ghost"
        size="sm"
        @click="toggleExpanded"
        class="h-5 w-5 p-0"
      >
        <ChevronDown 
          class="h-2.5 w-2.5 transition-transform" 
          :class="{ 'rotate-180': expanded }"
        />
      </Button>
      
      <!-- 새로고침 버튼 -->
      <Button
        variant="ghost"
        size="sm"
        @click="refresh"
        :disabled="isLoading"
        class="h-5 w-5 p-0"
      >
        <RotateCcw 
          class="h-2.5 w-2.5" 
          :class="{ 'animate-spin': isLoading }"
        />
      </Button>
      
      <!-- 설정 버튼 -->
      <Button
        variant="ghost"
        size="sm"
        @click="openSettings"
        class="h-5 w-5 p-0"
      >
        <Settings class="h-2.5 w-2.5" />
      </Button>
    </div>
  </div>

  <!-- 확장된 정보 패널 -->
  <Transition
    enter-active-class="transition-all duration-200 ease-out"
    leave-active-class="transition-all duration-150 ease-in"
    enter-from-class="opacity-0 scale-95 -translate-y-1"
    leave-to-class="opacity-0 scale-95 -translate-y-1"
  >
    <div 
      v-if="expanded && hasVectorStore" 
      class="mt-2 p-3 bg-card border border-border rounded-lg shadow-sm"
    >
      <div class="space-y-2">
        <!-- 벡터 스토어 정보 -->
        <div class="grid grid-cols-2 gap-3 text-xs">
          <div class="space-y-1">
            <div class="text-muted-foreground">전체 문서</div>
            <div class="font-medium">{{ vectorStoreInfo?.file_counts?.total || 0 }}</div>
          </div>
          <div class="space-y-1">
            <div class="text-muted-foreground">처리 완료</div>
            <div class="font-medium text-green-600">{{ vectorStoreInfo?.file_counts?.completed || 0 }}</div>
          </div>
          <div class="space-y-1">
            <div class="text-muted-foreground">처리 중</div>
            <div class="font-medium text-blue-600">{{ vectorStoreInfo?.file_counts?.in_progress || 0 }}</div>
          </div>
          <div class="space-y-1">
            <div class="text-muted-foreground">실패</div>
            <div class="font-medium text-red-600">{{ vectorStoreInfo?.file_counts?.failed || 0 }}</div>
          </div>
        </div>
        
        <!-- 진행률 바 -->
        <div v-if="progressPercentage < 100" class="space-y-1">
          <div class="flex justify-between text-xs">
            <span class="text-muted-foreground">처리 진행률</span>
            <span class="font-medium">{{ progressPercentage }}%</span>
          </div>
          <div class="w-full bg-muted rounded-full h-1.5">
            <div 
              class="bg-primary h-1.5 rounded-full transition-all duration-300"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>
        </div>
        
        <!-- 빠른 액션 -->
        <div class="flex items-center gap-1 pt-1">
          <Button
            variant="outline"
            size="sm"
            @click="openVectorStorePanel"
            class="h-6 text-xs flex-1"
          >
            <Search class="h-2.5 w-2.5 mr-1" />
            검색
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="openFileUpload"
            class="h-6 text-xs flex-1"
          >
            <Upload class="h-2.5 w-2.5 mr-1" />
            업로드
          </Button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { 
  Database, 
  Zap, 
  ChevronDown, 
  RotateCcw, 
  Settings,
  Search,
  Upload
} from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Badge } from '@/core/components/ui/badge'

interface Props {
  sessionId: string
  autoRefresh?: boolean
  refreshInterval?: number
}

interface VectorStoreInfo {
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

interface Emits {
  openPanel: []
  openUpload: []
  settingsClick: []
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: true,
  refreshInterval: 30000 // 30초
})

const emit = defineEmits<Emits>()

// 상태
const vectorStoreInfo = ref<VectorStoreInfo | null>(null)
const isLoading = ref(false)
const expanded = ref(false)

// 계산된 속성
const hasVectorStore = computed(() => vectorStoreInfo.value !== null)

const isActive = computed(() => {
  if (!vectorStoreInfo.value) return false
  return vectorStoreInfo.value.file_counts.total > 0
})

const fileCount = computed(() => {
  return vectorStoreInfo.value?.file_counts?.total || 0
})

const progressPercentage = computed(() => {
  if (!vectorStoreInfo.value || vectorStoreInfo.value.file_counts.total === 0) return 100
  
  const { completed, total } = vectorStoreInfo.value.file_counts
  return Math.round((completed / total) * 100)
})

const statusText = computed(() => {
  if (!hasVectorStore.value) {
    return '지식베이스 없음'
  }
  
  if (!isActive.value) {
    return '지식베이스 비어있음'
  }
  
  if (progressPercentage.value < 100) {
    return '문서 처리 중'
  }
  
  return '지식베이스 활성'
})

const detailText = computed(() => {
  if (!vectorStoreInfo.value) return ''
  
  const { completed, total, in_progress } = vectorStoreInfo.value.file_counts
  
  if (in_progress > 0) {
    return `${completed}/${total} 완료, ${in_progress}개 처리 중`
  }
  
  return `${total}개 문서 인덱싱 완료`
})

// 메서드
const loadVectorStoreInfo = async () => {
  if (!props.sessionId || isLoading.value) return
  
  try {
    isLoading.value = true
    
    const response = await fetch(`/api/v1/sessions/${props.sessionId}/vector-store`)
    
    if (response.ok) {
      const data = await response.json()
      vectorStoreInfo.value = data.vector_store || null
    } else if (response.status === 404) {
      vectorStoreInfo.value = null
    } else {
      throw new Error('Failed to load vector store info')
    }
  } catch (error) {
    console.error('Error loading vector store info:', error)
    vectorStoreInfo.value = null
  } finally {
    isLoading.value = false
  }
}

const refresh = () => {
  loadVectorStoreInfo()
}

const toggleExpanded = () => {
  expanded.value = !expanded.value
}

const openSettings = () => {
  emit('settingsClick')
}

const openVectorStorePanel = () => {
  emit('openPanel')
}

const openFileUpload = () => {
  emit('openUpload')
}

// 자동 새로고침 설정
let refreshTimer: NodeJS.Timeout | null = null

const startAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  
  if (props.autoRefresh && props.refreshInterval > 0) {
    refreshTimer = setInterval(() => {
      loadVectorStoreInfo()
    }, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 라이프사이클
watch(() => props.sessionId, () => {
  if (props.sessionId) {
    loadVectorStoreInfo()
    startAutoRefresh()
  } else {
    vectorStoreInfo.value = null
    stopAutoRefresh()
  }
}, { immediate: true })

watch(() => [props.autoRefresh, props.refreshInterval], () => {
  stopAutoRefresh()
  startAutoRefresh()
})

onMounted(() => {
  if (props.sessionId) {
    loadVectorStoreInfo()
    startAutoRefresh()
  }
})

// 컴포넌트 언마운트 시 타이머 정리
import { onUnmounted } from 'vue'
onUnmounted(() => {
  stopAutoRefresh()
})
</script>