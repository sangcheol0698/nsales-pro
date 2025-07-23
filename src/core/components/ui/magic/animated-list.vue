<template>
  <div>
    <div
      v-for="(item, index) in items"
      :key="item.id || index"
      :class="cn(
        'mx-auto w-full',
        className
      )"
      :style="{
        '--animation-delay': `${delay * index}ms`
      }"
      class="animate-in slide-in-from-bottom-5 fade-in duration-300"
    >
      <!-- 슬롯을 통해 커스텀 렌더링 허용 -->
      <slot :item="item" :index="index">
        <!-- 기본 렌더링 -->
        <div class="flex items-center space-x-4 p-4 border rounded-lg">
          <div v-if="item.icon" class="flex-shrink-0">
            <component :is="item.icon" class="h-5 w-5" />
          </div>
          <div class="flex-1 min-w-0">
            <p v-if="item.title" class="text-sm font-medium text-foreground truncate">
              {{ item.title }}
            </p>
            <p v-if="item.description" class="text-sm text-muted-foreground">
              {{ item.description }}
            </p>
          </div>
          <div v-if="item.time" class="text-xs text-muted-foreground">
            {{ item.time }}
          </div>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { cn } from '@/shared/utils/utils'

interface AnimatedListItem {
  id?: string | number
  title?: string
  description?: string
  icon?: any
  time?: string
  [key: string]: any
}

interface Props {
  items: AnimatedListItem[]
  className?: string
  delay?: number
}

const props = withDefaults(defineProps<Props>(), {
  delay: 100,
  className: ''
})
</script>

<style scoped>
@keyframes slide-in-from-bottom {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-in {
  animation-delay: var(--animation-delay);
  animation-fill-mode: both;
}

.slide-in-from-bottom-5 {
  animation-name: slide-in-from-bottom;
}

.fade-in {
  animation-name: fade-in;
}

.duration-300 {
  animation-duration: 300ms;
}
</style>