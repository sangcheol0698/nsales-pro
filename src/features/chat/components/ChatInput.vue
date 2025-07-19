<template>
  <div class="p-4">
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

    <!-- 메인 입력 영역 -->
    <div class="flex items-end gap-2">
      <!-- 추가 기능 버튼들 -->
      <div class="flex items-center gap-1 pb-2">
        <!-- 파일 첨부 버튼 -->
        <Button
          variant="ghost"
          size="sm"
          @click="triggerFileInput"
          :disabled="disabled"
          class="h-9 w-9 p-0 hover:bg-muted/80"
        >
          <Paperclip class="h-4 w-4" />
        </Button>
        
        <!-- 이모지 버튼 -->
        <Button
          variant="ghost"
          size="sm"
          @click="toggleEmojiPicker"
          :disabled="disabled"
          class="h-9 w-9 p-0 hover:bg-muted/80"
        >
          <Smile class="h-4 w-4" />
        </Button>
        
        <!-- 음성 입력 버튼 -->
        <Button
          variant="ghost"
          size="sm"
          @click="toggleVoiceInput"
          :disabled="disabled"
          class="h-9 w-9 p-0 hover:bg-muted/80"
          :class="{ 'bg-red-500 text-white hover:bg-red-600': isRecording }"
        >
          <Mic v-if="!isRecording" class="h-4 w-4" />
          <Square v-else class="h-4 w-4" />
        </Button>
      </div>

      <!-- 입력 필드 -->
      <div class="flex-1 relative">
        <Textarea
          ref="textareaRef"
          v-model="inputMessage"
          :placeholder="placeholder"
          :disabled="disabled"
          class="min-h-[44px] max-h-32 resize-none pr-12 transition-all duration-200 focus:ring-2 focus:ring-primary/20"
          @keydown="handleKeyDown"
          @input="adjustHeight"
          @compositionstart="handleCompositionStart"
          @compositionend="handleCompositionEnd"
        />
        
        <!-- 전송 버튼 -->
        <Button
          type="submit"
          size="sm"
          @click="handleSubmit"
          :disabled="disabled || (!inputMessage.trim() && attachedFiles.length === 0)"
          class="absolute right-2 bottom-2 h-8 w-8 p-0 bg-primary hover:bg-primary/90 transition-all duration-200"
        >
          <Send class="h-4 w-4" />
        </Button>
      </div>
    </div>
    
    <!-- 웹 검색 알림 -->
    <div class="flex items-center gap-2 mt-3 text-sm text-blue-600 dark:text-blue-400">
      <div class="flex items-center gap-1.5 bg-blue-50 dark:bg-blue-950/50 px-3 py-2 rounded-lg border border-blue-200 dark:border-blue-800">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0 9l-3-3m-3 3l3-3m0-6v6m0-6l3 3m-3-3l-3 3"/>
        </svg>
        <span class="font-medium">웹 검색이 활성화되었습니다</span>
      </div>
      <div class="text-xs text-muted-foreground">
        최신 정보가 필요할 때 AI가 자동으로 웹 검색을 수행합니다
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="flex items-center gap-2 mt-3 text-sm text-muted-foreground">
      <div class="flex gap-1">
        <div class="w-2 h-2 bg-current rounded-full animate-bounce"></div>
        <div class="w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
        <div class="w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
      </div>
      <span>AI가 응답하고 있습니다...</span>
    </div>
    
    <!-- 음성 입력 상태 -->
    <div v-if="isRecording" class="flex items-center gap-2 mt-3 text-sm text-red-600">
      <div class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
      <span>음성 입력 중... (말하기를 멈추면 자동으로 전송됩니다)</span>
    </div>
    
    <!-- 이모지 선택기 -->
    <div
      v-if="showEmojiPicker"
      class="absolute bottom-full left-4 right-4 mb-2 bg-card border border-border rounded-lg shadow-lg p-4 z-50"
    >
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium">이모지 선택</h3>
        <Button
          variant="ghost"
          size="sm"
          @click="toggleEmojiPicker"
          class="h-6 w-6 p-0"
        >
          <X class="h-3 w-3" />
        </Button>
      </div>
      
      <div class="grid grid-cols-8 gap-2 max-h-48 overflow-y-auto">
        <Button
          v-for="emoji in emojiList"
          :key="emoji.unicode"
          variant="ghost"
          size="sm"
          @click="insertEmoji(emoji)"
          class="h-8 w-8 p-0 text-lg hover:bg-muted/80"
        >
          {{ emoji.unicode }}
        </Button>
      </div>
    </div>

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
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { Send, Paperclip, Smile, Mic, Square, X, FileText } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Textarea } from '@/core/components/ui/textarea'
import { useToast } from '@/core/composables'

interface Props {
  disabled?: boolean
  isLoading?: boolean
  placeholder?: string
}

interface Emits {
  submit: [message: string, files?: File[]]
}

interface EmojiItem {
  unicode: string
  name: string
  category: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  isLoading: false,
  placeholder: '메시지를 입력하세요...',
})

const emit = defineEmits<Emits>()
const toast = useToast()

// 기본 상태
const inputMessage = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const fileInputRef = ref<HTMLInputElement>()
const isComposing = ref(false)

// 새로운 기능 상태
const attachedFiles = ref<File[]>([])
const showEmojiPicker = ref(false)
const isRecording = ref(false)
const mediaRecorder = ref<MediaRecorder | null>(null)
const recognition = ref<SpeechRecognition | null>(null)

// 이모지 데이터
const emojiList: EmojiItem[] = [
  { unicode: '😀', name: 'grinning', category: 'emotions' },
  { unicode: '😃', name: 'grinning_big', category: 'emotions' },
  { unicode: '😄', name: 'grinning_eyes', category: 'emotions' },
  { unicode: '😁', name: 'grinning_sweat', category: 'emotions' },
  { unicode: '😅', name: 'sweat_smile', category: 'emotions' },
  { unicode: '😂', name: 'joy', category: 'emotions' },
  { unicode: '🤣', name: 'rofl', category: 'emotions' },
  { unicode: '😊', name: 'blush', category: 'emotions' },
  { unicode: '😇', name: 'innocent', category: 'emotions' },
  { unicode: '🙂', name: 'slight_smile', category: 'emotions' },
  { unicode: '🙃', name: 'upside_down', category: 'emotions' },
  { unicode: '😉', name: 'wink', category: 'emotions' },
  { unicode: '😌', name: 'relieved', category: 'emotions' },
  { unicode: '😍', name: 'heart_eyes', category: 'emotions' },
  { unicode: '🥰', name: 'smiling_face_with_hearts', category: 'emotions' },
  { unicode: '😘', name: 'kissing_heart', category: 'emotions' },
  { unicode: '🤔', name: 'thinking', category: 'emotions' },
  { unicode: '🤨', name: 'raised_eyebrow', category: 'emotions' },
  { unicode: '😐', name: 'neutral', category: 'emotions' },
  { unicode: '😑', name: 'expressionless', category: 'emotions' },
  { unicode: '🙄', name: 'eye_roll', category: 'emotions' },
  { unicode: '😏', name: 'smirk', category: 'emotions' },
  { unicode: '😒', name: 'unamused', category: 'emotions' },
  { unicode: '😞', name: 'disappointed', category: 'emotions' },
  { unicode: '😔', name: 'pensive', category: 'emotions' },
  { unicode: '😟', name: 'worried', category: 'emotions' },
  { unicode: '😕', name: 'confused', category: 'emotions' },
  { unicode: '🙁', name: 'slight_frown', category: 'emotions' },
  { unicode: '😰', name: 'cold_sweat', category: 'emotions' },
  { unicode: '😨', name: 'fearful', category: 'emotions' },
  { unicode: '😢', name: 'cry', category: 'emotions' },
  { unicode: '😭', name: 'sob', category: 'emotions' },
  { unicode: '👍', name: 'thumbs_up', category: 'gestures' },
  { unicode: '👎', name: 'thumbs_down', category: 'gestures' },
  { unicode: '👌', name: 'ok_hand', category: 'gestures' },
  { unicode: '✌️', name: 'peace', category: 'gestures' },
  { unicode: '🤞', name: 'fingers_crossed', category: 'gestures' },
  { unicode: '🤟', name: 'love_you', category: 'gestures' },
  { unicode: '🤘', name: 'rock_on', category: 'gestures' },
  { unicode: '👏', name: 'clap', category: 'gestures' },
  { unicode: '🙌', name: 'raised_hands', category: 'gestures' },
  { unicode: '👐', name: 'open_hands', category: 'gestures' },
  { unicode: '🤲', name: 'palms_up', category: 'gestures' },
  { unicode: '🤝', name: 'handshake', category: 'gestures' },
  { unicode: '🙏', name: 'pray', category: 'gestures' },
  { unicode: '💪', name: 'muscle', category: 'gestures' },
  { unicode: '🎉', name: 'party', category: 'objects' },
  { unicode: '🎊', name: 'confetti', category: 'objects' },
  { unicode: '🔥', name: 'fire', category: 'objects' },
  { unicode: '💯', name: 'hundred', category: 'objects' },
  { unicode: '✨', name: 'sparkles', category: 'objects' },
  { unicode: '⭐', name: 'star', category: 'objects' },
  { unicode: '🌟', name: 'star2', category: 'objects' },
  { unicode: '💫', name: 'dizzy', category: 'objects' },
  { unicode: '⚡', name: 'zap', category: 'objects' },
  { unicode: '💥', name: 'boom', category: 'objects' },
  { unicode: '❤️', name: 'heart', category: 'objects' },
  { unicode: '💙', name: 'blue_heart', category: 'objects' },
  { unicode: '💚', name: 'green_heart', category: 'objects' },
  { unicode: '💛', name: 'yellow_heart', category: 'objects' },
  { unicode: '💜', name: 'purple_heart', category: 'objects' },
  { unicode: '🖤', name: 'black_heart', category: 'objects' },
  { unicode: '🤍', name: 'white_heart', category: 'objects' },
  { unicode: '🤎', name: 'brown_heart', category: 'objects' },
  { unicode: '💔', name: 'broken_heart', category: 'objects' },
  { unicode: '💕', name: 'two_hearts', category: 'objects' },
  { unicode: '💖', name: 'sparkling_heart', category: 'objects' },
  { unicode: '💗', name: 'heartpulse', category: 'objects' },
  { unicode: '💘', name: 'cupid', category: 'objects' },
  { unicode: '💝', name: 'gift_heart', category: 'objects' },
]

const handleSubmit = () => {
  const message = inputMessage.value.trim()
  if ((!message && attachedFiles.value.length === 0) || props.disabled || isComposing.value) return

  emit('submit', message, attachedFiles.value.length > 0 ? attachedFiles.value : undefined)
  inputMessage.value = ''
  attachedFiles.value = []
  
  nextTick(() => {
    adjustHeight()
    focus()
  })
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    // 한글 입력 중이 아닐 때만 제출
    if (!isComposing.value) {
      handleSubmit()
    }
  }
}

const handleCompositionStart = () => {
  isComposing.value = true
}

const handleCompositionEnd = () => {
  isComposing.value = false
}

const adjustHeight = () => {
  const textareaComponent = textareaRef.value
  if (!textareaComponent) return

  // Vue 컴포넌트에서 실제 DOM 요소 가져오기
  const textarea = textareaComponent.$el || textareaComponent
  if (!textarea || !textarea.style) return

  textarea.style.height = 'auto'
  const scrollHeight = textarea.scrollHeight
  const maxHeight = 128 // max-h-32 = 8rem = 128px
  
  textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`
}

// 외부에서 포커스할 수 있도록 expose
const focus = () => {
  try {
    if (textareaRef.value) {
      // Textarea 컴포넌트가 내부 input 요소를 가지고 있을 수 있으므로
      const element = textareaRef.value.$el || textareaRef.value
      if (element && typeof element.focus === 'function') {
        element.focus()
      }
    }
  } catch (error) {
    console.warn('Failed to focus textarea:', error)
  }
}

// 파일 관련 함수들
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    const newFiles = Array.from(files)
    const validFiles = newFiles.filter(file => {
      // 파일 크기 제한 (10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('파일 크기 제한', {
          description: `${file.name}은 10MB를 초과합니다.`
        })
        return false
      }
      return true
    })
    
    attachedFiles.value = [...attachedFiles.value, ...validFiles]
    
    // 입력 필드 초기화
    if (target) {
      target.value = ''
    }
  }
}

const removeFile = (fileToRemove: File) => {
  attachedFiles.value = attachedFiles.value.filter(file => file !== fileToRemove)
}

// 이모지 관련 함수들
const toggleEmojiPicker = () => {
  showEmojiPicker.value = !showEmojiPicker.value
}

const insertEmoji = (emoji: EmojiItem) => {
  const textarea = textareaRef.value
  if (textarea) {
    const element = textarea.$el || textarea
    const start = element.selectionStart
    const end = element.selectionEnd
    const text = inputMessage.value
    
    inputMessage.value = text.slice(0, start) + emoji.unicode + text.slice(end)
    
    nextTick(() => {
      element.selectionStart = element.selectionEnd = start + emoji.unicode.length
      element.focus()
    })
  } else {
    inputMessage.value += emoji.unicode
  }
  
  showEmojiPicker.value = false
}

// 음성 입력 관련 함수들
const initSpeechRecognition = () => {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition.value = new SpeechRecognition()
    
    recognition.value.continuous = true
    recognition.value.interimResults = true
    recognition.value.lang = 'ko-KR'
    
    recognition.value.onresult = (event) => {
      let transcript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          transcript += event.results[i][0].transcript
        }
      }
      
      if (transcript) {
        inputMessage.value = transcript
        adjustHeight()
      }
    }
    
    recognition.value.onend = () => {
      if (isRecording.value) {
        // 음성 입력이 끝나면 자동으로 전송
        if (inputMessage.value.trim()) {
          handleSubmit()
        }
        isRecording.value = false
      }
    }
    
    recognition.value.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      isRecording.value = false
      toast.error('음성 인식 오류', {
        description: '음성 인식 중 오류가 발생했습니다.'
      })
    }
  }
}

const toggleVoiceInput = () => {
  if (!recognition.value) {
    toast.error('음성 인식 불가', {
      description: '이 브라우저에서는 음성 인식을 지원하지 않습니다.'
    })
    return
  }
  
  if (isRecording.value) {
    recognition.value.stop()
    isRecording.value = false
  } else {
    inputMessage.value = ''
    recognition.value.start()
    isRecording.value = true
  }
}

// 라이프사이클 훅
onMounted(() => {
  initSpeechRecognition()
  
  // 클릭 아웃사이드로 이모지 선택기 닫기
  document.addEventListener('click', (event) => {
    const target = event.target as HTMLElement
    if (showEmojiPicker.value && !target.closest('.emoji-picker')) {
      showEmojiPicker.value = false
    }
  })
})

onUnmounted(() => {
  if (recognition.value) {
    recognition.value.stop()
  }
})

defineExpose({ focus })
</script>