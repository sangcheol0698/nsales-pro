<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed, ref, watch } from 'vue'
import { CalendarIcon, X } from 'lucide-vue-next'

import { cn } from '@/shared/utils/utils'
import { Button } from '@/core/components/ui/button'
import { Calendar } from '@/core/components/ui/calendar'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/core/components/ui/popover'

interface DataTableDateRangeFilterProps<TData, TValue> {
  column?: Column<TData, TValue>
  title?: string
  placeholder?: string
}

const props = withDefaults(defineProps<DataTableDateRangeFilterProps<any, any>>(), {
  title: '날짜 범위',
  placeholder: '날짜 선택',
})

const date = ref<{start: Date, end: Date} | undefined>()

const selectedValues = computed(() => props.column?.getFilterValue() as {start: Date, end: Date} | undefined)

// Watch for changes in column filter value
watch(() => selectedValues.value, (newValue) => {
  date.value = newValue
}, { immediate: true })

function handleSelect(selectedDate: {start: Date, end: Date} | undefined) {
  date.value = selectedDate
  props.column?.setFilterValue(selectedDate)
}

function clearFilter() {
  date.value = undefined
  props.column?.setFilterValue(undefined)
}

const displayText = computed(() => {
  if (!date.value?.start) return props.placeholder
  
  if (date.value.end) {
    return `${date.value.start.toLocaleDateString('ko-KR')} - ${date.value.end.toLocaleDateString('ko-KR')}`
  }
  
  return date.value.start.toLocaleDateString('ko-KR')
})
</script>

<template>
  <div class="flex items-center space-x-2">
    <Popover>
      <PopoverTrigger as-child>
        <Button
          variant="outline"
          size="sm"
          :class="cn(
            'h-8 justify-start text-left font-normal',
            !date?.start && 'text-muted-foreground border-dashed'
          )"
        >
          <CalendarIcon class="mr-2 h-4 w-4" />
          {{ displayText }}
        </Button>
      </PopoverTrigger>
      <PopoverContent class="w-auto p-0" align="start">
        <Calendar
          v-model="date"
          mode="range"
          :placeholder="date?.start"
          @update:model-value="handleSelect"
        />
      </PopoverContent>
    </Popover>
    
    <Button
      v-if="date?.start"
      variant="ghost"
      size="sm"
      class="h-8 px-2"
      @click="clearFilter"
    >
      <X class="h-4 w-4" />
    </Button>
  </div>
</template>