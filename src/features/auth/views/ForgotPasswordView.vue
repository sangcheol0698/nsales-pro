<template>
  <AuthLayout logoHref="/auths/forgot-password">
    <div class="flex flex-col gap-6">
      <Card>
        <CardHeader class="flex flex-col gap-1">
          <CardTitle class="text-xl">비밀번호 찾기</CardTitle>
          <CardDescription>가입한 이메일을 입력하세요.</CardDescription>
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
                <Button class="w-full" type="submit" :disabled="Object.keys(errors).length > 0">
                  비밀번호 재설정 링크 전송
                </Button>
              </div>
              <div class="text-center text-sm">
                <a href="/auths/login" class="underline underline-offset-4">
                  로그인으로 돌아가기
                </a>
              </div>
            </div>
          </Form>
        </CardContent>
      </Card>
    </div>
  </AuthLayout>
</template>

<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import type FindPassword from '@/features/auth/entity/FindPassword.ts';
import { useRouter } from 'vue-router';
import type HttpError from '@/core/http/HttpError.ts';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import AuthRepository from '@/features/auth/repository/AuthRepository.ts';
import AuthLayout from '@/core/layouts/AuthLayout.vue';

// 비밀번호 찾기 폼 검증 스키마 정의
const forgotPasswordSchema = toTypedSchema(
  z.object({
    email: z
      .string({
        required_error: '이메일을 입력해주세요.',
      })
      .email('유효한 이메일 주소를 입력해주세요.'),
  }),
);

const toast = useToast();
const router = useRouter();

const AUTH_REPOSITORY = container.resolve(AuthRepository);

async function handleForgotPassword(values: FindPassword) {
  await AUTH_REPOSITORY.findPassword(values)
    .then(() => {
      toast.success('이메일 전송 완료', {
        description: '비밀번호 재설정 링크가 이메일로 전송되었습니다.',
        position: 'bottom-right',
      });
      router.push({ path: '/auths/login' });
    })
    .catch((e: HttpError) => {
      toast.error('이메일 전송 실패', { description: e.getMessage() });
    });
}
</script>

<style scoped></style>