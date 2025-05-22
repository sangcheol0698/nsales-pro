<template>
  <SidebarMenu>
    <SidebarMenuItem>
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <SidebarMenuButton
            size="lg"
            class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
          >
            <Avatar class="h-8 w-8 rounded-lg">
              <AvatarImage :src="user.avatar" :alt="user.name" />
              <AvatarFallback class="rounded-lg"> CN</AvatarFallback>
            </Avatar>
            <div class="grid flex-1 text-left text-sm leading-tight">
              <span class="truncate font-semibold">{{ user.name }}</span>
              <span class="truncate text-xs">{{ user.email }}</span>
            </div>
            <ChevronsUpDown class="ml-auto size-4" />
          </SidebarMenuButton>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          class="w-[--reka-dropdown-menu-trigger-width] min-w-56 rounded-lg"
          :side="isMobile ? 'bottom' : 'right'"
          align="end"
          :side-offset="4"
        >
          <DropdownMenuLabel class="p-0 font-normal">
            <div class="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
              <Avatar class="h-8 w-8 rounded-lg">
                <AvatarImage :src="user.avatar" :alt="user.name" />
                <AvatarFallback class="rounded-lg"> CN</AvatarFallback>
              </Avatar>
              <div class="grid flex-1 text-left text-sm leading-tight">
                <span class="truncate font-semibold">{{ user.name }}</span>
                <span class="truncate text-xs">{{ user.email }}</span>
              </div>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem>
              <Sparkles />
              Upgrade to Pro
            </DropdownMenuItem>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem>
              <BadgeCheck />
              Account
            </DropdownMenuItem>
            <DropdownMenuItem>
              <CreditCard />
              Billing
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Bell />
              Notifications
            </DropdownMenuItem>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <Sun v-if="theme !== 'system' && effectiveTheme === 'light'" />
                <Moon v-if="theme !== 'system' && effectiveTheme === 'dark'" />
                <Monitor v-if="theme === 'system'" />
                테마 설정
              </DropdownMenuSubTrigger>
              <DropdownMenuPortal>
                <DropdownMenuSubContent>
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
                </DropdownMenuSubContent>
              </DropdownMenuPortal>
            </DropdownMenuSub>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuItem @click="handleLogout">
            <LogOut />
            로그아웃
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  </SidebarMenu>
</template>

<script setup lang="ts">
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';
import { BadgeCheck, Bell, Check, ChevronsUpDown, CreditCard, LogOut, Monitor, Moon, Sparkles, Sun } from 'lucide-vue-next';
import { container } from 'tsyringe';
import AuthRepository from '@/repository/AuthRepository.ts';
import { useRouter } from 'vue-router';
import type HttpError from '@/http/HttpError.ts';
import { useAlertDialog, useTheme, useToast } from '@/composables';

const props = defineProps<{
  user: {
    name: string;
    email: string;
    avatar: string;
  };
}>();

const router = useRouter();
const toast = useToast();
const alertDialog = useAlertDialog();
const { theme, effectiveTheme, setTheme, toggleTheme } = useTheme();

const AUTH_REPOSITORY = container.resolve(AuthRepository);
const handleLogout = async () => {
  alertDialog.open({
    title: '로그아웃',
    description: '정말 로그아웃 하시겠습니까?',
    confirmText: '로그아웃',
    cancelText: '취소',
    onConfirm: () => {
      AUTH_REPOSITORY.logout()
        .then(() => {
          toast.info('로그아웃', {
            description: '로그아웃 되었습니다!',
            position: 'bottom-right',
          });
          router.push('/auths/login');
        })
        .catch((e: HttpError) => {
          toast.error('로그아웃 실패', { description: e.getMessage() });
        });
    },
  });
};

const { isMobile } = useSidebar();
</script>
