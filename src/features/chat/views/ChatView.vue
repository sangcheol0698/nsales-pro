<template>
  <SidebarLayout>
    <div class="h-full flex bg-background">
      <!-- 사이드바: 채팅 세션 목록 -->
      <div class="w-80 border-r border-border/50 bg-card flex flex-col shadow-sm">
        <div class="p-6 border-b border-border/50 bg-gradient-to-r from-card to-card/95">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3">
              <div class="p-2.5 bg-gradient-to-br from-primary/20 to-primary/10 rounded-xl shadow-sm">
                <Bot class="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 class="text-lg font-bold text-foreground">AI Assistant</h2>
                <p class="text-sm text-foreground/60 font-medium">영업 AI 도우미</p>
              </div>
            </div>
            <Button 
              size="sm" 
              @click="createNewChat" 
              class="rounded-xl shadow-sm hover:shadow-md transition-all duration-200 bg-primary/90 hover:bg-primary"
            >
              <Plus class="h-4 w-4 mr-2" />
              새 채팅
            </Button>
          </div>
          
          <div class="relative">
            <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-foreground/40" />
            <Input
              v-model="searchQuery"
              placeholder="채팅 검색..."
              class="pl-10 bg-background/50 border-border/50 rounded-xl h-10 focus:bg-background"
            />
          </div>
        </div>

      <ScrollArea class="flex-1">
        <div class="p-3 space-y-2">
          <div
            v-for="session in filteredSessions"
            :key="session.id"
            class="group p-4 rounded-xl cursor-pointer hover:bg-background/80 transition-all duration-200 border border-transparent hover:border-border/50"
            :class="{ 'bg-background shadow-sm border-border/50 ring-1 ring-primary/20': currentSessionId === session.id }"
            @click="selectSession(session.id)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <div class="w-2 h-2 bg-primary rounded-full opacity-60"></div>
                  <h4 class="font-medium truncate text-foreground">{{ session.title }}</h4>
                </div>
                <p class="text-xs text-foreground/50 ml-4">
                  {{ formatDate(session.updatedAt) }}
                </p>
              </div>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    class="opacity-0 group-hover:opacity-100 h-8 w-8 p-0 rounded-lg hover:bg-background/80"
                  >
                    <MoreVertical class="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                
                <DropdownMenuContent align="end">
                  <DropdownMenuItem @click="renameSession(session)">
                    <Edit2 class="h-4 w-4 mr-2" />
                    이름 변경
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    @click="deleteSession(session.id)"
                    class="text-destructive focus:text-destructive"
                  >
                    <Trash2 class="h-4 w-4 mr-2" />
                    삭제
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          
          <div v-if="sessions.length === 0" class="text-center py-8 text-foreground/70">
            <MessageCircle class="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>아직 채팅이 없습니다</p>
            <p class="text-sm">새 채팅을 시작해보세요!</p>
          </div>
        </div>
      </ScrollArea>
    </div>

    <!-- 메인 채팅 영역 -->
    <div class="flex-1 flex flex-col">
      <ChatWidget
        v-if="currentSessionId"
        :key="currentSessionId"
        :session-id="currentSessionId"
      />
      
      <div v-else class="flex-1 flex items-center justify-center bg-gradient-to-br from-background to-background/80">
        <div class="text-center max-w-lg mx-auto p-8">
          <div class="relative mb-8">
            <div class="absolute inset-0 bg-primary/10 blur-3xl rounded-full"></div>
            <Bot class="relative h-24 w-24 mx-auto text-primary" />
          </div>
          <h3 class="text-2xl font-bold mb-3 bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
            AI Assistant에 오신 것을 환영합니다
          </h3>
          <p class="text-foreground/70 mb-8 text-lg leading-relaxed">
            영업 데이터 분석, 프로젝트 정보 조회, 업무 도움 등<br>
            무엇이든 물어보세요.
          </p>
          <Button 
            @click="createNewChat" 
            size="lg"
            class="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-200 rounded-xl px-8 py-3"
          >
            <MessageCircle class="h-5 w-5 mr-2" />
            채팅 시작하기
          </Button>
        </div>
      </div>
    </div>
    </div>

    <!-- 세션 이름 변경 다이얼로그 -->
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
        <Button variant="outline" @click="isRenameDialogOpen = false">
          취소
        </Button>
        <Button @click="confirmRename">
          변경
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Plus,
  Search,
  MoreVertical,
  Edit2,
  Trash2,
  MessageCircle,
  Bot,
} from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Input } from '@/core/components/ui/input'
import { ScrollArea } from '@/core/components/ui/scroll-area'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/core/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu'
import { useToast } from '@/core/composables'
import { SidebarLayout } from '@/shared/components/sidebar'
import ChatWidget from '../components/ChatWidget.vue'
import { ChatRepository } from '../repository/ChatRepository'
import type { ChatSession } from '../entity/ChatMessage'

const toast = useToast()
const chatRepository = new ChatRepository()

const sessions = ref<ChatSession[]>([])
const currentSessionId = ref<string>()
const searchQuery = ref('')
const isRenameDialogOpen = ref(false)
const sessionToRename = ref<ChatSession>()
const newSessionTitle = ref('')

const filteredSessions = computed(() => {
  if (!searchQuery.value) return sessions.value
  
  return sessions.value.filter(session =>
    session.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const createNewChat = async () => {
  try {
    const newSession = await chatRepository.createSession()
    sessions.value.unshift(newSession)
    currentSessionId.value = newSession.id
  } catch (error) {
    console.error('Create chat error:', error)
    toast.error('새 채팅 생성 실패', {
      description: '새 채팅을 생성하는 중 오류가 발생했습니다.',
    })
  }
}

const selectSession = (sessionId: string) => {
  currentSessionId.value = sessionId
}

const loadSessions = async () => {
  try {
    // 데모 데이터 초기화
    await chatRepository.initializeDemoData()
    
    const result = await chatRepository.getSessions({ page: 0, size: 50 })
    sessions.value = result.sessions
    
    // 첫 번째 세션을 자동 선택
    if (sessions.value.length > 0 && !currentSessionId.value) {
      currentSessionId.value = sessions.value[0].id
    }
  } catch (error) {
    console.error('Load sessions error:', error)
    toast.error('채팅 목록 로드 실패', {
      description: '채팅 목록을 불러오는 중 오류가 발생했습니다.',
    })
  }
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
    sessionToRename.value = undefined
    newSessionTitle.value = ''
    
    toast.success('채팅 이름 변경 완료', {
      description: '채팅 이름이 변경되었습니다.',
    })
  } catch (error) {
    console.error('Rename session error:', error)
    toast.error('채팅 이름 변경 실패', {
      description: '채팅 이름 변경 중 오류가 발생했습니다.',
    })
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
      currentSessionId.value = sessions.value[0]?.id
    }
    
    toast.success('채팅 삭제 완료', {
      description: '채팅이 삭제되었습니다.',
    })
  } catch (error) {
    console.error('Delete session error:', error)
    toast.error('채팅 삭제 실패', {
      description: '채팅 삭제 중 오류가 발생했습니다.',
    })
  }
}

const formatDate = (date: Date | string) => {
  const now = new Date()
  const targetDate = typeof date === 'string' ? new Date(date) : date
  const diffTime = now.getTime() - targetDate.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return '오늘'
  } else if (diffDays === 1) {
    return '어제'
  } else if (diffDays < 7) {
    return `${diffDays}일 전`
  } else {
    return new Intl.DateTimeFormat('ko-KR', {
      month: 'short',
      day: 'numeric',
    }).format(targetDate)
  }
}

onMounted(() => {
  loadSessions()
})
</script>