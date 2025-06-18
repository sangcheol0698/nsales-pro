<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/shared/utils/utils.ts'
import { Primitive, type PrimitiveProps } from 'reka-ui'
import { type ButtonVariants, buttonVariants } from '.'

interface Props extends PrimitiveProps {
  variant?: ButtonVariants['variant']
  size?: ButtonVariants['size']
  class?: HTMLAttributes['class']
  loading?: boolean
  loadingText?: string
}

const props = withDefaults(defineProps<Props>(), {
  as: 'button',
  loading: false,
  loadingText: '로딩 중...',
})
</script>

<template>
  <Primitive
    data-slot="button"
    :as="as"
    :as-child="asChild"
    :disabled="loading || $attrs.disabled"
    :class="cn(buttonVariants({ variant, size }), props.class)"
  >
    <div class="flex items-center justify-center gap-2">
      <div
        v-if="loading"
        class="size-4 animate-spin rounded-full border-2 border-current border-t-transparent"
      />
      <slot v-if="!loading" />
      <span v-else>{{ loadingText }}</span>
    </div>
  </Primitive>
</template>
