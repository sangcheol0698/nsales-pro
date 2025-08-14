<template>
  <div class="rounded-md border">
    <Table>
      <TableHeader>
        <TableRow v-for="headerGroup in tableInstance.getHeaderGroups()" :key="headerGroup.id">
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
        <template v-if="tableInstance.getRowModel().rows?.length">
          <template v-for="row in tableInstance.getRowModel().rows" :key="row.id">
            <TableRow
              :data-state="row.getIsSelected() && 'selected'"
              class="cursor-pointer hover:bg-muted/50"
              @click="onRowClick(row.original)"
            >
              <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                <FlexRender
                  :render="cell.column.columnDef.cell"
                  :props="cell.getContext()"
                />
              </TableCell>
            </TableRow>
            
            <!-- Expanded content -->
            <TableRow v-if="row.getIsExpanded() && $slots['expanded-row']" :key="`${row.id}-expanded`">
              <TableCell :colspan="row.getVisibleCells().length">
                <slot name="expanded-row" :row="row" />
              </TableCell>
            </TableRow>
          </template>
        </template>
        
        <TableRow v-else>
          <TableCell :colspan="columns.length" class="h-24 text-center">
            <div v-if="loading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              <span class="ml-2 text-muted-foreground">로딩 중...</span>
            </div>
            <div v-else class="flex flex-col items-center justify-center space-y-2">
              <p class="text-muted-foreground">{{ emptyMessage }}</p>
              <p class="text-sm text-muted-foreground">{{ emptyDescription }}</p>
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>

<script setup lang="ts">
import type { ColumnDef, Table as TanstackTable } from '@tanstack/vue-table';
import { FlexRender } from '@tanstack/vue-table';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface DataTableProps {
  columns: ColumnDef<any>[];
  data: any[];
  loading?: boolean;
  emptyMessage?: string;
  emptyDescription?: string;
  tableInstance: TanstackTable<any>;
}

defineProps<DataTableProps>();

const emit = defineEmits<{
  rowClick: [row: any];
}>();

function onRowClick(row: any) {
  emit('rowClick', row);
}
</script>