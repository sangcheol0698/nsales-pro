<template>
  <div class="flex flex-col gap-6">
    <Card>
      <CardHeader class="flex flex-col gap-1">
        <CardTitle class="text-xl"> 비밀번호 설정 </CardTitle>
        <CardDescription> 새 비밀번호를 입력하세요. </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent>
          <div class="grid gap-6">
            <div class="grid gap-6">
              <div class="grid gap-2">
                <Label html-for="password">비밀번호</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="새 비밀번호"
                  v-model="state.setPassword.newPassword"
                />
              </div>
              <div class="grid gap-2">
                <Label html-for="confirmPassword">비밀번호 확인</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="비밀번호 확인"
                  v-model="state.setPassword.newPasswordConfirm"
                />
              </div>
              <Button class="w-full" @click="handleSetPassword"> 비밀번호 설정 </Button>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { onMounted, ref } from 'vue';
import SetPassword from '@/enity/member/SetPassword.ts';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from '@/composables';
import AxiosHttpClient from '@/http/AxiosHttpClient.ts';
import type HttpError from '@/http/HttpError.ts';

const state = ref({
  setPassword: new SetPassword(),
});

const router = useRouter();
const route = useRoute();
const toast = useToast();

onMounted(() => {
  // Get token from route params
  const token = route.query.token as string;
  if (!token) {
    toast.error('유효하지 않은 링크', { description: '비밀번호 설정 링크가 유효하지 않습니다.' });
    router.push('/auths/login');
    return;
  }

  state.value.setPassword.token = token;
});

function handleSetPassword() {
  // Validate passwords match
  if (state.value.setPassword.newPassword !== state.value.setPassword.newPasswordConfirm) {
    toast.error('비밀번호 불일치', {
      description: '비밀번호와 비밀번호 확인이 일치하지 않습니다.',
    });
    return;
  }

  // Validate password length
  if (state.value.setPassword.newPassword.length < 8) {
    toast.error('비밀번호 오류', { description: '비밀번호는 최소 8자 이상이어야 합니다.' });
    return;
  }

  const httpClient = new AxiosHttpClient();

  httpClient
    .patch({
      path: '/api/v1/auths/initialize',
      body: state.value.setPassword,
    })
    .then(() => {
      toast.success('비밀번호 설정 성공', {
        description: '비밀번호가 성공적으로 설정되었습니다. 이제 로그인할 수 있습니다.',
      });
      router.push('/auths/login');
    })
    .catch((e: HttpError) => {
      toast.error('비밀번호 설정 실패', { description: e.getMessage() });
    });
}
</script>
