<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed, ref, onMounted } from 'vue'
import { Search, X } from 'lucide-vue-next'

import { cn } from '@/shared/utils/utils'
import { Input } from '@/core/components/ui/input'
import { Button } from '@/core/components/ui/button'

interface DataTableModernSearchProps<TData, TValue> {
  column?: Column<TData, TValue>
  placeholder?: string
}

const props = withDefaults(defineProps<DataTableModernSearchProps<any, any>>(), {
  placeholder: '검색...',
})

const inputRef = ref<HTMLInputElement>()
const isFocused = ref(false)
const isEmpty = ref(true)

const searchValue = computed({
  get: () => (props.column?.getFilterValue() as string) ?? '',
  set: (value: string) => {
    props.column?.setFilterValue(value || undefined)
    isEmpty.value = !value
  }
})

function clearSearch() {
  searchValue.value = ''
  inputRef.value?.focus()
}

function handleFocus() {
  isFocused.value = true
}

function handleBlur() {
  isFocused.value = false
}

onMounted(() => {
  isEmpty.value = !searchValue.value
})
</script>

<template>
  <div class="relative group">
    <!-- Modern search container -->
    <div 
      :class="cn(
        'relative flex items-center rounded-lg border transition-all duration-200',
        'bg-background/50 backdrop-blur-sm shadow-sm',
        isFocused 
          ? 'border-primary/60 shadow-md shadow-primary/10 bg-background' 
          : 'border-border/60 hover:border-border'
      )"
    >
      <!-- Modern search icon -->
      <div class="relative flex items-center justify-center w-10 h-9">
        <Search 
          :class="cn(
            'h-4 w-4 transition-all duration-200',
            isFocused 
              ? 'text-primary' 
              : 'text-muted-foreground'
          )" 
        />
      </div>
      
      <!-- Modern input field -->
      <Input
        ref="inputRef"
        v-model="searchValue"
        :placeholder="placeholder"
        :class="cn(
          'border-0 bg-transparent px-0 py-2 text-sm placeholder:text-muted-foreground/70',
          'focus-visible:ring-0 focus-visible:ring-offset-0 h-9',
          'transition-all duration-200'
        )"
        @focus="handleFocus"
        @blur="handleBlur"
      />
      
      <!-- Modern clear button -->
      <div 
        v-if="searchValue" 
        class="flex items-center justify-center w-10 h-9"
      >
        <Button
          variant="ghost"
          size="sm"
          :class="cn(
            'h-6 w-6 p-0 rounded-md',
            'hover:bg-muted hover:text-destructive',
            'transition-all duration-200'
          )"
          @click="clearSearch"
        >
          <X class="h-3 w-3" />
        </Button>
      </div>
    </div>
    
    <!-- Modern focus ring -->
    <div 
      :class="cn(
        'absolute inset-0 rounded-lg pointer-events-none transition-opacity duration-200',
        'ring-2 ring-primary/20',
        isFocused ? 'opacity-100' : 'opacity-0'
      )"
    />
  </div>
</template>