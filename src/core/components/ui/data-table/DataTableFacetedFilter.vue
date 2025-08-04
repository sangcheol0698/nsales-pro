<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed } from 'vue'
import { CheckIcon, PlusCircleIcon } from 'lucide-vue-next'

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

interface DataTableFacetedFilterProps<TData, TValue> {
  column?: Column<TData, TValue>
  title?: string
  options: {
    label: string
    value: string
    icon?: any
  }[]
}

const props = defineProps<DataTableFacetedFilterProps<any, any>>()

const facets = computed(() => props.column?.getFacetedUniqueValues())
const selectedValues = computed(() => {
  const filterValue = props.column?.getFilterValue() as string[] | undefined
  return new Set(filterValue || [])
})
</script>

<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline" size="sm" class="h-8 border-dashed">
        <PlusCircleIcon class="mr-2 h-4 w-4" />
        {{ title }}
        <template v-if="selectedValues.value.size > 0">
          <Separator orientation="vertical" class="mx-2 h-4" />
          <Badge
            variant="secondary"
            class="rounded-sm px-1 font-normal lg:hidden"
          >
            {{ selectedValues.value.size }}
          </Badge>
          <div class="hidden space-x-1 lg:flex">
            <Badge
              v-if="selectedValues.value.size > 2"
              variant="secondary"
              class="rounded-sm px-1 font-normal"
            >
              {{ selectedValues.value.size }} selected
            </Badge>
            <template v-else>
              <Badge
                v-for="option in options.filter((option) => selectedValues.value.has(option.value))"
                :key="option.value"
                variant="secondary"
                class="rounded-sm px-1 font-normal"
              >
                {{ option.label }}
              </Badge>
            </template>
          </div>
        </template>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[200px] p-0" align="start">
      <Command>
        <CommandInput :placeholder="title" />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup>
            <CommandItem
              v-for="option in options"
              :key="option.value"
              :value="option.value"
              @select="(value) => {
                const currentValues = new Set(selectedValues.value)
                if (currentValues.has(value)) {
                  currentValues.delete(value)
                } else {
                  currentValues.add(value)
                }
                const filterValues = Array.from(currentValues)
                column?.setFilterValue(
                  filterValues.length ? filterValues : undefined
                )
              }"
            >
              <div
                :class="cn(
                  'mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary',
                  selectedValues.value.has(option.value)
                    ? 'bg-primary text-primary-foreground'
                    : 'opacity-50 [&_svg]:invisible'
                )"
              >
                <CheckIcon class="h-4 w-4" />
              </div>
              <component
                v-if="option.icon"
                :is="option.icon"
                class="mr-2 h-4 w-4 text-muted-foreground"
              />
              <span>{{ option.label }}</span>
              <span
                v-if="facets?.get(option.value)"
                class="ml-auto flex h-4 w-4 items-center justify-center font-mono text-xs"
              >
                {{ facets.get(option.value) }}
              </span>
            </CommandItem>
          </CommandGroup>
          <template v-if="selectedValues.value.size > 0">
            <CommandSeparator />
            <CommandGroup>
              <CommandItem
                :value="''"
                class="justify-center text-center"
                @select="column?.setFilterValue(undefined)"
              >
                Clear filters
              </CommandItem>
            </CommandGroup>
          </template>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>