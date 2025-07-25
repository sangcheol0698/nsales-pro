<template>
  <div>
    <Button
      variant="outline"
      :class="'bg-muted/25 text-muted-foreground hover:bg-muted/50 relative  w-full flex-1 justify-start rounded-md text-sm font-normal shadow-none sm:pr-12 md:w-40 md:flex-none lg:w-56 xl:w-64'"
      @click="handleOpenChange"
    >
      <Search aria-hidden="true" class="absolute top-1/2 left-1.5 -translate-y-1/2 h-4 w-4" />
      <span class="ml-3">검색</span>
      <kbd
        class="bg-muted pointer-events-none absolute top-[0.3rem] right-[0.3rem] hidden h-6 items-center gap-1 rounded border px-1.5 font-mono text-[10px] font-medium opacity-100 select-none sm:flex"
      >
        <span class="text-xs">{{ isMac ? '⌘' : 'Ctrl' }}</span
        >K
      </kbd>
    </Button>
    <CommandDialog v-model:open="open" modal>
      <CommandInput placeholder="검색" v-model="searchQuery" />
      <CommandList>
        <CommandEmpty>검색 결과가 없습니다.</CommandEmpty>

        <!-- Pages -->
        <CommandGroup heading="페이지">
          <CommandItem
            v-for="page in filteredPages"
            :key="page.url"
            :value="page.url"
            @click="navigateTo(page.url)"
            class="flex items-center"
          >
            <component :is="page.icon" class="mr-2 h-4 w-4 text-muted-foreground" />
            <span>{{ page.title }}</span>
          </CommandItem>
        </CommandGroup>

        <CommandSeparator />

        <!-- Projects -->
        <CommandGroup heading="프로젝트">
          <div v-if="isLoadingProjects" class="py-6 text-center text-sm text-muted-foreground">
            프로젝트 로딩 중...
          </div>
          <template v-else>
            <CommandItem
              v-for="project in filteredProjects"
              :key="project.id"
              :value="project.id.toString()"
              @click="navigateTo(`/projects/${project.id}`)"
              class="flex items-center"
            >
              <FileText class="mr-2 h-4 w-4 text-muted-foreground" />
              <span>{{ project.name }}</span>
            </CommandItem>
            <div
              v-if="filteredProjects.length === 0 && !isLoadingProjects && searchQuery"
              class="py-6 text-center text-sm text-muted-foreground"
            >
              일치하는 프로젝트가 없습니다.
            </div>
          </template>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  </div>
</template>

<script setup lang="ts">
import { useMagicKeys } from '@vueuse/core';

import { computed, ref, watch } from 'vue';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/core/components/ui/command';
import Hangul from 'hangul-js';
import {
  Building2,
  FileBarChart2,
  FileText,
  LayoutDashboard,
  Search,
  Users,
  Wallet,
} from 'lucide-vue-next';
import { Button } from '@/core/components/ui/button';
import { useRouter } from 'vue-router';
import { container } from 'tsyringe';
import ProjectRepository from '@/features/project/repository/ProjectRepository';
import type { ProjectSearch } from '@/features/project/entity/ProjectSearch';

const router = useRouter();
const PROJECT_REPOSITORY = container.resolve(ProjectRepository);

// Detect if user is on Mac for keyboard shortcut display
const isMac = ref(navigator.platform.toUpperCase().indexOf('MAC') >= 0);

// Command dialog state
const open = ref(false);
const searchQuery = ref('');

// Navigation pages for search
const navigationPages = [
  { title: '대시보드', url: '/', icon: LayoutDashboard },
  { title: '프로젝트', url: '/projects', icon: FileText },
  { title: '구성원', url: '/employees', icon: Users },
  { title: '협력사', url: '/partners', icon: Building2 },
  { title: '매출', url: '/sales', icon: Wallet },
  { title: '공지사항', url: '/notices', icon: FileBarChart2 },
];

// Projects for search
const projects = ref<ProjectSearch[]>([]);
const isLoadingProjects = ref(false);

const { Meta_K, Ctrl_K, Escape } = useMagicKeys({
  passive: false,
  onEventFired(e) {
    if (e.key === 'k' && (e.metaKey || e.ctrlKey)) e.preventDefault();
  },
});

watch([Meta_K, Ctrl_K], (v) => {
  if (v[0] || v[1]) handleOpenChange();
});

// Close dialog when Escape key is pressed
watch(Escape, (v) => {
  if (v && open.value) open.value = false;
});

function handleOpenChange() {
  open.value = !open.value;

  // Reset search query when dialog is closed
  if (!open.value) {
    searchQuery.value = '';
  } else {
    // Fetch projects when dialog is opened
    fetchProjects();
  }
}

// Fetch projects for search
const fetchProjects = async () => {
  isLoadingProjects.value = true;
  try {
    const response = await PROJECT_REPOSITORY.getProjects({ limit: 20 });
    projects.value = response.content;
  } catch (error) {
    console.error('Error fetching projects:', error);
  } finally {
    isLoadingProjects.value = false;
  }
};

// Helper function for Korean and English text search
const containsKorean = (text: string, query: string): boolean => {
  if (!text || !query) return false;

  // Convert to lowercase for case-insensitive English search
  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();

  // Check if the text contains the query (case-insensitive)
  if (lowerText.includes(lowerQuery)) {
    return true;
  }

  // Split text into words and check each word with Hangul.js for Korean
  const words = text.split(/\s+/);
  for (const word of words) {
    if (Hangul.search(word, query) >= 0) {
      return true;
    }
  }

  // If no match found in individual words, check the entire text with Hangul.js
  return Hangul.search(text, query) >= 0;
};

// Filter pages based on search query
const filteredPages = computed(() => {
  if (!searchQuery.value) return navigationPages;
  return navigationPages.filter((page) => containsKorean(page.title, searchQuery.value));
});

// Filter projects based on search query
const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value;
  return projects.value.filter((project) => containsKorean(project.name, searchQuery.value));
});

// Navigate to page or project
const navigateTo = (url: string) => {
  router.push(url);
  open.value = false;
};
</script>
