# DataTableWithUrl Component

A reusable data table component that synchronizes its state with URL parameters, built on top of shadcn's data-table components.

## Features

- Sortable columns
- Filtering and search
- Pagination
- Column visibility toggle
- Row selection
- Row expansion
- Loading states
- Empty states
- URL synchronization for:
  - Search/filter conditions
  - Pagination information
  - Sorting information
- Debounced URL updates for search input

## Usage

```vue
<template>
  <DataTableWithUrl
    :columns="columns"
    :fetchData="fetchData"
    searchPlaceholder="검색..."
    searchColumnId="name"
    :getColumnLabel="getColumnLabel"
    emptyMessage="데이터가 없습니다"
    emptyDescription="데이터가 생성되면 여기에 표시됩니다"
  />
</template>

<script setup lang="ts">
import { DataTableWithUrl } from '@/shared/components/table';
import { DataTableColumnHeader } from '@/core/components/ui/data-table';
import { h } from 'vue';
import type { ColumnDef } from '@tanstack/vue-table';
import PageResponse from '@/core/common/PageResponse';

// Define your data interface
interface User {
  id: string;
  name: string;
  email: string;
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
];

// Define your column label function
function getColumnLabel(columnId: string): string {
  switch (columnId) {
    case 'name': return '이름';
    case 'email': return '이메일';
    default: return columnId;
  }
}

// Define your data fetching function
async function fetchData(params: Record<string, any>): Promise<PageResponse<User>> {
  try {
    // Call your API with the params
    const response = await api.getUsers(params);
    return response;
  } catch (error) {
    console.error('Error loading data:', error);
    throw error;
  }
}
</script>
```

## Props

| Prop | Type | Description | Default |
|------|------|-------------|---------|
| columns | `ColumnDef<TData, any>[]` | Table column definitions | Required |
| fetchData | `(params: Record<string, any>) => Promise<PageResponse<TData>>` | Function to fetch data | Required |
| searchColumnId | `string` | Column ID to search in | `'name'` |
| searchPlaceholder | `string` | Placeholder for search input | `'검색...'` |
| emptyMessage | `string` | Message to display when table is empty | `'데이터가 없습니다'` |
| emptyDescription | `string` | Description to display when table is empty | `'데이터가 생성되면 여기에 표시됩니다'` |
| getColumnLabel | `(columnId: string) => string` | Function to get column label | `(columnId) => columnId` |
| initialParams | `Record<string, any>` | Initial parameters for data fetching | `{}` |
| debounceTime | `number` | Debounce time for search input in milliseconds | `300` |

## Slots

| Slot | Description |
|------|-------------|
| toolbar | Additional content for the toolbar |
| expanded-row | Content for expanded rows |

## Testing

When testing the DataTableWithUrl component, ensure the following functionality works correctly:

1. **Initial Load**:
   - Table loads data correctly on initial render
   - URL parameters are respected on initial load

2. **Sorting**:
   - Clicking a column header sorts the data
   - Sorting state is reflected in the URL
   - Navigating to a URL with sort parameters applies the correct sorting

3. **Filtering/Search**:
   - Entering text in the search input filters the data
   - Search state is reflected in the URL (after debounce)
   - Navigating to a URL with search parameters applies the correct filtering

4. **Pagination**:
   - Changing page loads the correct data
   - Changing page size loads the correct data
   - Pagination state is reflected in the URL
   - Navigating to a URL with pagination parameters shows the correct page

5. **Column Visibility**:
   - Toggling column visibility works correctly

6. **Browser Navigation**:
   - Using browser back/forward buttons maintains the correct table state
   - Refreshing the page maintains the correct table state

7. **Edge Cases**:
   - Empty data set displays the empty message
   - Error handling works correctly
   - Loading states are displayed appropriately