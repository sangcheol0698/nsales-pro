<template>
  <div class="space-y-4">
    <!-- Search and filters -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <Input
          v-model="searchValue"
          :placeholder="searchPlaceholder"
          class="w-64 search-input"
          @input="onSearchChange"
        />
      </div>
      
      <div class="flex items-center space-x-2">
        <!-- Column visibility -->
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="outline" size="sm" class="btn-outline">
              <Settings class="h-4 w-4 mr-2" />
              열 설정
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              v-for="column in table.getAllColumns().filter(c => c.getCanHide())"
              :key="column.id"
              @click="column.toggleVisibility()"
            >
              <Checkbox
                :checked="column.getIsVisible()"
                class="mr-2"
              />
              {{ getColumnLabel(column.id) }}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>

    <!-- Data table -->
    <div class="table-container">
      <Table>
        <TableHeader class="table-header">
          <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <TableHead v-for="header in headerGroup.headers" :key="header.id" class="table-cell font-medium">
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
            <TableRow
              v-for="row in table.getRowModel().rows"
              :key="row.id"
              :data-state="row.getIsSelected() && 'selected'"
              class="table-row cursor-pointer"
              @click="() => onRowClick?.(row.original)"
            >
              <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id" class="table-cell">
                <FlexRender
                  :render="cell.column.columnDef.cell"
                  :props="cell.getContext()"
                />
              </TableCell>
            </TableRow>
          </template>
          <template v-else>
            <TableRow>
              <TableCell :colspan="columns.length" class="h-24 text-center table-cell">
                <div class="flex flex-col items-center justify-center space-y-2">
                  <p class="text-muted-foreground">{{ emptyMessage }}</p>
                  <p class="text-sm text-muted-foreground">{{ emptyDescription }}</p>
                </div>
              </TableCell>
            </TableRow>
          </template>
        </TableBody>
      </Table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <p class="text-sm text-muted-foreground">
          총 {{ pagination.totalElements }}개 중 {{ pagination.size * pagination.number + 1 }}-{{ Math.min(pagination.size * (pagination.number + 1), pagination.totalElements) }}개 표시
        </p>
      </div>
      
      <div class="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          class="btn-outline"
          :disabled="!table.getCanPreviousPage()"
          @click="table.previousPage()"
        >
          이전
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="btn-outline"
          :disabled="!table.getCanNextPage()"
          @click="table.nextPage()"
        >
          다음
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import {
  useVueTable,
  FlexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type VisibilityState,
} from '@tanstack/vue-table';
import { Settings } from 'lucide-vue-next';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Props {
  columns: ColumnDef<any>[];
  fetchData: (params: Record<string, any>) => Promise<{ content: any[]; totalElements: number; number: number; size: number }>;
  searchPlaceholder?: string;
  searchColumnId?: string;
  getColumnLabel: (columnId: string) => string;
  emptyMessage?: string;
  emptyDescription?: string;
  onRowClick?: (row: any) => void;
}

const props = withDefaults(defineProps<Props>(), {
  searchPlaceholder: '검색...',
  searchColumnId: 'name',
  emptyMessage: '데이터가 없습니다',
  emptyDescription: '새 항목을 추가하거나 검색 조건을 변경해보세요',
});

// State
const data = ref<any[]>([]);
const searchValue = ref('');
const sorting = ref<SortingState>([]);
const columnFilters = ref<ColumnFiltersState>([]);
const columnVisibility = ref<VisibilityState>({});
const pagination = ref({
  totalElements: 0,
  number: 0,
  size: 10,
});

// Table instance
const table = useVueTable({
  get data() { return data.value; },
  get columns() { return props.columns; },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  state: {
    get sorting() { return sorting.value; },
    get columnFilters() { return columnFilters.value; },
    get columnVisibility() { return columnVisibility.value; },
  },
  onSortingChange: (updater) => {
    sorting.value = typeof updater === 'function' ? updater(sorting.value) : updater;
  },
  onColumnFiltersChange: (updater) => {
    columnFilters.value = typeof updater === 'function' ? updater(columnFilters.value) : updater;
  },
  onColumnVisibilityChange: (updater) => {
    columnVisibility.value = typeof updater === 'function' ? updater(columnVisibility.value) : updater;
  },
  manualPagination: true,
  pageCount: computed(() => Math.ceil(pagination.value.totalElements / pagination.value.size)).value,
});

// Methods
async function loadData() {
  try {
    const params = {
      page: table.getState().pagination.pageIndex,
      size: table.getState().pagination.pageSize,
      [props.searchColumnId]: searchValue.value || undefined,
    };

    const response = await props.fetchData(params);
    data.value = response.content;
    pagination.value = {
      totalElements: response.totalElements,
      number: response.number,
      size: response.size,
    };
  } catch (error) {
    console.error('Error loading data:', error);
  }
}

function onSearchChange() {
  table.setPageIndex(0);
  loadData();
}

// Watchers
watch(() => table.getState().pagination.pageIndex, loadData);
watch(() => table.getState().pagination.pageSize, loadData);

// Lifecycle
onMounted(() => {
  loadData();
});
</script>