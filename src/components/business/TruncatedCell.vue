<template>
  <div 
    :class="cn(
      'truncate max-w-0 cursor-default',
      className
    )"
    :style="{ maxWidth: maxWidth }"
  >
    {{ text || '-' }}
  </div>
</template>

<script setup lang="ts">
import { cn } from '@/lib/utils';

interface Props {
  text: string | null | undefined;
  maxWidth?: string;
  className?: string;
}

const props = withDefaults(defineProps<Props>(), {
  maxWidth: '12rem',
  className: '',
});
</script>