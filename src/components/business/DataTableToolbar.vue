<template>
  <div class="flex items-center justify-between">
    <div class="flex flex-1 items-center space-x-2">
      <!-- Global search -->
      <Input
        :placeholder="searchPlaceholder"
        :model-value="table.getColumn(searchColumnId)?.getFilterValue() as string ?? ''"
        @update:model-value="table.getColumn(searchColumnId)?.setFilterValue($event)"
        class="h-8 w-[150px] lg:w-[250px]"
      />
      
      <!-- Additional filters slot -->
      <slot name="filters" />
    </div>
    
    <div class="flex items-center space-x-2">
      <!-- Additional actions slot -->
      <slot name="actions" />
      
      <!-- Column visibility -->
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="outline" size="sm" class="ml-auto h-8">
            <Settings class="mr-2 h-4 w-4" />
            컬럼
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="w-[200px]">
          <DropdownMenuCheckboxItem
            v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
            :key="column.id"
            class="capitalize"
            :checked="column.getIsVisible()"
            @update:checked="(value) => column.toggleVisibility(!!value)"
          >
            {{ getColumnLabel(column.id) }}
          </DropdownMenuCheckboxItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Table } from '@tanstack/vue-table';
import { Settings } from 'lucide-vue-next';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';

interface DataTableToolbarProps {
  table: Table<any>;
  searchPlaceholder?: string;
  searchColumnId?: string;
  getColumnLabel: (columnId: string) => string;
}

defineProps<DataTableToolbarProps>();
</script>