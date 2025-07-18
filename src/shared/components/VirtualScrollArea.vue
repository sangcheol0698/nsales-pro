<template>
  <div 
    ref="containerRef"
    class="relative overflow-auto"
    :style="{ height: height + 'px' }"
    @scroll="handleScroll"
  >
    <!-- 스크롤바 높이 조정을 위한 더미 요소 -->
    <div :style="{ height: totalHeight + 'px', position: 'relative' }">
      <!-- 실제 렌더링되는 아이템들 -->
      <div 
        :style="{ 
          transform: `translateY(${offsetY}px)`,
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
        }"
      >
        <div
          v-for="item in visibleItems"
          :key="getItemKey(item)"
          :style="{ height: itemHeight + 'px' }"
          class="flex items-center"
        >
          <slot :item="item" :index="item.index" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  items: any[]
  itemHeight: number
  height: number
  buffer?: number
  getItemKey?: (item: any) => string | number
}

const props = withDefaults(defineProps<Props>(), {
  buffer: 5,
  getItemKey: (item: any) => item.id || item.index
})

const containerRef = ref<HTMLDivElement>()
const scrollTop = ref(0)

const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleRange = computed(() => {
  const containerHeight = props.height
  const start = Math.floor(scrollTop.value / props.itemHeight)
  const end = Math.min(
    props.items.length - 1,
    Math.ceil((scrollTop.value + containerHeight) / props.itemHeight)
  )
  
  return {
    start: Math.max(0, start - props.buffer),
    end: Math.min(props.items.length - 1, end + props.buffer)
  }
})

const visibleItems = computed(() => {
  const { start, end } = visibleRange.value
  return props.items.slice(start, end + 1).map((item, index) => ({
    ...item,
    index: start + index
  }))
})

const offsetY = computed(() => {
  return visibleRange.value.start * props.itemHeight
})

const handleScroll = (event: Event) => {
  const target = event.target as HTMLDivElement
  scrollTop.value = target.scrollTop
}

// 스크롤 위치 제어 함수
const scrollToIndex = (index: number) => {
  if (containerRef.value) {
    const targetScrollTop = index * props.itemHeight
    containerRef.value.scrollTop = targetScrollTop
  }
}

const scrollToBottom = () => {
  if (containerRef.value) {
    containerRef.value.scrollTop = totalHeight.value
  }
}

// 외부에서 사용할 수 있도록 expose
defineExpose({
  scrollToIndex,
  scrollToBottom,
  scrollTop: scrollTop.value
})
</script>