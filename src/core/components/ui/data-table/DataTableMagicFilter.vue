<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed, ref } from 'vue'
import { CheckIcon, Sparkles } from 'lucide-vue-next'

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

interface DataTableMagicFilterProps<TData, TValue> {
  column?: Column<TData, TValue>
  title?: string
  options: {
    label: string
    value: string
    icon?: any
    color?: string
  }[]
}

const props = defineProps<DataTableMagicFilterProps<any, any>>()

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
          'h-8 border-dashed transition-all duration-300 group relative overflow-hidden',
          selectedValues.size > 0 
            ? 'border-primary bg-primary/5 shadow-md' 
            : 'hover:border-primary/50'
        )"
      >
        <!-- Magic sparkle effect -->
        <div 
          :class="cn(
            'absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-300',
            'bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-pink-500/20'
          )"
        />
        
        <div class="relative flex items-center">
          <Sparkles 
            :class="cn(
              'mr-2 h-4 w-4 transition-all duration-300',
              selectedValues.size > 0 
                ? 'text-primary animate-pulse' 
                : 'text-muted-foreground group-hover:text-primary'
            )" 
          />
          <span :class="cn(
            'transition-colors duration-300',
            selectedValues.size > 0 ? 'text-primary font-medium' : ''
          )">
            {{ title }}
          </span>
          
          <template v-if="selectedValues.size > 0">
            <Separator orientation="vertical" class="mx-2 h-4" />
            <Badge
              variant="secondary"
              :class="cn(
                'rounded-sm px-1 font-normal lg:hidden',
                'bg-primary/10 text-primary border-primary/20'
              )"
            >
              {{ selectedValues.size }}
            </Badge>
            <div class="hidden space-x-1 lg:flex">
              <Badge
                v-if="selectedValues.size > 2"
                variant="secondary"
                :class="cn(
                  'rounded-sm px-1 font-normal',
                  'bg-primary/10 text-primary border-primary/20'
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
                    'rounded-sm px-1 font-normal',
                    'bg-primary/10 text-primary border-primary/20'
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
      class="w-[250px] p-0 border-2 shadow-2xl" 
      align="start"
    >
      <!-- Magic glow effect -->
      <div class="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-pink-500/5 rounded-lg" />
      
      <Command class="relative">
        <CommandInput 
          :placeholder="`${title} 검색...`" 
          class="border-none focus:ring-0"
        />
        <CommandList>
          <CommandEmpty>결과가 없습니다.</CommandEmpty>
          <CommandGroup>
            <CommandItem
              v-for="option in options"
              :key="option.value"
              :value="option.value"
              :class="cn(
                'cursor-pointer transition-all duration-200',
                'hover:bg-gradient-to-r hover:from-primary/5 hover:to-primary/10'
              )"
              @select="toggleOption(option.value)"
            >
              <div
                :class="cn(
                  'mr-2 flex h-4 w-4 items-center justify-center rounded-sm border transition-all duration-200',
                  selectedValues.has(option.value)
                    ? 'bg-primary text-primary-foreground border-primary shadow-lg scale-110'
                    : 'border-muted-foreground/50 hover:border-primary/50'
                )"
              >
                <CheckIcon 
                  :class="cn(
                    'h-4 w-4 transition-all duration-200',
                    selectedValues.has(option.value) 
                      ? 'opacity-100 scale-100' 
                      : 'opacity-0 scale-75'
                  )" 
                />
              </div>
              
              <component
                v-if="option.icon"
                :is="option.icon"
                class="mr-2 h-4 w-4 text-muted-foreground"
              />
              
              <span class="flex-1">{{ option.label }}</span>
              
              <span
                v-if="facets?.get(option.value)"
                :class="cn(
                  'ml-auto flex h-4 w-4 items-center justify-center font-mono text-xs',
                  'rounded-full bg-muted text-muted-foreground transition-colors duration-200',
                  selectedValues.has(option.value) && 'bg-primary/20 text-primary'
                )"
              >
                {{ facets.get(option.value) }}
              </span>
            </CommandItem>
          </CommandGroup>
          
          <template v-if="selectedValues.size > 0">
            <CommandSeparator />
            <CommandGroup>
              <CommandItem
                value=""
                :class="cn(
                  'justify-center text-center cursor-pointer',
                  'hover:bg-destructive/5 hover:text-destructive transition-colors duration-200'
                )"
                @select="clearFilters"
              >
                필터 초기화
              </CommandItem>
            </CommandGroup>
          </template>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>