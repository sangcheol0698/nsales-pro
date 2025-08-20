<template>
  <div class="h-[120px] w-full">
    <div class="h-[80px] flex items-center justify-center mb-4">
      <div class="relative">
        <svg width="80" height="80" viewBox="0 0 80 80" class="transform -rotate-90">
          <circle
            cx="40"
            cy="40"
            r="30"
            stroke="currentColor"
            stroke-width="8"
            fill="transparent"
            class="text-muted-foreground/20"
          />
          <circle
            v-for="(item, index) in chartData"
            :key="item.name"
            cx="40"
            cy="40"
            r="30"
            :stroke="item.color"
            stroke-width="8"
            fill="transparent"
            :stroke-dasharray="`${(item.value / 100) * circumference} ${circumference}`"
            :stroke-dashoffset="`-${getOffset(index)}`"
            class="transition-all duration-1000 ease-in-out"
          />
        </svg>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-center">
            <div class="text-sm font-semibold">100%</div>
            <div class="text-xs text-muted-foreground">Traffic</div>
          </div>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-2 gap-2 text-xs">
      <div v-for="item in chartData" :key="item.name" class="flex items-center gap-2">
        <div class="h-2 w-2 rounded-full" :style="{ backgroundColor: item.color }" />
        <span class="text-muted-foreground">{{ item.name }}</span>
        <span class="ml-auto font-medium">{{ item.value }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const chartData = ref([
  { name: 'Organic', value: 45, color: 'hsl(var(--primary))' },
  { name: 'Social', value: 25, color: 'hsl(var(--secondary))' },
  { name: 'Direct', value: 20, color: 'hsl(var(--accent))' },
  { name: 'Email', value: 10, color: 'hsl(var(--muted))' },
])

const circumference = computed(() => 2 * Math.PI * 30) // 30 is the radius

const getOffset = (index: number): number => {
  let offset = 0
  for (let i = 0; i < index; i++) {
    offset += (chartData.value[i].value / 100) * circumference.value
  }
  return offset
}
</script>