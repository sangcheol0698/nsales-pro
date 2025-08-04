<script setup lang="ts">
import type { Table } from '@tanstack/vue-table'
import { computed } from 'vue'
import { ChevronDown, X, Settings, Sparkles, Filter } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu'
import { Badge } from '@/core/components/ui/badge'
import { cn } from '@/shared/utils/utils'
import DataTableMagicSearch from './DataTableMagicSearch.vue'

interface DataTableMagicToolbarProps<TData> {
  table: Table<TData>
  searchPlaceholder?: string
  searchColumnId?: string
  getColumnLabel?: (columnId: string) => string
  title?: string
  description?: string
}

const props = defineProps<DataTableMagicToolbarProps<any>>()

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
  <div class="space-y-4">
    <!-- Header section with magic gradient -->
    <div v-if="title || description" class="relative">
      <div class="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5 rounded-lg" />
      <div class="relative p-4 space-y-1">
        <div v-if="title" class="flex items-center gap-2">
          <Sparkles class="h-5 w-5 text-primary animate-pulse" />
          <h2 class="text-lg font-semibold tracking-tight">{{ title }}</h2>
        </div>
        <p v-if="description" class="text-sm text-muted-foreground">
          {{ description }}
        </p>
      </div>
    </div>

    <!-- Main toolbar -->
    <div class="flex flex-col space-y-4">
      <!-- Search and filter controls -->
      <div class="flex items-center justify-between">
        <div class="flex flex-1 items-center space-x-3">
          <!-- Magic search -->
          <div class="w-full max-w-sm">
            <DataTableMagicSearch
              :column="searchColumn"
              :placeholder="searchPlaceholder || '검색...'"
            />
          </div>
          
          <!-- Filter section -->
          <div class="flex items-center space-x-2">
            <slot name="filters"></slot>
          </div>
          
          <!-- Active filters indicator -->
          <div v-if="isFiltered" class="flex items-center space-x-2">
            <Badge 
              variant="secondary"
              :class="cn(
                'h-6 px-2 text-xs font-medium transition-all duration-300',
                'bg-primary/10 text-primary border-primary/20 hover:bg-primary/20'
              )"
            >
              <Filter class="mr-1 h-3 w-3" />
              {{ filterCount }}개 필터 활성
            </Badge>
            
            <Button
              variant="ghost"
              size="sm"
              :class="cn(
                'h-6 px-2 text-xs transition-all duration-200',
                'hover:bg-destructive/10 hover:text-destructive hover:scale-105'
              )"
              @click="resetFilters"
            >
              <X class="mr-1 h-3 w-3" />
              초기화
            </Button>
          </div>
        </div>
        
        <!-- Action buttons -->
        <div class="flex items-center space-x-2">
          <slot name="actions"></slot>
          
          <!-- Column visibility with magic effect -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button 
                variant="outline" 
                size="sm" 
                :class="cn(
                  'ml-auto h-8 group relative overflow-hidden',
                  'hover:border-primary/50 transition-all duration-300'
                )"
              >
                <!-- Magic hover effect -->
                <div class="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                <div class="relative flex items-center">
                  <Settings 
                    :class="cn(
                      'mr-2 h-4 w-4 transition-all duration-300',
                      'group-hover:text-primary group-hover:rotate-90'
                    )" 
                  />
                  컬럼
                  <ChevronDown 
                    :class="cn(
                      'ml-2 h-4 w-4 transition-all duration-300',
                      'group-hover:rotate-180'
                    )" 
                  />
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent 
              align="end" 
              class="w-[200px] border-2 shadow-2xl"
            >
              <div class="p-2">
                <p class="text-xs font-medium text-muted-foreground mb-2">컬럼 표시 설정</p>
                <div class="space-y-1">
                  <DropdownMenuCheckboxItem
                    v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
                    :key="column.id"
                    :class="cn(
                      'capitalize transition-all duration-200',
                      'hover:bg-primary/5 hover:text-primary'
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
      
      <!-- Custom toolbar content via default slot -->
      <slot></slot>
    </div>
  </div>
</template>