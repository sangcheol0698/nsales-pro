<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="max-w-3xl mx-auto w-full">
        <Card>
          <CardHeader class="flex flex-col gap-1">
            <CardTitle class="text-xl">내 프로필</CardTitle>
            <CardDescription>내 계정 정보를 확인하고 관리할 수 있습니다.</CardDescription>
          </CardHeader>
          <CardContent>
            <div v-if="loading" class="flex justify-center items-center p-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
            <div v-else class="space-y-6">
              <div class="flex items-center gap-4">
                <Avatar class="h-20 w-20">
                  <AvatarFallback>{{ getInitials(member?.name) }}</AvatarFallback>
                </Avatar>
                <div>
                  <h3 class="text-lg font-medium">{{ member?.name }}</h3>
                  <p class="text-sm text-muted-foreground">{{ member?.username }}</p>
                </div>
              </div>

              <Separator />

              <div class="space-y-4">
                <h4 class="text-sm font-medium">계정 정보</h4>

                <div class="grid gap-4">
                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">이름</Label>
                    <div class="col-span-3">
                      <Input disabled :value="member?.name" />
                    </div>
                  </div>

                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">이메일</Label>
                    <div class="col-span-3">
                      <Input disabled :value="member?.username" />
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <div class="space-y-4">
                <h4 class="text-sm font-medium">보안</h4>

                <div class="grid gap-4">
                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">비밀번호</Label>
                    <div class="col-span-3 flex items-center gap-2">
                      <Input disabled type="password" value="********" />
                      <Button variant="outline" @click="handleChangePassword">
                        변경
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>

    <!-- 비밀번호 변경 다이얼로그 -->
    <PasswordChangeDialog 
      :open="isPasswordDialogOpen" 
      @update:open="isPasswordDialogOpen = $event"
      @password-changed="handlePasswordChanged"
    />
  </SidebarLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { SidebarLayout } from '@/shared/components/sidebar';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/core/components/ui/card';
import { Button } from '@/core/components/ui/button';
import { Input } from '@/core/components/ui/input';
import { Label } from '@/core/components/ui/label';
import { Separator } from '@/core/components/ui/separator';
import { Avatar, AvatarFallback } from '@/core/components/ui/avatar';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import MemberRepository from '@/features/member/repository/MemberRepository.ts';
import type Member from '@/features/member/entity/Member';
import { useRouter } from 'vue-router';
import PasswordChangeDialog from '@/features/member/components/PasswordChangeDialog.vue';

const toast = useToast();
const router = useRouter();
const MEMBER_REPOSITORY = container.resolve(MemberRepository);

const member = ref<Member | null>(null);
const loading = ref(true);
const isPasswordDialogOpen = ref(false);

// 사용자 정보 로드 함수
async function loadUserInfo() {
  loading.value = true;
  try {
    // 로컬 스토리지에서 사용자 정보 가져오기
    const userStr = localStorage.getItem('user');
    if (userStr) {
      member.value = JSON.parse(userStr);
    }

    // API에서 최신 사용자 정보 가져오기
    const myInfo = await MEMBER_REPOSITORY.getMyInfo();
    member.value = myInfo;

    // 로컬 스토리지 업데이트
    localStorage.setItem('user', JSON.stringify(myInfo));
  } catch (error) {
    toast.error('프로필 정보 로드 실패', {
      description: '사용자 정보를 불러오는데 실패했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadUserInfo();
});

// 이름의 이니셜을 가져오는 함수
function getInitials(name?: string): string {
  if (!name) return '';

  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .toUpperCase();
}

// 비밀번호 변경 다이얼로그 열기
function handleChangePassword() {
  isPasswordDialogOpen.value = true;
}

// 비밀번호 변경 완료 후 처리
function handlePasswordChanged() {
  // 사용자 정보 다시 로드
  loadUserInfo();
}
</script>
