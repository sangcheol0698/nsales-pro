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

interface DataTableMagicProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  loading?: boolean;
  emptyMessage?: string;
  emptyDescription?: string;
  columnVisibility?: VisibilityState;
  onColumnVisibilityChange?: (visibility: VisibilityState) => void;
  tableInstance?: any;
}

const props = defineProps<DataTableMagicProps<any, any>>();

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

// Loading skeleton rows
const skeletonRows = computed(() => Array.from({ length: 5 }, (_, i) => i))
</script>

<template>
  <div class="relative">
    <!-- Magic container with gradient border -->
    <div 
      :class="cn(
        'relative rounded-lg border-2 overflow-hidden transition-all duration-300',
        loading 
          ? 'border-primary/20 shadow-lg' 
          : 'border-border hover:border-primary/30'
      )"
    >
      <!-- Magic glow effect -->
      <div 
        :class="cn(
          'absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-pink-500/5',
          'opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none'
        )" 
      />
      
      <Table class="relative">
        <TableHeader>
          <TableRow 
            v-for="headerGroup in table.getHeaderGroups()" 
            :key="headerGroup.id"
            :class="cn(
              'border-b border-border/50 hover:bg-muted/30 transition-colors duration-200'
            )"
          >
            <TableHead 
              v-for="header in headerGroup.headers" 
              :key="header.id"
              :class="cn(
                'relative group transition-all duration-200',
                'hover:bg-primary/5'
              )"
            >
              <!-- Header magic underline -->
              <div class="absolute bottom-0 left-0 h-0.5 w-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-300 group-hover:w-full" />
              
              <FlexRender
                v-if="!header.isPlaceholder"
                :render="header.column.columnDef.header"
                :props="header.getContext()"
              />
            </TableHead>
          </TableRow>
        </TableHeader>
        
        <TableBody>
          <!-- Loading skeleton -->
          <template v-if="loading">
            <TableRow 
              v-for="index in skeletonRows" 
              :key="`skeleton-${index}`"
              class="hover:bg-muted/50 transition-colors duration-200"
            >
              <TableCell 
                v-for="column in columns" 
                :key="`skeleton-cell-${index}-${column.id || 'unknown'}`"
                class="py-4"
              >
                <div 
                  :class="cn(
                    'h-4 bg-gradient-to-r from-muted via-muted/50 to-muted rounded',
                    'animate-pulse bg-[length:200%_100%]'
                  )"
                  :style="{
                    width: Math.random() * 60 + 40 + '%',
                    animationDelay: `${Math.random() * 0.5}s`
                  }"
                />
              </TableCell>
            </TableRow>
          </template>
          
          <!-- Data rows with magic effects -->
          <template v-else-if="table.getRowModel().rows?.length">
            <template v-for="(row, index) in table.getRowModel().rows" :key="row.id">
              <TableRow
                :data-state="row.getIsSelected() && 'selected'"
                :class="cn(
                  'cursor-pointer group relative transition-all duration-300',
                  'hover:bg-gradient-to-r hover:from-primary/5 hover:via-primary/3 hover:to-transparent',
                  'hover:shadow-md hover:shadow-primary/10',
                  row.getIsSelected() && 'bg-primary/10 border-primary/20'
                )"
                :style="{ animationDelay: `${index * 0.05}s` }"
                @click="$emit('rowClick', row.original)"
              >
                <!-- Row magic border effect -->
                <div class="absolute inset-0 border-l-2 border-transparent group-hover:border-primary transition-colors duration-300" />
                
                <TableCell 
                  v-for="cell in row.getVisibleCells()" 
                  :key="cell.id"
                  :class="cn(
                    'relative transition-all duration-200',
                    'group-hover:transform group-hover:scale-[1.02]'
                  )"
                >
                  <FlexRender 
                    :render="cell.column.columnDef.cell" 
                    :props="cell.getContext()" 
                  />
                </TableCell>
              </TableRow>
              
              <!-- Expanded row with magic effect -->
              <TableRow v-if="row.getIsExpanded()">
                <TableCell 
                  :colspan="row.getAllCells().length"
                  :class="cn(
                    'bg-gradient-to-r from-primary/5 via-primary/3 to-transparent',
                    'border-l-2 border-primary/30'
                  )"
                >
                  <div class="p-4 rounded-md bg-background/80 backdrop-blur-sm">
                    <slot name="expanded-row" :row="row">
                      <pre class="text-xs text-muted-foreground">{{ JSON.stringify(row.original, null, 2) }}</pre>
                    </slot>
                  </div>
                </TableCell>
              </TableRow>
            </template>
          </template>
          
          <!-- Empty state with magic -->
          <template v-else>
            <TableEmpty :colspan="columns.length">
              <div class="flex flex-col items-center py-12 space-y-4">
                <!-- Magic empty state animation -->
                <div class="relative">
                  <div class="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20 flex items-center justify-center">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 opacity-30 animate-pulse" />
                  </div>
                  <div class="absolute inset-0 w-16 h-16 rounded-full bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 animate-ping" />
                </div>
                
                <div class="text-center space-y-2">
                  <p class="text-lg font-medium text-muted-foreground">
                    {{ emptyMessage || '데이터가 없습니다' }}
                  </p>
                  <p v-if="emptyDescription" class="text-sm text-muted-foreground/70">
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