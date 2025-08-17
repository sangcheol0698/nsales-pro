<template>
  <TooltipProvider>
    <Tooltip>
      <TooltipTrigger as-child>
        <div 
          :class="cn(
            'truncate max-w-0 cursor-default',
            className
          )"
          :style="{ maxWidth: maxWidth }"
        >
          {{ text || '-' }}
        </div>
      </TooltipTrigger>
      <TooltipContent v-if="shouldShowTooltip" side="top" align="start">
        <p class="max-w-xs break-words">{{ text }}</p>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { cn } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface Props {
  text: string | null | undefined;
  maxWidth?: string;
  className?: string;
}

const props = withDefaults(defineProps<Props>(), {
  maxWidth: '12rem',
  className: '',
});

// 텍스트가 있고 비어있지 않을 때만 tooltip 표시
const shouldShowTooltip = computed(() => {
  return props.text && props.text.trim().length > 0;
});
</script>