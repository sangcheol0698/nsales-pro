<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/shared/utils/utils.ts'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div
    data-slot="sidebar-header"
    data-sidebar="header"
    :class="cn('flex flex-col gap-2 p-2', props.class)"
  >
    <slot />
  </div>
</template>
