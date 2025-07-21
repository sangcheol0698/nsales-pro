<template>
  <SidebarLayout>
    <div class="flex h-full w-full overflow-hidden" @keydown="handleGlobalKeydown">
      <!-- 왼쪽 패널: 채팅 세션 목록 -->
      <aside
        class="w-80 bg-background border-r border-border flex flex-col"
        role="complementary"
        :aria-label="$t ? $t('chat.chatSessions') : '채팅 세션 목록'"
      >
        <!-- 세션 헤더 -->
        <div class="p-4 border-b border-border flex-shrink-0">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <div class="p-1.5 bg-primary/10 rounded-lg">
                <Bot class="h-4 w-4 text-primary" />
              </div>
              <div>
                <h2 class="text-sm font-semibold text-foreground">AI Assistant</h2>
              </div>
            </div>

            <Button
              size="sm"
              @click="createNewChat"
              class="h-8 px-3 rounded-lg"
            >
              <Plus class="h-3 w-3 mr-1" />
              <span class="text-xs">새 채팅</span>
            </Button>
          </div>

          <!-- 검색 -->
          <div class="relative mb-3">
            <Search
              class="absolute left-3 top-1/2 transform -translate-y-1/2 h-3 w-3 text-muted-foreground"
            />
            <Input
              ref="searchInputRef"
              v-model="searchQuery"
              placeholder="채팅 검색..."
              class="pl-9 h-8 text-sm bg-background/50 border-border/50 rounded-lg focus:bg-background"
              @keydown.escape="searchQuery = ''"
            />
          </div>

          <!-- 필터 및 정렬 -->
          <div class="flex items-center gap-1">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" class="h-7 px-2 flex-1 text-xs">
                  <Filter class="h-3 w-3 mr-1" />
                  필터
                  <Badge
                    v-if="activeFilters.length > 0"
                    variant="secondary"
                    class="ml-1 h-3 w-3 p-0 text-xs"
                  >
                    {{ activeFilters.length }}
                  </Badge>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" class="w-48">
                <DropdownMenuLabel>시간 필터</DropdownMenuLabel>
                <DropdownMenuItem @click="setTimeFilter('today')">
                  <CheckCircle2 v-if="timeFilter === 'today'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  오늘
                </DropdownMenuItem>
                <DropdownMenuItem @click="setTimeFilter('week')">
                  <CheckCircle2 v-if="timeFilter === 'week'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  이번 주
                </DropdownMenuItem>
                <DropdownMenuItem @click="setTimeFilter('month')">
                  <CheckCircle2 v-if="timeFilter === 'month'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  이번 달
                </DropdownMenuItem>
                <DropdownMenuItem @click="setTimeFilter('all')">
                  <CheckCircle2 v-if="timeFilter === 'all'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  전체
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" class="h-7 px-2 flex-1 text-xs">
                  <ArrowUpDown class="h-3 w-3 mr-1" />
                  정렬
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" class="w-40">
                <DropdownMenuItem @click="setSortBy('recent')">
                  <CheckCircle2 v-if="sortBy === 'recent'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  최신순
                </DropdownMenuItem>
                <DropdownMenuItem @click="setSortBy('oldest')">
                  <CheckCircle2 v-if="sortBy === 'oldest'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  오래된순
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <!-- 벡터 스토어 상태 (세션이 있을 때만) -->
          <div v-if="currentSessionId" class="mt-3">
            <VectorStoreStatus
              :session-id="currentSessionId"
              @open-panel="toggleKnowledgePanel"
              @open-upload="showUploadZone = true"
              @settings-click="showVectorStoreSettings = true"
            />
          </div>
        </div>

        <!-- 세션 목록 -->
        <div class="flex-1 overflow-y-auto">
          <div class="p-2 space-y-1">
            <div
              v-for="(session, index) in filteredSessions"
              :key="session.id"
              class="group p-3 rounded-lg cursor-pointer hover:bg-muted/50 transition-all duration-200 border border-transparent hover:border-border/50"
              :class="{
                'bg-muted shadow-sm border-border/50 ring-1 ring-primary/20':
                  currentSessionId === session.id,
              }"
              @click="selectSession(session.id)"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <div
                      class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                      :class="session.messageCount > 0 ? 'bg-primary' : 'bg-muted-foreground/50'"
                    ></div>
                    <h4 class="font-medium truncate text-foreground text-sm">{{ session.title }}</h4>
                    <Badge
                      v-if="session.messageCount > 0"
                      variant="secondary"
                      class="text-xs px-1.5 py-0.5 h-4 ml-auto flex-shrink-0"
                    >
                      {{ session.messageCount }}
                    </Badge>
                  </div>
                  <div class="flex items-center gap-2 ml-4 text-xs text-muted-foreground">
                    <span>{{ formatDate(session.updatedAt) }}</span>
                  </div>
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      class="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 rounded-md hover:bg-muted/80"
                    >
                      <MoreVertical class="h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem @click="renameSession(session)">
                      <Edit2 class="h-3 w-3 mr-2" />
                      이름 변경
                    </DropdownMenuItem>
                    <DropdownMenuItem @click="deleteSession(session.id)" class="text-destructive">
                      <Trash2 class="h-3 w-3 mr-2" />
                      삭제
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>

            <div v-if="sessions.length === 0" class="text-center py-12 text-muted-foreground">
              <MessageCircle class="h-10 w-10 mx-auto mb-3 opacity-50" />
              <p class="text-sm font-medium">아직 채팅이 없습니다</p>
              <p class="text-xs mt-1">새 채팅을 시작해보세요!</p>
            </div>
          </div>
        </div>
      </aside>

      <!-- 중앙 패널: 메인 채팅 영역 -->
      <main 
        class="flex-1 flex flex-col min-w-0 overflow-hidden relative" 
        role="main"
        :class="{ 'pr-0': !showKnowledgePanel, 'pr-4': showKnowledgePanel }"
      >
        <!-- 채팅 위젯 -->
        <div v-if="currentSessionId" class="flex-1 flex flex-col">
          <!-- 상단 툴바 -->
          <div class="flex items-center justify-between p-4 border-b border-border bg-background/95 backdrop-blur-sm">
            <div class="flex items-center gap-3">
              <h1 class="text-lg font-semibold">{{ getCurrentSessionTitle() }}</h1>
              <Badge variant="outline" class="text-xs">
                {{ getCurrentSessionMessageCount() }}개 메시지
              </Badge>
            </div>
            
            <div class="flex items-center gap-2">
              <!-- 파일 업로드 토글 -->
              <Button
                variant="outline"
                size="sm"
                @click="showUploadZone = !showUploadZone"
                :class="{ 'bg-primary/10 border-primary/30': showUploadZone }"
                class="h-8 px-3"
              >
                <Upload class="h-3 w-3 mr-1" />
                <span class="text-xs">파일 업로드</span>
              </Button>
              
              <!-- 지식베이스 검색 토글 -->
              <Button
                variant="outline"
                size="sm"
                @click="showKnowledgeSearch = !showKnowledgeSearch"
                :class="{ 'bg-primary/10 border-primary/30': showKnowledgeSearch }"
                class="h-8 px-3"
              >
                <Search class="h-3 w-3 mr-1" />
                <span class="text-xs">지식 검색</span>
              </Button>
              
              <!-- 지식 패널 토글 -->
              <Button
                variant="outline"
                size="sm"
                @click="toggleKnowledgePanel"
                :class="{ 'bg-primary/10 border-primary/30': showKnowledgePanel }"
                class="h-8 px-3"
              >
                <PanelRight class="h-3 w-3 mr-1" />
                <span class="text-xs">지식 패널</span>
              </Button>
            </div>
          </div>

          <!-- 파일 업로드 존 (확장 시) -->
          <div v-if="showUploadZone" class="border-b border-border bg-muted/20">
            <div class="p-4">
              <FileUploadDropZone
                :session-id="currentSessionId"
                @file-uploaded="handleFileUploaded"
                @files-cleared="handleFilesCleared"
              />
            </div>
          </div>

          <!-- 지식베이스 검색 (확장 시) -->
          <div v-if="showKnowledgeSearch" class="border-b border-border bg-muted/20">
            <div class="p-4">
              <KnowledgeBaseSearch
                :session-id="currentSessionId"
                @insert-to-chat="insertToChat"
                @result-selected="handleSearchResultSelected"
              />
            </div>
          </div>

          <!-- 채팅 위젯 -->
          <div class="flex-1 flex">
            <div class="flex-1">
              <ChatWidget 
                :key="currentSessionId" 
                :session-id="currentSessionId" 
                @message-insert="insertToChat"
              />
            </div>
          </div>
        </div>

        <!-- 빈 상태 -->
        <div
          v-else
          class="flex-1 flex items-center justify-center p-4"
        >
          <div class="text-center max-w-md mx-auto">
            <div class="relative mb-6">
              <div class="absolute inset-0 bg-primary/10 blur-3xl rounded-full"></div>
              <Bot class="relative h-12 lg:h-16 w-12 lg:w-16 mx-auto text-primary" />
            </div>
            <h3 class="text-lg lg:text-xl font-bold mb-2 text-foreground">
              AI Assistant에 오신 것을 환영합니다
            </h3>
            <p class="text-muted-foreground mb-6 text-sm lg:text-base leading-relaxed">
              영업 데이터 분석, 프로젝트 정보 조회, 업무 도움 등<br class="hidden sm:block" />
              무엇이든 물어보세요. 문서를 업로드하면 자동으로 지식베이스에 추가됩니다.
            </p>
            <div class="space-y-3">
              <Button
                @click="createNewChat"
                size="default"
                class="bg-primary hover:bg-primary/90 text-primary-foreground shadow-md hover:shadow-lg transition-all duration-200 rounded-lg px-6 py-2"
              >
                <MessageCircle class="h-4 w-4 mr-2" />
                채팅 시작하기
              </Button>
              
              <div class="flex items-center gap-2 justify-center">
                <div class="h-px bg-border flex-1"></div>
                <span class="text-xs text-muted-foreground px-2">또는</span>
                <div class="h-px bg-border flex-1"></div>
              </div>
              
              <Button
                @click="() => { createNewChat(); showUploadZone = true; }"
                variant="outline"
                size="default"
                class="px-6 py-2"
              >
                <Upload class="h-4 w-4 mr-2" />
                파일 업로드로 시작
              </Button>
            </div>
          </div>
        </div>
      </main>

      <!-- 오른쪽 패널: 지식 베이스 패널 -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        leave-active-class="transition-all duration-200 ease-in"
        enter-from-class="translate-x-full opacity-0"
        leave-to-class="translate-x-full opacity-0"
      >
        <aside
          v-if="showKnowledgePanel && currentSessionId"
          class="w-96 bg-background border-l border-border flex flex-col overflow-hidden"
          role="complementary"
        >
          <!-- 패널 헤더 -->
          <div class="p-4 border-b border-border flex-shrink-0">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <Database class="h-4 w-4 text-primary" />
                <h3 class="font-semibold text-sm">지식 베이스</h3>
              </div>
              <Button
                variant="ghost"
                size="sm"
                @click="toggleKnowledgePanel"
                class="h-6 w-6 p-0"
              >
                <X class="h-3 w-3" />
              </Button>
            </div>
          </div>

          <!-- 패널 내용 -->
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <VectorStorePanel :session-id="currentSessionId" />
          </div>
        </aside>
      </Transition>
    </div>

    <!-- 다이얼로그들 -->
    <Dialog v-model:open="isRenameDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>채팅 이름 변경</DialogTitle>
        </DialogHeader>
        <div class="py-4">
          <Input
            v-model="newSessionTitle"
            placeholder="새 채팅 이름을 입력하세요"
            @keydown.enter="confirmRename"
          />
        </div>
        <DialogFooter>
          <Button variant="outline" @click="isRenameDialogOpen = false">취소</Button>
          <Button @click="confirmRename">변경</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- 벡터 스토어 설정 다이얼로그 -->
    <Dialog v-model:open="showVectorStoreSettings">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>지식베이스 설정</DialogTitle>
        </DialogHeader>
        <div class="py-4 space-y-4">
          <div class="space-y-2">
            <Label>자동 업로드</Label>
            <div class="flex items-center gap-2">
              <Switch v-model:checked="autoUploadToVectorStore" />
              <span class="text-sm text-muted-foreground">
                파일 업로드 시 자동으로 지식베이스에 추가
              </span>
            </div>
          </div>
          <div class="space-y-2">
            <Label>검색 결과 수</Label>
            <select v-model="defaultSearchLimit" class="w-full p-2 border rounded">
              <option value="3">3개</option>
              <option value="5">5개</option>
              <option value="10">10개</option>
            </select>
          </div>
        </div>
        <DialogFooter>
          <Button @click="showVectorStoreSettings = false">확인</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowUpDown,
  Bot,
  CheckCircle2,
  Edit2,
  Filter,
  MessageCircle,
  MoreVertical,
  Plus,
  Search,
  Trash2,
  X,
  Upload,
  PanelRight,
  Database
} from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Input } from '@/core/components/ui/input'
import { Label } from '@/core/components/ui/label'
import { Switch } from '@/core/components/ui/switch'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/core/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu'
import { Badge } from '@/core/components/ui/badge'
import { useToast } from '@/core/composables'
import { SidebarLayout } from '@/shared/components/sidebar'
import ChatWidget from '../components/ChatWidget.vue'
import VectorStorePanel from '../components/VectorStorePanel.vue'
import VectorStoreStatus from '../components/VectorStoreStatus.vue'
import FileUploadDropZone from '../components/FileUploadDropZone.vue'
import KnowledgeBaseSearch from '../components/KnowledgeBaseSearch.vue'
import { ChatRepository } from '../repository/ChatRepository'
import type { ChatSession } from '../entity/ChatMessage'

const toast = useToast()
const chatRepository = new ChatRepository()
const route = useRoute()
const router = useRouter()

// 기존 상태들
const sessions = ref<ChatSession[]>([])
const currentSessionId = ref<string>()
const searchQuery = ref('')
const isRenameDialogOpen = ref(false)
const sessionToRename = ref<ChatSession>()
const newSessionTitle = ref('')

// 새로운 UI 상태들
const showKnowledgePanel = ref(false)
const showUploadZone = ref(false)
const showKnowledgeSearch = ref(false)
const showVectorStoreSettings = ref(false)

// 설정들
const autoUploadToVectorStore = ref(true)
const defaultSearchLimit = ref(5)

// 필터 상태
const timeFilter = ref<'today' | 'week' | 'month' | 'all'>('all')
const messageCountFilter = ref<'none' | 'active' | 'empty'>('none')
const sortBy = ref<'recent' | 'oldest' | 'alphabetical' | 'messages'>('recent')

// 계산된 속성들
const activeFilters = computed(() => {
  const filters: Array<{key: string, label: string}> = []
  if (timeFilter.value !== 'all') {
    const labels = { today: '오늘', week: '이번 주', month: '이번 달' }
    filters.push({ key: 'time', label: labels[timeFilter.value] })
  }
  if (messageCountFilter.value !== 'none') {
    const labels = { active: '활성 채팅', empty: '비어있는 채팅' }
    filters.push({ key: 'messageCount', label: labels[messageCountFilter.value] })
  }
  return filters
})

const filteredSessions = computed(() => {
  let filtered = [...sessions.value]
  
  if (searchQuery.value) {
    filtered = filtered.filter(session =>
      session.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  
  // 시간 필터 적용
  if (timeFilter.value !== 'all') {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const monthAgo = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
    
    filtered = filtered.filter(session => {
      const sessionDate = new Date(session.updatedAt)
      switch (timeFilter.value) {
        case 'today': return sessionDate >= today
        case 'week': return sessionDate >= weekAgo
        case 'month': return sessionDate >= monthAgo
        default: return true
      }
    })
  }
  
  // 메시지 수 필터 적용
  if (messageCountFilter.value !== 'none') {
    filtered = filtered.filter(session => {
      switch (messageCountFilter.value) {
        case 'active': return session.messageCount >= 5
        case 'empty': return session.messageCount === 0
        default: return true
      }
    })
  }
  
  // 정렬 적용
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'recent': return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      case 'oldest': return new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime()
      case 'alphabetical': return a.title.localeCompare(b.title)
      case 'messages': return b.messageCount - a.messageCount
      default: return 0
    }
  })
  
  return filtered
})

// 메서드들
const getCurrentSessionTitle = () => {
  const session = sessions.value.find(s => s.id === currentSessionId.value)
  return session?.title || '새 채팅'
}

const getCurrentSessionMessageCount = () => {
  const session = sessions.value.find(s => s.id === currentSessionId.value)
  return session?.messageCount || 0
}

const createNewChat = async () => {
  try {
    const newSession = await chatRepository.createSession()
    sessions.value.unshift(newSession)
    router.push({ name: 'chatEnhancedSession', params: { sessionId: newSession.id } })
  } catch (error) {
    console.error('Create chat error:', error)
    toast.error('새 채팅 생성 실패')
  }
}

const selectSession = (sessionId: string) => {
  if (route.params.sessionId !== sessionId) {
    router.push({ name: 'chatEnhancedSession', params: { sessionId } })
  }
}

const toggleKnowledgePanel = () => {
  showKnowledgePanel.value = !showKnowledgePanel.value
}

const setTimeFilter = (filter: typeof timeFilter.value) => {
  timeFilter.value = filter
}

const setSortBy = (sort: typeof sortBy.value) => {
  sortBy.value = sort
}

const formatDate = (date: Date | string) => {
  const now = new Date()
  const targetDate = typeof date === 'string' ? new Date(date) : date
  const diffTime = now.getTime() - targetDate.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return '오늘'
  if (diffDays === 1) return '어제'
  if (diffDays < 7) return `${diffDays}일 전`
  
  return new Intl.DateTimeFormat('ko-KR', {
    month: 'short',
    day: 'numeric',
  }).format(targetDate)
}

const handleFileUploaded = (file: any) => {
  toast.success('파일 업로드 완료', {
    description: `${file.name}이 지식베이스에 추가되었습니다.`
  })
}

const handleFilesCleared = () => {
  toast.info('파일 목록 정리됨')
}

const insertToChat = (content: string) => {
  // ChatWidget으로 메시지 삽입
  toast.success('채팅에 추가됨')
}

const handleSearchResultSelected = (result: any) => {
  console.log('Search result selected:', result)
}

const renameSession = (session: ChatSession) => {
  sessionToRename.value = session
  newSessionTitle.value = session.title
  isRenameDialogOpen.value = true
}

const confirmRename = async () => {
  if (!sessionToRename.value || !newSessionTitle.value.trim()) return
  
  try {
    await chatRepository.updateSession(sessionToRename.value.id, newSessionTitle.value)
    
    const index = sessions.value.findIndex(s => s.id === sessionToRename.value?.id)
    if (index !== -1) {
      sessions.value[index].title = newSessionTitle.value
    }
    
    isRenameDialogOpen.value = false
    toast.success('채팅 이름 변경 완료')
  } catch (error) {
    console.error('Rename error:', error)
    toast.error('채팅 이름 변경 실패')
  }
}

const deleteSession = async (sessionId: string) => {
  try {
    await chatRepository.deleteSession(sessionId)
    
    const index = sessions.value.findIndex(s => s.id === sessionId)
    if (index !== -1) {
      sessions.value.splice(index, 1)
    }
    
    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        router.push({ name: 'chatSession', params: { sessionId: sessions.value[0].id } })
      } else {
        router.push({ name: 'chat' })
      }
    }
    
    toast.success('채팅 삭제 완료')
  } catch (error) {
    console.error('Delete error:', error)
    toast.error('채팅 삭제 실패')
  }
}

const loadSessions = async () => {
  try {
    await chatRepository.initializeDemoData()
    const result = await chatRepository.getSessions({ page: 0, size: 50 })
    sessions.value = result.sessions
  } catch (error) {
    console.error('Load sessions error:', error)
    toast.error('채팅 목록 로드 실패')
  }
}

const handleGlobalKeydown = (event: KeyboardEvent) => {
  // Escape로 패널들 닫기
  if (event.key === 'Escape') {
    showKnowledgePanel.value = false
    showUploadZone.value = false
    showKnowledgeSearch.value = false
  }
  
  // Ctrl/Cmd + K로 지식 검색 토글
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault()
    showKnowledgeSearch.value = !showKnowledgeSearch.value
  }
  
  // Ctrl/Cmd + U로 파일 업로드 토글
  if ((event.ctrlKey || event.metaKey) && event.key === 'u') {
    event.preventDefault()
    showUploadZone.value = !showUploadZone.value
  }
}

// URL 파라미터 감지
watch(() => route.params.sessionId, (newSessionId) => {
  if (typeof newSessionId === 'string') {
    currentSessionId.value = newSessionId
  } else {
    currentSessionId.value = undefined
  }
}, { immediate: true })

// 세션 자동 리다이렉트
watch([sessions, () => route.path], ([newSessions, newPath]) => {
  if (newPath === '/chat' && newSessions.length > 0 && !currentSessionId.value) {
    router.replace({ name: 'chatSession', params: { sessionId: newSessions[0].id } })
  }
})

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.transition-all {
  transition: all 0.2s ease;
}
</style>