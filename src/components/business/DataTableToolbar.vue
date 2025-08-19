<template>
  <div class="space-y-3">
    <!-- 첫 번째 줄: 필터들 (데스크톱은 항상 표시, 모바일은 토글) -->
    <div 
      v-if="$slots.filters"
      :class="[
        'flex items-center space-x-2 flex-wrap gap-y-2',
        'md:flex',
        showFilters ? 'flex' : 'hidden'
      ]"
    >
      <slot name="filters" />
      
      <!-- Clear filters button (mobile) -->
      <Button
        v-if="isFiltered"
        variant="ghost"
        size="sm"
        class="h-8 px-2 md:hidden"
        @click="resetFilters"
      >
        <X class="mr-2 h-4 w-4" />
        초기화
      </Button>
    </div>
    
    <!-- 두 번째 줄: 검색 + 필터 토글 + 액션들 -->
    <div class="flex items-center justify-between gap-3">
      <div class="flex flex-1 items-center space-x-2 min-w-0">
        <!-- Global search -->
        <Input
          :placeholder="searchPlaceholder"
          :model-value="table.getColumn(searchColumnId)?.getFilterValue() as string ?? ''"
          @update:model-value="table.getColumn(searchColumnId)?.setFilterValue($event)"
          class="h-8 w-[120px] sm:w-[180px] lg:w-[250px]"
        />
        
        <!-- Filter toggle button (mobile) -->
        <Button
          variant="outline"
          size="sm"
          class="h-8 md:hidden"
          @click="showFilters = !showFilters"
        >
          <Filter class="h-4 w-4" />
          <span v-if="hasActiveFilters" class="ml-1 text-xs bg-primary text-primary-foreground rounded-full px-1">
            {{ activeFilterCount }}
          </span>
        </Button>
        
        <!-- Clear filters button (desktop) -->
        <Button
          v-if="isFiltered"
          variant="ghost"
          size="sm"
          class="h-8 px-2 hidden md:flex"
          @click="resetFilters"
        >
          <X class="mr-2 h-4 w-4" />
          <span class="hidden lg:inline">필터 초기화</span>
          <span class="lg:hidden">초기화</span>
        </Button>
      </div>
      
      <div class="flex items-center space-x-2 shrink-0">
        <!-- Selected rows info -->
        <div 
          v-if="showSelectedInfo && selectedRowCount > 0"
          class="flex items-center space-x-2 text-sm text-muted-foreground"
        >
          <span class="hidden sm:inline">{{ selectedRowCount }}개 선택됨</span>
          <span class="sm:hidden">{{ selectedRowCount }}개</span>
          <Button
            variant="ghost"
            size="sm"
            class="h-8 px-2"
            @click="table.toggleAllPageRowsSelected(false)"
          >
            <span class="hidden sm:inline">선택 해제</span>
            <span class="sm:hidden">해제</span>
          </Button>
        </div>
        
        <!-- Additional actions slot -->
        <slot name="actions" />
        
        <!-- Column visibility -->
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="outline" size="sm" class="h-8">
              <Settings class="h-4 w-4" />
              <span class="hidden sm:inline ml-2">컬럼</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" class="w-[200px]">
            <DropdownMenuLabel>컬럼 표시/숨기기</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <div 
              v-for="column in hideableColumns"
              :key="`${column.id}-${forceUpdate}`"
              class="flex items-center space-x-2 p-2 cursor-pointer hover:bg-muted rounded-sm"
              @click="() => {
                column.toggleVisibility();
                forceUpdate.value++;
              }"
            >
              <Checkbox 
                :modelValue="column.getIsVisible()" 
                @click.stop
                @update:modelValue="(value) => {
                  column.toggleVisibility(!!value);
                  forceUpdate.value++;
                }"
              />
              <span class="text-sm">
                {{ getColumnLabel(column.id) }}
              </span>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Table } from '@tanstack/vue-table';
import { computed, ref } from 'vue';
import { 
  Settings, 
  X,
  Filter
} from 'lucide-vue-next';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';

interface DataTableToolbarProps {
  table: Table<any>;
  searchPlaceholder?: string;
  searchColumnId?: string;
  getColumnLabel: (columnId: string) => string;
  showSelectedInfo?: boolean;
}

const props = withDefaults(defineProps<DataTableToolbarProps>(), {
  showSelectedInfo: true,
});

// Force reactivity for column visibility
const forceUpdate = ref(0);

// Mobile filter visibility
const showFilters = ref(false);

// Get hideable columns with reactivity
const hideableColumns = computed(() => {
  // This will trigger when forceUpdate changes
  forceUpdate.value; 
  return props.table.getAllColumns().filter((column) => column.getCanHide());
});

const isFiltered = computed(() => {
  return props.table.getState().columnFilters.length > 0;
});

const selectedRowCount = computed(() => {
  return Object.keys(props.table.getState().rowSelection).length;
});

// Check if there are active filters
const hasActiveFilters = computed(() => {
  return props.table.getState().columnFilters.length > 0;
});

// Count active filters
const activeFilterCount = computed(() => {
  return props.table.getState().columnFilters.length;
});

function resetFilters() {
  props.table.resetColumnFilters();
  showFilters.value = false; // Close mobile filter panel after reset
}
</script>