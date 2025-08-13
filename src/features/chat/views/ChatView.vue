<template>
  <SidebarLayout>
    <div class="flex h-full w-full overflow-hidden" @keydown="handleGlobalKeydown">
      <!-- 사이드바: 채팅 세션 목록 -->
      <aside
        class="w-80 bg-background border-r border-border flex flex-col"
        role="complementary"
        :aria-label="$t ? $t('chat.chatSessions') : '채팅 세션 목록'"
      >
        <!-- 헤더 -->
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
              :aria-label="$t ? $t('chat.searchPlaceholder') : '채팅 검색'"
              role="searchbox"
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
                <DropdownMenuSeparator />
                <DropdownMenuLabel>메시지 수</DropdownMenuLabel>
                <DropdownMenuItem @click="setMessageCountFilter('none')">
                  <CheckCircle2 v-if="messageCountFilter === 'none'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  전체
                </DropdownMenuItem>
                <DropdownMenuItem @click="setMessageCountFilter('active')">
                  <CheckCircle2 v-if="messageCountFilter === 'active'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  활성 (5개 이상)
                </DropdownMenuItem>
                <DropdownMenuItem @click="setMessageCountFilter('empty')">
                  <CheckCircle2 v-if="messageCountFilter === 'empty'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  비어있음
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
                <DropdownMenuItem @click="setSortBy('alphabetical')">
                  <CheckCircle2 v-if="sortBy === 'alphabetical'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  이름순
                </DropdownMenuItem>
                <DropdownMenuItem @click="setSortBy('messages')">
                  <CheckCircle2 v-if="sortBy === 'messages'" class="h-3 w-3 mr-2" />
                  <div v-else class="w-3 mr-2"></div>
                  메시지 수
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <!-- 활성 필터 표시 -->
          <div v-if="activeFilters.length > 0" class="flex flex-wrap gap-1 mt-2">
            <Badge
              v-for="filter in activeFilters"
              :key="filter.key"
              variant="secondary"
              class="text-xs px-2 py-0.5 h-5"
            >
              {{ filter.label }}
              <Button
                variant="ghost"
                size="sm"
                @click="removeFilter(filter.key)"
                class="h-3 w-3 p-0 ml-1 hover:bg-destructive/20"
              >
                <X class="h-2 w-2" />
              </Button>
            </Badge>
          </div>
        </div>

        <!-- 세션 목록 -->
        <div class="flex-1 overflow-y-auto">
          <div
            class="p-2 space-y-1"
            role="list"
            :aria-label="$t ? $t('chat.sessionsList') : '채팅 세션 목록'"
          >
            <div
              v-for="(session, index) in filteredSessions"
              :key="session.id"
              class="group p-3 rounded-lg cursor-pointer hover:bg-muted/50 transition-all duration-200 border border-transparent hover:border-border/50 focus:outline-none focus:ring-2 focus:ring-primary/50"
              :class="{
                'bg-muted shadow-sm border-border/50 ring-1 ring-primary/20':
                  currentSessionId === session.id,
              }"
              role="listitem"
              tabindex="0"
              :aria-label="`${session.title}, ${session.messageCount}개 메시지, ${formatDate(session.updatedAt)} 업데이트`"
              :aria-selected="currentSessionId === session.id"
              @click="selectSession(session.id)"
              @keydown.enter="selectSession(session.id)"
              @keydown.space.prevent="selectSession(session.id)"
              @keydown.arrow-up.prevent="focusSession(index - 1)"
              @keydown.arrow-down.prevent="focusSession(index + 1)"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <div
                      class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                      :class="session.messageCount > 0 ? 'bg-primary' : 'bg-muted-foreground/50'"
                    ></div>
                    <div class="flex items-center gap-1 min-w-0">
                      <h4 class="font-medium truncate text-foreground text-sm">{{ session.title }}</h4>
                      <Sparkles 
                        v-if="session.titleGenerated" 
                        class="h-3 w-3 text-primary/70 flex-shrink-0" 
                        :title="'AI가 생성한 제목 (' + formatDate(session.titleGeneratedAt || session.updatedAt) + ')'"
                      />
                    </div>
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
                    <span v-if="session.messageCount === 0" class="text-muted-foreground/70">
                      비어있음
                    </span>
                  </div>
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      class="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 rounded-md hover:bg-muted/80 ml-2 flex-shrink-0"
                    >
                      <MoreVertical class="h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>

                  <DropdownMenuContent align="end">
                    <DropdownMenuItem @click="renameSession(session)">
                      <Edit2 class="h-3 w-3 mr-2" />
                      이름 변경
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      @click="generateTitle(session.id)"
                      :disabled="session.messageCount < 2"
                    >
                      <Sparkles class="h-3 w-3 mr-2" />
                      AI 제목 생성
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      @click="deleteSession(session.id)"
                      class="text-destructive focus:text-destructive"
                    >
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

      <!-- 메인 채팅 영역 -->
      <main class="flex-1 flex flex-col min-w-0 overflow-hidden" role="main">
        <!-- 채팅 위젯 -->
        <ChatWidget 
          v-if="currentSessionId" 
          :key="currentSessionId" 
          :session-id="currentSessionId" 
          @message-completed="refreshSessionInfo"
        />

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
            <h3
              class="text-lg lg:text-xl font-bold mb-2 text-foreground"
            >
              AI Assistant에 오신 것을 환영합니다
            </h3>
            <p class="text-muted-foreground mb-6 text-sm lg:text-base leading-relaxed">
              영업 데이터 분석, 프로젝트 정보 조회, 업무 도움 등<br class="hidden sm:block" />
              무엇이든 물어보세요.
            </p>
            <Button
              @click="createNewChat"
              size="default"
              class="bg-primary hover:bg-primary/90 text-primary-foreground shadow-md hover:shadow-lg transition-all duration-200 rounded-lg px-6 py-2"
            >
              <MessageCircle class="h-4 w-4 mr-2" />
              채팅 시작하기
            </Button>
          </div>
        </div>
      </main>
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
          <Button variant="outline" @click="isRenameDialogOpen = false"> 취소 </Button>
          <Button @click="confirmRename"> 변경 </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
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
  Sparkles,
  Trash2,
  X,
} from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/core/composables';
import { SidebarLayout } from '@/shared/components/sidebar';
import ChatWidget from '../components/ChatWidget.vue';
import { ChatRepository } from '../repository/ChatRepository';
import type { ChatSession } from '../entity/ChatMessage';

const toast = useToast();
const chatRepository = new ChatRepository();
const route = useRoute();
const router = useRouter();

const sessions = ref<ChatSession[]>([]);
const currentSessionId = ref<string>();
const searchQuery = ref('');
const isRenameDialogOpen = ref(false);
const sessionToRename = ref<ChatSession>();
const newSessionTitle = ref('');

// 접근성 관련 상태
const searchInputRef = ref<HTMLInputElement>();
const focusedSessionIndex = ref(-1);

// 필터 및 정렬 상태
const timeFilter = ref<'today' | 'week' | 'month' | 'all'>('all');
const messageCountFilter = ref<'none' | 'active' | 'empty'>('none');
const sortBy = ref<'recent' | 'oldest' | 'alphabetical' | 'messages'>('recent');

interface FilterItem {
  key: string;
  label: string;
}

const activeFilters = computed((): FilterItem[] => {
  const filters: FilterItem[] = [];

  if (timeFilter.value !== 'all') {
    const labels = {
      today: '오늘',
      week: '이번 주',
      month: '이번 달',
    };
    filters.push({
      key: 'time',
      label: labels[timeFilter.value],
    });
  }

  if (messageCountFilter.value !== 'none') {
    const labels = {
      active: '활성 채팅',
      empty: '비어있는 채팅',
    };
    filters.push({
      key: 'messageCount',
      label: labels[messageCountFilter.value],
    });
  }

  return filters;
});

const filteredSessions = computed(() => {
  let filtered = [...sessions.value];

  // 텍스트 검색 필터
  if (searchQuery.value) {
    filtered = filtered.filter((session) =>
      session.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }

  // 시간 필터
  if (timeFilter.value !== 'all') {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const monthAgo = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());

    filtered = filtered.filter((session) => {
      const sessionDate = new Date(session.updatedAt);
      switch (timeFilter.value) {
        case 'today':
          return sessionDate >= today;
        case 'week':
          return sessionDate >= weekAgo;
        case 'month':
          return sessionDate >= monthAgo;
        default:
          return true;
      }
    });
  }

  // 메시지 수 필터
  if (messageCountFilter.value !== 'none') {
    filtered = filtered.filter((session) => {
      switch (messageCountFilter.value) {
        case 'active':
          return session.messageCount >= 5;
        case 'empty':
          return session.messageCount === 0;
        default:
          return true;
      }
    });
  }

  // 정렬
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'recent':
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
      case 'oldest':
        return new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime();
      case 'alphabetical':
        return a.title.localeCompare(b.title);
      case 'messages':
        return b.messageCount - a.messageCount;
      default:
        return 0;
    }
  });

  return filtered;
});

const createNewChat = async () => {
  try {
    const newSession = await chatRepository.createSession();
    sessions.value.unshift(newSession);
    // 새 세션 생성시 URL 업데이트
    router.push({ name: 'chatSession', params: { sessionId: newSession.id } });
  } catch (error) {
    console.error('Create chat error:', error);
    toast.error('새 채팅 생성 실패', {
      description: '새 채팅을 생성하는 중 오류가 발생했습니다.',
    });
  }
};

const selectSession = (sessionId: string) => {
  // URL을 업데이트하여 브라우저 히스토리에 반영
  if (route.params.sessionId !== sessionId) {
    router.push({ name: 'chatSession', params: { sessionId } });
  } else {
    currentSessionId.value = sessionId;
  }
};

// 필터 및 정렬 함수들
const setTimeFilter = (filter: 'today' | 'week' | 'month' | 'all') => {
  timeFilter.value = filter;
};

const setMessageCountFilter = (filter: 'none' | 'active' | 'empty') => {
  messageCountFilter.value = filter;
};

const setSortBy = (sort: 'recent' | 'oldest' | 'alphabetical' | 'messages') => {
  sortBy.value = sort;
};

const removeFilter = (filterKey: string) => {
  switch (filterKey) {
    case 'time':
      timeFilter.value = 'all';
      break;
    case 'messageCount':
      messageCountFilter.value = 'none';
      break;
  }
};

// 키보드 내비게이션 함수들
const handleGlobalKeydown = (event: KeyboardEvent) => {
  // Ctrl/Cmd + F: 검색 포커스
  if ((event.ctrlKey || event.metaKey) && event.key === 'f') {
    event.preventDefault();
    searchInputRef.value?.focus();
    return;
  }

  // Ctrl/Cmd + N: 새 채팅
  if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
    event.preventDefault();
    createNewChat();
    return;
  }

  // Escape: 검색 초기화
  if (event.key === 'Escape') {
    if (searchQuery.value) {
      searchQuery.value = '';
    }
    return;
  }

  // Alt + 숫자: 세션 선택
  if (event.altKey && event.key >= '1' && event.key <= '9') {
    event.preventDefault();
    const index = parseInt(event.key) - 1;
    if (index < filteredSessions.value.length) {
      selectSession(filteredSessions.value[index].id);
    }
    return;
  }
};

const focusSession = (index: number) => {
  const sessions = filteredSessions.value;
  if (index < 0 || index >= sessions.length) return;

  focusedSessionIndex.value = index;

  // DOM 요소에 포커스 설정
  nextTick(() => {
    const sessionElements = document.querySelectorAll('[role="listitem"]');
    const targetElement = sessionElements[index] as HTMLElement;
    if (targetElement) {
      targetElement.focus();
    }
  });
};

const loadSessions = async () => {
  try {
    // 데모 데이터 초기화
    await chatRepository.initializeDemoData();

    const result = await chatRepository.getSessions({ page: 0, size: 50 });
    sessions.value = result.sessions;

    // URL 기반으로 세션 선택 (watch에서 처리)
    // 더 이상 자동 선택하지 않음
  } catch (error) {
    console.error('Load sessions error:', error);
    toast.error('채팅 목록 로드 실패', {
      description: '채팅 목록을 불러오는 중 오류가 발생했습니다.',
    });
  }
};

const renameSession = (session: ChatSession) => {
  sessionToRename.value = session;
  newSessionTitle.value = session.title;
  isRenameDialogOpen.value = true;
};

const confirmRename = async () => {
  if (!sessionToRename.value || !newSessionTitle.value.trim()) return;

  try {
    await chatRepository.updateSession(sessionToRename.value.id, newSessionTitle.value);

    const index = sessions.value.findIndex((s) => s.id === sessionToRename.value?.id);
    if (index !== -1) {
      sessions.value[index].title = newSessionTitle.value;
    }

    isRenameDialogOpen.value = false;
    sessionToRename.value = undefined;
    newSessionTitle.value = '';

    toast.success('채팅 이름 변경 완료', {
      description: '채팅 이름이 변경되었습니다.',
    });
  } catch (error) {
    console.error('Rename session error:', error);
    toast.error('채팅 이름 변경 실패', {
      description: '채팅 이름 변경 중 오류가 발생했습니다.',
    });
  }
};

const deleteSession = async (sessionId: string) => {
  try {
    await chatRepository.deleteSession(sessionId);

    const index = sessions.value.findIndex((s) => s.id === sessionId);
    if (index !== -1) {
      sessions.value.splice(index, 1);
    }

    // 현재 보고 있던 세션이 삭제된 경우
    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        // 첫 번째 세션으로 이동
        router.push({ name: 'chatSession', params: { sessionId: sessions.value[0].id } });
      } else {
        // 세션이 없으면 기본 채팅 페이지로 이동
        router.push({ name: 'chat' });
      }
    }

    toast.success('채팅 삭제 완료', {
      description: '채팅이 삭제되었습니다.',
    });
  } catch (error) {
    console.error('Delete session error:', error);
    toast.error('채팅 삭제 실패', {
      description: '채팅 삭제 중 오류가 발생했습니다.',
    });
  }
};

/**
 * AI 기반 제목 생성 (수동 트리거)
 */
const generateTitle = async (sessionId: string) => {
  try {
    const result = await chatRepository.generateTitle(sessionId);
    
    if (result.success) {
      // 세션 목록에서 해당 세션의 제목 업데이트
      const sessionIndex = sessions.value.findIndex(s => s.id === sessionId);
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].title = result.title;
        sessions.value[sessionIndex].titleGenerated = true;
        sessions.value[sessionIndex].titleGeneratedAt = new Date();
      }
      
      toast.success('AI 제목 생성 완료', {
        description: `새 제목: ${result.title}`,
      });
    } else {
      toast.warning('AI 제목 생성 실패', {
        description: result.message || '제목 생성 중 오류가 발생했습니다.',
      });
    }
  } catch (error) {
    console.error('Generate title error:', error);
    toast.error('AI 제목 생성 실패', {
      description: '제목 생성 중 오류가 발생했습니다.',
    });
  }
};

/**
 * 세션 정보 실시간 업데이트 (제목 변경 감지)
 */
const refreshSessionInfo = async (sessionId: string) => {
  try {
    const updatedSession = await chatRepository.getSession(sessionId);
    const sessionIndex = sessions.value.findIndex(s => s.id === sessionId);
    
    if (sessionIndex !== -1) {
      const currentSession = sessions.value[sessionIndex];
      
      // 제목이 변경되었는지 확인
      if (currentSession.title !== updatedSession.title) {
        sessions.value[sessionIndex] = {
          ...currentSession,
          title: updatedSession.title,
          titleGenerated: updatedSession.titleGenerated,
          titleGeneratedAt: updatedSession.titleGeneratedAt,
          updatedAt: updatedSession.updatedAt,
        };
        
        // AI가 자동으로 제목을 생성한 경우 알림 표시
        if (updatedSession.titleGenerated && !currentSession.titleGenerated) {
          toast.success('AI가 제목을 자동 생성했습니다', {
            description: `새 제목: ${updatedSession.title}`,
            duration: 3000,
          });
        }
      }
    }
  } catch (error) {
    console.error('Refresh session info error:', error);
  }
};

const formatDate = (date: Date | string) => {
  const now = new Date();
  const targetDate = typeof date === 'string' ? new Date(date) : date;
  const diffTime = now.getTime() - targetDate.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return '오늘';
  } else if (diffDays === 1) {
    return '어제';
  } else if (diffDays < 7) {
    return `${diffDays}일 전`;
  } else {
    return new Intl.DateTimeFormat('ko-KR', {
      month: 'short',
      day: 'numeric',
    }).format(targetDate);
  }
};

// URL 파라미터 변화 감지
watch(() => route.params.sessionId, (newSessionId) => {
  if (typeof newSessionId === 'string') {
    currentSessionId.value = newSessionId;
  } else if (!newSessionId && currentSessionId.value) {
    // URL에서 sessionId가 제거된 경우 (예: /chat로 이동)
    currentSessionId.value = undefined;
  }
}, { immediate: true });

// /chat 경로로 접근시 첫 번째 세션으로 리다이렉트
watch([sessions, () => route.path], ([newSessions, newPath]) => {
  if (newPath === '/chat' && newSessions.length > 0 && !currentSessionId.value) {
    router.replace({ name: 'chatSession', params: { sessionId: newSessions[0].id } });
  }
});

// 현재 세션의 메시지 수 변화 감지하여 제목 업데이트 확인
watch(
  () => currentSessionId.value,
  async (newSessionId, oldSessionId) => {
    if (newSessionId && newSessionId !== oldSessionId) {
      // 세션이 변경될 때 약간의 지연 후 제목 업데이트 확인
      setTimeout(async () => {
        await refreshSessionInfo(newSessionId);
      }, 1000);
    }
  }
);

// 자식 컴포넌트에서 호출할 수 있도록 메서드 노출
defineExpose({
  refreshSessionInfo,
});

onMounted(() => {
  loadSessions();
});
</script>