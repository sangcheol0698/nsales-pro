<template>
  <div class="h-[350px] w-full">
    <div class="h-full w-full flex items-center justify-center bg-muted/20 rounded-lg border-2 border-dashed border-muted-foreground/25">
      <div class="text-center">
        <TrendingUp class="mx-auto h-12 w-12 text-muted-foreground" />
        <h3 class="mt-2 text-sm font-medium text-muted-foreground">Revenue Chart</h3>
        <p class="mt-1 text-xs text-muted-foreground">
          Revenue data: ${{ currentRevenue.toLocaleString() }}
        </p>
        <div class="mt-4 w-full max-w-xs mx-auto">
          <div class="flex justify-between text-xs text-muted-foreground mb-2">
            <span>Jan</span>
            <span>Dec</span>
          </div>
          <div class="h-2 bg-muted rounded-full overflow-hidden">
            <div 
              class="h-full bg-primary transition-all duration-1000 ease-in-out" 
              :style="{ width: `${Math.min(100, (currentRevenue / 60000) * 100)}%` }"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { TrendingUp } from 'lucide-vue-next'

const currentRevenue = ref(45231)

// Simulate real-time updates
let updateInterval: NodeJS.Timeout | null = null

onMounted(() => {
  updateInterval = setInterval(() => {
    currentRevenue.value = Math.floor(Math.random() * 15000) + 40000
  }, 5000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>