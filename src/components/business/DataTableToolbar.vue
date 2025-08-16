<template>
  <div class="flex items-center justify-between">
    <div class="flex flex-1 items-center space-x-2">
      <!-- Global search -->
      <Input
        :placeholder="searchPlaceholder"
        :model-value="table.getColumn(searchColumnId)?.getFilterValue() as string ?? ''"
        @update:model-value="table.getColumn(searchColumnId)?.setFilterValue($event)"
        class="h-8 w-[150px] lg:w-[250px]"
      />
      
      <!-- Additional filters slot -->
      <slot name="filters" />
      
      <!-- Clear filters button -->
      <Button
        v-if="isFiltered"
        variant="ghost"
        size="sm"
        class="h-8 px-2 lg:px-3"
        @click="resetFilters"
      >
        <X class="mr-2 h-4 w-4" />
        필터 초기화
      </Button>
    </div>
    
    <div class="flex items-center space-x-2">
      <!-- Selected rows info -->
      <div 
        v-if="showSelectedInfo && selectedRowCount > 0"
        class="flex items-center space-x-2 text-sm text-muted-foreground"
      >
        <span>{{ selectedRowCount }}개 선택됨</span>
        <Button
          variant="ghost"
          size="sm"
          class="h-8 px-2"
          @click="table.toggleAllPageRowsSelected(false)"
        >
          선택 해제
        </Button>
      </div>
      
      <!-- Additional actions slot -->
      <slot name="actions" />
      
      <!-- Column visibility -->
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="outline" size="sm" class="ml-auto h-8">
            <Settings class="mr-2 h-4 w-4" />
            컬럼
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
      
      <!-- Export menu -->
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="outline" size="sm" class="h-8">
            <Download class="mr-2 h-4 w-4" />
            내보내기
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="w-[150px]">
          <DropdownMenuItem @click="$emit('export', 'csv')">
            <FileText class="mr-2 h-4 w-4" />
            CSV
          </DropdownMenuItem>
          <DropdownMenuItem @click="$emit('export', 'excel')">
            <FileSpreadsheet class="mr-2 h-4 w-4" />
            Excel
          </DropdownMenuItem>
          <DropdownMenuItem @click="$emit('export', 'pdf')">
            <FileDown class="mr-2 h-4 w-4" />
            PDF
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Table } from '@tanstack/vue-table';
import { computed, ref } from 'vue';
import { 
  Settings, 
  X, 
  Download, 
  FileText, 
  FileSpreadsheet, 
  FileDown 
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

const emit = defineEmits<{
  export: [format: 'csv' | 'excel' | 'pdf'];
}>();

// Force reactivity for column visibility
const forceUpdate = ref(0);

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

function resetFilters() {
  props.table.resetColumnFilters();
}
</script>