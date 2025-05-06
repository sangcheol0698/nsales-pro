<template>
  <div class="flex flex-col gap-6">
    <Card>
      <CardHeader class="flex flex-col gap-1">
        <CardTitle class="text-xl"> 회원 등록 </CardTitle>
        <CardDescription> 이름과 회사 이메일을 입력하세요. </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent>
          <div class="grid gap-6">
            <div class="grid gap-6">
              <div class="grid gap-2">
                <Label html-for="name">이름</Label>
                <Input id="name" type="text" placeholder="홍길동" v-model="state.register.name" />
              </div>
              <div class="grid gap-2">
                <Label html-for="email">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="email@iabacus.co.kr"
                  v-model="state.register.email"
                />
              </div>
              <Button class="w-full" @click="handleRegister"> 회원 등록 </Button>
            </div>
            <div class="text-center text-sm">
              이미 계정이 있으신가요?
              <a href="/auths/login" class="underline underline-offset-4"> 로그인 </a>
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
import Register from '@/enity/member/Register.ts';
import { useRouter } from 'vue-router';
import { useToast } from '@/composables';
import AxiosHttpClient from '@/http/AxiosHttpClient.ts';
import type HttpError from '@/http/HttpError.ts';

const state = ref({
  register: new Register(),
});

const router = useRouter();
const toast = useToast();

function handleRegister() {
  const httpClient = new AxiosHttpClient();

  httpClient
    .post({
      path: '/api/v1/auths/register',
      body: state.value.register,
    })
    .then(() => {
      toast.success('회원 등록 성공', {
        description: '이메일로 비밀번호 설정 링크가 전송되었습니다. 이메일을 확인해주세요.',
      });
      router.push('/auths/login');
    })
    .catch((e: HttpError) => {
      toast.error('회원 등록 실패', { description: e.getMessage() });
    });
}
</script>
