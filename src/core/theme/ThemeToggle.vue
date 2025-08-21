<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" size="icon" class="relative">
        <Sun
          v-if="!isSystemMode"
          class="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
        />
        <Moon
          v-if="!isSystemMode"
          class="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
        />
        <Monitor v-if="isSystemMode" class="h-[1.2rem] w-[1.2rem] transition-all" />
        <span class="sr-only">테마 변경</span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem @click="handleLightMode" :class="{ 'bg-accent': !isDark && !isSystemMode }">
        <Sun class="mr-2 h-4 w-4" />
        <span>라이트 모드</span>
        <Check v-if="!isDark && !isSystemMode" class="ml-auto h-4 w-4" />
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleDarkMode" :class="{ 'bg-accent': isDark && !isSystemMode }">
        <Moon class="mr-2 h-4 w-4" />
        <span>다크 모드</span>
        <Check v-if="isDark && !isSystemMode" class="ml-auto h-4 w-4" />
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleSystemMode" :class="{ 'bg-accent': isSystemMode }">
        <Monitor class="mr-2 h-4 w-4" />
        <span>시스템 설정</span>
        <Check v-if="isSystemMode" class="ml-auto h-4 w-4" />
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Check, Monitor, Moon, Sun } from 'lucide-vue-next';
import { useTheme } from '@/core/composables';

const { isDark, setDarkMode } = useTheme();

// 시스템 설정 모드 관리 (localStorage에서 별도 관리)
const SYSTEM_MODE_KEY = 'nsales-system-mode';
const isSystemMode = ref(localStorage.getItem(SYSTEM_MODE_KEY) === 'true');

// 시스템 다크 모드 감지
const systemDarkMode = ref(window.matchMedia('(prefers-color-scheme: dark)').matches);

// 시스템 설정 변경 감지
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  systemDarkMode.value = e.matches;
  if (isSystemMode.value) {
    setDarkMode(e.matches);
  }
});

const handleLightMode = () => {
  isSystemMode.value = false;
  localStorage.setItem(SYSTEM_MODE_KEY, 'false');
  setDarkMode(false);
};

const handleDarkMode = () => {
  isSystemMode.value = false;
  localStorage.setItem(SYSTEM_MODE_KEY, 'false');
  setDarkMode(true);
};

const handleSystemMode = () => {
  isSystemMode.value = true;
  localStorage.setItem(SYSTEM_MODE_KEY, 'true');
  setDarkMode(systemDarkMode.value);
};
</script>
