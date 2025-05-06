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
        <Form
          :validation-schema="forgotPasswordSchema"
          @submit="handleForgotPassword"
          v-slot="{ errors }"
        >
          <div class="grid gap-6">
            <div class="grid gap-6">
              <FormField name="email" v-slot="{ field }">
                <FormItem>
                  <FormLabel>이메일</FormLabel>
                  <FormControl>
                    <Input id="email" type="email" placeholder="email@iabacus.co.kr" v-bind="field" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>
              <Button class="w-full" type="submit" :disabled="Object.keys(errors).length > 0">
                비밀번호 찾기
              </Button>
            </div>
            <div class="text-center text-sm">
              <a href="/auths/login" class="underline underline-offset-4"> 로그인으로 돌아가기 </a>
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
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';

// 비밀번호 찾기 폼 검증 스키마 정의
const forgotPasswordSchema = toTypedSchema(
  z.object({
    email: z
      .string({
        required_error: '이메일을 입력해주세요.',
      })
      .email('유효한 이메일 주소를 입력해주세요.'),
  })
);

const router = useRouter();
const toast = useToast();

function handleForgotPassword(values: { email: string }) {
  const httpClient = new AxiosHttpClient();

  httpClient
    .post({
      path: '/api/v1/auths/find-password',
      body: { email: values.email },
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
