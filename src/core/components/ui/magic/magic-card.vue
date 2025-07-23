<template>
  <div
    ref="cardRef"
    :class="cn(
      'relative overflow-hidden rounded-xl border bg-background p-4 transition-all duration-300',
      'before:absolute before:inset-0 before:rounded-xl before:p-px before:opacity-0 before:transition-opacity before:duration-300',
      'hover:before:opacity-100',
      className
    )"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <!-- 마우스 팔로우 그라데이션 테두리 -->
    <div
      ref="gradientRef"
      class="absolute inset-0 rounded-xl opacity-0 transition-opacity duration-300 pointer-events-none"
      :style="gradientStyle"
    />
    
    <!-- 콘텐츠 -->
    <div class="relative z-10">
      <slot />
    </div>
    
    <!-- 백드롭 -->
    <div class="absolute inset-px bg-background rounded-xl" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { cn } from '@/shared/utils/utils'

interface Props {
  className?: string
  gradientSize?: number
  gradientColor?: string
  gradientOpacity?: number
}

const props = withDefaults(defineProps<Props>(), {
  className: '',
  gradientSize: 200,
  gradientColor: '#3b82f6',
  gradientOpacity: 0.3
})

const cardRef = ref<HTMLElement>()
const gradientRef = ref<HTMLElement>()
const mouseX = ref(0)
const mouseY = ref(0)
const isHovered = ref(false)

const gradientStyle = computed(() => {
  if (!isHovered.value) return { opacity: '0' }

  const hex = props.gradientColor.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)

  return {
    background: `radial-gradient(${props.gradientSize}px circle at ${mouseX.value}px ${mouseY.value}px, rgba(${r}, ${g}, ${b}, ${props.gradientOpacity}) 0%, transparent 65%)`,
    opacity: '1'
  }
})

const handleMouseMove = (e: MouseEvent) => {
  if (!cardRef.value) return

  const rect = cardRef.value.getBoundingClientRect()
  mouseX.value = e.clientX - rect.left
  mouseY.value = e.clientY - rect.top
  isHovered.value = true
}

const handleMouseLeave = () => {
  isHovered.value = false
}
</script>

<style scoped>
.before\:absolute::before {
  content: '';
  position: absolute;
}

.before\:inset-0::before {
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.before\:rounded-xl::before {
  border-radius: 0.75rem;
}

.before\:p-px::before {
  padding: 1px;
}

.before\:opacity-0::before {
  opacity: 0;
}

.before\:transition-opacity::before {
  transition-property: opacity;
}

.before\:duration-300::before {
  transition-duration: 300ms;
}

.hover\:before\:opacity-100:hover::before {
  opacity: 1;
}
</style>