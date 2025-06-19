<script setup lang="ts">
import type { ColumnDef, Table as TableType, VisibilityState } from '@tanstack/vue-table'
import { FlexRender, getCoreRowModel, useVueTable } from '@tanstack/vue-table'
import { computed, ref, toRef, watch } from 'vue'
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableHead,
  TableHeader,
  TableRow,
} from '@/core/components/ui/table'

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  loading?: boolean
  emptyMessage?: string
  emptyDescription?: string
  columnVisibility?: VisibilityState
  onColumnVisibilityChange?: (visibility: VisibilityState) => void
}

const props = defineProps<DataTableProps<any, any>>()

const emit = defineEmits<{
  (e: 'update:columnVisibility', value: VisibilityState): void
}>()

const columnVisibility = ref<VisibilityState>(props.columnVisibility || {})

// Create a table instance
const table = useVueTable({
  get data() { return props.data },
  get columns() { return props.columns },
  getCoreRowModel: getCoreRowModel(),
  onColumnVisibilityChange: (updaterOrValue) => {
    if (typeof updaterOrValue === 'function') {
      columnVisibility.value = updaterOrValue(columnVisibility.value)
    } else {
      columnVisibility.value = updaterOrValue
    }
    emit('update:columnVisibility', columnVisibility.value)
    if (props.onColumnVisibilityChange) {
      props.onColumnVisibilityChange(columnVisibility.value)
    }
  },
  state: {
    get columnVisibility() { return columnVisibility.value }
  },
})

// Expose the table instance to the parent component
defineExpose({ table })
</script>

<template>
  <div class="rounded-md border overflow-auto">
    <div v-if="loading" class="flex justify-center items-center p-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
    <Table v-else>
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
            <TableRow :data-state="row.getIsSelected() && 'selected'">
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