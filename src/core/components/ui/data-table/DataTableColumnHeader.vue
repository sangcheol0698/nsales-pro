<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { cn } from '@/shared/utils/utils'

interface DataTableColumnHeaderProps<TData, TValue> {
  column: Column<TData, TValue>
  title: string
  class?: string
}

const props = defineProps<DataTableColumnHeaderProps<any, any>>()

// Log the column instance for debugging
console.log('DataTableColumnHeader - column instance:', {
  columnId: props.column.id,
  columnDef: props.column.columnDef,
  table: props.column.table
})

function toggleSorting(column: Column<any, any>) {
  // Cycle through three states: no sorting -> asc -> desc -> no sorting
  const currentSortingState = column.getIsSorted()
  console.log('DataTableColumnHeader - toggleSorting called', { 
    columnId: column.id, 
    currentSortingState 
  })

  if (currentSortingState === false) {
    // Currently not sorted, set to ascending
    console.log('DataTableColumnHeader - Setting to ascending')
    column.toggleSorting(false)
  } else if (currentSortingState === 'asc') {
    // Currently ascending, set to descending
    console.log('DataTableColumnHeader - Setting to descending')
    column.toggleSorting(true)
  } else {
    // Currently descending, clear sorting
    console.log('DataTableColumnHeader - Clearing sorting')
    column.clearSorting()
  }
}
</script>

<template>
  <div :class="cn('flex items-center space-x-2', props.class)">
    <Button
      variant="ghost"
      size="sm"
      class="-ml-3 h-8 data-[state=open]:bg-accent"
      @click="toggleSorting(column)"
    >
      <span>{{ title }}</span>
      <ArrowUpDown v-if="!column.getIsSorted()" class="ml-2 h-4 w-4" />
      <ArrowUp v-else-if="column.getIsSorted() === 'asc'" class="ml-2 h-4 w-4" />
      <ArrowDown v-else class="ml-2 h-4 w-4" />
    </Button>
  </div>
</template>
