<script setup lang="ts">
import type { Table } from '@tanstack/vue-table'
import { computed } from 'vue'
import { ChevronDown, Settings2, Filter, RotateCcw } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu'
import { Badge } from '@/core/components/ui/badge'
import { cn } from '@/shared/utils/utils'
import DataTableModernSearch from './DataTableModernSearch.vue'

interface DataTableModernToolbarProps<TData> {
  table: Table<TData>
  searchPlaceholder?: string
  searchColumnId?: string
  getColumnLabel?: (columnId: string) => string
  title?: string
  description?: string
}

const props = defineProps<DataTableModernToolbarProps<any>>()

function getColumnLabel(columnId: string): string {
  if (props.getColumnLabel) {
    return props.getColumnLabel(columnId)
  }
  return columnId
}

// Check if any filters are active
const isFiltered = computed(() => {
  return props.table.getState().columnFilters.length > 0
})

const filterCount = computed(() => {
  return props.table.getState().columnFilters.length
})

// Reset all filters
function resetFilters() {
  props.table.resetColumnFilters()
}

function getSearchColumn() {
  const searchColumnId = props.searchColumnId || 'name'
  return props.table.getColumn(searchColumnId)
}

const searchColumn = computed(() => getSearchColumn())
</script>

<template>
  <div class="space-y-6">
    <!-- Modern header section -->
    <div v-if="title || description" class="relative">
      <div class="absolute inset-0 bg-gradient-to-r from-primary/5 via-primary/2 to-transparent rounded-xl" />
      <div class="relative p-6 space-y-2">
        <div v-if="title" class="flex items-center gap-3">
          <div class="w-1 h-6 bg-gradient-to-b from-primary to-primary/60 rounded-full" />
          <h1 class="text-2xl font-bold text-foreground/90 tracking-tight">{{ title }}</h1>
        </div>
        <p v-if="description" class="text-muted-foreground text-base leading-relaxed ml-4">
          {{ description }}
        </p>
      </div>
    </div>

    <!-- Modern main toolbar -->
    <div class="flex flex-col space-y-4">
      <!-- Primary controls row -->
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div class="flex flex-col sm:flex-row flex-1 items-stretch sm:items-center gap-4">
          <!-- Modern search -->
          <div class="w-full sm:max-w-md">
            <DataTableModernSearch
              :column="searchColumn"
              :placeholder="searchPlaceholder || '검색...'"
            />
          </div>
          
          <!-- Filter section with modern spacing -->
          <div class="flex items-center gap-2 sm:gap-3 flex-wrap">
            <slot name="filters"></slot>
          </div>
        </div>
        
        <!-- Action buttons with modern spacing -->
        <div class="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          <slot name="actions"></slot>
          
          <!-- Modern column visibility dropdown -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button 
                variant="outline" 
                size="sm" 
                :class="cn(
                  'h-9 px-3 border-border/60 group relative overflow-hidden',
                  'hover:border-primary/50 hover:bg-primary/5 transition-all duration-200'
                )"
              >
                <div class="relative flex items-center gap-2">
                  <Settings2 
                    :class="cn(
                      'h-4 w-4 transition-all duration-200',
                      'text-muted-foreground group-hover:text-primary'
                    )" 
                  />
                  <span class="text-sm font-medium">컬럼</span>
                  <ChevronDown 
                    :class="cn(
                      'h-4 w-4 transition-all duration-200',
                      'text-muted-foreground group-hover:text-primary group-hover:rotate-180'
                    )" 
                  />
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent 
              align="end" 
              class="w-52 border-border/60 shadow-xl"
            >
              <div class="p-3 space-y-3">
                <div class="flex items-center gap-2 pb-2 border-b border-border/20">
                  <Settings2 class="h-4 w-4 text-muted-foreground" />
                  <span class="text-sm font-medium text-foreground/80">컬럼 표시 설정</span>
                </div>
                <div class="space-y-1">
                  <DropdownMenuCheckboxItem
                    v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
                    :key="column.id"
                    :class="cn(
                      'capitalize transition-all duration-200 rounded-md px-2 py-2',
                      'hover:bg-primary/5 hover:text-primary text-sm'
                    )"
                    :model-value="column.getIsVisible()"
                    @update:model-value="(value) => {
                      column.toggleVisibility(!!value)
                    }"
                  >
                    {{ getColumnLabel(column.id) }}
                  </DropdownMenuCheckboxItem>
                </div>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      
      <!-- Modern filter status row -->
      <div v-if="isFiltered" class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <Filter class="h-4 w-4 text-primary" />
            <span class="text-sm font-medium text-foreground/80">활성 필터:</span>
          </div>
          
          <Badge 
            variant="secondary"
            :class="cn(
              'h-7 px-3 text-xs font-medium rounded-full',
              'bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 transition-colors'
            )"
          >
            {{ filterCount }}개 필터 적용됨
          </Badge>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          :class="cn(
            'h-8 px-3 text-xs gap-2',
            'text-muted-foreground hover:text-destructive hover:bg-destructive/5',
            'transition-all duration-200'
          )"
          @click="resetFilters"
        >
          <RotateCcw class="h-3 w-3" />
          필터 초기화
        </Button>
      </div>
      
      <!-- Custom toolbar content via default slot -->
      <slot></slot>
    </div>
  </div>
</template>