<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed, ref, onMounted } from 'vue'
import { Search, X, Sparkles } from 'lucide-vue-next'

import { cn } from '@/shared/utils/utils'
import { Input } from '@/core/components/ui/input'
import { Button } from '@/core/components/ui/button'

interface DataTableMagicSearchProps<TData, TValue> {
  column?: Column<TData, TValue>
  placeholder?: string
}

const props = withDefaults(defineProps<DataTableMagicSearchProps<any, any>>(), {
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
    <!-- Magic background gradient -->
    <div 
      :class="cn(
        'absolute inset-0 rounded-md transition-all duration-300',
        'bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10',
        'opacity-0 group-hover:opacity-100 blur-sm'
      )"
    />
    
    <!-- Input container with border animation -->
    <div 
      :class="cn(
        'relative flex items-center rounded-md border transition-all duration-300',
        'bg-background/95 backdrop-blur-sm',
        isFocused 
          ? 'border-primary shadow-lg shadow-primary/20 ring-2 ring-primary/10' 
          : 'border-input hover:border-primary/50'
      )"
    >
      <!-- Search icon with animation -->
      <div class="relative pl-3">
        <Search 
          :class="cn(
            'h-4 w-4 transition-all duration-300',
            isFocused 
              ? 'text-primary scale-110' 
              : 'text-muted-foreground group-hover:text-primary'
          )" 
        />
        
        <!-- Sparkle effect on focus -->
        <Sparkles 
          :class="cn(
            'absolute inset-0 h-4 w-4 text-primary transition-all duration-500',
            isFocused && !isEmpty 
              ? 'opacity-100 animate-pulse scale-125' 
              : 'opacity-0 scale-75'
          )" 
        />
      </div>
      
      <!-- Input field -->
      <Input
        ref="inputRef"
        v-model="searchValue"
        :placeholder="placeholder"
        :class="cn(
          'border-0 bg-transparent px-2 py-2 text-sm placeholder:text-muted-foreground',
          'focus-visible:ring-0 focus-visible:ring-offset-0',
          'transition-all duration-300'
        )"
        @focus="handleFocus"
        @blur="handleBlur"
      />
      
      <!-- Clear button with magic effect -->
      <div 
        v-if="searchValue" 
        class="relative pr-2"
      >
        <Button
          variant="ghost"
          size="sm"
          :class="cn(
            'h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive',
            'transition-all duration-200 hover:scale-110'
          )"
          @click="clearSearch"
        >
          <X class="h-3 w-3" />
        </Button>
      </div>
    </div>
    
    <!-- Magic cursor follower -->
    <div 
      :class="cn(
        'absolute inset-0 rounded-md pointer-events-none transition-opacity duration-300',
        'bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5',
        isFocused ? 'opacity-100' : 'opacity-0'
      )"
    />
  </div>
</template>