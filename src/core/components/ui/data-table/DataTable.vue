<script setup lang="ts">
import type { ColumnDef, VisibilityState } from '@tanstack/vue-table';
import { FlexRender, getCoreRowModel, useVueTable } from '@tanstack/vue-table';
import { ref } from 'vue';
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableHead,
  TableHeader,
  TableRow,
} from '@/core/components/ui/table';

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  emptyMessage?: string;
  emptyDescription?: string;
  columnVisibility?: VisibilityState;
  onColumnVisibilityChange?: (visibility: VisibilityState) => void;
  tableInstance?: any; // Allow passing a table instance
}

const props = defineProps<DataTableProps<any, any>>();

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

// Log the table instance for debugging
console.log('DataTable - table instance:', {
  isProvidedInstance: !!props.tableInstance,
  tableInstance: table,
});

// Expose the table instance to the parent component
defineExpose({ table });
</script>

<template>
  <div class="rounded-md border overflow-auto">
    <Table>
      <TableHeader>
        <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
          <TableHead v-for="header in headerGroup.headers" :key="header.id">
            <FlexRender
              v-if="!header.isPlaceholder"
              :render="header.column.columnDef.header"
              :props="header.getContext()"
            />
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <template v-if="table.getRowModel().rows?.length">
          <template v-for="row in table.getRowModel().rows" :key="row.id">
            <TableRow
              :data-state="row.getIsSelected() && 'selected'"
              class="cursor-pointer"
              @click="$emit('rowClick', row.original)"
            >
              <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
              </TableCell>
            </TableRow>
            <TableRow v-if="row.getIsExpanded()">
              <TableCell :colspan="row.getAllCells().length">
                <slot name="expanded-row" :row="row">
                  <pre>{{ JSON.stringify(row.original, null, 2) }}</pre>
                </slot>
              </TableCell>
            </TableRow>
          </template>
        </template>
        <template v-else>
          <TableEmpty :colspan="columns.length">
            <div class="flex flex-col items-center">
              <p class="text-lg font-medium">{{ emptyMessage || '데이터가 없습니다' }}</p>
              <p v-if="emptyDescription" class="text-sm text-muted-foreground">
                {{ emptyDescription }}
              </p>
            </div>
          </TableEmpty>
        </template>
      </TableBody>
    </Table>
  </div>
</template>
