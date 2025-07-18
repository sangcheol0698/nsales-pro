<template>
  <div class="border-t bg-background p-4">
    <form @submit.prevent="handleSubmit" class="flex gap-2">
      <div class="flex-1 relative">
        <Textarea
          ref="textareaRef"
          v-model="inputMessage"
          :placeholder="placeholder"
          :disabled="disabled"
          class="min-h-[44px] max-h-32 resize-none pr-12"
          @keydown="handleKeyDown"
          @input="adjustHeight"
          @compositionstart="handleCompositionStart"
          @compositionend="handleCompositionEnd"
        />
        <Button
          type="submit"
          size="sm"
          class="absolute right-2 bottom-2 h-8 w-8 p-0"
          :disabled="disabled || !inputMessage.trim()"
        >
          <Send class="h-4 w-4" />
        </Button>
      </div>
    </form>
    
    <div v-if="isLoading" class="flex items-center gap-2 mt-2 text-sm text-foreground/70">
      <div class="flex gap-1">
        <div class="w-2 h-2 bg-current rounded-full animate-bounce"></div>
        <div class="w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
        <div class="w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
      </div>
      <span>AI가 응답하고 있습니다...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { Send } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Textarea } from '@/core/components/ui/textarea'

interface Props {
  disabled?: boolean
  isLoading?: boolean
  placeholder?: string
}

interface Emits {
  submit: [message: string]
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  isLoading: false,
  placeholder: '메시지를 입력하세요...',
})

const emit = defineEmits<Emits>()

const inputMessage = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const isComposing = ref(false) // 한글 입력 중인지 추적

const handleSubmit = () => {
  const message = inputMessage.value.trim()
  if (!message || props.disabled || isComposing.value) return

  emit('submit', message)
  inputMessage.value = ''
  
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

defineExpose({ focus })
</script>