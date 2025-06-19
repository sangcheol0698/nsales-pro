<template>
  <div>
    <DataTableToolbar 
      :table="table" 
      :searchPlaceholder="searchPlaceholder" 
      :searchColumnId="searchColumnId"
      :getColumnLabel="getColumnLabel"
    >
      <slot name="toolbar"></slot>
    </DataTableToolbar>
    
    <DataTable 
      :columns="columns" 
      :data="data" 
      :loading="pagination.loading"
      :emptyMessage="emptyMessage"
      :emptyDescription="emptyDescription"
    >
      <template v-if="$slots['expanded-row']" #expanded-row="slotProps">
        <slot name="expanded-row" v-bind="slotProps"></slot>
      </template>
    </DataTable>
    
    <DataTablePagination
      :page="params.page"
      :pageSize="params.limit"
      :totalPages="pagination.totalPages"
      :totalElements="pagination.totalElements"
      :loading="pagination.loading"
      :selectedRowCount="table.getFilteredSelectedRowModel().rows.length"
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
} from '@tanstack/vue-table'
import {
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useVueTable,
} from '@tanstack/vue-table'
import { onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { valueUpdater } from '@/core/components/ui/table/utils'
import { debounce } from 'lodash-es'
import PageResponse from '@/core/common/PageResponse'
import {
  DataTable,
  DataTablePagination,
  DataTableToolbar,
} from '@/core/components/ui/data-table'

interface DataTableWithUrlProps<TData> {
  columns: ColumnDef<TData, any>[]
  fetchData: (params: Record<string, any>) => Promise<PageResponse<TData>>
  searchColumnId?: string
  searchPlaceholder?: string
  emptyMessage?: string
  emptyDescription?: string
  getColumnLabel?: (columnId: string) => string
  initialParams?: Record<string, any>
  debounceTime?: number
}

const props = withDefaults(defineProps<DataTableWithUrlProps<any>>(), {
  searchColumnId: 'name',
  searchPlaceholder: '검색...',
  emptyMessage: '데이터가 없습니다',
  emptyDescription: '데이터가 생성되면 여기에 표시됩니다',
  debounceTime: 300,
})

const router = useRouter()
const route = useRoute()

const data = ref<any[]>([])
const sorting = ref<SortingState>([])
const columnFilters = ref<ColumnFiltersState>([])
const columnVisibility = ref<VisibilityState>({})
const rowSelection = ref({})
const expanded = ref<ExpandedState>({})

interface PaginationState {
  totalPages: number
  totalElements: number
  loading: boolean
}

const pagination = ref<PaginationState>({
  totalPages: 0,
  totalElements: 0,
  loading: false,
})

// Initialize params from URL or defaults
const params = ref<Record<string, any>>({
  page: 1,
  limit: 10,
  ...props.initialParams,
})

// Create table instance
const table = useVueTable({
  get data() { return data.value },
  columns: props.columns,
  manualPagination: true,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
  onSortingChange: updaterOrValue => {
    valueUpdater(updaterOrValue, sorting)

    // Update params with sorting information
    if (sorting.value.length > 0) {
      const sort = sorting.value[0]
      params.value = {
        ...params.value,
        sort: sort.id,
        direction: sort.desc ? 'desc' : 'asc'
      }
    } else if (params.value.sort) {
      // Remove sorting if not present
      const { sort, direction, ...rest } = params.value
      params.value = rest
    }

    // Update URL and fetch data
    updateUrl()
    loadData()
  },
  onColumnFiltersChange: updaterOrValue => {
    valueUpdater(updaterOrValue, columnFilters)

    // Get the filter value for the search column
    const searchFilter = columnFilters.value.find(filter => filter.id === props.searchColumnId)?.value as string

    // Update params with the search filter
    if (searchFilter) {
      params.value = { ...params.value, [props.searchColumnId]: searchFilter }
    } else if (params.value[props.searchColumnId]) {
      // Remove the search filter if it's not present
      const { [props.searchColumnId]: _, ...rest } = params.value
      params.value = rest
    }

    // Reset to first page
    params.value.page = 1
    
    // Update URL and fetch data with debouncing for search
    updateUrlDebounced()
    loadData()
  },
  onColumnVisibilityChange: updaterOrValue => valueUpdater(updaterOrValue, columnVisibility),
  onRowSelectionChange: updaterOrValue => valueUpdater(updaterOrValue, rowSelection),
  onExpandedChange: updaterOrValue => valueUpdater(updaterOrValue, expanded),
  state: {
    get sorting() { return sorting.value },
    get columnFilters() { return columnFilters.value },
    get columnVisibility() { return columnVisibility.value },
    get rowSelection() { return rowSelection.value },
    get expanded() { return expanded.value },
  },
})

// Debounced URL update function
const updateUrlDebounced = debounce(updateUrl, props.debounceTime)

// Update URL with current params
function updateUrl() {
  router.replace({
    query: { ...params.value }
  })
}

// Load data from API
function loadData() {
  pagination.value.loading = true

  props.fetchData(params.value)
    .then((response: PageResponse<any>) => {
      data.value = response.content
      pagination.value.totalPages = response.totalPages
      pagination.value.totalElements = response.totalElements
    })
    .catch((error) => {
      console.error('Error loading data:', error)
    })
    .finally(() => {
      pagination.value.loading = false
    })
}

// Page change handler
function onPageChange(page: number) {
  params.value.page = page
  updateUrl()
  loadData()
}

// Page size change handler
function onPageSizeChange(size: number) {
  params.value.limit = size
  params.value.page = 1 // Reset to first page when changing page size
  updateUrl()
  loadData()
}

// Function to get column label (uses prop function if provided)
function getColumnLabel(columnId: string): string {
  if (props.getColumnLabel) {
    return props.getColumnLabel(columnId)
  }
  return columnId
}

// Load initial state from URL on mount
onMounted(() => {
  // Get params from URL
  const query = route.query

  // Update params from URL
  if (query.page) params.value.page = Number(query.page)
  if (query.limit) params.value.limit = Number(query.limit)
  
  // Handle sort params
  if (query.sort && query.direction) {
    params.value.sort = query.sort as string
    params.value.direction = query.direction as string
    
    // Update sorting state
    sorting.value = [{
      id: query.sort as string,
      desc: query.direction === 'desc'
    }]
  }
  
  // Handle search filter
  if (query[props.searchColumnId]) {
    params.value[props.searchColumnId] = query[props.searchColumnId] as string
    
    // Update column filters state
    columnFilters.value = [{
      id: props.searchColumnId,
      value: query[props.searchColumnId] as string
    }]
  }
  
  // Load data with initial params
  loadData()
})

// Watch for route changes to update state
watch(
  () => route.query,
  (newQuery) => {
    // Only update if the change wasn't triggered by this component
    if (
      newQuery.page !== params.value.page.toString() ||
      newQuery.limit !== params.value.limit.toString() ||
      newQuery.sort !== params.value.sort ||
      newQuery.direction !== params.value.direction ||
      newQuery[props.searchColumnId] !== params.value[props.searchColumnId]
    ) {
      // Update params from URL
      if (newQuery.page) params.value.page = Number(newQuery.page)
      if (newQuery.limit) params.value.limit = Number(newQuery.limit)
      
      // Handle sort params
      if (newQuery.sort && newQuery.direction) {
        params.value.sort = newQuery.sort as string
        params.value.direction = newQuery.direction as string
        
        // Update sorting state
        sorting.value = [{
          id: newQuery.sort as string,
          desc: newQuery.direction === 'desc'
        }]
      } else if (!newQuery.sort && sorting.value.length > 0) {
        sorting.value = []
      }
      
      // Handle search filter
      if (newQuery[props.searchColumnId]) {
        params.value[props.searchColumnId] = newQuery[props.searchColumnId] as string
        
        // Update column filters state
        columnFilters.value = [{
          id: props.searchColumnId,
          value: newQuery[props.searchColumnId] as string
        }]
      } else if (!newQuery[props.searchColumnId] && columnFilters.value.length > 0) {
        columnFilters.value = []
      }
      
      // Load data with updated params
      loadData()
    }
  },
  { deep: true }
)

// Expose table instance and data
defineExpose({
  table,
  data,
  params,
  pagination,
  loadData
})
</script>