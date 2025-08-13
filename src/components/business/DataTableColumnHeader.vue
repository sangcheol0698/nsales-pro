<template>
  <div v-if="!column.getCanSort()" class="flex items-center space-x-2">
    <span>{{ title }}</span>
  </div>
  
  <DropdownMenu v-else>
    <DropdownMenuTrigger as-child>
      <Button
        variant="ghost"
        size="sm"
        class="-ml-3 h-8 data-[state=open]:bg-accent"
      >
        <span>{{ title }}</span>
        <template v-if="column.getIsSorted() === 'desc'">
          <ArrowDown class="ml-2 h-4 w-4" />
        </template>
        <template v-else-if="column.getIsSorted() === 'asc'">
          <ArrowUp class="ml-2 h-4 w-4" />
        </template>
        <template v-else>
          <ArrowUpDown class="ml-2 h-4 w-4" />
        </template>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start">
      <DropdownMenuItem @click="column.toggleSorting(false)">
        <ArrowUp class="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
        오름차순
      </DropdownMenuItem>
      <DropdownMenuItem @click="column.toggleSorting(true)">
        <ArrowDown class="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
        내림차순
      </DropdownMenuItem>
      <DropdownMenuItem @click="column.clearSorting()">
        <ArrowUpDown class="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
        정렬 해제
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup lang="ts">
import type { Column } from '@tanstack/vue-table';
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Props {
  column: Column<any>;
  title: string;
}

defineProps<Props>();
</script>