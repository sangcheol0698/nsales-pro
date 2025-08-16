<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-2xl">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Settings class="h-5 w-5" />
          설정
        </DialogTitle>
        <DialogDescription>
          애플리케이션 설정을 관리합니다.
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-6 py-4">
        <!-- 테마 설정 -->
        <div class="space-y-3">
          <h3 class="text-sm font-medium">테마</h3>
          <div class="flex items-center space-x-4">
            <Button
              variant="outline"
              size="sm"
              @click="setTheme('light')"
              :class="currentTheme === 'light' ? 'bg-primary text-primary-foreground' : ''"
            >
              <Sun class="mr-2 h-4 w-4" />
              라이트
            </Button>
            <Button
              variant="outline"
              size="sm"
              @click="setTheme('dark')"
              :class="currentTheme === 'dark' ? 'bg-primary text-primary-foreground' : ''"
            >
              <Moon class="mr-2 h-4 w-4" />
              다크
            </Button>
            <Button
              variant="outline"
              size="sm"
              @click="setTheme('system')"
              :class="currentTheme === 'system' ? 'bg-primary text-primary-foreground' : ''"
            >
              <Monitor class="mr-2 h-4 w-4" />
              시스템
            </Button>
          </div>
        </div>

        <Separator />

        <!-- 언어 설정 -->
        <div class="space-y-3">
          <h3 class="text-sm font-medium">언어</h3>
          <Select v-model="selectedLanguage">
            <SelectTrigger class="w-48">
              <SelectValue placeholder="언어를 선택하세요" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ko">한국어</SelectItem>
              <SelectItem value="en">English</SelectItem>
              <SelectItem value="ja">日本語</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Separator />

        <!-- 알림 설정 -->
        <div class="space-y-3">
          <h3 class="text-sm font-medium">알림</h3>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <div class="space-y-0.5">
                <label class="text-sm font-medium">데스크톱 알림</label>
                <p class="text-xs text-muted-foreground">새로운 메시지나 업데이트에 대한 알림을 받습니다.</p>
              </div>
              <Checkbox v-model:checked="desktopNotifications" />
            </div>
            <div class="flex items-center justify-between">
              <div class="space-y-0.5">
                <label class="text-sm font-medium">이메일 알림</label>
                <p class="text-xs text-muted-foreground">중요한 업데이트를 이메일로 받습니다.</p>
              </div>
              <Checkbox v-model:checked="emailNotifications" />
            </div>
          </div>
        </div>

        <Separator />

        <!-- 사이드바 설정 -->
        <div class="space-y-3">
          <h3 class="text-sm font-medium">사이드바</h3>
          <div class="flex items-center justify-between">
            <div class="space-y-0.5">
              <label class="text-sm font-medium">사이드바 자동 접기</label>
              <p class="text-xs text-muted-foreground">화면이 작을 때 자동으로 사이드바를 접습니다.</p>
            </div>
            <Checkbox v-model:checked="autoCollapseSidebar" />
          </div>
        </div>

        <Separator />

        <!-- 키보드 단축키 -->
        <div class="space-y-3">
          <h3 class="text-sm font-medium">키보드 단축키</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span>Command Palette 열기</span>
              <kbd
                class="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
                <span class="text-xs">⌘</span>K
              </kbd>
            </div>
            <div class="flex justify-between">
              <span>새 프로젝트</span>
              <kbd
                class="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
                <span class="text-xs">⌘</span>N
              </kbd>
            </div>
            <div class="flex justify-between">
              <span>페이지 새로고침</span>
              <kbd
                class="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
                <span class="text-xs">⌘</span>R
              </kbd>
            </div>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">
          취소
        </Button>
        <Button @click="saveSettings">
          저장
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useTheme } from '@/core/composables/useTheme';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Monitor, Moon, Settings, Sun } from 'lucide-vue-next';

interface Props {
  open: boolean;
}

defineProps<Props>();
const emit = defineEmits<{
  'update:open': [open: boolean];
}>();

const { theme, setTheme } = useTheme();

// 현재 테마 상태
const currentTheme = computed(() => theme.value);

// 설정 상태
const selectedLanguage = ref('ko');
const desktopNotifications = ref(true);
const emailNotifications = ref(false);
const autoCollapseSidebar = ref(true);

// 설정 로드
onMounted(() => {
  loadSettings();
});

// 로컬 스토리지에서 설정 로드
function loadSettings() {
  const settings = localStorage.getItem('nsales-settings');
  if (settings) {
    try {
      const parsed = JSON.parse(settings);
      selectedLanguage.value = parsed.language || 'ko';
      desktopNotifications.value = parsed.desktopNotifications ?? true;
      emailNotifications.value = parsed.emailNotifications ?? false;
      autoCollapseSidebar.value = parsed.autoCollapseSidebar ?? true;
    } catch (error) {
      console.error('설정 로드 중 오류:', error);
    }
  }
}

// 설정 저장
function saveSettings() {
  const settings = {
    language: selectedLanguage.value,
    desktopNotifications: desktopNotifications.value,
    emailNotifications: emailNotifications.value,
    autoCollapseSidebar: autoCollapseSidebar.value,
    theme: currentTheme.value,
  };

  localStorage.setItem('nsales-settings', JSON.stringify(settings));

  // 성공 알림 (나중에 toast로 변경)
  console.log('설정이 저장되었습니다.');

  emit('update:open', false);
}
</script>