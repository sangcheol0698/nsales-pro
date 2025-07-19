<template>
  <div
    class="group relative flex mb-4 px-4 py-2 hover:bg-muted/30 rounded-lg transition-colors focus-within:bg-muted/30"
    :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
    role="article"
    :aria-label="`${message.role === 'user' ? '사용자' : 'AI'} 메시지: ${message.content}`"
    :data-message-id="message.id"
  >
    <div class="flex gap-3 max-w-[85%] sm:max-w-[75%] lg:max-w-[70%]">
      <Avatar
        v-if="message.role === 'assistant'"
        class="h-8 w-8 flex-shrink-0 mt-1"
      >
        <AvatarFallback class="bg-primary text-primary-foreground text-xs font-medium">
          AI
        </AvatarFallback>
      </Avatar>

      <div class="flex-1 space-y-2">
        <!-- 메시지 헤더 -->
        <div class="flex items-center gap-2 text-xs text-muted-foreground">
          <span class="font-medium">
            {{ message.role === 'user' ? '나' : 'AI Assistant' }}
          </span>
          <span>{{ formatTime(message.timestamp) }}</span>
        </div>

        <!-- 메시지 내용 -->
        <div
          class="rounded-2xl p-4 break-words shadow-sm border"
          :class="[
            message.role === 'user'
              ? 'bg-primary text-primary-foreground border-primary/20 ml-auto'
              : 'bg-card text-card-foreground border-border/50',
          ]"
        >
          <!-- 타이핑 인디케이터 -->
          <div v-if="isTyping" class="flex items-center gap-2 text-muted-foreground">
            <div class="flex gap-1">
              <div class="w-2 h-2 bg-current rounded-full animate-pulse"></div>
              <div class="w-2 h-2 bg-current rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-current rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
            </div>
            <span class="text-sm">AI가 타이핑 중...</span>
          </div>

          <!-- Assistant 메시지 -->
          <div
            v-else-if="message.role === 'assistant'"
            class="markdown-content prose prose-sm max-w-none dark:prose-invert"
          >
            <div v-if="isProcessing" class="flex items-center gap-2 text-muted-foreground">
              <div class="w-2 h-2 bg-current rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-current rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              <span class="text-sm">코드 하이라이트 중...</span>
            </div>
            <div v-else v-html="formattedContent" />
          </div>

          <!-- User 메시지 -->
          <div v-else class="whitespace-pre-wrap leading-relaxed">
            {{ message.content }}
          </div>
        </div>

        <!-- 메시지 액션 -->
        <div 
          v-if="!isTyping"
          class="flex items-center gap-2 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity"
          role="toolbar"
          aria-label="메시지 액션"
        >
          <Button
            variant="ghost"
            size="sm"
            @click="copyMessage"
            class="h-8 px-2 text-xs hover:bg-muted/80 focus:opacity-100"
            aria-label="메시지 복사"
          >
            <Copy class="h-3 w-3 mr-1" />
            복사
          </Button>
          
          <Button
            v-if="message.role === 'assistant'"
            variant="ghost"
            size="sm"
            @click="regenerateMessage"
            class="h-8 px-2 text-xs hover:bg-muted/80 focus:opacity-100"
            aria-label="메시지 재생성"
          >
            <RefreshCw class="h-3 w-3 mr-1" />
            재생성
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            @click="deleteMessage"
            class="h-8 px-2 text-xs hover:bg-destructive/10 hover:text-destructive focus:opacity-100"
            aria-label="메시지 삭제"
          >
            <Trash2 class="h-3 w-3 mr-1" />
            삭제
          </Button>
        </div>
      </div>

      <Avatar
        v-if="message.role === 'user'"
        class="h-8 w-8 flex-shrink-0 mt-1"
      >
        <AvatarFallback class="bg-muted text-muted-foreground text-xs font-medium">
          나
        </AvatarFallback>
      </Avatar>
    </div>

    <!-- 복사 성공 토스트 -->
    <div
      v-if="showCopySuccess"
      class="absolute top-2 right-2 bg-green-500 text-white px-3 py-1 rounded-md text-sm shadow-lg animate-in fade-in-0 slide-in-from-top-2"
    >
      복사됨!
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { marked } from 'marked'
import { codeToHtml } from 'shiki'
import he from 'he'
import { Copy, RefreshCw, Trash2 } from 'lucide-vue-next'
import { Avatar, AvatarFallback } from '@/core/components/ui/avatar'
import { Button } from '@/core/components/ui/button'
import { useToast } from '@/core/composables'
import type { ChatMessage } from '../entity/ChatMessage'

interface Props {
  message: ChatMessage
  isTyping?: boolean
}

interface Emits {
  regenerate: [messageId: string]
  delete: [messageId: string]
}

const props = withDefaults(defineProps<Props>(), {
  isTyping: false
})

const emit = defineEmits<Emits>()
const toast = useToast()

const showCopySuccess = ref(false)

// Shiki 캐시를 위한 변수
const highlightCache = new Map<string, string>()

// Configure marked (Shiki는 비동기이므로 후처리로 사용)
marked.setOptions({
  breaks: true,
  gfm: true,
  langPrefix: 'language-',
  sanitize: false,
  smartypants: false,
})

// 다크 모드 감지
const isDarkMode = computed(() => {
  return document.documentElement.classList.contains('dark')
})

// Shiki로 코드 하이라이트 처리하는 함수
const highlightWithShiki = async (code: string, lang: string): Promise<string> => {
  const cacheKey = `${lang}:${code}:${isDarkMode.value ? 'dark' : 'light'}`
  if (highlightCache.has(cacheKey)) {
    return highlightCache.get(cacheKey)!
  }

  try {
    console.log('🎨 Highlighting with Shiki:', { lang, codeLength: code.length, theme: isDarkMode.value ? 'one-dark-pro' : 'github-light' })
    
    // 언어 매핑
    const langMap: Record<string, string> = {
      'js': 'javascript',
      'ts': 'typescript',
      'py': 'python',
      'sh': 'bash',
      'shell': 'bash'
    }
    
    const shikiLang = langMap[lang.toLowerCase()] || lang.toLowerCase()
    
    // 다크/라이트 모드에 따라 테마 선택
    const theme = isDarkMode.value ? 'one-dark-pro' : 'github-light'
    
    const html = await codeToHtml(code, {
      lang: shikiLang,
      theme: theme,
      transformers: []
    })
    
    console.log('✅ Shiki success:', html.includes('style=') ? 'Has styles' : 'No styles')
    highlightCache.set(cacheKey, html)
    return html
  } catch (error) {
    console.warn('⚠️ Shiki fallback to JavaScript:', error)
    try {
      const theme = isDarkMode.value ? 'one-dark-pro' : 'github-light'
      const html = await codeToHtml(code, {
        lang: 'javascript',
        theme: theme
      })
      highlightCache.set(cacheKey, html)
      return html
    } catch (fallbackError) {
      console.error('❌ Shiki complete failure:', fallbackError)
      const fallback = `<pre><code>${he.encode(code)}</code></pre>`
      highlightCache.set(cacheKey, fallback)
      return fallback
    }
  }
}

// 유니코드 안전한 base64 인코딩/디코딩 함수
const unicodeToBtoa = (str: string) => {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, (match, p1) => {
    return String.fromCharCode(parseInt(p1, 16))
  }))
}

const btoaToUnicode = (str: string) => {
  return decodeURIComponent(Array.prototype.map.call(atob(str), (c: string) => {
    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
  }).join(''))
}

const formattedContent = ref('')
const isProcessing = ref(false)

// 비동기로 콘텐츠 처리
const processContent = async () => {
  if (props.message.role !== 'assistant') {
    formattedContent.value = props.message.content
    return
  }

  isProcessing.value = true
  try {
    let html = marked(props.message.content)
    console.log('Original marked HTML (first 200 chars):', html.substring(0, 200))
    
    // 코드 블록 찾기
    const codeBlockRegex = /<pre><code(?:\s+class="([^"]*)")?[^>]*>([\s\S]*?)<\/code><\/pre>/g
    const codeBlocks: Array<{ match: string; classAttr?: string; code: string; lang: string }> = []
    let match
    
    while ((match = codeBlockRegex.exec(html)) !== null) {
      const [fullMatch, classAttr, code] = match
      const langMatch = classAttr?.match(/(?:^|\s)language-(\w+)(?:\s|$)/)
      const lang = langMatch?.[1] || 'text'
      
      // HTML 디코딩
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = code
      const plainCode = tempDiv.textContent || tempDiv.innerText || ''
      
      codeBlocks.push({ match: fullMatch, classAttr, code: plainCode, lang })
    }
    
    console.log('Found code blocks:', codeBlocks.length)
    
    // 각 코드 블록을 Shiki로 처리
    for (const block of codeBlocks) {
      console.log('Processing code block:', block.lang)
      const highlightedHtml = await highlightWithShiki(block.code, block.lang)
      
      // 복사 버튼과 함께 래핑
      const buttonId = `copy-${Math.random().toString(36).substr(2, 9)}`
      const encodedCode = unicodeToBtoa(block.code)
      
      const wrappedCode = `
        <div class="code-block-container" data-language="${block.lang}">
          <div class="code-block-header">
            <span class="code-language">${block.lang.toUpperCase()}</span>
            <button 
              class="copy-code-btn" 
              onclick="copyCodeBlock('${buttonId}', this)"
              data-code="${encodedCode}"
              title="코드 복사"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
              <span class="copy-text">복사</span>
            </button>
          </div>
          <div id="${buttonId}" class="shiki-wrapper">${highlightedHtml}</div>
        </div>
      `
      
      html = html.replace(block.match, wrappedCode)
    }
    
    formattedContent.value = html
  } catch (error) {
    console.error('Content processing error:', error)
    formattedContent.value = marked(props.message.content)
  } finally {
    isProcessing.value = false
  }
}

// 메시지 내용이 변경될 때마다 처리
watch(() => props.message.content, processContent, { immediate: true })

// 다크 모드 변경 시 코드 하이라이트 다시 처리
watch(isDarkMode, () => {
  if (props.message.role === 'assistant') {
    // 캐시 클리어 후 다시 처리
    highlightCache.clear()
    processContent()
  }
})

const formatTime = (timestamp: Date | string) => {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
  
  // 유효한 날짜인지 확인
  if (isNaN(date.getTime())) {
    return '시간 정보 없음'
  }
  
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

// 메시지 복사 함수
const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    showCopySuccess.value = true
    setTimeout(() => {
      showCopySuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('복사 실패:', error)
    toast.error('복사 실패', {
      description: '메시지를 복사하는 중 오류가 발생했습니다.'
    })
  }
}

// 메시지 재생성 함수
const regenerateMessage = () => {
  emit('regenerate', props.message.id)
}

// 메시지 삭제 함수
const deleteMessage = () => {
  emit('delete', props.message.id)
}

// 코드 블록 복사 함수를 전역으로 등록
const copyCodeBlock = (buttonId: string, button: HTMLElement) => {
  const codeElement = document.getElementById(buttonId)
  const codeData = button.getAttribute('data-code')
  
  if (codeData) {
    try {
      const decodedCode = btoaToUnicode(codeData)
      navigator.clipboard.writeText(decodedCode).then(() => {
        const copyText = button.querySelector('.copy-text')
        const originalText = copyText?.textContent
        
        if (copyText) {
          copyText.textContent = '복사됨!'
          button.classList.add('copied')
          
          setTimeout(() => {
            copyText.textContent = originalText
            button.classList.remove('copied')
          }, 2000)
        }
      }).catch(err => {
        console.error('복사 실패:', err)
        toast.error('복사 실패', {
          description: '코드를 복사하는 중 오류가 발생했습니다.'
        })
      })
    } catch (err) {
      console.error('코드 디코딩 실패:', err)
      toast.error('디코딩 실패', {
        description: '코드를 디코딩하는 중 오류가 발생했습니다.'
      })
    }
  }
}

onMounted(() => {
  // 전역 함수로 등록
  ;(window as any).copyCodeBlock = copyCodeBlock
})

onUnmounted(() => {
  // 정리
  delete (window as any).copyCodeBlock
})
</script>

<style>
/* Magic MCP 기반 모던 마크다운 스타일 */
.markdown-content {
  color: hsl(var(--foreground));
  line-height: 1.7;
  font-size: 0.95rem;
}

/* 제목 스타일 - 그라데이션과 마진 최적화 */
.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(var(--primary)/0.8) 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
  margin: 1.5em 0 0.75em 0;
  line-height: 1.3;
  letter-spacing: -0.025em;
}

.markdown-content h1 { font-size: 1.75rem; }
.markdown-content h2 { font-size: 1.5rem; }
.markdown-content h3 { font-size: 1.25rem; }
.markdown-content h4 { font-size: 1.125rem; }
.markdown-content h5 { font-size: 1rem; }
.markdown-content h6 { font-size: 0.9rem; }

/* 첫 번째 제목의 상단 마진 제거 */
.markdown-content h1:first-child,
.markdown-content h2:first-child,
.markdown-content h3:first-child,
.markdown-content h4:first-child,
.markdown-content h5:first-child,
.markdown-content h6:first-child {
  margin-top: 0;
}

/* 강조 텍스트 */
.markdown-content strong {
  color: hsl(var(--foreground));
  font-weight: 650;
  background: hsl(var(--primary)/0.1);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.markdown-content em {
  color: hsl(var(--muted-foreground));
  font-style: italic;
}

/* 문단 스타일 */
.markdown-content p {
  margin: 1em 0;
  color: hsl(var(--foreground));
  line-height: 1.7;
}

.markdown-content p:first-child {
  margin-top: 0;
}

.markdown-content p:last-child {
  margin-bottom: 0;
}

/* 리스트 스타일 - 더 모던한 불릿과 간격 */
.markdown-content ul,
.markdown-content ol {
  margin: 1.25em 0;
  padding-left: 1.75rem;
}

.markdown-content ul {
  list-style: none;
}

.markdown-content ul li {
  position: relative;
  margin: 0.75em 0;
  line-height: 1.6;
}

.markdown-content ul li::before {
  content: '';
  position: absolute;
  left: -1.25rem;
  top: 0.7em;
  width: 6px;
  height: 6px;
  background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(var(--primary)/0.7) 100%);
  border-radius: 50%;
  transform: translateY(-50%);
}

.markdown-content ol li {
  margin: 0.75em 0;
  line-height: 1.6;
}

.markdown-content ol {
  counter-reset: list-counter;
}

.markdown-content ol li {
  counter-increment: list-counter;
  position: relative;
}

.markdown-content ol li::marker {
  content: counter(list-counter) ". ";
  color: hsl(var(--primary));
  font-weight: 600;
}

/* 중첩 리스트 */
.markdown-content ul ul,
.markdown-content ol ol,
.markdown-content ul ol,
.markdown-content ol ul {
  margin: 0.5em 0;
}

/* 인용문 - 글래스모피즘 효과 */
.markdown-content blockquote {
  position: relative;
  margin: 1.5em 0;
  padding: 1.25rem 1.5rem;
  background: hsl(var(--muted)/0.5);
  backdrop-filter: blur(8px);
  border-left: 4px solid hsl(var(--primary));
  border-radius: 0 0.75rem 0.75rem 0;
  font-style: italic;
  color: hsl(var(--muted-foreground));
  box-shadow: 0 4px 6px -1px hsl(var(--primary)/0.1), 0 2px 4px -1px hsl(var(--primary)/0.06);
}

.markdown-content blockquote::before {
  content: '"';
  position: absolute;
  top: -0.5rem;
  left: 1rem;
  font-size: 2rem;
  color: hsl(var(--primary)/0.6);
  font-weight: bold;
}

.markdown-content blockquote p {
  margin: 0.5em 0;
}

.markdown-content blockquote p:first-child {
  margin-top: 0;
}

.markdown-content blockquote p:last-child {
  margin-bottom: 0;
}

/* 인라인 코드 - 더 예쁜 배경과 타이포그래피 */
.markdown-content code {
  background: linear-gradient(135deg, hsl(var(--muted)) 0%, hsl(var(--muted)/0.8) 100%);
  color: hsl(var(--primary));
  padding: 0.2rem 0.4rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
  font-weight: 500;
  border: 1px solid hsl(var(--border)/0.5);
  box-shadow: 0 1px 2px hsl(var(--foreground)/0.05);
}

/* 코드 블록 컨테이너 - 모던한 디자인과 복사 기능 */
.markdown-content .code-block-container {
  position: relative;
  margin: 1.5em 0;
  background: linear-gradient(135deg, hsl(var(--muted)) 0%, hsl(var(--muted)/0.9) 100%);
  border: 1px solid hsl(var(--border));
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px hsl(var(--foreground)/0.1), 0 2px 4px -1px hsl(var(--foreground)/0.06);
  backdrop-filter: blur(8px);
}

.markdown-content .code-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: hsl(var(--muted)/0.3);
  border-bottom: 1px solid hsl(var(--border)/0.5);
  backdrop-filter: blur(4px);
}

.markdown-content .code-language {
  font-size: 0.75rem;
  font-weight: 600;
  color: hsl(var(--muted-foreground));
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.markdown-content .copy-code-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: hsl(var(--background));
  border: 1px solid hsl(var(--border));
  border-radius: 0.375rem;
  color: hsl(var(--muted-foreground));
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.markdown-content .copy-code-btn:hover {
  background: hsl(var(--muted));
  color: hsl(var(--foreground));
  border-color: hsl(var(--border));
  transform: translateY(-1px);
  box-shadow: 0 2px 4px hsl(var(--foreground)/0.1);
}

.markdown-content .copy-code-btn.copied {
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  border-color: hsl(var(--primary));
}

.markdown-content .copy-code-btn svg {
  width: 14px;
  height: 14px;
  transition: transform 0.2s ease;
}

.markdown-content .copy-code-btn:hover svg {
  transform: scale(1.1);
}

.markdown-content .code-block-container pre {
  margin: 0;
  padding: 1.5rem;
  background: transparent;
  border: none;
  border-radius: 0;
  box-shadow: none;
}

.markdown-content .code-block-container pre code {
  background: transparent;
  padding: 0;
  border: none;
  font-size: 0.875rem;
  color: hsl(var(--foreground));
  box-shadow: none;
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
}

/* Shiki 래퍼 스타일 - Shiki는 인라인 스타일을 사용하므로 래퍼만 설정 */
.markdown-content .shiki-wrapper {
  overflow-x: auto;
  border-radius: 0.5rem;
}

.markdown-content .shiki-wrapper pre {
  margin: 0 !important;
  padding: 1.5rem !important;
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  overflow-x: auto !important;
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace !important;
  line-height: 1.5 !important;
  tab-size: 4 !important;
}

.markdown-content .shiki-wrapper code {
  background: transparent !important;
  padding: 0 !important;
  border: none !important;
  box-shadow: none !important;
  font-family: inherit !important;
}

/* 다크 테마에서 더 잘 보이도록 배경색 조정 */
.dark .markdown-content .code-block-container {
  background: linear-gradient(135deg, #1e1e1e 0%, #252526 100%);
}

.dark .markdown-content .code-block-header {
  background: rgba(30, 30, 30, 0.8);
  border-bottom-color: #3e3e42;
}

/* 기존 pre 스타일은 코드 블록 컨테이너가 없는 경우를 위해 유지 */
.markdown-content pre:not(.code-block-container pre) {
  position: relative;
  margin: 1.5em 0;
  padding: 1.5rem;
  background: linear-gradient(135deg, hsl(var(--muted)) 0%, hsl(var(--muted)/0.9) 100%);
  border: 1px solid hsl(var(--border));
  border-radius: 0.75rem;
  overflow-x: auto;
  box-shadow: 0 4px 6px -1px hsl(var(--foreground)/0.1), 0 2px 4px -1px hsl(var(--foreground)/0.06);
  backdrop-filter: blur(8px);
}

/* 링크 - 호버 효과와 애니메이션 */
.markdown-content a {
  color: hsl(var(--primary));
  text-decoration: none;
  position: relative;
  font-weight: 500;
  transition: all 0.2s ease;
}

.markdown-content a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, hsl(var(--primary)) 0%, hsl(var(--primary)/0.6) 100%);
  transition: width 0.3s ease;
}

.markdown-content a:hover {
  color: hsl(var(--primary)/0.8);
}

.markdown-content a:hover::after {
  width: 100%;
}

/* 테이블 - 모던한 그리드 스타일 */
.markdown-content table {
  width: 100%;
  margin: 1.5em 0;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px hsl(var(--foreground)/0.1), 0 2px 4px -1px hsl(var(--foreground)/0.06);
}

.markdown-content th,
.markdown-content td {
  padding: 0.875rem 1rem;
  text-align: left;
  border-bottom: 1px solid hsl(var(--border));
}

.markdown-content th {
  background: linear-gradient(135deg, hsl(var(--muted)) 0%, hsl(var(--muted)/0.8) 100%);
  font-weight: 650;
  color: hsl(var(--foreground));
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.05em;
}

.markdown-content td {
  background: hsl(var(--card));
}

.markdown-content tr:hover td {
  background: hsl(var(--muted)/0.3);
}

.markdown-content tr:last-child td {
  border-bottom: none;
}

/* 구분선 */
.markdown-content hr {
  margin: 2rem 0;
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, hsl(var(--border)) 20%, hsl(var(--border)) 80%, transparent 100%);
}

/* 이미지 */
.markdown-content img {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px hsl(var(--foreground)/0.1);
  margin: 1rem 0;
}

/* 애니메이션 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.markdown-content {
  animation: fadeInUp 0.3s ease-out;
}

/* 다크 모드 최적화 */
.dark .markdown-content h1,
.dark .markdown-content h2,
.dark .markdown-content h3,
.dark .markdown-content h4,
.dark .markdown-content h5,
.dark .markdown-content h6 {
  background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(var(--primary)/0.9) 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 모바일 최적화 */
@media (max-width: 768px) {
  .markdown-content {
    font-size: 0.9rem;
    line-height: 1.6;
  }
  
  .markdown-content h1 { font-size: 1.5rem; }
  .markdown-content h2 { font-size: 1.35rem; }
  .markdown-content h3 { font-size: 1.2rem; }
  .markdown-content h4 { font-size: 1.1rem; }
  
  .markdown-content pre {
    padding: 1rem;
    margin: 1rem 0;
    font-size: 0.8rem;
  }
  
  .markdown-content code {
    font-size: 0.8rem;
  }
  
  .markdown-content blockquote {
    padding: 1rem;
    margin: 1rem 0;
  }
  
  .markdown-content table {
    font-size: 0.85rem;
  }
  
  .markdown-content th,
  .markdown-content td {
    padding: 0.625rem 0.75rem;
  }
}

/* 웹 검색 출처 섹션 스타일링 */
.markdown-content p:has(strong:contains("참고 출처")) {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid hsl(var(--border));
}

.markdown-content strong:contains("참고 출처") {
  color: hsl(var(--primary));
  background: hsl(var(--primary)/0.1);
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid hsl(var(--primary)/0.2);
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

/* 출처 링크 스타일 개선 */
.markdown-content p:has(strong:contains("참고 출처")) + ol {
  margin-top: 0.75rem;
  background: hsl(var(--muted)/0.3);
  padding: 1rem 1.5rem;
  border-radius: 0.75rem;
  border: 1px solid hsl(var(--border)/0.5);
  backdrop-filter: blur(4px);
}

.markdown-content p:has(strong:contains("참고 출처")) + ol li {
  margin: 0.5rem 0;
  padding: 0.25rem 0;
}

.markdown-content p:has(strong:contains("참고 출처")) + ol li a {
  font-weight: 600;
  color: hsl(var(--primary));
  text-decoration: none;
  background: hsl(var(--background));
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  border: 1px solid hsl(var(--border));
  transition: all 0.2s ease;
  display: inline-block;
}

.markdown-content p:has(strong:contains("참고 출처")) + ol li a:hover {
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  transform: translateY(-1px);
  box-shadow: 0 2px 4px hsl(var(--primary)/0.2);
}

/* 스크롤바 스타일링 */
.markdown-content pre::-webkit-scrollbar {
  height: 8px;
}

.markdown-content pre::-webkit-scrollbar-track {
  background: hsl(var(--muted)/0.3);
  border-radius: 4px;
}

.markdown-content pre::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground)/0.3);
  border-radius: 4px;
}

.markdown-content pre::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground)/0.5);
}
</style>