<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" size="icon" class="relative">
        <Sun v-if="theme !== 'system'" class="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
        <Moon v-if="theme !== 'system'" class="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        <Monitor v-if="theme === 'system'" class="h-[1.2rem] w-[1.2rem] transition-all" />
        <span class="sr-only">테마 변경</span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem @click="setTheme('light')" :class="{ 'bg-accent': theme === 'light' }">
        <Sun class="mr-2 h-4 w-4" />
        <span>라이트 모드</span>
        <Check v-if="theme === 'light'" class="ml-auto h-4 w-4" />
      </DropdownMenuItem>
      <DropdownMenuItem @click="setTheme('dark')" :class="{ 'bg-accent': theme === 'dark' }">
        <Moon class="mr-2 h-4 w-4" />
        <span>다크 모드</span>
        <Check v-if="theme === 'dark'" class="ml-auto h-4 w-4" />
      </DropdownMenuItem>
      <DropdownMenuItem @click="setTheme('system')" :class="{ 'bg-accent': theme === 'system' }">
        <Monitor class="mr-2 h-4 w-4" />
        <span>시스템 설정</span>
        <Check v-if="theme === 'system'" class="ml-auto h-4 w-4" />
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup lang="ts">
import { Button } from '@/core/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu';
import { Check, Moon, Monitor, Sun } from 'lucide-vue-next';
import { useTheme } from '@/composables';

const { theme, setTheme } = useTheme();
</script>
