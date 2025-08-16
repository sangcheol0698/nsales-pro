<template>
  <div class="space-y-4">
    <DataTableToolbar
      :table="table"
      :searchPlaceholder="searchPlaceholder"
      :searchColumnId="searchColumnId"  
      :getColumnLabel="getColumnLabel"
    >
      <template #filters>
        <slot name="filters" :table="table"></slot>
      </template>
      
      <template #actions>
        <slot name="actions" :table="table"></slot>
      </template>
      
      <slot name="toolbar"></slot>
    </DataTableToolbar>

    <DataTable
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
    </DataTable>

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
import { onMounted, ref, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { valueUpdater } from '@/components/ui/table/utils';
import { debounce } from 'lodash-es';
import PageResponse from '@/core/common/PageResponse';
import DataTable from './DataTable.vue';
import DataTablePagination from './DataTablePagination.vue';
import DataTableToolbar from './DataTableToolbar.vue';

interface DataTableWithUrlProps<TData> {
  columns: ColumnDef<TData, any>[];
  fetchData: (params: Record<string, any>) => Promise<PageResponse<TData>>;
  searchColumnId?: string;
  searchPlaceholder?: string;
  emptyMessage?: string;
  emptyDescription?: string;
  getColumnLabel?: (columnId: string) => string;
  initialParams?: Record<string, any>;
  debounceTime?: number;
  storageKey?: string; // Key for localStorage to persist column visibility
}

const props = withDefaults(defineProps<DataTableWithUrlProps<any>>(), {
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

// Function to get storage key for column visibility
function getStorageKey(): string {
  return props.storageKey || `table-column-visibility-${route.name || 'default'}`;
}

// Function to load column visibility from localStorage
function loadColumnVisibility(): VisibilityState {
  try {
    const stored = localStorage.getItem(getStorageKey());
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.warn('Failed to load column visibility from localStorage:', error);
  }
  return {};
}

// Function to save column visibility to localStorage
function saveColumnVisibility(visibility: VisibilityState) {
  try {
    localStorage.setItem(getStorageKey(), JSON.stringify(visibility));
  } catch (error) {
    console.warn('Failed to save column visibility to localStorage:', error);
  }
}

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
  // Use row.id as the selection key instead of row index
  getRowId: (row) => row.id?.toString() || '',
  onSortingChange: (updaterOrValue) => {
    valueUpdater(updaterOrValue, sorting);

    // Update params with sorting information
    if (sorting.value.length > 0) {
      const sort = sorting.value[0];
      // Format sort parameter as expected by Spring Boot: 'property,direction'
      const sortParam = `${sort.id},${sort.desc ? 'desc' : 'asc'}`;

      params.value = {
        ...params.value,
        sort: sortParam,
      };

      // Keep separate direction parameter for URL display and backward compatibility
      params.value.direction = sort.desc ? 'desc' : 'asc';
    } else if (params.value.sort) {
      // Remove sorting if not present
      const { sort, direction, ...rest } = params.value;
      params.value = rest;
    }

    // Update URL and fetch data
    updateUrl();
    loadData();
  },
  onColumnFiltersChange: (updaterOrValue) => {
    valueUpdater(updaterOrValue, columnFilters);

    // Process all column filters and update params
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
        // Handle array values (for multi-select filters)
        if (Array.isArray(filter.value) && filter.value.length > 0) {
          newParams[filter.id] = filter.value.join(',');
        }
        // Handle date range values
        else if (typeof filter.value === 'object' && filter.value.start) {
          newParams[`${filter.id}From`] = filter.value.start.toISOString().split('T')[0];
          if (filter.value.end) {
            newParams[`${filter.id}To`] = filter.value.end.toISOString().split('T')[0]; 
          }
        }
        // Handle simple string/number values
        else {
          newParams[filter.id] = filter.value;
        }
      }
    });

    params.value = newParams;

    // Reset to first page when filters change
    params.value.page = 1;

    // Update URL and fetch data with debouncing for text searches
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
  onColumnVisibilityChange: (updaterOrValue) => {
    valueUpdater(updaterOrValue, columnVisibility);
    // Save to localStorage whenever column visibility changes
    saveColumnVisibility(columnVisibility.value);
  },
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

  // Ensure sort parameter is in the correct format for Spring Boot
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
  // Clear row selection when changing page size
  rowSelection.value = {};

  params.value.size = size;
  params.value.page = 1; // Reset to first page when changing page size
  updateUrl();
  loadData();
}

// Function to get column label (uses prop function if provided)
function getColumnLabel(columnId: string): string {
  if (props.getColumnLabel) {
    return props.getColumnLabel(columnId);
  }
  return columnId;
}

// Load initial state from URL on mount
onMounted(() => {
  // Load column visibility from localStorage
  columnVisibility.value = loadColumnVisibility();
  console.log('🔄 Loading column visibility from localStorage:', columnVisibility.value);

  // Get params from URL
  const query = route.query;
  console.log('🔄 Mounting DataTableWithUrl - URL query:', query);

  // Update params from URL
  if (query.page) params.value.page = Number(query.page);
  if (query.size) params.value.size = Number(query.size);
  // Handle legacy limit parameter for backward compatibility
  else if (query.limit) params.value.size = Number(query.limit);

  // Handle sort params
  if (query.sort) {
    const sortValue = query.sort as string;

    // Check if sort parameter contains direction (property,direction format)
    if (sortValue.includes(',')) {
      const [property, direction] = sortValue.split(',');

      params.value.sort = sortValue;
      params.value.direction = direction;

      // Update sorting state
      sorting.value = [
        {
          id: property,
          desc: direction === 'desc',
        },
      ];
    }
    // Backward compatibility for separate sort and direction parameters
    else if (query.direction) {
      const direction = query.direction as string;

      params.value.sort = `${sortValue},${direction}`;
      params.value.direction = direction;

      // Update sorting state
      sorting.value = [
        {
          id: sortValue,
          desc: direction === 'desc',
        },
      ];
    } else {
      // Add default direction (asc) if not present
      params.value.sort = `${sortValue},asc`;
      params.value.direction = 'asc';

      // Update sorting state
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
      
      // Handle date range filters (ending with From/To)
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
      // Handle array values (comma-separated)
      else if (typeof value === 'string' && value.includes(',')) {
        const arrayValue = value.split(',');
        console.log(`🎯 Restoring array filter - ${key}:`, arrayValue);
        newColumnFilters.push({
          id: key,
          value: arrayValue,
        });
      }
      // Handle simple values
      else {
        console.log(`🎯 Restoring simple filter - ${key}:`, value);
        newColumnFilters.push({
          id: key,
          value: value,
        });
      }
    }
  });
  
  // Apply filters after table is ready
  if (newColumnFilters.length > 0) {
    // Use nextTick to ensure table is fully initialized
    nextTick(() => {
      columnFilters.value = newColumnFilters;
      console.log('🔄 Initial column filters restored (after nextTick):', newColumnFilters);
      console.log('🔄 Table columns available:', table.getAllColumns().map(c => c.id));
    });
  }
  
  console.log('🔄 Final params:', params.value);

  // Load data with initial params
  loadData();
});

// Watch for route changes to update state
watch(
  () => route.query,
  (newQuery) => {
    // Only update if the change wasn't triggered by this component
    // Simplify the sort change detection logic
    const sortChanged = String(newQuery.sort) !== String(params.value.sort);

    if (
      newQuery.page !== params.value.page.toString() ||
      newQuery.size !== params.value.size.toString() ||
      sortChanged ||
      newQuery[props.searchColumnId] !== params.value[props.searchColumnId]
    ) {
      // Update params from URL
      if (newQuery.page) params.value.page = Number(newQuery.page);
      if (newQuery.size) params.value.size = Number(newQuery.size);
      // Handle legacy limit parameter for backward compatibility
      else if (newQuery.limit) params.value.size = Number(newQuery.limit);

      // Handle sort params
      if (newQuery.sort) {
        const sortValue = newQuery.sort as string;

        // Check if sort parameter contains direction (property,direction format)
        if (sortValue.includes(',')) {
          const [property, direction] = sortValue.split(',');

          params.value.sort = sortValue;
          params.value.direction = direction;

          // Update sorting state
          sorting.value = [
            {
              id: property,
              desc: direction === 'desc',
            },
          ];
        }
        // Backward compatibility for separate sort and direction parameters
        else if (newQuery.direction) {
          const direction = newQuery.direction as string;

          params.value.sort = `${sortValue},${direction}`;
          params.value.direction = direction;

          // Update sorting state
          sorting.value = [
            {
              id: sortValue,
              desc: direction === 'desc',
            },
          ];
        } else {
          // Add default direction (asc) if not present
          params.value.sort = `${sortValue},asc`;
          params.value.direction = 'asc';

          // Update sorting state
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
          
          // Handle date range filters (ending with From/To)
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
          // Handle array values (comma-separated)
          else if (typeof value === 'string' && value.includes(',')) {
            newColumnFilters.push({
              id: key,
              value: value.split(','),
            });
          }
          // Handle simple values
          else {
            newColumnFilters.push({
              id: key,
              value: value,
            });
          }
        }
      });
      
      // Apply filters after table is ready (same as onMounted)
      if (newColumnFilters.length > 0) {
        nextTick(() => {
          columnFilters.value = newColumnFilters;
          console.log('🔄 Route change - column filters restored (after nextTick):', newColumnFilters);
        });
      } else {
        columnFilters.value = newColumnFilters;
      }

      // Load data with updated params
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