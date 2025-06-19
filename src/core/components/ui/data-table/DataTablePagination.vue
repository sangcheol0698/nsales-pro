<script setup lang="ts">
import { Button } from '@/core/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/core/components/ui/select'

interface DataTablePaginationProps {
  page: number
  pageSize: number
  totalPages: number
  totalElements: number
  loading?: boolean
  pageSizeOptions?: number[]
  selectedRowCount?: number
}

const props = defineProps<DataTablePaginationProps>()

const emit = defineEmits<{
  (e: 'pageChange', page: number): void
  (e: 'pageSizeChange', pageSize: number): void
}>()

function onPageChange(page: number) {
  emit('pageChange', page)
}

function onPageSizeChange(pageSize: string) {
  emit('pageSizeChange', Number(pageSize))
}
</script>

<template>
  <div class="flex flex-col md:flex-row items-center justify-between gap-4 py-4">
    <!-- Summary info (moved to left) -->
    <div class="text-sm text-muted-foreground order-2 md:order-1 w-full md:w-auto">
      <span v-if="selectedRowCount !== undefined">
        {{ selectedRowCount }} /
      </span>
      {{ totalElements }} 행
      <span v-if="totalPages > 0">
        | {{ page }} / {{ totalPages }} 페이지
      </span>
    </div>

    <!-- Right side container for page size and pagination -->
    <div class="flex flex-col md:flex-row items-center gap-4 order-1 md:order-2 w-full md:w-auto">
      <!-- Row count info (moved to right) -->
      <div class="flex items-center gap-2 w-full md:w-auto">
        <p class="text-sm text-muted-foreground whitespace-nowrap">
          페이지당 행 수
        </p>
        <Select
          :model-value="pageSize.toString()"
          @update:model-value="onPageSizeChange"
        >
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
        <template v-if="totalPages <= 5">
          <!-- Show all pages if 5 or fewer -->
          <Button
            v-for="pageNum in totalPages"
            :key="pageNum"
            variant="outline"
            size="sm"
            :class="{ 'bg-primary text-primary-foreground': pageNum === page }"
            @click="onPageChange(pageNum)"
          >
            {{ pageNum }}
          </Button>
        </template>
        <template v-else>
          <!-- Show first page -->
          <Button
            v-if="page > 3"
            variant="outline"
            size="sm"
            class="hidden sm:inline-flex"
            @click="onPageChange(1)"
          >
            1
          </Button>

          <!-- Show ellipsis if needed -->
          <span v-if="page > 4" class="hidden sm:inline-flex px-1">...</span>

          <!-- Show pages around current page -->
          <Button
            v-for="pageNum in Array.from({ length: 3 }, (_, i) => {
              const start = Math.max(1, Math.min(page - 1, totalPages - 2));
              return start + i;
            }).filter(num => num > 0 && num <= totalPages)"
            :key="pageNum"
            variant="outline"
            size="sm"
            :class="{ 'bg-primary text-primary-foreground': pageNum === page }"
            @click="onPageChange(pageNum)"
          >
            {{ pageNum }}
          </Button>

          <!-- Show ellipsis if needed -->
          <span v-if="page < totalPages - 3" class="hidden sm:inline-flex px-1">...</span>

          <!-- Show last page -->
          <Button
            v-if="page < totalPages - 2"
            variant="outline"
            size="sm"
            class="hidden sm:inline-flex"
            @click="onPageChange(totalPages)"
          >
            {{ totalPages }}
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
