<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed, ref } from 'vue'
import { Check, Plus, X } from 'lucide-vue-next'

import { cn } from '@/shared/utils/utils'
import { Badge } from '@/core/components/ui/badge'
import { Button } from '@/core/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/core/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/core/components/ui/popover'
import { Separator } from '@/core/components/ui/separator'

interface DataTableModernFilterProps<TData, TValue> {
  column?: Column<TData, TValue>
  title?: string
  options: {
    label: string
    value: string
    icon?: any
    color?: string
  }[]
}

const props = defineProps<DataTableModernFilterProps<any, any>>()

const isOpen = ref(false)
const facets = computed(() => props.column?.getFacetedUniqueValues())
const selectedValues = computed(() => {
  const filterValue = props.column?.getFilterValue() as string[] | undefined
  return new Set(filterValue || [])
})

function toggleOption(value: string) {
  const currentValues = new Set(selectedValues.value)
  if (currentValues.has(value)) {
    currentValues.delete(value)
  } else {
    currentValues.add(value)
  }
  const filterValues = Array.from(currentValues)
  props.column?.setFilterValue(
    filterValues.length ? filterValues : undefined
  )
}

function clearFilters() {
  props.column?.setFilterValue(undefined)
}
</script>

<template>
  <Popover v-model:open="isOpen">
    <PopoverTrigger as-child>
      <Button 
        variant="outline" 
        size="sm" 
        :class="cn(
          'h-9 px-3 border-dashed transition-all duration-200 group relative',
          selectedValues.size > 0 
            ? 'border-primary/60 bg-primary/5 text-primary shadow-sm' 
            : 'border-border/60 hover:border-primary/50 hover:bg-primary/5'
        )"
      >
        <div class="flex items-center gap-2">
          <Plus 
            :class="cn(
              'h-4 w-4 transition-all duration-200',
              selectedValues.size > 0 
                ? 'text-primary' 
                : 'text-muted-foreground group-hover:text-primary'
            )" 
          />
          <span :class="cn(
            'text-sm font-medium transition-colors duration-200',
            selectedValues.size > 0 ? 'text-primary' : 'text-foreground/70'
          )">
            {{ title }}
          </span>
          
          <template v-if="selectedValues.size > 0">
            <Separator orientation="vertical" class="h-4" />
            <Badge
              variant="secondary"
              :class="cn(
                'h-5 px-1.5 text-xs font-medium rounded-md lg:hidden',
                'bg-primary/15 text-primary border-0'
              )"
            >
              {{ selectedValues.size }}
            </Badge>
            <div class="hidden lg:flex items-center gap-1">
              <Badge
                v-if="selectedValues.size > 2"
                variant="secondary"
                :class="cn(
                  'h-5 px-1.5 text-xs font-medium rounded-md',
                  'bg-primary/15 text-primary border-0'
                )"
              >
                {{ selectedValues.size }} 선택됨
              </Badge>
              <template v-else>
                <Badge
                  v-for="option in options.filter((option) => selectedValues.has(option.value))"
                  :key="option.value"
                  variant="secondary"
                  :class="cn(
                    'h-5 px-1.5 text-xs font-medium rounded-md',
                    'bg-primary/15 text-primary border-0'
                  )"
                >
                  {{ option.label }}
                </Badge>
              </template>
            </div>
          </template>
        </div>
      </Button>
    </PopoverTrigger>
    
    <PopoverContent 
      class="w-64 p-0 border-border/60 shadow-xl" 
      align="start"
    >
      <Command class="rounded-lg">
        <CommandInput 
          :placeholder="`${title} 검색...`" 
          class="h-9 border-0 focus:ring-0"
        />
        <CommandList>
          <CommandEmpty class="py-6 text-center text-sm text-muted-foreground">
            검색 결과가 없습니다.
          </CommandEmpty>
          <CommandGroup class="p-2">
            <CommandItem
              v-for="option in options"
              :key="option.value"
              :value="option.value"
              :class="cn(
                'flex items-center space-x-2 rounded-md px-2 py-2 text-sm cursor-pointer',
                'hover:bg-primary/5 hover:text-primary transition-all duration-150',
                'aria-selected:bg-primary/10 aria-selected:text-primary'
              )"
              @select="toggleOption(option.value)"
            >
              <div
                :class="cn(
                  'flex h-4 w-4 items-center justify-center rounded border transition-all duration-150',
                  selectedValues.has(option.value)
                    ? 'bg-primary text-primary-foreground border-primary shadow-sm'
                    : 'border-muted-foreground/40 hover:border-primary/60'
                )"
              >
                <Check 
                  :class="cn(
                    'h-3 w-3 transition-all duration-150',
                    selectedValues.has(option.value) 
                      ? 'opacity-100 scale-100' 
                      : 'opacity-0 scale-75'
                  )" 
                />
              </div>
              
              <component
                v-if="option.icon"
                :is="option.icon"
                class="h-4 w-4 text-muted-foreground"
              />
              
              <span class="flex-1 font-medium">{{ option.label }}</span>
              
              <Badge
                v-if="facets?.get(option.value)"
                variant="secondary"
                :class="cn(
                  'h-5 px-1.5 text-xs font-mono rounded-md',
                  'bg-muted/50 text-muted-foreground border-0',
                  selectedValues.has(option.value) && 'bg-primary/15 text-primary'
                )"
              >
                {{ facets.get(option.value) }}
              </Badge>
            </CommandItem>
          </CommandGroup>
          
          <template v-if="selectedValues.size > 0">
            <CommandSeparator class="mx-2" />
            <CommandGroup class="p-2">
              <CommandItem
                value=""
                :class="cn(
                  'flex items-center justify-center rounded-md px-2 py-2 text-sm cursor-pointer',
                  'text-muted-foreground hover:text-destructive hover:bg-destructive/5',
                  'transition-all duration-150'
                )"
                @select="clearFilters"
              >
                <X class="mr-2 h-3 w-3" />
                필터 초기화
              </CommandItem>
            </CommandGroup>
          </template>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>