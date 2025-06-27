<script setup lang="ts">
import { computed } from 'vue';
import { Button } from '@/core/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/core/components/ui/select';

interface DataTablePaginationProps {
  page: number;
  pageSize: number;
  totalPages: number;
  totalElements: number;
  loading?: boolean;
  pageSizeOptions?: number[];
  selectedRowCount?: number;
}

const props = defineProps<DataTablePaginationProps>();

const emit = defineEmits<{
  (e: 'pageChange', page: number): void;
  (e: 'pageSizeChange', pageSize: number): void;
}>();

const pages = computed(() => {
  const total = props.totalPages;
  if (total <= 1) return [];

  const current = props.page;
  const maxVisible = 6;

  if (total <= maxVisible) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  // Near start: 1, 2, 3, 4, 5, ..., total
  if (current < 5) {
    return [1, 2, 3, 4, 5, '...', total];
  }

  // Near end: 1, ..., total-4, total-3, total-2, total-1, total
  if (current > total - 4) {
    return [1, '...', total - 4, total - 3, total - 2, total - 1, total];
  }

  // Middle: 1, ..., c-2, c-1, c, c+1, ..., total
  return [1, '...', current - 2, current - 1, current, current + 1, '...', total];
});

function onPageChange(page: number) {
  emit('pageChange', page);
}

function onPageSizeChange(pageSize: string) {
  emit('pageSizeChange', Number(pageSize));
}
</script>

<template>
  <div class="flex flex-col md:flex-row items-center justify-between gap-4 py-4">
    <!-- Summary info (moved to left) -->
    <div class="text-sm text-muted-foreground order-2 md:order-1 w-full md:w-auto">
      <span v-if="selectedRowCount !== undefined"> {{ selectedRowCount }} / </span>
      {{ totalElements }} 행
      <span v-if="totalPages > 0"> | {{ page }} / {{ totalPages }} 페이지 </span>
    </div>

    <!-- Right side container for page size and pagination -->
    <div class="flex flex-col md:flex-row items-center gap-4 order-1 md:order-2 w-full md:w-auto">
      <!-- Row count info (moved to right) -->
      <div class="flex items-center gap-2 w-full md:w-auto">
        <p class="text-sm text-muted-foreground whitespace-nowrap">페이지당 행 수</p>
        <Select :model-value="pageSize.toString()" @update:model-value="onPageSizeChange">
          <SelectTrigger class="h-8 w-[70px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem
              v-for="option in pageSizeOptions || [5, 10, 20, 50]"
              :key="option"
              :value="option.toString()"
            >
              {{ option }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- Pagination controls -->
      <div class="flex items-center justify-center gap-1 w-full md:w-auto">
        <Button
          variant="outline"
          size="sm"
          class="hidden sm:inline-flex"
          :disabled="page <= 1 || loading"
          @click="onPageChange(1)"
        >
          처음
        </Button>
        <Button
          variant="outline"
          size="sm"
          :disabled="page <= 1 || loading"
          @click="onPageChange(page - 1)"
        >
          이전
        </Button>

        <!-- Page number buttons -->
        <div class="flex items-center gap-1 mx-1">
          <template v-for="(p, i) in pages" :key="`${p}-${i}`">
            <span v-if="p === '...'" class="hidden sm:inline-flex px-1">...</span>
            <Button
              v-else
              variant="outline"
              size="sm"
              :class="{ 'is-active': p === page }"
              @click="onPageChange(p as number)"
            >
              {{ p }}
            </Button>
          </template>
        </div>

        <Button
          variant="outline"
          size="sm"
          :disabled="page >= totalPages || loading"
          @click="onPageChange(page + 1)"
        >
          다음
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="hidden sm:inline-flex"
          :disabled="page >= totalPages || loading"
          @click="onPageChange(totalPages)"
        >
          마지막
        </Button>
      </div>
    </div>
  </div>
</template>
