<template>
  <CommandDialog :open="open" @update:open="$emit('update:open', $event)">
    <CommandInput placeholder="명령어를 입력하거나 검색하세요..." />
    <CommandList>
      <CommandEmpty>검색 결과가 없습니다.</CommandEmpty>
      
      <!-- 빠른 작업 그룹 -->
      <CommandGroup heading="빠른 작업">
        <CommandItem
          v-for="action in quickActions"
          :key="action.title"
          :value="`action-${action.title}`"
          @select="executeAction(action)"
        >
          <component :is="action.icon" class="mr-2 h-4 w-4" />
          <span>{{ action.title }}</span>
          <CommandShortcut v-if="action.shortcut">{{ action.shortcut }}</CommandShortcut>
        </CommandItem>
      </CommandGroup>
      
      <CommandSeparator />
      
      <!-- 페이지 이동 그룹 -->
      <CommandGroup heading="페이지 이동">
        <CommandItem
          v-for="page in pages"
          :key="page.title"
          :value="`page-${page.title}`"
          @select="executeAction(page)"
        >
          <component :is="page.icon" class="mr-2 h-4 w-4" />
          <span>{{ page.title }}</span>
          <span v-if="page.path" class="ml-auto text-xs text-muted-foreground">{{ page.path }}</span>
        </CommandItem>
      </CommandGroup>
    </CommandList>
  </CommandDialog>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@/components/ui/command';
import {
  LayoutDashboard,
  Users,
  FileText,
  Building2,
  Wallet,
  Settings,
  HelpCircle,
  Plus,
  RefreshCw,
} from 'lucide-vue-next';

interface Props {
  open: boolean;
  onOpenSettings?: () => void;
}

interface CommandAction {
  title: string;
  description?: string;
  icon: any;
  action: () => void;
  path?: string;
  shortcut?: string;
  keywords?: string[];
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:open': [open: boolean];
}>();

const router = useRouter();

// 빠른 작업들
const quickActions: CommandAction[] = [
  {
    title: '페이지 새로고침',
    icon: RefreshCw,
    shortcut: '⌘R',
    action: () => window.location.reload(),
    keywords: ['새로고침', 'refresh', 'reload'],
  },
  {
    title: '새 프로젝트 추가',
    icon: Plus,
    shortcut: '⌘N',
    action: () => router.push('/projects/new'),
    keywords: ['새로운', '프로젝트', 'new', 'project', '추가', 'add'],
  },
  {
    title: '설정',
    icon: Settings,
    shortcut: '⌘,',
    action: () => props.onOpenSettings?.(),
    keywords: ['설정', 'settings', 'config', 'preferences'],
  },
  {
    title: '도움말',
    icon: HelpCircle,
    shortcut: '⌘?',
    action: () => console.log('도움말 열기'),
    keywords: ['도움말', 'help', '가이드', 'guide', '매뉴얼', 'manual'],
  },
];

// 페이지 목록
const pages: CommandAction[] = [
  {
    title: '대시보드',
    icon: LayoutDashboard,
    path: '/',
    action: () => router.push('/'),
    keywords: ['대시보드', 'dashboard', 'home'],
  },
  {
    title: '프로젝트',
    icon: FileText,
    path: '/projects',
    action: () => router.push('/projects'),
    keywords: ['프로젝트', 'project', 'projects'],
  },
  {
    title: '구성원',
    icon: Users,
    path: '/employees',
    action: () => router.push('/employees'),
    keywords: ['구성원', '직원', 'employee', 'employees', 'members'],
  },
  {
    title: '협력사',
    icon: Building2,
    path: '/partners',
    action: () => router.push('/partners'),
    keywords: ['협력사', '파트너', 'partner', 'partners'],
  },
  {
    title: '매출',
    icon: Wallet,
    path: '/sales',
    action: () => router.push('/sales'),
    keywords: ['매출', 'sales', 'revenue'],
  },
];

// 명령어 실행
function executeAction(action: CommandAction) {
  action.action();
  emit('update:open', false);
}
</script>