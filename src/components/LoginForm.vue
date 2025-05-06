<template>
  <div class="flex flex-col gap-6">
    <Card>
      <CardHeader class="flex flex-col gap-1">
        <CardTitle class="text-xl"> 로그인 </CardTitle>
        <CardDescription> 이메일과 비밀번호를 입력하세요. </CardDescription>
      </CardHeader>
      <CardContent>
        <Form :validation-schema="loginSchema" @submit="handleLogin" v-slot="{ errors }">
          <div class="grid gap-6">
            <div class="grid gap-6">
              <FormField name="username" v-slot="{ field }">
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      id="email"
                      type="email"
                      placeholder="email@iabacus.co.kr"
                      v-bind="field"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>
              <FormField name="password" v-slot="{ field }">
                <FormItem>
                  <div class="flex items-center">
                    <FormLabel>Password</FormLabel>
                    <a
                      href="/auths/forgot-password"
                      class="ml-auto text-sm underline-offset-4 hover:underline"
                    >
                      비밀번호를 잊으셨나요?
                    </a>
                  </div>
                  <FormControl>
                    <Input id="password" type="password" v-bind="field" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>
              <Button
                class="w-full"
                type="submit"
                :disabled="Object.keys(errors).length > 0"
                @click="handleLogin"
              >
                Login
              </Button>
            </div>
            <div class="text-center text-sm">
              계정이 없으신가요?
              <a href="/auths/register" class="underline underline-offset-4"> 회원등록 </a>
            </div>
          </div>
        </Form>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useRouter } from 'vue-router';
import { useToast } from '@/composables';
import AxiosHttpClient from '@/http/AxiosHttpClient.ts';
import type HttpError from '@/http/HttpError.ts';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';

// 로그인 폼 검증 스키마 정의
const loginSchema = toTypedSchema(
  z.object({
    username: z.string({
      required_error: '이메일을 입력해주세요.',
    }),
    password: z.string({
      required_error: '비밀번호를 입력해주세요.',
    }),
  })
);

const router = useRouter();
const toast = useToast();

function handleLogin(values: { username: string; password: string }) {
  const httpClient = new AxiosHttpClient();

  httpClient
    .post({
      path: '/api/v1/auths/login',
      body: values,
    })
    .then(() => {
      toast.success('로그인 성공', { description: '환영합니다! 로그인에 성공했습니다.' });
      router.push('/');
    })
    .catch((e: HttpError) => {
      toast.error('로그인 실패', { description: e.getMessage() });
    });
}
</script>
