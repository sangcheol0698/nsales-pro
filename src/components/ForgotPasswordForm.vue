<template>
  <div class="flex flex-col gap-6">
    <Card>
      <CardHeader class="flex flex-col gap-1">
        <CardTitle class="text-xl"> 비밀번호 찾기 </CardTitle>
        <CardDescription>
          가입한 이메일을 입력하세요.<br />
          비밀번호 재설정 링크를 보내드립니다.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent>
          <div class="grid gap-6">
            <div class="grid gap-6">
              <div class="grid gap-2">
                <Label html-for="email">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="email@iabacus.co.kr"
                  v-model="state.forgotPassword.email"
                />
              </div>
              <Button class="w-full" @click="handleForgotPassword"> 비밀번호 찾기 </Button>
            </div>
            <div class="text-center text-sm">
              <a href="/auths/login" class="underline underline-offset-4"> 로그인으로 돌아가기 </a>
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
import { ref } from 'vue';
import ForgotPassword from '@/enity/member/ForgotPassword.ts';
import { useRouter } from 'vue-router';
import { useToast } from '@/composables';
import AxiosHttpClient from '@/http/AxiosHttpClient.ts';
import type HttpError from '@/http/HttpError.ts';

const state = ref({
  forgotPassword: new ForgotPassword(),
});

const router = useRouter();
const toast = useToast();

function handleForgotPassword() {
  // 이메일 유효성 검사
  if (!state.value.forgotPassword.email) {
    toast.error('이메일 오류', { description: '이메일을 입력해주세요.' });
    return;
  }

  const httpClient = new AxiosHttpClient();

  httpClient
    .post({
      path: '/api/v1/auths/find-password',
      body: state.value.forgotPassword,
    })
    .then(() => {
      toast.success('비밀번호 찾기 요청 성공', {
        description:
          '입력하신 이메일로 비밀번호 재설정 링크가 전송되었습니다. 이메일을 확인해주세요.',
      });
      router.push('/auths/login');
    })
    .catch((e: HttpError) => {
      toast.error('비밀번호 찾기 요청 실패', { description: e.getMessage() });
    });
}
</script>
