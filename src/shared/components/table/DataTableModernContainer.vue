<template>
  <div class="space-y-6">
    <DataTableModernToolbar
      :table="table" 
      :searchPlaceholder="searchPlaceholder"
      :searchColumnId="searchColumnId"
      :getColumnLabel="getColumnLabel"
      :title="title"
      :description="description"
    >
      <template #filters>
        <slot name="filters" :table="table"></slot>
      </template>
      
      <template #actions>
        <slot name="actions" :table="table"></slot>
      </template>
      
      <slot name="toolbar"></slot>
    </DataTableModernToolbar>

    <DataTableModern
      :columns="columns"
      :data="data"
      :loading="pagination.loading"
      :emptyMessage="emptyMessage"
      :emptyDescription="emptyDescription"
      :tableInstance="table"
      @rowClick="$emit('rowClick', $event)"
    >
      <template v-if="$slots['expanded-row']" #expanded-row="slotProps">
        <slot name="expanded-row" v-bind="slotProps"></slot>
      </template>
    </DataTableModern>

    <DataTablePagination
      :page="params.page"
      :pageSize="params.size"
      :totalPages="pagination.totalPages"
      :totalElements="pagination.totalElements"
      :loading="pagination.loading"
      :selectedRowCount="Object.keys(rowSelection).length"
      @pageChange="onPageChange"
      @pageSizeChange="onPageSizeChange"
    />
  </div>
</template>

<script setup lang="ts">
import type {
  ColumnDef,
  ColumnFiltersState,
  ExpandedState,
  SortingState,
  VisibilityState,
} from '@tanstack/vue-table';
import {
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getSortedRowModel,
  useVueTable,
} from '@tanstack/vue-table';
import { onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { valueUpdater } from '@/core/components/ui/table/utils';
import { debounce } from 'lodash-es';
import PageResponse from '@/core/common/PageResponse';
import { 
  DataTableModern, 
  DataTableModernToolbar, 
  DataTablePagination 
} from '@/core/components/ui/data-table';

interface DataTableModernContainerProps<TData> {
  columns: ColumnDef<TData, any>[];
  fetchData: (params: Record<string, any>) => Promise<PageResponse<TData>>;
  searchColumnId?: string;
  searchPlaceholder?: string;
  emptyMessage?: string;
  emptyDescription?: string;
  getColumnLabel?: (columnId: string) => string;
  initialParams?: Record<string, any>;
  debounceTime?: number;
  title?: string;
  description?: string;
}

const props = withDefaults(defineProps<DataTableModernContainerProps<any>>(), {
  searchColumnId: 'name',
  searchPlaceholder: '검색...',
  emptyMessage: '데이터가 없습니다',
  emptyDescription: '데이터가 생성되면 여기에 표시됩니다',
  debounceTime: 300,
});

const router = useRouter();
const route = useRoute();

const data = ref<any[]>([]);
const sorting = ref<SortingState>([]);
const columnFilters = ref<ColumnFiltersState>([]);
const columnVisibility = ref<VisibilityState>({});
const rowSelection = ref({});
const expanded = ref<ExpandedState>({});

interface PaginationState {
  totalPages: number;
  totalElements: number;
  loading: boolean;
}

const pagination = ref<PaginationState>({
  totalPages: 0,
  totalElements: 0,
  loading: false,
});

// Initialize params from URL or defaults
const params = ref<Record<string, any>>({
  page: 1,
  size: 10,
  ...props.initialParams,
});

// Create table instance
const table = useVueTable({
  get data() {
    return data.value;
  },
  columns: props.columns,
  manualPagination: true,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getFacetedRowModel: getFacetedRowModel(),
  getFacetedUniqueValues: getFacetedUniqueValues(),
  getExpandedRowModel: getExpandedRowModel(),
  getRowId: (row) => row.id?.toString() || '',
  onSortingChange: (updaterOrValue) => {
    valueUpdater(updaterOrValue, sorting);

    if (sorting.value.length > 0) {
      const sort = sorting.value[0];
      const sortParam = `${sort.id},${sort.desc ? 'desc' : 'asc'}`;

      params.value = {
        ...params.value,
        sort: sortParam,
      };

      params.value.direction = sort.desc ? 'desc' : 'asc';
    } else if (params.value.sort) {
      const { sort, direction, ...rest } = params.value;
      params.value = rest;
    }

    updateUrl();
    loadData();
  },
  onColumnFiltersChange: (updaterOrValue) => {
    valueUpdater(updaterOrValue, columnFilters);

    const newParams = { ...params.value };
    
    // Clear existing filter params (except page, size, sort)
    Object.keys(newParams).forEach(key => {
      if (!['page', 'size', 'sort', 'direction'].includes(key)) {
        delete newParams[key];
      }
    });

    // Add all active column filters to params
    columnFilters.value.forEach(filter => {
      if (filter.value !== undefined && filter.value !== null && filter.value !== '') {
        if (Array.isArray(filter.value) && filter.value.length > 0) {
          newParams[filter.id] = filter.value.join(',');
        }
        else if (typeof filter.value === 'object' && (filter.value as any).start) {
          newParams[`${filter.id}From`] = (filter.value as any).start.toISOString().split('T')[0];
          if ((filter.value as any).end) {
            newParams[`${filter.id}To`] = (filter.value as any).end.toISOString().split('T')[0]; 
          }
        }
        else {
          newParams[filter.id] = filter.value;
        }
      }
    });

    params.value = newParams;
    params.value.page = 1;

    const hasTextFilter = columnFilters.value.some(filter => 
      filter.id === props.searchColumnId && typeof filter.value === 'string'
    );
    
    if (hasTextFilter) {
      updateUrlDebounced();
    } else {
      updateUrl();
    }
    
    loadData();
  },
  onColumnVisibilityChange: (updaterOrValue) => valueUpdater(updaterOrValue, columnVisibility),
  onRowSelectionChange: (updaterOrValue) => valueUpdater(updaterOrValue, rowSelection),
  onExpandedChange: (updaterOrValue) => valueUpdater(updaterOrValue, expanded),
  state: {
    get sorting() {
      return sorting.value;
    },
    get columnFilters() {
      return columnFilters.value;
    },
    get columnVisibility() {
      return columnVisibility.value;
    },
    get rowSelection() {
      return rowSelection.value;
    },
    get expanded() {
      return expanded.value;
    },
  },
});

// Debounced URL update function
const updateUrlDebounced = debounce(updateUrl, props.debounceTime);

// Update URL with current params
function updateUrl() {
  router.replace({
    query: { ...params.value },
  });
}

// Load data from API
function loadData() {
  pagination.value.loading = true;

  if (params.value.sort && !params.value.sort.includes(',')) {
    params.value.sort = `${params.value.sort},asc`;
    params.value.direction = 'asc';
  }

  props
    .fetchData(params.value)
    .then((response: PageResponse<any>) => {
      data.value = response.content;
      pagination.value.totalPages = response.totalPages;
      pagination.value.totalElements = response.totalElements;
    })
    .catch((error) => {
      console.error('Error loading data:', error);
    })
    .finally(() => {
      pagination.value.loading = false;
    });
}

// Page change handler
function onPageChange(page: number) {
  params.value.page = page;
  updateUrl();
  loadData();
}

// Page size change handler
function onPageSizeChange(size: number) {
  rowSelection.value = {};
  params.value.size = size;
  params.value.page = 1;
  updateUrl();
  loadData();
}

// Function to get column label
function getColumnLabel(columnId: string): string {
  if (props.getColumnLabel) {
    return props.getColumnLabel(columnId);
  }
  return columnId;
}

// Load initial state from URL on mount
onMounted(() => {
  const query = route.query;

  if (query.page) params.value.page = Number(query.page);
  if (query.size) params.value.size = Number(query.size);
  else if (query.limit) params.value.size = Number(query.limit);

  if (query.sort) {
    const sortValue = query.sort as string;

    if (sortValue.includes(',')) {
      const [property, direction] = sortValue.split(',');

      params.value.sort = sortValue;
      params.value.direction = direction;

      sorting.value = [
        {
          id: property,
          desc: direction === 'desc',
        },
      ];
    }
    else if (query.direction) {
      const direction = query.direction as string;

      params.value.sort = `${sortValue},${direction}`;
      params.value.direction = direction;

      sorting.value = [
        {
          id: sortValue,
          desc: direction === 'desc',
        },
      ];
    } else {
      params.value.sort = `${sortValue},asc`;
      params.value.direction = 'asc';

      sorting.value = [
        {
          id: sortValue,
          desc: false,
        },
      ];
    }
  }

  // Handle all query parameters as potential column filters
  const newColumnFilters: any[] = [];
  
  Object.entries(query).forEach(([key, value]) => {
    if (!['page', 'size', 'sort', 'direction', 'limit'].includes(key) && value) {
      params.value[key] = value;
      
      if (key.endsWith('From') || key.endsWith('To')) {
        const baseKey = key.replace(/From$|To$/, '');
        const existingFilter = newColumnFilters.find(f => f.id === baseKey);
        
        if (existingFilter) {
          if (key.endsWith('From')) {
            existingFilter.value.start = new Date(value as string);
          } else {
            existingFilter.value.end = new Date(value as string);
          }
        } else {
          const dateRangeValue: any = {};
          if (key.endsWith('From')) {
            dateRangeValue.start = new Date(value as string);
          } else {
            dateRangeValue.end = new Date(value as string);
          }
          
          newColumnFilters.push({
            id: baseKey,
            value: dateRangeValue,
          });
        }
      }
      else if (typeof value === 'string' && value.includes(',')) {
        newColumnFilters.push({
          id: key,
          value: value.split(','),
        });
      }
      else {
        newColumnFilters.push({
          id: key,
          value: value,
        });
      }
    }
  });
  
  columnFilters.value = newColumnFilters;

  loadData();
});

// Watch for route changes to update state
watch(
  () => route.query,
  (newQuery) => {
    const sortChanged = String(newQuery.sort) !== String(params.value.sort);

    if (
      newQuery.page !== params.value.page.toString() ||
      newQuery.size !== params.value.size.toString() ||
      sortChanged ||
      newQuery[props.searchColumnId] !== params.value[props.searchColumnId]
    ) {
      if (newQuery.page) params.value.page = Number(newQuery.page);
      if (newQuery.size) params.value.size = Number(newQuery.size);
      else if (newQuery.limit) params.value.size = Number(newQuery.limit);

      if (newQuery.sort) {
        const sortValue = newQuery.sort as string;

        if (sortValue.includes(',')) {
          const [property, direction] = sortValue.split(',');

          params.value.sort = sortValue;
          params.value.direction = direction;

          sorting.value = [
            {
              id: property,
              desc: direction === 'desc',
            },
          ];
        }
        else if (newQuery.direction) {
          const direction = newQuery.direction as string;

          params.value.sort = `${sortValue},${direction}`;
          params.value.direction = direction;

          sorting.value = [
            {
              id: sortValue,
              desc: direction === 'desc',
            },
          ];
        } else {
          params.value.sort = `${sortValue},asc`;
          params.value.direction = 'asc';

          sorting.value = [
            {
              id: sortValue,
              desc: false,
            },
          ];
        }
      } else if (!newQuery.sort && sorting.value.length > 0) {
        sorting.value = [];
      }

      // Handle all query parameters as potential column filters
      const newColumnFilters: any[] = [];
      
      Object.entries(newQuery).forEach(([key, value]) => {
        if (!['page', 'size', 'sort', 'direction', 'limit'].includes(key) && value) {
          params.value[key] = value;
          
          if (key.endsWith('From') || key.endsWith('To')) {
            const baseKey = key.replace(/From$|To$/, '');
            const existingFilter = newColumnFilters.find(f => f.id === baseKey);
            
            if (existingFilter) {
              if (key.endsWith('From')) {
                existingFilter.value.start = new Date(value as string);
              } else {
                existingFilter.value.end = new Date(value as string);
              }
            } else {
              const dateRangeValue: any = {};
              if (key.endsWith('From')) {
                dateRangeValue.start = new Date(value as string);
              } else {
                dateRangeValue.end = new Date(value as string);
              }
              
              newColumnFilters.push({
                id: baseKey,
                value: dateRangeValue,
              });
            }
          }
          else if (typeof value === 'string' && value.includes(',')) {
            newColumnFilters.push({
              id: key,
              value: value.split(','),
            });
          }
          else {
            newColumnFilters.push({
              id: key,
              value: value,
            });
          }
        }
      });
      
      columnFilters.value = newColumnFilters;

      loadData();
    }
  },
  { deep: true }
);

// Expose table instance and data
defineExpose({
  table,
  data,
  params,
  pagination,
  loadData,
});
</script>