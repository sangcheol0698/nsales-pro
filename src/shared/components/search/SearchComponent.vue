<template>
  <!-- Search Button with Keyboard Shortcut -->
  <Button
    variant="outline"
    class="relative text-sm text-muted-foreground"
    @click="isCommandDialogOpen = true"
  >
    <Search class="mr-2 h-4 w-4" />
    <span>검색</span>
    <kbd
      class="pointer-events-none absolute right-1.5 top-1.5 hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex"
    >
      <span class="text-xs">{{ isMac ? '⌘' : 'Ctrl' }}</span
      >K
    </kbd>
  </Button>

  <CommandDialog modal :open="isCommandDialogOpen" @open-change="setIsCommandDialogOpen">
    <CommandInput placeholder="페이지 또는 프로젝트 검색..." v-model="searchQuery" />
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

      <!-- Projects -->
      <CommandGroup heading="프로젝트">
        <div v-if="isLoadingProjects" class="py-6 text-center text-sm text-muted-foreground">
          프로젝트 로딩 중...
        </div>
        <template v-else>
          <CommandItem
            v-for="project in filteredProjects"
            :key="project.id"
            :value="project.id"
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
</template>

<script setup lang="ts">
import { Button } from '@/core/components/ui/button';
import {
  Building2,
  FileBarChart2,
  FileText,
  LayoutDashboard,
  Search,
  Users,
  Wallet,
} from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import { computed, ref } from 'vue';
import { useEventListener } from '@vueuse/core';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/core/components/ui/command';
import { container } from 'tsyringe';
import ProjectRepository from '@/features/project/repository/ProjectRepository';
import type { ProjectSearch } from '@/features/project/entity/ProjectSearch';

const router = useRouter();
const PROJECT_REPOSITORY = container.resolve(ProjectRepository);

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

// Command dialog state
const isCommandDialogOpen = ref(false);
const searchQuery = ref('');

const setIsCommandDialogOpen = (open: boolean) => {
  isCommandDialogOpen.value = open;

  // Reset search query when dialog is closed
  if (!open) {
    searchQuery.value = '';
  } else {
    // Fetch projects when dialog is opened
    fetchProjects();
  }
};

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

// Filter pages based on search query
const filteredPages = computed(() => {
  if (!searchQuery.value) return navigationPages;
  return navigationPages.filter((page) =>
    page.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Filter projects based on search query
const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value;
  return projects.value.filter((project) =>
    project.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Navigate to page or project
const navigateTo = (url: string) => {
  router.push(url);
  isCommandDialogOpen.value = false;
};

// Detect if user is on Mac for keyboard shortcut display
const isMac = ref(navigator.platform.toUpperCase().indexOf('MAC') >= 0);

// Keyboard shortcut for command dialog (Cmd/Ctrl + K) and esc to close
useEventListener('keydown', (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    isCommandDialogOpen.value = !isCommandDialogOpen.value;
  }
  if (e.key === 'Escape') {
    isCommandDialogOpen.value = false;
  }
});
</script>