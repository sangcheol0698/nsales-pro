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
              <AvatarFallback class="rounded-lg"> CN </AvatarFallback>
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
                <AvatarFallback class="rounded-lg"> CN </AvatarFallback>
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
              프로 업그레이드
            </DropdownMenuItem>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem @click="router.push('/my-page')">
              <BadgeCheck />
              내 프로필
            </DropdownMenuItem>
            <DropdownMenuItem>
              <CreditCard />
              결제 정보
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Bell />
              알림
            </DropdownMenuItem>
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
import { Avatar, AvatarFallback, AvatarImage } from '@/core/components/ui/avatar';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/core/components/ui/dropdown-menu';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/core/components/ui/sidebar';
import { BadgeCheck, Bell, ChevronsUpDown, CreditCard, LogOut, Sparkles } from 'lucide-vue-next';
import { container } from 'tsyringe';
import AuthRepository from '@/features/auth/repository/AuthRepository.ts';
import { useRouter } from 'vue-router';
import type HttpError from '@/core/http/HttpError.ts';
import { useAlertDialog, useToast } from '@/core/composables';
import { computed, ref } from 'vue';
import type Member from '@/features/member/entity/Member';

// 기존 props 정의는 유지하되 선택적으로 변경
const props = defineProps<{
  user?: {
    name: string;
    email: string;
    avatar: string;
  };
}>();

// localStorage에서 사용자 정보 가져오기
const storedUser = ref<Member | null>(null);

// 컴포넌트 마운트 시 localStorage에서 사용자 정보 로드
try {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    storedUser.value = JSON.parse(userStr);
  }
} catch (error) {
  console.error('Failed to parse user from localStorage:', error);
}

// props로 전달된 사용자 정보와 localStorage의 사용자 정보를 합쳐서 사용
const user = computed(() => {
  if (storedUser.value) {
    return {
      name: storedUser.value.name,
      email: storedUser.value.username, // Member 엔티티의 username은 이메일
      avatar: props.user?.avatar || '', // avatar는 localStorage에 없으므로 props에서 가져오거나 빈 문자열 사용
    };
  }
  return props.user || { name: '', email: '', avatar: '' };
});

const router = useRouter();
const toast = useToast();
const alertDialog = useAlertDialog();

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
