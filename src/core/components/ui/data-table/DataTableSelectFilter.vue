<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed } from 'vue'
import { CheckIcon, PlusCircleIcon } from 'lucide-vue-next'

import { Button } from '@/core/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/core/components/ui/select'

interface DataTableSelectFilterProps<TData, TValue> {
  column?: Column<TData, TValue>
  title?: string
  placeholder?: string
  options: {
    label: string
    value: string
  }[]
}

const props = withDefaults(defineProps<DataTableSelectFilterProps<any, any>>(), {
  title: '선택',
  placeholder: '선택하세요',
})

const selectedValue = computed(() => props.column?.getFilterValue() as string | undefined)

function handleValueChange(value: string) {
  if (value === 'all') {
    props.column?.setFilterValue(undefined)
  } else {
    props.column?.setFilterValue(value)
  }
}
</script>

<template>
  <Select :model-value="selectedValue || 'all'" @update:model-value="handleValueChange">
    <SelectTrigger class="h-8 w-[150px] border-dashed">
      <SelectValue :placeholder="title" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="all">
        전체
      </SelectItem>
      <SelectItem
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </SelectItem>
    </SelectContent>
  </Select>
</template>