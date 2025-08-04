<script setup lang="ts">
import type { ColumnDef, VisibilityState } from '@tanstack/vue-table';
import { FlexRender, getCoreRowModel, useVueTable } from '@tanstack/vue-table';
import { ref, computed } from 'vue';
import { cn } from '@/shared/utils/utils'
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableHead,
  TableHeader,
  TableRow,
} from '@/core/components/ui/table';

interface DataTableModernProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  loading?: boolean;
  emptyMessage?: string;
  emptyDescription?: string;
  columnVisibility?: VisibilityState;
  onColumnVisibilityChange?: (visibility: VisibilityState) => void;
  tableInstance?: any;
}

const props = defineProps<DataTableModernProps<any, any>>();

const emit = defineEmits<{
  (e: 'update:columnVisibility', value: VisibilityState): void;
  (e: 'rowClick', row: any): void;
}>();

const columnVisibility = ref<VisibilityState>(props.columnVisibility || {});

// Use provided table instance or create a new one
const table =
  props.tableInstance ||
  useVueTable({
    get data() {
      return props.data;
    },
    get columns() {
      return props.columns;
    },
    getCoreRowModel: getCoreRowModel(),
    onColumnVisibilityChange: (updaterOrValue) => {
      if (typeof updaterOrValue === 'function') {
        columnVisibility.value = updaterOrValue(columnVisibility.value);
      } else {
        columnVisibility.value = updaterOrValue;
      }
      emit('update:columnVisibility', columnVisibility.value);
      if (props.onColumnVisibilityChange) {
        props.onColumnVisibilityChange(columnVisibility.value);
      }
    },
    state: {
      get columnVisibility() {
        return columnVisibility.value;
      },
    },
  });

// Expose the table instance to the parent component
defineExpose({ table });

// 디버깅: 컬럼 ID 확인
if (props.columns.length > 0) {
  console.log('Column definitions:', props.columns.map((col, index) => ({
    index,
    id: col.id,
    accessorKey: (col as any).accessorKey,
    actualId: col.id || (col as any).accessorKey,
    header: typeof col.header === 'string' ? col.header : 'function'
  })))
  
  // Table instance가 있을 때 헤더 그룹도 확인
  if (props.tableInstance) {
    console.log('Header groups:', props.tableInstance.getHeaderGroups().map(group => 
      group.headers.map((header: any, index: number) => ({
        index,
        id: header.id,
        columnId: header.column.id,
        isPlaceholder: header.isPlaceholder
      }))
    ))
  }
}

// Loading skeleton rows - 현재 페이지 크기에 맞춰서 생성
const skeletonRows = computed(() => {
  // tableInstance가 있으면 현재 페이지 크기를 사용, 없으면 기본값 10
  const pageSize = props.tableInstance?.getState().pagination?.pageSize || 10
  return Array.from({ length: pageSize }, (_, i) => i)
})
</script>

<template>
  <div class="relative overflow-hidden">
    <!-- Modern container with subtle border and backdrop -->    
    <div 
      :class="cn(
        'relative bg-card/30 backdrop-blur-sm overflow-hidden',
        'shadow-lg shadow-black/5',
        'rounded-xl border border-border/40 sm:rounded-xl sm:border-border/40',
        'sm:shadow-lg sm:shadow-black/5',
        loading && 'animate-pulse'
      )"
    >
      <!-- Subtle gradient overlay -->
      <div class="absolute inset-0 bg-gradient-to-br from-background/80 via-background/60 to-background/80 pointer-events-none" />
      
      <Table class="relative w-full table-fixed">
        <colgroup>
          <col 
            v-for="(column, index) in table.getAllColumns()" 
            :key="column.id"
            :data-col-index="index"
            :data-col-id="column.id"
            :class="cn(
              column.id === 'select' && 'w-12',
              column.id === 'name' && 'w-48',
              column.id === 'teamName' && 'w-32',
              column.id === 'rank' && 'w-24',
              column.id === 'joinDate' && 'w-32',
              column.id === 'status' && 'w-24'
            )"
          />
        </colgroup>
        <TableHeader>
          <TableRow 
            v-for="headerGroup in table.getHeaderGroups()" 
            :key="headerGroup.id"
            :class="cn(
              'border-b border-border/30 bg-muted/20',
              'hover:bg-muted/30 transition-all duration-200'
            )"
          >
            <TableHead 
              v-for="(header, headerIndex) in headerGroup.headers" 
              :key="header.id"
              :data-column-id="header.column.id"
              :data-header-index="headerIndex"
              :class="cn(
                'relative group font-semibold text-foreground/80 px-4 py-4 text-left transition-all duration-200',
                'hover:text-foreground hover:bg-muted/10'
              )"
            >
              <!-- Modern underline effect -->
              <div class="absolute bottom-0 left-4 right-4 h-px bg-gradient-to-r from-transparent via-primary/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              
              <FlexRender
                v-if="!header.isPlaceholder"
                :render="header.column.columnDef.header"
                :props="header.getContext()"
              />
            </TableHead>
          </TableRow>
        </TableHeader>
        
        <TableBody>
          <!-- Loading skeleton with modern shimmer -->
          <template v-if="loading">
            <TableRow 
              v-for="index in skeletonRows" 
              :key="`skeleton-${index}`"
              class="hover:bg-muted/20 transition-colors duration-200"
            >
              <TableCell 
                v-for="column in table.getAllColumns()" 
                :key="`skeleton-cell-${index}-${column.id || 'unknown'}`"
                :class="cn(
                  'px-4 py-4'
                )"
              >
                <div 
                  :class="cn(
                    'h-4 rounded-md bg-gradient-to-r from-muted via-muted/60 to-muted',
                    'animate-pulse'
                  )"
                  :style="{
                    width: Math.random() * 60 + 40 + '%',
                    animationDelay: `${Math.random() * 0.5}s`
                  }"
                />
              </TableCell>
            </TableRow>
          </template>
          
          <!-- Data rows with modern styling -->
          <template v-else-if="table.getRowModel().rows?.length">
            <template v-for="(row, index) in table.getRowModel().rows" :key="row.id">
              <TableRow
                :data-state="row.getIsSelected() && 'selected'"
                :class="cn(
                  'cursor-pointer group relative transition-all duration-200',
                  'hover:bg-gradient-to-r hover:from-muted/20 hover:via-muted/10 hover:to-transparent',
                  'hover:shadow-sm border-b border-border/20',
                  row.getIsSelected() && 'bg-primary/5 border-primary/20 shadow-sm'
                )"
                :style="{ 
                  animationDelay: `${index * 0.03}s`,
                  opacity: loading ? 0.7 : 1
                }"
                @click="$emit('rowClick', row.original)"
              >
                <!-- Modern selection indicator -->
                <div 
                  :class="cn(
                    'absolute left-0 top-0 bottom-0 w-1 transition-all duration-200',
                    row.getIsSelected() 
                      ? 'bg-primary shadow-lg shadow-primary/50' 
                      : 'bg-transparent group-hover:bg-primary/30'
                  )" 
                />
                
                <TableCell 
                  v-for="(cell, cellIndex) in row.getVisibleCells()" 
                  :key="cell.id"
                  :data-column-id="cell.column.id"
                  :data-cell-index="cellIndex"
                  :class="cn(
                    'px-4 py-4 transition-all duration-200 text-sm text-foreground/90'
                  )"
                >
                  <FlexRender 
                    :render="cell.column.columnDef.cell" 
                    :props="cell.getContext()" 
                  />
                </TableCell>
              </TableRow>
              
              <!-- Expanded row with modern styling -->
              <TableRow v-if="row.getIsExpanded()">
                <TableCell 
                  :colspan="row.getAllCells().length"
                  :class="cn(
                    'bg-gradient-to-r from-muted/10 via-muted/5 to-transparent',
                    'border-l-2 border-primary/20'
                  )"
                >
                  <div class="p-6 rounded-lg bg-card/50 backdrop-blur-sm border border-border/20">
                    <slot name="expanded-row" :row="row">
                      <pre class="text-xs text-muted-foreground font-mono">{{ JSON.stringify(row.original, null, 2) }}</pre>
                    </slot>
                  </div>
                </TableCell>
              </TableRow>
            </template>
          </template>
          
          <!-- Modern empty state -->
          <template v-else>
            <TableEmpty :colspan="table.getAllColumns().length">
              <div class="flex flex-col items-center py-16 space-y-6">
                <!-- Modern empty icon -->
                <div class="relative">
                  <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-muted/40 via-muted/20 to-transparent flex items-center justify-center">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-muted via-muted/60 to-muted/40" />
                  </div>
                  <div class="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-background border-2 border-border/20" />
                </div>
                
                <div class="text-center space-y-2 max-w-md">
                  <h3 class="text-lg font-semibold text-foreground/80">
                    {{ emptyMessage || '데이터가 없습니다' }}
                  </h3>
                  <p v-if="emptyDescription" class="text-sm text-muted-foreground leading-relaxed">
                    {{ emptyDescription }}
                  </p>
                </div>
              </div>
            </TableEmpty>
          </template>
        </TableBody>
      </Table>
    </div>
  </div>
</template>