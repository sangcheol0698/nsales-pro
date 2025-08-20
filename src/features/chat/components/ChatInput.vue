<template>
  <div
    ref="chatInputContainer"
    class="p-4 relative transition-all duration-300"
    :class="{
      'bg-primary/5 border-primary/20': isDragOver,
      'bg-background': !isDragOver
    }"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
  >
    <!-- 첨부된 파일 미리보기 -->
    <div v-if="attachedFiles.length > 0" class="mb-3">
      <div class="flex flex-wrap gap-2">
        <div
          v-for="file in attachedFiles"
          :key="file.name"
          class="flex items-center gap-2 bg-muted px-3 py-2 rounded-lg text-sm"
        >
          <FileText class="h-4 w-4 text-muted-foreground" />
          <span class="truncate max-w-40">{{ file.name }}</span>
          <Button
            variant="ghost"
            size="sm"
            @click="removeFile(file)"
            class="h-6 w-6 p-0 hover:bg-destructive/20 hover:text-destructive"
          >
            <X class="h-3 w-3" />
          </Button>
        </div>
      </div>
    </div>

    <!-- 드래그 앤 드롭 오버레이 -->
    <div v-if="isDragOver"
         class="absolute inset-0 z-50 bg-primary/10 backdrop-blur-sm rounded-lg border-2 border-dashed border-primary flex items-center justify-center">
      <div class="text-center space-y-3">
        <div class="mx-auto w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center animate-pulse">
          <Upload class="h-8 w-8 text-primary animate-bounce" />
        </div>
        <div>
          <p class="text-sm font-medium text-primary">파일을 여기에 놓으세요</p>
          <p class="text-xs text-primary/70">{{ draggedFileCount }}개 파일</p>
        </div>
      </div>
    </div>

    <!-- 메인 입력 영역 -->
    <div class="relative">
      <!-- 상단 컨트롤 바 -->
      <div class="flex items-center gap-2 mb-3">
        <!-- 모델 선택 버튼 -->
        <Button
          variant="outline"
          size="sm"
          @click="
            () => {
              console.log('Model button clicked');
              showModelSelector = !showModelSelector;
            }
          "
          :disabled="disabled"
          data-model-trigger
          class="h-8 px-3 text-xs font-medium hover:bg-muted/50 relative border-dashed"
        >
          <Bot class="h-3 w-3 mr-1.5" />
          {{ getCurrentModelName() }}
          <ChevronDown
            class="h-3 w-3 ml-1.5 transition-transform"
            :class="{ 'rotate-180': showModelSelector }"
          />
        </Button>

        <!-- 웹 검색 토글 -->
        <Button
          variant="outline"
          size="sm"
          @click="webSearchEnabled = !webSearchEnabled"
          :disabled="disabled"
          class="h-8 px-3 text-xs font-medium hover:bg-muted/50 transition-all duration-200"
          :class="{
            'bg-primary/10 text-primary border-primary/30':
              webSearchEnabled,
            'border-dashed': !webSearchEnabled,
          }"
        >
          <Search class="h-3 w-3 mr-1.5" />
          Web 검색
          <span
            v-if="webSearchEnabled"
            class="ml-1.5 w-2 h-2 bg-primary rounded-full animate-pulse"
          ></span>
        </Button>

        <!-- AI Tools 토글 -->
        <Button
          variant="outline"
          size="sm"
          @click="toolsEnabled = !toolsEnabled"
          :disabled="disabled"
          class="h-8 px-3 text-xs font-medium hover:bg-muted/50 transition-all duration-200"
          :class="{
            'bg-secondary/50 text-secondary-foreground border-secondary':
              toolsEnabled,
            'border-dashed': !toolsEnabled,
          }"
          title="Google 캘린더, Gmail 등 AI Tools 사용"
        >
          <Wrench class="h-3 w-3 mr-1.5" />
          AI Tools
          <span
            v-if="toolsEnabled"
            class="ml-1.5 w-2 h-2 bg-secondary rounded-full animate-pulse"
          ></span>
        </Button>

        <!-- 우측 액션 버튼들 -->
        <div class="ml-auto flex items-center gap-1">
          <!-- 파일 첨부 -->
          <Button
            variant="ghost"
            size="sm"
            @click="triggerFileInput"
            :disabled="disabled"
            class="h-8 w-8 p-0 hover:bg-muted/80"
          >
            <Paperclip class="h-3 w-3" />
          </Button>

          <!-- 음성 입력 -->
          <Button
            variant="ghost"
            size="sm"
            @click="toggleVoiceInput"
            :disabled="disabled"
            class="h-8 w-8 p-0 hover:bg-muted/80 transition-all duration-200"
            :class="{ 'bg-destructive text-destructive-foreground hover:bg-destructive/90': isRecording }"
          >
            <Mic v-if="!isRecording" class="h-3 w-3" />
            <Square v-else class="h-3 w-3" />
          </Button>
        </div>
      </div>

      <!-- 입력 필드 -->
      <div class="relative">
        <!-- 멘션 추천 드롭다운 -->
        <div
          v-if="showMentionSuggestions"
          class="absolute bottom-full left-0 right-0 mb-2 bg-background border rounded-lg shadow-lg z-50 max-h-40 overflow-y-auto"
        >
          <div class="p-2">
            <div class="text-xs text-muted-foreground mb-2 font-medium">사용 가능한 서비스</div>
            <div
              v-for="(mention, index) in filteredMentions"
              :key="mention.trigger"
              class="flex items-center gap-3 p-2 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
              :class="{ 'bg-muted': selectedMentionIndex === index }"
              @click="selectMention(mention)"
            >
              <div class="text-lg">{{ mention.icon }}</div>
              <div class="flex-1">
                <div class="font-medium text-sm">{{ mention.trigger }}</div>
                <div class="text-xs text-muted-foreground">{{ mention.description }}</div>
              </div>
              <div class="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                {{ mention.category }}
              </div>
            </div>
          </div>
        </div>

        <Textarea
          ref="textareaRef"
          v-model="inputMessage"
          :placeholder="getPlaceholder()"
          :disabled="disabled"
          class="min-h-[50px] max-h-32 resize-none pr-12 pl-4 py-3 border-2 rounded-xl transition-all duration-200 focus:ring-2 focus:ring-primary/20 focus:border-primary/40"
          @keydown="handleKeyDown"
          @input="handleInput"
          @compositionstart="handleCompositionStart"
          @compositionend="handleCompositionEnd"
        />

        <!-- 전송 버튼 -->
        <Button
          type="submit"
          size="sm"
          @click="handleSubmit"
          :disabled="disabled || (!inputMessage.trim() && attachedFiles.length === 0)"
          class="absolute right-2 bottom-2 h-8 w-8 p-0 bg-primary hover:bg-primary/90 transition-all duration-200 rounded-lg"
        >
          <Send class="h-4 w-4" />
        </Button>
      </div>
    </div>

    <!-- 모델 선택 드롭다운 -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      leave-active-class="transition-all duration-150 ease-in"
      enter-from-class="opacity-0 scale-95 translate-y-2"
      leave-to-class="opacity-0 scale-95 translate-y-2"
    >
      <div
        v-if="showModelSelector"
        data-modal="model-selector"
        class="absolute bottom-full left-0 right-0 mb-2 bg-card border border-border rounded-xl shadow-lg p-3 z-50 backdrop-blur-sm"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-semibold flex items-center gap-2">
            <Bot class="h-4 w-4" />
            AI 모델 선택
          </h3>
          <Button
            variant="ghost"
            size="sm"
            @click="showModelSelector = false"
            class="h-6 w-6 p-0 hover:bg-muted rounded-md"
          >
            <X class="h-3 w-3" />
          </Button>
        </div>

        <div class="space-y-2">
          <div
            v-if="Object.keys(availableModels).length === 0"
            class="text-sm text-muted-foreground p-3"
          >
            모델을 로딩 중입니다...
          </div>
          <button
            v-for="(model, key) in availableModels"
            :key="key"
            @click="
              () => {
                console.log('Model clicked:', key);
                selectModel(key);
              }
            "
            class="w-full flex items-center gap-3 px-3 py-3 rounded-lg text-left hover:bg-muted/60 transition-all duration-150 group"
            :class="{ 'bg-primary/10 border border-primary/30 shadow-sm': selectedModel === key }"
          >
            <div
              class="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-primary/20 to-primary/10 group-hover:from-primary/30 group-hover:to-primary/20 transition-all duration-200"
            >
              <Bot class="h-5 w-5 text-primary" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-sm">{{ model.name }}</span>
                <span
                  v-if="model.supports_web_search"
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-primary/10 text-primary font-medium"
                >
                  <Search class="h-2.5 w-2.5" />
                  Web
                </span>
              </div>
              <p class="text-xs text-muted-foreground truncate">{{ model.description }}</p>
            </div>
            <div v-if="selectedModel === key" class="text-primary flex-shrink-0">
              <div class="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">
                <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
            </div>
          </button>
        </div>
      </div>
    </Transition>

    <!-- 음성 입력 상태 -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 translate-y-2"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-if="isRecording"
        class="flex items-center gap-3 mt-3 p-3 bg-destructive/10 rounded-lg border border-destructive/20"
      >
        <div class="w-3 h-3 bg-destructive rounded-full animate-pulse"></div>
        <span class="text-sm text-destructive font-medium"
        >음성 입력 중... (말하기를 멈추면 자동으로 전송됩니다)</span
        >
      </div>
    </Transition>

    <!-- 숨겨진 파일 입력 -->
    <input
      ref="fileInputRef"
      type="file"
      multiple
      accept="image/*,text/*,.pdf,.doc,.docx"
      @change="handleFileSelect"
      class="hidden"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { Bot, ChevronDown, FileText, Mic, Paperclip, Search, Send, Square, Upload, Wrench, X } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/core/composables';

interface Props {
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
}

interface Emits {
  submit: [
    message: string,
    files?: File[],
    model?: string,
    webSearch?: boolean,
    useEnhancedAPI?: boolean,
  ];
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  isLoading: false,
  placeholder: '메시지를 입력하세요...',
});

const emit = defineEmits<Emits>();
const toast = useToast();

// 기본 상태
const inputMessage = ref('');
const textareaRef = ref<HTMLTextAreaElement>();
const fileInputRef = ref<HTMLInputElement>();
const isComposing = ref(false);

// AI 모델 관련 상태
const selectedModel = ref('gpt-4o');
const availableModels = ref<Record<string, any>>({});
const showModelSelector = ref(false);

// 웹 검색 상태 (localStorage에서 불러오기)
const webSearchEnabled = ref(localStorage.getItem('webSearchEnabled') === 'true');

// AI Tools 상태 (localStorage에서 불러오기)
const toolsEnabled = ref(localStorage.getItem('toolsEnabled') === 'true');

// 새로운 기능 상태
const attachedFiles = ref<File[]>([]);
const isRecording = ref(false);

// 드래그 앤 드롭 상태
const isDragOver = ref(false);
const draggedFileCount = ref(0);
const chatInputContainer = ref<HTMLDivElement>();

// 멘션 시스템 상태
const showMentionSuggestions = ref(false);
const selectedMentionIndex = ref(0);
const mentionQuery = ref('');

// 사용 가능한 멘션 목록
const availableMentions = ref([
  {
    trigger: '@캘린더',
    icon: '📅',
    description: 'Google Calendar 일정 관리',
    category: 'Google',
    keywords: ['calendar', 'schedule', '일정', '캘린더'],
  },
  {
    trigger: '@메일',
    icon: '📧',
    description: 'Gmail 이메일 관리',
    category: 'Google',
    keywords: ['email', 'mail', '메일', '이메일'],
  },
  {
    trigger: '@일정생성',
    icon: '➕',
    description: '새로운 캘린더 일정 생성',
    category: 'Google',
    keywords: ['create', 'new', '생성', '새로운'],
  },
  {
    trigger: '@빈시간',
    icon: '🕐',
    description: '사용 가능한 시간 찾기',
    category: 'Google',
    keywords: ['free', 'available', '빈시간', '가능한'],
  },
  {
    trigger: '@웹검색',
    icon: '🔍',
    description: '웹에서 최신 정보 검색',
    category: '검색',
    keywords: ['web', 'search', '검색', '웹'],
  },
]);

// 필터링된 멘션 목록
const filteredMentions = computed(() => {
  if (!mentionQuery.value) return availableMentions.value;

  const query = mentionQuery.value.toLowerCase();
  return availableMentions.value.filter(
    (mention) =>
      mention.trigger.toLowerCase().includes(query) ||
      mention.description.toLowerCase().includes(query) ||
      mention.keywords.some((keyword) => keyword.toLowerCase().includes(query)),
  );
});
const mediaRecorder = ref<MediaRecorder | null>(null);
const recognition = ref<any>(null);

const getCurrentModelName = () => {
  const model = availableModels.value[selectedModel.value];
  return model?.name || 'GPT-4o';
};

const getPlaceholder = () => {
  if (webSearchEnabled.value && toolsEnabled.value) {
    return '웹 검색 및 AI Tools가 활성화되었습니다. 최신 정보나 캘린더, 이메일을 물어보세요...';
  } else if (webSearchEnabled.value) {
    return '웹 검색이 활성화되었습니다. 최신 정보를 물어보세요...';
  } else if (toolsEnabled.value) {
    return 'AI Tools가 활성화되었습니다. 캘린더 일정이나 이메일에 대해 물어보세요...';
  }
  return props.placeholder;
};

const selectModel = (modelKey: string) => {
  console.log('Selecting model:', modelKey);
  selectedModel.value = modelKey;
  showModelSelector.value = false;

  toast.success('모델 변경됨', {
    description: `${getCurrentModelName()}로 변경되었습니다.`,
  });
};

const handleSubmit = () => {
  const message = inputMessage.value.trim();
  if ((!message && attachedFiles.value.length === 0) || props.disabled || isComposing.value) return;

  const finalModel = selectedModel.value;
  const webSearch = webSearchEnabled.value;
  const useEnhancedAPI = toolsEnabled.value;

  emit(
    'submit',
    message,
    attachedFiles.value.length > 0 ? attachedFiles.value : undefined,
    finalModel,
    webSearch,
    useEnhancedAPI,
  );

  inputMessage.value = '';
  attachedFiles.value = [];
  // webSearchEnabled와 toolsEnabled는 지속적으로 유지 (사용자가 명시적으로 끌 때까지)

  nextTick(() => {
    adjustHeight();
    focus();
  });
};

// 사용 가능한 모델 목록 로드
const loadAvailableModels = async () => {
  try {
    console.log('Loading models from API...');
    const response = await fetch('http://localhost:8000/api/v1/models');
    console.log('Response status:', response.status);
    const data = await response.json();
    console.log('Response data:', data);
    availableModels.value = data.models;
    console.log('Available models loaded:', Object.keys(data.models));
  } catch (error) {
    console.error('Failed to load available models:', error);
    toast.error('모델 로드 실패', {
      description: '사용 가능한 AI 모델을 불러오는데 실패했습니다.',
    });
  }
};

// 멘션 관련 함수들
const detectMention = () => {
  const input = inputMessage.value;
  const textarea = textareaRef.value as any;
  const cursorPos = textarea?.$el?.selectionStart || textarea?.selectionStart || 0;

  // @ 문자를 찾기
  const beforeCursor = input.substring(0, cursorPos);
  const mentionMatch = beforeCursor.match(/@([^\s]*)$/);

  if (mentionMatch) {
    mentionQuery.value = mentionMatch[1];
    showMentionSuggestions.value = true;
    selectedMentionIndex.value = 0;
  } else {
    showMentionSuggestions.value = false;
    mentionQuery.value = '';
  }
};

const selectMention = (mention: any) => {
  const input = inputMessage.value;
  const textarea = textareaRef.value as any;
  const cursorPos = textarea?.$el?.selectionStart || textarea?.selectionStart || 0;

  // @ 문자 위치 찾기
  const beforeCursor = input.substring(0, cursorPos);
  const mentionMatch = beforeCursor.match(/@([^\s]*)$/);

  if (mentionMatch) {
    const mentionStart = beforeCursor.lastIndexOf('@');
    const beforeMention = input.substring(0, mentionStart);
    const afterCursor = input.substring(cursorPos);

    // 멘션 텍스트로 교체
    inputMessage.value = beforeMention + mention.trigger + ' ' + afterCursor;

    // 커서 위치 조정
    nextTick(() => {
      const newPos = mentionStart + mention.trigger.length + 1;
      const textarea = textareaRef.value as any;
      const element = textarea?.$el || textarea;
      if (element) {
        element.selectionStart = newPos;
        element.selectionEnd = newPos;
      }
    });
  }

  showMentionSuggestions.value = false;
  mentionQuery.value = '';
};

const handleKeyDown = (event: KeyboardEvent) => {
  // 멘션 추천이 보일 때의 키보드 이벤트 처리
  if (showMentionSuggestions.value) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      selectedMentionIndex.value = Math.min(
        selectedMentionIndex.value + 1,
        filteredMentions.value.length - 1,
      );
      return;
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      selectedMentionIndex.value = Math.max(selectedMentionIndex.value - 1, 0);
      return;
    }

    if (event.key === 'Enter' || event.key === 'Tab') {
      event.preventDefault();
      if (filteredMentions.value[selectedMentionIndex.value]) {
        selectMention(filteredMentions.value[selectedMentionIndex.value]);
      }
      return;
    }

    if (event.key === 'Escape') {
      event.preventDefault();
      showMentionSuggestions.value = false;
      mentionQuery.value = '';
      return;
    }
  }

  // 일반적인 키보드 이벤트 처리
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    // 한글 입력 중이 아닐 때만 제출
    if (!isComposing.value) {
      handleSubmit();
    }
  }

  // Escape 키로 모달 닫기
  if (event.key === 'Escape') {
    showModelSelector.value = false;
    showMentionSuggestions.value = false;
  }
};

const handleInput = () => {
  adjustHeight();
  detectMention();
};

const handleCompositionStart = () => {
  isComposing.value = true;
};

const handleCompositionEnd = () => {
  isComposing.value = false;
};

const adjustHeight = () => {
  const textareaComponent = textareaRef.value;
  if (!textareaComponent) return;

  // Vue 컴포넌트에서 실제 DOM 요소 가져오기
  const textarea = textareaComponent.$el || textareaComponent;
  if (!textarea || !textarea.style) return;

  textarea.style.height = 'auto';
  const scrollHeight = textarea.scrollHeight;
  const maxHeight = 128; // max-h-32 = 8rem = 128px

  textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
};

// 외부에서 포커스할 수 있도록 expose
const focus = () => {
  try {
    if (textareaRef.value) {
      // Textarea 컴포넌트가 내부 input 요소를 가지고 있을 수 있으므로
      const element = textareaRef.value.$el || textareaRef.value;
      if (element && typeof element.focus === 'function') {
        element.focus();
      }
    }
  } catch (error) {
    console.warn('Failed to focus textarea:', error);
  }
};

// 파일 관련 함수들
const triggerFileInput = () => {
  fileInputRef.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (files) {
    const newFiles = Array.from(files);
    const validFiles = newFiles.filter((file) => {
      // 파일 크기 제한 (10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('파일 크기 제한', {
          description: `${file.name}은 10MB를 초과합니다.`,
        });
        return false;
      }
      return true;
    });

    attachedFiles.value = [...attachedFiles.value, ...validFiles];

    // 입력 필드 초기화
    if (target) {
      target.value = '';
    }
  }
};

const removeFile = (fileToRemove: File) => {
  attachedFiles.value = attachedFiles.value.filter((file) => file !== fileToRemove);
};

// 드래그 앤 드롭 핸들러
const handleDragOver = (event: DragEvent) => {
  if (props.disabled) return;
  isDragOver.value = true;

  // 드래그된 파일 개수 확인
  const files = event.dataTransfer?.files;
  if (files) {
    draggedFileCount.value = files.length;
  }
};

const handleDragLeave = (event: DragEvent) => {
  if (props.disabled) return;
  // 컨테이너 밖으로 나갔을 때만 isDragOver를 false로 설정
  const rect = chatInputContainer.value?.getBoundingClientRect();
  if (rect) {
    const { clientX, clientY } = event;
    if (
      clientX < rect.left ||
      clientX > rect.right ||
      clientY < rect.top ||
      clientY > rect.bottom
    ) {
      isDragOver.value = false;
    }
  }
};

const handleDrop = (event: DragEvent) => {
  if (props.disabled) return;
  isDragOver.value = false;

  const files = event.dataTransfer?.files;
  if (files) {
    const newFiles = Array.from(files);
    const validFiles = newFiles.filter((file) => {
      // 파일 크기 제한 (10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('파일 크기 제한', {
          description: `${file.name}은 10MB를 초과합니다.`,
        });
        return false;
      }
      return true;
    });

    if (validFiles.length > 0) {
      attachedFiles.value = [...attachedFiles.value, ...validFiles];
      toast.success('파일 추가됨', {
        description: `${validFiles.length}개 파일이 추가되었습니다.`,
      });
    }
  }
};


// 음성 입력 관련 함수들
const initSpeechRecognition = () => {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition.value = new SpeechRecognition();

    recognition.value.continuous = true;
    recognition.value.interimResults = true;
    recognition.value.lang = 'ko-KR';

    recognition.value.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          transcript += event.results[i][0].transcript;
        }
      }

      if (transcript) {
        inputMessage.value = transcript;
        adjustHeight();
      }
    };

    recognition.value.onend = () => {
      if (isRecording.value) {
        // 음성 입력이 끝나면 자동으로 전송
        if (inputMessage.value.trim()) {
          handleSubmit();
        }
        isRecording.value = false;
      }
    };

    recognition.value.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      isRecording.value = false;
      toast.error('음성 인식 오류', {
        description: '음성 인식 중 오류가 발생했습니다.',
      });
    };
  }
};

const toggleVoiceInput = () => {
  if (!recognition.value) {
    toast.error('음성 인식 불가', {
      description: '이 브라우저에서는 음성 인식을 지원하지 않습니다.',
    });
    return;
  }

  if (isRecording.value) {
    recognition.value.stop();
    isRecording.value = false;
  } else {
    inputMessage.value = '';
    recognition.value.start();
    isRecording.value = true;
    showModelSelector.value = false;
  }
};

// 상태 변경 시 localStorage에 저장
watch(webSearchEnabled, (newValue) => {
  localStorage.setItem('webSearchEnabled', newValue.toString());
});

watch(toolsEnabled, (newValue) => {
  localStorage.setItem('toolsEnabled', newValue.toString());
});

// 라이프사이클 훅
onMounted(() => {
  initSpeechRecognition();
  loadAvailableModels();
});

onUnmounted(() => {
  if (recognition.value) {
    recognition.value.stop();
  }
});

defineExpose({ focus });
</script>
