<template>
  <Button variant="outline" size="icon" class="relative" @click="toggleTheme">
    <Sun
      class="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
    />
    <Moon
      class="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
    />
    <span class="sr-only">테마 변경</span>
  </Button>
</template>

<script setup lang="ts">
import { Button } from '@/core/components/ui/button';
import { Moon, Sun } from 'lucide-vue-next';
import { useTheme } from '@/core/composables';

const { toggleTheme } = useTheme();
</script>
