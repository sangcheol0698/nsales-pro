<template>
  <div class="relative">
    <!-- 단축키 도움말 버튼 -->
    <Button
      variant="ghost"
      size="sm"
      @click="toggleHelp"
      class="h-8 w-8 p-0"
      :aria-label="$t ? $t('chat.keyboardShortcuts') : '키보드 단축키'"
    >
      <HelpCircle class="h-4 w-4" />
    </Button>

    <!-- 키보드 단축키 도움말 -->
    <div
      v-if="isHelpOpen"
      class="absolute top-full right-0 mt-2 w-80 bg-card border border-border rounded-lg shadow-lg p-4 z-50"
      role="dialog"
      :aria-label="$t ? $t('chat.keyboardShortcutsDialog') : '키보드 단축키 도움말'"
    >
      <div class="space-y-4">
        <!-- 헤더 -->
        <div class="flex items-center justify-between">
          <h3 class="font-semibold">키보드 단축키</h3>
          <Button
            variant="ghost"
            size="sm"
            @click="toggleHelp"
            class="h-6 w-6 p-0"
          >
            <X class="h-3 w-3" />
          </Button>
        </div>

        <!-- 단축키 목록 -->
        <div class="space-y-3">
          <div class="space-y-2">
            <h4 class="text-sm font-medium text-muted-foreground">일반</h4>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Ctrl</kbd>
                <span>+</span>
                <kbd class="px-2 py-1 bg-muted rounded text-xs">F</kbd>
                <span class="text-muted-foreground">검색</span>
              </div>
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Ctrl</kbd>
                <span>+</span>
                <kbd class="px-2 py-1 bg-muted rounded text-xs">N</kbd>
                <span class="text-muted-foreground">새 채팅</span>
              </div>
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Esc</kbd>
                <span class="text-muted-foreground">검색 취소</span>
              </div>
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Enter</kbd>
                <span class="text-muted-foreground">메시지 전송</span>
              </div>
            </div>
          </div>

          <div class="space-y-2">
            <h4 class="text-sm font-medium text-muted-foreground">내비게이션</h4>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">↑</kbd>
                <kbd class="px-2 py-1 bg-muted rounded text-xs">↓</kbd>
                <span class="text-muted-foreground">세션 이동</span>
              </div>
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Alt</kbd>
                <span>+</span>
                <kbd class="px-2 py-1 bg-muted rounded text-xs">1-9</kbd>
                <span class="text-muted-foreground">빠른 선택</span>
              </div>
            </div>
          </div>

          <div class="space-y-2">
            <h4 class="text-sm font-medium text-muted-foreground">입력</h4>
            <div class="grid grid-cols-1 gap-2 text-sm">
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Shift</kbd>
                <span>+</span>
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Enter</kbd>
                <span class="text-muted-foreground">줄바꿈</span>
              </div>
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Ctrl</kbd>
                <span>+</span>
                <kbd class="px-2 py-1 bg-muted rounded text-xs">V</kbd>
                <span class="text-muted-foreground">붙여넣기</span>
              </div>
            </div>
          </div>

          <div class="space-y-2">
            <h4 class="text-sm font-medium text-muted-foreground">메시지</h4>
            <div class="grid grid-cols-1 gap-2 text-sm">
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Ctrl</kbd>
                <span>+</span>
                <kbd class="px-2 py-1 bg-muted rounded text-xs">C</kbd>
                <span class="text-muted-foreground">복사</span>
              </div>
              <div class="flex items-center gap-2">
                <kbd class="px-2 py-1 bg-muted rounded text-xs">Del</kbd>
                <span class="text-muted-foreground">삭제</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 팁 -->
        <div class="pt-3 border-t border-border">
          <div class="flex items-start gap-2">
            <div class="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span class="text-xs text-white">💡</span>
            </div>
            <div class="text-sm text-muted-foreground">
              <p class="font-medium">팁:</p>
              <p>메시지 위에 마우스를 올리면 추가 옵션이 표시됩니다.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { HelpCircle, X } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'

const isHelpOpen = ref(false)

const toggleHelp = () => {
  isHelpOpen.value = !isHelpOpen.value
}

// 클릭 아웃사이드로 도움말 닫기
document.addEventListener('click', (event) => {
  const target = event.target as HTMLElement
  if (isHelpOpen.value && !target.closest('.keyboard-shortcuts')) {
    isHelpOpen.value = false
  }
})
</script>

<style scoped>
kbd {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", monospace;
}
</style>