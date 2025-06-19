# Data Table

A powerful data table component built on top of [@tanstack/vue-table](https://tanstack.com/table/v8/docs/adapters/vue-table) and shadcn-vue UI components.

## Features

- Sortable columns
- Filtering and search
- Pagination
- Column visibility toggle
- Row selection
- Row expansion
- Loading states
- Empty states

## Components

The data table is composed of several components:

- `DataTable`: The main table component
- `DataTableColumnHeader`: A component for sortable column headers
- `DataTablePagination`: A component for pagination controls
- `DataTableToolbar`: A component for the table toolbar (search, column visibility)

## Usage

### Basic Example

```vue
<template>
  <div>
    <DataTableToolbar 
      :table="table" 
      searchPlaceholder="검색..." 
      searchColumnId="name"
      :getColumnLabel="getColumnLabel"
    />
    <DataTable 
      :columns="columns" 
      :data="data" 
      :loading="loading"
      emptyMessage="데이터가 없습니다"
      emptyDescription="데이터가 생성되면 여기에 표시됩니다"
    />
    <DataTablePagination
      :page="page"
      :pageSize="pageSize"
      :totalPages="totalPages"
      :totalElements="totalElements"
      :loading="loading"
      :selectedRowCount="table.getFilteredSelectedRowModel().rows.length"
      @pageChange="onPageChange"
      @pageSizeChange="onPageSizeChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { h } from 'vue';
import type { ColumnDef, ColumnFiltersState, SortingState, VisibilityState } from '@tanstack/vue-table';
import { getCoreRowModel, getFilteredRowModel, getSortedRowModel, useVueTable } from '@tanstack/vue-table';
import { valueUpdater } from '@/core/components/ui/table/utils';
import { 
  DataTable, 
  DataTableColumnHeader, 
  DataTablePagination, 
  DataTableToolbar 
} from '@/core/components/ui/data-table';

// Define your data interface
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

// Define your columns
const columns: ColumnDef<User>[] = [
  {
    accessorKey: 'name',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '이름' }),
    cell: ({ row }) => h('div', {}, row.getValue('name')),
  },
  {
    accessorKey: 'email',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '이메일' }),
    cell: ({ row }) => h('div', {}, row.getValue('email')),
  },
  {
    accessorKey: 'role',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '역할' }),
    cell: ({ row }) => h('div', {}, row.getValue('role')),
  }
];

// State management
const data = ref<User[]>([]);
const loading = ref(true);
const sorting = ref<SortingState>([]);
const columnFilters = ref<ColumnFiltersState>([]);
const columnVisibility = ref<VisibilityState>({});
const rowSelection = ref({});

// Pagination state
const page = ref(1);
const pageSize = ref(10);
const totalPages = ref(1);
const totalElements = ref(0);

// Create table instance
const table = useVueTable({
  get data() { return data.value },
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  onSortingChange: updaterOrValue => valueUpdater(updaterOrValue, sorting),
  onColumnFiltersChange: updaterOrValue => valueUpdater(updaterOrValue, columnFilters),
  onColumnVisibilityChange: updaterOrValue => valueUpdater(updaterOrValue, columnVisibility),
  onRowSelectionChange: updaterOrValue => valueUpdater(updaterOrValue, rowSelection),
  state: {
    get sorting() { return sorting.value },
    get columnFilters() { return columnFilters.value },
    get columnVisibility() { return columnVisibility.value },
    get rowSelection() { return rowSelection.value },
  },
});

// Column label helper
function getColumnLabel(columnId: string): string {
  switch (columnId) {
    case 'name': return '이름';
    case 'email': return '이메일';
    case 'role': return '역할';
    default: return columnId;
  }
}

// Page change handler
function onPageChange(newPage: number) {
  page.value = newPage;
  fetchData();
}

// Page size change handler
function onPageSizeChange(newPageSize: number) {
  pageSize.value = newPageSize;
  page.value = 1; // Reset to first page when changing page size
  fetchData();
}

// Fetch data from API
function fetchData() {
  loading.value = true;
  
  // Replace with your API call
  yourApiService.getUsers({
    page: page.value,
    pageSize: pageSize.value,
    // Add other params as needed (sorting, filtering)
  }).then(response => {
    data.value = response.content;
    totalElements.value = response.totalElements;
    totalPages.value = response.totalPages;
  }).finally(() => {
    loading.value = false;
  });
}

// Load data on mount
onMounted(() => {
  fetchData();
});
</script>
```

## Component Props

### DataTable

| Prop | Type | Description |
|------|------|-------------|
| columns | `ColumnDef<TData, TValue>[]` | Table column definitions |
| data | `TData[]` | Table data |
| loading | `boolean` | Loading state |
| emptyMessage | `string` | Message to display when table is empty |
| emptyDescription | `string` | Description to display when table is empty |
| columnVisibility | `VisibilityState` | Column visibility state |
| onColumnVisibilityChange | `(visibility: VisibilityState) => void` | Column visibility change handler |

### DataTableColumnHeader

| Prop | Type | Description |
|------|------|-------------|
| column | `Column<TData, TValue>` | Column instance |
| title | `string` | Column title |
| class | `string` | Additional CSS classes |

### DataTablePagination

| Prop | Type | Description |
|------|------|-------------|
| page | `number` | Current page |
| pageSize | `number` | Page size |
| totalPages | `number` | Total number of pages |
| totalElements | `number` | Total number of elements |
| loading | `boolean` | Loading state |
| pageSizeOptions | `number[]` | Available page size options |
| selectedRowCount | `number` | Number of selected rows |

### DataTableToolbar

| Prop | Type | Description |
|------|------|-------------|
| table | `Table<TData>` | Table instance |
| searchPlaceholder | `string` | Placeholder for search input |
| searchColumnId | `string` | Column ID to search in |
| getColumnLabel | `(columnId: string) => string` | Function to get column label |