<template>
  <MyPageLayout :loading="loading">
    <div class="space-y-6">
      <div class="space-y-2">
        <h3 class="text-lg font-medium">보안 설정</h3>
        <p class="text-sm text-muted-foreground">계정 보안 관련 설정을 관리합니다.</p>
      </div>
      <div class="space-y-6">
        <div class="space-y-4">
          <h4 class="text-sm font-medium">비밀번호 변경</h4>

          <div class="grid gap-4">
            <div class="grid grid-cols-4 items-center gap-4">
              <Label class="text-right">비밀번호</Label>
              <div class="col-span-3 flex items-center gap-2">
                <Input disabled type="password" model-value="********" />
                <Button variant="outline" @click="handleChangePassword"> 변경</Button>
              </div>
            </div>
          </div>
        </div>

        <Separator />

        <div class="space-y-4">
          <h4 class="text-sm font-medium">로그인 세션 관리</h4>
          <p class="text-sm text-muted-foreground">현재 활성화된 로그인 세션을 관리합니다.</p>
          <Button variant="outline" disabled>다른 기기에서 로그아웃</Button>
          <p class="text-xs text-muted-foreground">이 기능은 현재 개발 중입니다.</p>
        </div>
      </div>
    </div>
  </MyPageLayout>

  <PasswordChangeDialog :open="isPasswordDialogOpen" @update:open="isPasswordDialogOpen = $event" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Button from '@/core/components/ui/button/Button.vue';
import Input from '@/core/components/ui/input/Input.vue';
import Label from '@/core/components/ui/label/Label.vue';
import Separator from '@/core/components/ui/separator/Separator.vue';
import PasswordChangeDialog from '@/features/member/components/PasswordChangeDialog.vue';
import MyPageLayout from '@/features/member/layouts/MyPageLayout.vue';

const loading = ref(false);
const isPasswordDialogOpen = ref(false);

// 비밀번호 변경 다이얼로그 열기
function handleChangePassword() {
  isPasswordDialogOpen.value = true;
}

// // 비밀번호 변경 완료 후 처리
// function handlePasswordChanged() {
//   toast.success('비밀번호 변경 완료', {
//     description: '비밀번호가 성공적으로 변경되었습니다.',
//     position: 'bottom-right',
//   });
// }
</script>

<style scoped></style>
