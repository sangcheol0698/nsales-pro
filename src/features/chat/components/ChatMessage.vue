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

          <!-- Tool 실행 상태 표시 -->
          <div v-if="message.toolCall" class="flex items-center gap-2 ml-2">
            <div class="h-1 w-1 bg-current rounded-full"></div>
            <div class="flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-medium"
                 :class="getToolStatusClass(message.toolStatus)">
              <component :is="getToolStatusIcon(message.toolStatus)" class="h-3 w-3"
                         :class="{ 'animate-spin': message.toolStatus === 'running' }" />
              <span>{{ message.toolCall }}</span>
              <span v-if="message.toolStatus === 'running'">실행 중...</span>
              <span v-else-if="message.toolStatus === 'completed'">완료</span>
              <span v-else-if="message.toolStatus === 'error'">오류</span>
            </div>
          </div>
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
          <!-- 이미지/문서 분석 중 인디케이터 -->
          <div v-if="message.isAnalyzing"
               class="flex items-center gap-3 text-muted-foreground mb-3 p-3 bg-muted/50 rounded-lg border border-muted">
            <div class="relative">
              <component
                :is="message.analyzingType === 'image' ? 'Image' : 'FileText'"
                class="h-5 w-5 text-primary"
              />
              <div class="absolute -inset-1">
                <div class="w-7 h-7 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
              </div>
            </div>
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-sm font-medium text-primary">
                  {{ message.analyzingType === 'image' ? '🖼️ 이미지 분석 중...' : '📄 문서 분석 중...' }}
                </span>
                <div class="flex gap-1">
                  <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></div>
                  <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
              </div>
              <p class="text-xs text-muted-foreground">
                {{ message.analyzingType === 'image'
                ? 'GPT-4o Vision이 이미지 내용을 분석하고 있습니다.'
                : '문서 내용을 추출하고 분석하고 있습니다.' }}
              </p>
            </div>
          </div>

          <!-- 타이핑 인디케이터 -->
          <div v-if="isTyping && !message.isAnalyzing" class="flex items-center gap-2 text-muted-foreground">
            <div class="flex gap-1">
              <div class="w-2 h-2 bg-current rounded-full animate-pulse"></div>
              <div class="w-2 h-2 bg-current rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-current rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
            </div>
            <span class="text-sm">AI가 타이핑 중...</span>
          </div>

          <!-- Assistant 메시지 -->
          <div v-else-if="message.role === 'assistant'">

            <!-- Google Tools 결과 카드 (Collapsible) -->
            <div v-if="googleToolResult && googleToolResult.type !== 'text'" class="mb-3">
              <GoogleToolsCollapsible :google-tool-result="googleToolResult" />
            </div>

            <!-- 일반 마크다운 내용 -->
            <div
              v-if="!googleToolResult || googleToolResult.type === 'text' || message.content.trim()"
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
          </div>

          <!-- User 메시지 -->
          <div v-else class="space-y-3">
            <!-- 첨부된 파일들 표시 -->
            <div v-if="message.attachedFiles && message.attachedFiles.length > 0" class="space-y-3">
              <!-- 이미지 파일들 -->
              <div v-if="attachedImageFiles.length > 0" class="space-y-2">
                <div class="text-xs text-primary-foreground/70 font-medium">📷 첨부된 이미지</div>
                <div class="grid gap-2"
                     :class="{
                       'grid-cols-1': attachedImageFiles.length === 1,
                       'grid-cols-2': attachedImageFiles.length === 2,
                       'grid-cols-2 sm:grid-cols-3': attachedImageFiles.length >= 3
                     }">
                  <div
                    v-for="(file, index) in attachedImageFiles"
                    :key="index"
                    class="relative group aspect-square rounded-lg overflow-hidden bg-white/10 border border-white/20"
                  >
                    <div class="w-full h-full flex items-center justify-center text-white/60">
                      <Image class="h-8 w-8" />
                    </div>
                    <div
                      class="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                      <div class="text-white text-xs font-medium bg-black/50 px-2 py-1 rounded">
                        {{ file.name.length > 15 ? file.name.substring(0, 15) + '...' : file.name }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 문서 파일들 -->
              <div v-if="attachedDocumentFiles.length > 0" class="space-y-2">
                <div class="text-xs text-primary-foreground/70 font-medium">📄 첨부된 문서</div>
                <div class="space-y-2">
                  <div
                    v-for="(file, index) in attachedDocumentFiles"
                    :key="index"
                    class="flex items-center gap-3 p-2 bg-white/10 border border-white/20 rounded-lg"
                  >
                    <div class="flex-shrink-0 w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                      <FileText class="h-4 w-4 text-white/80" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-white truncate">{{ file.name }}</div>
                      <div class="text-xs text-white/60">{{ formatFileSize(file.size) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 기존 이미지 표시 (하위 호환용) -->
            <div v-else-if="attachedImages.length > 0" class="space-y-2">
              <div class="grid gap-2"
                   :class="{
                     'grid-cols-1': attachedImages.length === 1,
                     'grid-cols-2': attachedImages.length === 2,
                     'grid-cols-2 sm:grid-cols-3': attachedImages.length >= 3
                   }">
                <div
                  v-for="(imagePath, index) in attachedImages"
                  :key="index"
                  class="relative group aspect-square rounded-lg overflow-hidden bg-white/10 cursor-pointer"
                  @click="openImageModal(imagePath)"
                >
                  <div class="w-full h-full flex items-center justify-center text-white/60">
                    <Image class="h-8 w-8" />
                  </div>
                  <div
                    class="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                    <div class="text-white text-xs font-medium bg-black/40 px-2 py-1 rounded">
                      🖼️ 이미지 {{ index + 1 }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 텍스트 내용 -->
            <div v-if="cleanMessageContent.trim()" class="whitespace-pre-wrap leading-relaxed">
              {{ cleanMessageContent }}
            </div>
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

  <!-- 이미지 확대 모달 -->
  <div v-if="selectedImageModal"
       class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
       @click="closeImageModal">
    <div class="relative max-w-4xl max-h-full">
      <div class="w-full h-96 bg-muted/20 rounded-lg flex items-center justify-center text-white">
        <div class="text-center space-y-2">
          <Image class="h-16 w-16 mx-auto opacity-60" />
          <p class="text-lg font-medium">이미지 미리보기</p>
          <p class="text-sm opacity-70">{{ selectedImageModal }}</p>
          <p class="text-xs opacity-50">실제 이미지는 백엔드 구현이 필요합니다</p>
        </div>
      </div>
      <Button
        variant="ghost"
        size="sm"
        @click="closeImageModal"
        class="absolute top-4 right-4 h-8 w-8 p-0 bg-black/20 hover:bg-black/40 text-white"
      >
        <X class="h-4 w-4" />
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { marked } from 'marked';
import { codeToHtml } from 'shiki';
import he from 'he';
import { CheckCircle, Copy, FileText, Image, Loader2, Play, RefreshCw, Trash2, X, XCircle } from 'lucide-vue-next';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { useToast } from '@/core/composables';
import type { ChatMessage } from '../entity/ChatMessage';
import GoogleToolsCollapsible from './GoogleToolsCollapsible.vue';
import { getGoogleToolResult } from '../utils/googleToolsParser';

interface Props {
  message: ChatMessage;
  isTyping?: boolean;
}

interface Emits {
  regenerate: [messageId: string];
  delete: [messageId: string];
}

const props = withDefaults(defineProps<Props>(), {
  isTyping: false,
});

const emit = defineEmits<Emits>();
const toast = useToast();

const showCopySuccess = ref(false);
const selectedImageModal = ref<string | null>(null);

// Shiki 캐시를 위한 변수
const highlightCache = new Map<string, string>();

// 첨부된 파일들 분류
const attachedImageFiles = computed(() => {
  return props.message.attachedFiles?.filter(file => file.type.startsWith('image/')) || [];
});

const attachedDocumentFiles = computed(() => {
  return props.message.attachedFiles?.filter(file => !file.type.startsWith('image/')) || [];
});

// 첨부된 이미지 추출 (기존 방식, 하위 호환용)
const attachedImages = computed(() => {
  const content = props.message.content;
  const imagePattern = /\[첨부된 이미지: ([^\]]+)\]/g;
  const images: string[] = [];
  let match;

  while ((match = imagePattern.exec(content)) !== null) {
    images.push(match[1]);
  }

  return images;
});

// 이미지 정보를 제거한 깨끗한 메시지 내용
const cleanMessageContent = computed(() => {
  return props.message.content.replace(/\[첨부된 이미지: [^\]]+\]/g, '').trim();
});

// Configure marked (Shiki는 비동기이므로 후처리로 사용)
marked.setOptions({
  breaks: true,
  gfm: true,
  langPrefix: 'language-',
  sanitize: false,
  smartypants: false,
});

// 다크 모드 감지
const isDarkMode = computed(() => {
  return document.documentElement.classList.contains('dark');
});

// Google Tools 결과 파싱
const googleToolResult = computed(() => {
  return getGoogleToolResult(props.message);
});

// Shiki로 코드 하이라이트 처리하는 함수
const highlightWithShiki = async (code: string, lang: string): Promise<string> => {
  const cacheKey = `${lang}:${code}:${isDarkMode.value ? 'dark' : 'light'}`;
  if (highlightCache.has(cacheKey)) {
    return highlightCache.get(cacheKey)!;
  }

  try {

    // 언어 매핑
    const langMap: Record<string, string> = {
      'js': 'javascript',
      'ts': 'typescript',
      'py': 'python',
      'sh': 'bash',
      'shell': 'bash',
    };

    const shikiLang = langMap[lang.toLowerCase()] || lang.toLowerCase();

    // 다크/라이트 모드에 따라 테마 선택
    const theme = isDarkMode.value ? 'one-dark-pro' : 'github-light';

    const html = await codeToHtml(code, {
      lang: shikiLang,
      theme: theme,
      transformers: [],
    });

    console.log('✅ Shiki success:', html.includes('style=') ? 'Has styles' : 'No styles');
    highlightCache.set(cacheKey, html);
    return html;
  } catch (error) {
    console.warn('⚠️ Shiki fallback to JavaScript:', error);
    try {
      const theme = isDarkMode.value ? 'one-dark-pro' : 'github-light';
      const html = await codeToHtml(code, {
        lang: 'javascript',
        theme: theme,
      });
      highlightCache.set(cacheKey, html);
      return html;
    } catch (fallbackError) {
      console.error('❌ Shiki complete failure:', fallbackError);
      const fallback = `<pre><code>${he.encode(code)}</code></pre>`;
      highlightCache.set(cacheKey, fallback);
      return fallback;
    }
  }
};

// 유니코드 안전한 base64 인코딩/디코딩 함수
const unicodeToBtoa = (str: string) => {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, (match, p1) => {
    return String.fromCharCode(parseInt(p1, 16));
  }));
};

const btoaToUnicode = (str: string) => {
  return decodeURIComponent(Array.prototype.map.call(atob(str), (c: string) => {
    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
  }).join(''));
};

// 파일 크기 포맷 함수
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

const formattedContent = ref('');
const isProcessing = ref(false);

// 비동기로 콘텐츠 처리
const processContent = async () => {
  if (props.message.role !== 'assistant') {
    formattedContent.value = props.message.content;
    return;
  }

  isProcessing.value = true;
  try {
    // Google Tools 메시지인 경우 JSON 코드 블록을 미리 제거
    let content = props.message.content;
    const isGoogleToolsMessage = props.message.toolCall &&
      ['get_calendar_events', 'get_emails', 'create_calendar_event', 'send_email', 'find_free_time'].includes(props.message.toolCall) &&
      props.message.toolStatus === 'completed';

    if (isGoogleToolsMessage) {
      // JSON 마크다운 블록 패턴 제거
      content = content.replace(/```json\s*[\s\S]*?\s*```/g, '');
    }

    let html = marked(content);

    // 코드 블록 찾기
    const codeBlockRegex = /<pre><code(?:\s+class="([^"]*)")?[^>]*>([\s\S]*?)<\/code><\/pre>/g;
    const codeBlocks: Array<{ match: string; classAttr?: string; code: string; lang: string }> = [];
    let match;

    while ((match = codeBlockRegex.exec(html)) !== null) {
      const [fullMatch, classAttr, code] = match;
      const langMatch = classAttr?.match(/(?:^|\s)language-(\w+)(?:\s|$)/);
      const lang = langMatch?.[1] || 'text';

      // HTML 디코딩
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = code;
      const plainCode = tempDiv.textContent || tempDiv.innerText || '';

      codeBlocks.push({ match: fullMatch, classAttr, code: plainCode, lang });
    }


    // 각 코드 블록을 Shiki로 처리
    for (const block of codeBlocks) {
      const highlightedHtml = await highlightWithShiki(block.code, block.lang);

      // 복사 버튼과 함께 래핑
      const buttonId = `copy-${Math.random().toString(36).substr(2, 9)}`;
      const encodedCode = unicodeToBtoa(block.code);

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
      `;

      html = html.replace(block.match, wrappedCode);
    }

    formattedContent.value = html;
  } catch (error) {
    console.error('Content processing error:', error);
    formattedContent.value = marked(props.message.content);
  } finally {
    isProcessing.value = false;
  }
};

// 메시지 내용이 변경될 때마다 처리
watch(() => props.message.content, processContent, { immediate: true });

// 다크 모드 변경 시 코드 하이라이트 다시 처리
watch(isDarkMode, () => {
  if (props.message.role === 'assistant') {
    // 캐시 클리어 후 다시 처리
    highlightCache.clear();
    processContent();
  }
});

// googleToolResult가 변경될 때마다 콘텐츠 재처리
watch(googleToolResult, () => {
  if (props.message.role === 'assistant') {
    processContent();
  }
});

const formatTime = (timestamp: Date | string) => {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;

  // 유효한 날짜인지 확인
  if (isNaN(date.getTime())) {
    return '시간 정보 없음';
  }

  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// 메시지 복사 함수
const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content);
    showCopySuccess.value = true;
    setTimeout(() => {
      showCopySuccess.value = false;
    }, 2000);
  } catch (error) {
    console.error('복사 실패:', error);
    toast.error('복사 실패', {
      description: '메시지를 복사하는 중 오류가 발생했습니다.',
    });
  }
};

// 메시지 재생성 함수
const regenerateMessage = () => {
  emit('regenerate', props.message.id);
};

// 메시지 삭제 함수
const deleteMessage = () => {
  emit('delete', props.message.id);
};

// 이미지 모달 함수들
const openImageModal = (imagePath: string) => {
  selectedImageModal.value = imagePath;
};

const closeImageModal = () => {
  selectedImageModal.value = null;
};

// Tool 상태에 따른 CSS 클래스 반환
const getToolStatusClass = (status?: string) => {
  switch (status) {
    case 'running':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
    case 'completed':
      return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
    case 'error':
      return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
    default:
      return 'bg-muted text-muted-foreground';
  }
};

// Tool 상태에 따른 아이콘 반환
const getToolStatusIcon = (status?: string) => {
  switch (status) {
    case 'running':
      return Loader2;
    case 'completed':
      return CheckCircle;
    case 'error':
      return XCircle;
    default:
      return Play;
  }
};

// 코드 블록 복사 함수를 전역으로 등록
const copyCodeBlock = (buttonId: string, button: HTMLElement) => {
  const codeElement = document.getElementById(buttonId);
  const codeData = button.getAttribute('data-code');

  if (codeData) {
    try {
      const decodedCode = btoaToUnicode(codeData);
      navigator.clipboard.writeText(decodedCode).then(() => {
        const copyText = button.querySelector('.copy-text');
        const originalText = copyText?.textContent;

        if (copyText) {
          copyText.textContent = '복사됨!';
          button.classList.add('copied');

          setTimeout(() => {
            copyText.textContent = originalText;
            button.classList.remove('copied');
          }, 2000);
        }
      }).catch(err => {
        console.error('복사 실패:', err);
        toast.error('복사 실패', {
          description: '코드를 복사하는 중 오류가 발생했습니다.',
        });
      });
    } catch (err) {
      console.error('코드 디코딩 실패:', err);
      toast.error('디코딩 실패', {
        description: '코드를 디코딩하는 중 오류가 발생했습니다.',
      });
    }
  }
};

onMounted(() => {
  // 전역 함수로 등록
  ;(window as any).copyCodeBlock = copyCodeBlock;
});

onUnmounted(() => {
  // 정리
  delete (window as any).copyCodeBlock;
});
</script>

<style>
.markdown-content {
  color: var(--foreground);
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
  background: linear-gradient(135deg, var(--primary) 0%, color-mix(in oklch, var(--primary), transparent 20%) 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
  margin: 1.5em 0 0.75em 0;
  line-height: 1.3;
  letter-spacing: -0.025em;
}

.markdown-content h1 {
  font-size: 1.75rem;
}

.markdown-content h2 {
  font-size: 1.5rem;
}

.markdown-content h3 {
  font-size: 1.25rem;
}

.markdown-content h4 {
  font-size: 1.125rem;
}

.markdown-content h5 {
  font-size: 1rem;
}

.markdown-content h6 {
  font-size: 0.9rem;
}

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
  color: var(--foreground);
  font-weight: 650;
  background: color-mix(in oklch, var(--primary), transparent 90%);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.markdown-content em {
  color: var(--muted-foreground);
  font-style: italic;
}

/* 문단 스타일 */
.markdown-content p {
  margin: 1em 0;
  color: var(--foreground);
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
  background: linear-gradient(135deg, var(--primary) 0%, color-mix(in oklch, var(--primary), transparent 30%) 100%);
  border-radius: 50%;
  transform: translateY(-50%);
}

.markdown-content ol li {
  margin: 0.75em 0;
  line-height: 1.6;
}

.markdown-content ol {
  list-style-type: decimal;
  list-style-position: outside;
}

.markdown-content ol li::marker {
  color: var(--primary);
  font-weight: 600;
}

/* 중첩 리스트 */
.markdown-content ul ul,
.markdown-content ol ol,
.markdown-content ul ol,
.markdown-content ol ul {
  margin: 0.5em 0;
}

.markdown-content ol ol {
  counter-reset: list-counter;
}

.markdown-content ol ol li::before {
  left: -1.5rem;
}

/* 인용문 - 글래스모피즘 효과 */
.markdown-content blockquote {
  position: relative;
  margin: 1.5em 0;
  padding: 1.25rem 1.5rem;
  background: color-mix(in oklch, var(--muted), transparent 50%);
  backdrop-filter: blur(8px);
  border-left: 4px solid var(--primary);
  border-radius: 0 0.75rem 0.75rem 0;
  font-style: italic;
  color: var(--muted-foreground);
  box-shadow: var(--shadow-md);
}

.markdown-content blockquote::before {
  content: '"';
  position: absolute;
  top: -0.5rem;
  left: 1rem;
  font-size: 2rem;
  color: color-mix(in oklch, var(--primary), transparent 40%);
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
.markdown-content code:not(pre code) {
  background: linear-gradient(135deg, var(--muted) 0%, color-mix(in oklch, var(--muted), transparent 20%) 100%);
  color: var(--primary);
  padding: 0.2rem 0.4rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-family: var(--font-mono);
  font-weight: 500;
  border: 1px solid color-mix(in oklch, var(--border), transparent 50%);
  box-shadow: var(--shadow-xs);
}

/* 헤더 내 인라인 코드 - 가독성 개선 */
.markdown-content h1 code:not(pre code),
.markdown-content h2 code:not(pre code),
.markdown-content h3 code:not(pre code),
.markdown-content h4 code:not(pre code),
.markdown-content h5 code:not(pre code),
.markdown-content h6 code:not(pre code) {
  -webkit-text-fill-color: var(--background) !important;
  background: var(--primary) !important;
  color: var(--primary-foreground) !important;
  border: 1px solid color-mix(in oklch, var(--primary), transparent 30%) !important;
  font-weight: 600;
  display: inline-block;
  vertical-align: baseline;
  margin: 0 0.125rem;
}

/* 코드 블록 컨테이너 - 모던한 디자인과 복사 기능 */
.markdown-content .code-block-container {
  position: relative;
  margin: 1.5em 0;
  background: color-mix(in oklch, var(--background), var(--foreground) 3%);
  border: 1px solid color-mix(in oklch, var(--border), var(--foreground) 20%);
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px color-mix(in oklch, var(--foreground), transparent 90%), 0 2px 4px -1px color-mix(in oklch, var(--foreground), transparent 94%);
  backdrop-filter: blur(8px);
}

.markdown-content .code-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: color-mix(in oklch, var(--background), var(--foreground) 5%);
  border-bottom: 1px solid color-mix(in oklch, var(--border), var(--foreground) 30%);
  backdrop-filter: blur(4px);
}

.markdown-content .code-language {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.markdown-content .copy-code-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  color: var(--muted-foreground);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.markdown-content .copy-code-btn:hover {
  background: var(--muted);
  color: var(--foreground);
  border-color: var(--border);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.markdown-content .copy-code-btn.copied {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
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
  tab-size: 4;
  -moz-tab-size: 4;
  -o-tab-size: 4;
}

.markdown-content .code-block-container pre code {
  background: transparent;
  padding: 0;
  border: none;
  font-size: 0.875rem;
  color: var(--foreground);
  box-shadow: none;
  font-family: var(--font-mono);
  tab-size: 4;
  -moz-tab-size: 4;
  -o-tab-size: 4;
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
  font-family: var(--font-mono) !important;
  line-height: 1.5 !important;
  tab-size: 4 !important;
  -moz-tab-size: 4 !important;
  -o-tab-size: 4 !important;
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
  background: color-mix(in oklch, var(--background), var(--foreground) 8%);
  border-color: color-mix(in oklch, var(--border), var(--foreground) 40%);
}

.dark .markdown-content .code-block-header {
  background: color-mix(in oklch, var(--background), var(--foreground) 12%);
  border-bottom-color: color-mix(in oklch, var(--border), var(--foreground) 50%);
}

/* 다크 모드 테이블 스타일 강화 */
.dark .markdown-content table {
  border-color: color-mix(in oklch, var(--border), var(--foreground) 40%);
}

.dark .markdown-content th {
  background: color-mix(in oklch, var(--background), var(--foreground) 15%);
  border-bottom-color: color-mix(in oklch, var(--border), var(--foreground) 50%);
}

.dark .markdown-content td {
  background: color-mix(in oklch, var(--background), var(--foreground) 5%);
  border-bottom-color: color-mix(in oklch, var(--border), var(--foreground) 40%);
}

.dark .markdown-content tr:hover td {
  background: color-mix(in oklch, var(--background), var(--foreground) 10%);
}

/* 기존 pre 스타일은 코드 블록 컨테이너가 없는 경우를 위해 유지 */
.markdown-content pre:not(.code-block-container pre) {
  position: relative;
  margin: 1.5em 0;
  padding: 1.5rem;
  background: linear-gradient(135deg, var(--muted) 0%, color-mix(in oklch, var(--muted), transparent 10%) 100%);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  overflow-x: auto;
  box-shadow: 0 4px 6px -1px color-mix(in oklch, var(--foreground), transparent 90%), 0 2px 4px -1px color-mix(in oklch, var(--foreground), transparent 94%);
  backdrop-filter: blur(8px);
  font-family: var(--font-mono);
  tab-size: 4;
  -moz-tab-size: 4;
  -o-tab-size: 4;
}

/* 링크 - 호버 효과와 애니메이션 */
.markdown-content a {
  color: var(--primary);
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
  background: linear-gradient(90deg, var(--primary) 0%, color-mix(in oklch, var(--primary), transparent 40%) 100%);
  transition: width 0.3s ease;
}

.markdown-content a:hover {
  color: color-mix(in oklch, var(--primary), transparent 20%);
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
  box-shadow: 0 4px 6px -1px color-mix(in oklch, var(--foreground), transparent 90%), 0 2px 4px -1px color-mix(in oklch, var(--foreground), transparent 94%);
  border: 1px solid color-mix(in oklch, var(--border), var(--foreground) 20%);
}

.markdown-content th,
.markdown-content td {
  padding: 0.875rem 1rem;
  text-align: left;
  border-bottom: 1px solid color-mix(in oklch, var(--border), var(--foreground) 30%);
}

.markdown-content th {
  background: color-mix(in oklch, var(--background), var(--foreground) 8%);
  font-weight: 650;
  color: var(--foreground);
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.05em;
}

.markdown-content td {
  background: color-mix(in oklch, var(--background), var(--foreground) 2%);
}

.markdown-content tr:hover td {
  background: color-mix(in oklch, var(--background), var(--foreground) 5%);
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
  background: linear-gradient(135deg, var(--primary) 0%, color-mix(in oklch, var(--primary), transparent 10%) 100%);
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

  .markdown-content h1 {
    font-size: 1.5rem;
  }

  .markdown-content h2 {
    font-size: 1.35rem;
  }

  .markdown-content h3 {
    font-size: 1.2rem;
  }

  .markdown-content h4 {
    font-size: 1.1rem;
  }

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