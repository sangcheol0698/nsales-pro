<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed, ref, watch } from 'vue'
import { Calendar as CalendarIcon, X } from 'lucide-vue-next'

import { cn } from '@/shared/utils/utils'
import { Button } from '@/core/components/ui/button'
import { Calendar } from '@/core/components/ui/calendar'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/core/components/ui/popover'

interface DataTableModernDateRangeProps<TData, TValue> {
  column?: Column<TData, TValue>
  title?: string
  placeholder?: string
}

const props = withDefaults(defineProps<DataTableModernDateRangeProps<any, any>>(), {
  title: '날짜 범위',
  placeholder: '날짜 선택',
})

// Use a simple date range object with start and end Date objects
const dateRange = ref<{ start?: Date; end?: Date }>({})

const selectedValues = computed(() => {
  const filterValue = props.column?.getFilterValue() as { start?: Date; end?: Date } | undefined
  return filterValue || {}
})

// Watch for changes in column filter value
watch(() => selectedValues.value, (newValue) => {
  dateRange.value = newValue || {}
}, { immediate: true })

function handleDateSelect(date: Date | undefined) {
  if (!date) {
    // Clear selection
    dateRange.value = {}
    props.column?.setFilterValue(undefined)
    return
  }

  const current = dateRange.value

  if (!current.start || (current.start && current.end)) {
    // Start new range
    dateRange.value = { start: date }
    props.column?.setFilterValue({ start: date })
  } else if (current.start && !current.end) {
    // Complete the range
    if (date >= current.start) {
      dateRange.value = { start: current.start, end: date }
      props.column?.setFilterValue({ start: current.start, end: date })
    } else {
      // If end date is before start, swap them
      dateRange.value = { start: date, end: current.start }
      props.column?.setFilterValue({ start: date, end: current.start })
    }
  }
}

function clearFilter() {
  dateRange.value = {}
  props.column?.setFilterValue(undefined)
}

const displayText = computed(() => {
  if (!dateRange.value.start) return props.placeholder
  
  const startStr = dateRange.value.start.toLocaleDateString('ko-KR')
  
  if (dateRange.value.end) {
    const endStr = dateRange.value.end.toLocaleDateString('ko-KR')
    return `${startStr} ~ ${endStr}`
  }
  
  return `${startStr} (종료일 선택)`
})

const hasSelection = computed(() => !!dateRange.value.start)
</script>

<template>
  <div class="flex items-center gap-2">
    <Popover>
      <PopoverTrigger as-child>
        <Button
          variant="outline"
          size="sm"
          :class="cn(
            'h-9 px-3 justify-start text-left font-medium min-w-[200px]',
            'border-dashed transition-all duration-200',
            hasSelection 
              ? 'border-primary/60 bg-primary/5 text-primary' 
              : 'border-border/60 text-muted-foreground hover:border-primary/50 hover:bg-primary/5'
          )"
        >
          <CalendarIcon 
            :class="cn(
              'mr-2 h-4 w-4 transition-colors duration-200',
              hasSelection ? 'text-primary' : 'text-muted-foreground'
            )" 
          />
          <span class="text-sm">{{ displayText }}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent class="w-auto p-0 border-border/60 shadow-xl" align="start">
        <div class="p-3 space-y-3">
          <div class="flex items-center gap-2 pb-2 border-b border-border/20">
            <CalendarIcon class="h-4 w-4 text-primary" />
            <span class="text-sm font-medium text-foreground/80">{{ title }} 선택</span>
          </div>
          
          <Calendar
            :model-value="dateRange.start"
            mode="single"
            :placeholder="dateRange.start"
            @update:model-value="handleDateSelect"
            class="rounded-md border-0"
          />
          
          <div v-if="dateRange.start && !dateRange.end" class="text-xs text-muted-foreground text-center p-2 bg-muted/20 rounded-md">
            종료 날짜를 선택해주세요
          </div>
          
          <div v-if="dateRange.start && dateRange.end" class="text-xs text-center p-2 bg-primary/5 text-primary rounded-md">
            {{ dateRange.start.toLocaleDateString('ko-KR') }} ~ {{ dateRange.end.toLocaleDateString('ko-KR') }}
          </div>
        </div>
      </PopoverContent>
    </Popover>
    
    <Button
      v-if="hasSelection"
      variant="ghost"
      size="sm"
      :class="cn(
        'h-7 w-7 p-0 rounded-md',
        'hover:bg-destructive/10 hover:text-destructive',
        'transition-all duration-200'
      )"
      @click="clearFilter"
    >
      <X class="h-3 w-3" />
    </Button>
  </div>
</template>