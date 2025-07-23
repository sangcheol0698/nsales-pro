<template>
  <button
    ref="buttonRef"
    :class="cn(
      'group relative cursor-pointer overflow-hidden rounded-lg px-6 py-3 font-medium text-white transition-transform duration-300 ease-in-out active:translate-y-px',
      className
    )"
    :style="{
      '--spread': '90deg',
      '--shimmer-color': shimmerColor,
      '--radius': borderRadius,
      '--speed': shimmerDuration,
      '--cut': shimmerSize,
      '--bg': background,
      'background': background,
      'borderRadius': borderRadius
    }"
    @click="$emit('click')"
  >
    <!-- Shimmer container -->
    <div class="absolute inset-0 -z-30 overflow-visible blur-[2px]">
      <!-- Shimmer -->
      <div class="absolute inset-0 h-full animate-shimmer-slide aspect-square border-radius-0">
        <!-- Shimmer before -->
        <div class="absolute -inset-full w-auto rotate-0 animate-spin-around shimmer-gradient" />
      </div>
    </div>
    
    <!-- Content -->
    <span class="relative z-10">
      <slot />
    </span>

    <!-- Highlight -->
    <div class="absolute inset-0 size-full rounded-2xl px-4 py-1.5 text-sm font-medium shadow-inner transition-all duration-300 ease-in-out group-hover:shadow-inner-strong group-active:shadow-inner-active" />

    <!-- Backdrop -->
    <div 
      class="absolute -z-20"
      :style="{
        background: background,
        borderRadius: borderRadius,
        inset: shimmerSize
      }"
    />
  </button>
</template>

<script setup lang="ts">
import { cn } from '@/shared/utils/utils'

interface Props {
  shimmerColor?: string
  shimmerSize?: string
  borderRadius?: string
  shimmerDuration?: string
  background?: string
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  shimmerColor: '#ffffff',
  shimmerSize: '0.05em',
  shimmerDuration: '3s',
  borderRadius: '100px',
  background: 'rgba(0, 0, 0, 1)',
  className: ''
})

defineEmits<{
  click: []
}>()
</script>

<style scoped>
@keyframes shimmer-slide {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes spin-around {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.animate-shimmer-slide {
  animation: shimmer-slide var(--speed) infinite;
}

.animate-spin-around {
  animation: spin-around var(--speed) linear infinite;
}

.shimmer-gradient {
  background: conic-gradient(
    from calc(270deg - (var(--spread) * 0.5)),
    transparent 0,
    var(--shimmer-color) var(--spread),
    transparent var(--spread)
  );
  transform: translate(0, 0);
}

.shadow-inner {
  box-shadow: inset 0 -8px 10px rgba(255, 255, 255, 0.12);
}

.shadow-inner-strong {
  box-shadow: inset 0 -6px 10px rgba(255, 255, 255, 0.25);
}

.shadow-inner-active {
  box-shadow: inset 0 -10px 10px rgba(255, 255, 255, 0.25);
}
</style>