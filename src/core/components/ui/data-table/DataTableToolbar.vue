<script setup lang="ts">
import type { Column, Table } from '@tanstack/vue-table'
import { ChevronDown } from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Input } from '@/core/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu'

interface DataTableToolbarProps<TData> {
  table: Table<TData>
  searchPlaceholder?: string
  searchColumnId?: string
  getColumnLabel?: (columnId: string) => string
}

const props = defineProps<DataTableToolbarProps<any>>()

function getColumnLabel(columnId: string): string {
  if (props.getColumnLabel) {
    return props.getColumnLabel(columnId)
  }
  return columnId
}

const searchColumnId = props.searchColumnId || 'name'
</script>

<template>
  <div class="flex items-center py-4">
    <Input
      class="max-w-sm"
      :placeholder="searchPlaceholder || '검색...'"
      :model-value="table.getColumn(searchColumnId)?.getFilterValue() as string"
      @update:model-value="table.getColumn(searchColumnId)?.setFilterValue($event)"
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
    <slot></slot>
  </div>
</template>