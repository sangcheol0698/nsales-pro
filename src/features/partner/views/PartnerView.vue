<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <div class="flex items-center py-4">
          <Input
            class="max-w-sm"
            placeholder="협력사 검색..."
            :model-value="table.getColumn('name')?.getFilterValue() as string"
            @update:model-value="table.getColumn('name')?.setFilterValue($event)"
          />
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="outline" class="ml-auto">
                컬럼 <ChevronDown class="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuCheckboxItem
                v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
                :key="column.id"
                class="capitalize"
                :model-value="column.getIsVisible()"
                @update:model-value="(value) => {
                  column.toggleVisibility(!!value)
                }"
              >
                {{ getColumnLabel(column.id) }}
              </DropdownMenuCheckboxItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <div class="rounded-md border overflow-auto">
          <div v-if="pagination.loading" class="flex justify-center items-center p-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
          <Table v-else>
            <TableHeader>
              <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
                <TableHead v-for="header in headerGroup.headers" :key="header.id">
                  <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header" :props="header.getContext()" />
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
                      <pre>{{ JSON.stringify(row.original, null, 2) }}</pre>
                    </TableCell>
                  </TableRow>
                </template>
              </template>
              <template v-else>
                <TableEmpty :colspan="columns.length">
                  <div class="flex flex-col items-center">
                    <p class="text-lg font-medium">협력사가 없습니다</p>
                    <p class="text-sm text-muted-foreground">
                      새 협력사를 추가하거나 검색 조건을 변경해보세요
                    </p>
                  </div>
                </TableEmpty>
              </template>
            </TableBody>
          </Table>
        </div>

        <div class="flex items-center justify-between space-x-2 py-4">
          <div class="flex items-center space-x-2">
            <p class="text-sm text-muted-foreground">
              페이지당 행 수
            </p>
            <Select
              :model-value="params.limit.toString()"
              @update:model-value="onPageSizeChange(Number($event))"
            >
              <SelectTrigger class="h-8 w-[70px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
                <SelectItem value="50">50</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="flex-1 text-sm text-muted-foreground text-center">
            {{ table.getFilteredSelectedRowModel().rows.length }} /
            {{ pagination.totalElements }} 행 선택됨 |
            {{ params.page }} / {{ pagination.totalPages }} 페이지
          </div>

          <div class="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              :disabled="params.page <= 1 || pagination.loading"
              @click="onPageChange(params.page - 1)"
            >
              이전
            </Button>
            <Button
              variant="outline"
              size="sm"
              :disabled="params.page >= pagination.totalPages || pagination.loading"
              @click="onPageChange(params.page + 1)"
            >
              다음
            </Button>
          </div>
        </div>
      </div>
    </main>
  </SidebarLayout>
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
  FlexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useVueTable,
} from '@tanstack/vue-table'
import { ArrowUpDown, ChevronDown } from 'lucide-vue-next'
import { h, onMounted, ref } from 'vue'
import { valueUpdater } from '@/core/components/ui/table/utils'
import { container } from 'tsyringe'
import PartnerRepository from '@/features/partner/repository/PartnerRepository.ts'
import type { PartnerSearch } from '@/features/partner/entity/PartnerSearch.ts'
import { SidebarLayout } from '@/shared/components/sidebar'

import { Button } from '@/core/components/ui/button'
import { Checkbox } from '@/core/components/ui/checkbox'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu'
import { Input } from '@/core/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableHead,
  TableHeader,
  TableRow,
} from '@/core/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/core/components/ui/select'

const PARTNER_REPOSITORY = container.resolve(PartnerRepository)
const data = ref<PartnerSearch[]>([])

const columns: ColumnDef<PartnerSearch>[] = [
  {
    id: 'select',
    header: ({ table }) => h(Checkbox, {
      'modelValue': table.getIsAllPageRowsSelected() || (table.getIsSomePageRowsSelected() && 'indeterminate'),
      'onUpdate:modelValue': value => table.toggleAllPageRowsSelected(!!value),
      'ariaLabel': '모두 선택',
    }),
    cell: ({ row }) => h(Checkbox, {
      'modelValue': row.getIsSelected(),
      'onUpdate:modelValue': value => row.toggleSelected(!!value),
      'ariaLabel': '행 선택',
    }),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'name',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['협력사명', h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })])
    },
    cell: ({ row }) => {
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'font-medium' }, row.getValue('name') || '-'),
        h('span', { class: 'text-xs text-muted-foreground' }, row.original.address || '')
      ])
    },
  },
  {
    accessorKey: 'ceoName',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['대표자', h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })])
    },
    cell: ({ row }) => h('div', {}, row.getValue('ceoName') || '-'),
  },
  {
    accessorKey: 'salesRepName',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['영업대표', h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })])
    },
    cell: ({ row }) => h('div', {}, row.getValue('salesRepName') || '-'),
  },
  {
    accessorKey: 'salesRepPhone',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['영업대표 연락처', h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })])
    },
    // Use a custom cell renderer to format the phone number
    cell: ({ row }) => h('div', {}, row.getValue('salesRepPhone') || '-'),
  },
  {
    accessorKey: 'salesRepEmail',
    header: '영업대표 이메일',
    cell: ({ row }) => h('div', {}, row.getValue('salesRepEmail') || '-'),
  },
  {
    accessorKey: 'grade',
    header: '등급',
    cell: ({ row }) => h('div', {}, row.getValue('grade') || '-'),
  },
]

const sorting = ref<SortingState>([])
const columnFilters = ref<ColumnFiltersState>([])
const columnVisibility = ref<VisibilityState>({})
const rowSelection = ref({})
const expanded = ref<ExpandedState>({})

const table = useVueTable({
  get data() { return data.value },
  columns,
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

    // Fetch data with new sorting
    fetchPartners()
  },
  onColumnFiltersChange: updaterOrValue => {
    valueUpdater(updaterOrValue, columnFilters)

    // Get the name filter value
    const nameFilter = columnFilters.value.find(filter => filter.id === 'name')?.value as string

    // Update params with the name filter
    if (nameFilter) {
      params.value = { ...params.value, name: nameFilter }
    } else if (params.value.name) {
      // Remove the name filter if it's not present
      const { name, ...rest } = params.value
      params.value = rest
    }

    // Reset to first page and fetch data
    params.value.page = 1
    fetchPartners()
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

function getColumnLabel(columnId: string): string {
  switch (columnId) {
    case 'name': return '협력사명'
    case 'businessNumber': return '사업자번호'
    case 'representative': return '대표자'
    case 'contactPerson': return '담당자'
    case 'contactEmail': return '이메일'
    case 'contactPhone': return '연락처'
    case 'status': return '상태'
    default: return columnId
  }
}

const params = ref({
  page: 1,
  limit: 10,
})

const pagination = ref({
  totalPages: 0,
  totalElements: 0,
  loading: false,
})

function fetchPartners() {
  pagination.value.loading = true
  console.log('Fetching partners with params:', params.value)

  PARTNER_REPOSITORY.getPartners(params.value)
    .then((response) => {
      data.value = response.content
      pagination.value.totalPages = response.totalPages
      pagination.value.totalElements = response.totalElements
      console.log('Partners loaded:', data.value)
    })
    .catch((error) => {
      console.error('Error loading partners:', error)
      // Show error message to user
      alert('협력사를 불러오는 중 오류가 발생했습니다. 다시 시도해주세요.')
    })
    .finally(() => {
      pagination.value.loading = false
    })
}

function onPageChange(page: number) {
  params.value.page = page
  fetchPartners()
}

function onPageSizeChange(size: number) {
  params.value.limit = size
  params.value.page = 1 // Reset to first page when changing page size
  fetchPartners()
}

onMounted(() => {
  fetchPartners()
})
</script>

<style scoped></style>