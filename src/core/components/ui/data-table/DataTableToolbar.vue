<script setup lang="ts">
import type { Column, Table } from '@tanstack/vue-table'
import { computed } from 'vue'
import { ChevronDown, X } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Input } from '@/core/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu'

interface FilterConfig {
  columnId: string
  type: 'text' | 'select' | 'dateRange' | 'faceted'
  title: string
  placeholder?: string
  options?: { label: string; value: string; icon?: any }[]
}

interface DataTableToolbarProps<TData> {
  table: Table<TData>
  searchPlaceholder?: string
  searchColumnId?: string
  getColumnLabel?: (columnId: string) => string
  filters?: FilterConfig[]
}

const props = defineProps<DataTableToolbarProps<any>>()

function getColumnLabel(columnId: string): string {
  if (props.getColumnLabel) {
    return props.getColumnLabel(columnId)
  }
  return columnId
}

// Check if any filters are active
const isFiltered = computed(() => {
  // Check if any column has an active filter
  return props.table.getState().columnFilters.length > 0
})

// Reset all filters
function resetFilters() {
  props.table.resetColumnFilters()
}

const searchColumnId = props.searchColumnId || 'name'
</script>

<template>
  <div class="flex flex-col space-y-4">
    <!-- Main search and controls row -->
    <div class="flex items-center justify-between">
      <div class="flex flex-1 items-center space-x-2">
        <!-- Primary search input -->
        <Input
          class="max-w-sm"
          :placeholder="searchPlaceholder || '검색...'"
          :model-value="table.getColumn(searchColumnId)?.getFilterValue() as string"
          @update:model-value="table.getColumn(searchColumnId)?.setFilterValue($event)"
        />
        
        <!-- Additional filter components will be added here via slot -->
        <slot name="filters"></slot>
        
        <!-- Reset filters button -->
        <Button
          v-if="isFiltered"
          variant="ghost"
          size="sm"
          class="h-8 px-2 lg:px-3"
          @click="resetFilters"
        >
          초기화
          <X class="ml-2 h-4 w-4" />
        </Button>
      </div>
      
      <!-- Column visibility dropdown -->
      <div class="flex items-center space-x-2">
        <slot name="actions"></slot>
        
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="outline" size="sm" class="ml-auto h-8">
              컬럼 <ChevronDown class="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuCheckboxItem
              v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
              :key="column.id"
              class="capitalize"
              :model-value="column.getIsVisible()"
              @update:model-value="(value) => {
                column.toggleVisibility(!!value)
              }"
            >
              {{ getColumnLabel(column.id) }}
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
    
    <!-- Custom toolbar content via default slot -->
    <slot></slot>
  </div>
</template>