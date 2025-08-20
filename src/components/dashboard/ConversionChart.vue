<template>
  <div class="h-full w-full flex items-center justify-center">
    <div class="text-center">
      <div class="relative w-16 h-16 mx-auto">
        <svg class="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
          <path
            class="text-muted stroke-current"
            stroke-width="3"
            fill="transparent"
            stroke-dasharray="100, 100"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            class="text-primary stroke-current transition-all duration-1000 ease-in-out"
            stroke-width="3"
            fill="transparent"
            :stroke-dasharray="`${conversionRate * 3.1}, 100`"
            stroke-linecap="round"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-xs font-semibold">{{ conversionRate.toFixed(1) }}%</span>
        </div>
      </div>
      <p class="text-xs text-muted-foreground mt-2">Conversion</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const conversionRate = ref(3.24)

// Simulate real-time updates
let updateInterval: NodeJS.Timeout | null = null

onMounted(() => {
  updateInterval = setInterval(() => {
    conversionRate.value = Math.max(1.5, Math.min(5, conversionRate.value + (Math.random() - 0.5) * 0.5))
  }, 3000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>