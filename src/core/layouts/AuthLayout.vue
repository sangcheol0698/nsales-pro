<template>
  <div class="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6 md:p-10">
    <div class="flex w-full max-w-sm flex-col gap-6">
      <a :href="logoHref" class="flex items-center gap-2 self-center font-medium">
        <div
          class="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground"
        >
          <GalleryVerticalEnd class="size-4" />
        </div>
        Abacus Inc.
      </a>
      <!-- 폼 컴포넌트를 위한 슬롯 -->
      <slot></slot>
      <!-- 약관 동의 텍스트 (선택적으로 표시) -->
      <div
        v-if="showTerms"
        class="text-balance text-center text-xs text-muted-foreground [&_a]:underline [&_a]:underline-offset-4 [&_a]:hover:text-primary"
      >
        By clicking continue, you agree to our <a href="#">Terms of Service</a> and
        <a href="#">Privacy Policy</a>.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { GalleryVerticalEnd } from 'lucide-vue-next';

// 로고 링크 경로를 위한 props
defineProps({
  // 로고 클릭 시 이동할 경로
  logoHref: {
    type: String,
    default: '/'
  },
  // 약관 동의 텍스트 표시 여부
  showTerms: {
    type: Boolean,
    default: true
  }
});
</script>

<style scoped></style>