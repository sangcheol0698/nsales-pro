<template>
  <AuthLayout logoHref="/auths/register">
    <div class="flex flex-col gap-6">
      <Card>
        <CardHeader class="flex flex-col gap-1">
          <CardTitle class="text-xl">회원가입</CardTitle>
          <CardDescription>이름과 이메일을 입력하세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form :validation-schema="registerSchema" @submit="handleRegister" v-slot="{ errors }">
            <div class="grid gap-6">
              <div class="grid gap-6">
                <FormField name="name" v-slot="{ field }">
                  <FormItem>
                    <FormLabel>이름</FormLabel>
                    <FormControl>
                      <Input id="name" type="text" placeholder="홍길동" v-bind="field" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                </FormField>
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
                  회원가입
                </Button>
              </div>
              <div class="text-center text-sm">
                이미 계정이 있으신가요?
                <a href="/auths/login" class="underline underline-offset-4"> 로그인 </a>
              </div>
            </div>
          </Form>
        </CardContent>
      </Card>
    </div>
  </AuthLayout>
</template>

<script setup lang="ts">
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/core/components/ui/card';
import { Button } from '@/core/components/ui/button';
import { Input } from '@/core/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/core/components/ui/form';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import type Register from '@/features/auth/entity/Register.ts';
import { useRouter } from 'vue-router';
import type HttpError from '@/core/http/HttpError.ts';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import AuthRepository from '@/features/auth/repository/AuthRepository.ts';
import AuthLayout from '@/core/layouts/AuthLayout.vue';

// 회원가입 폼 검증 스키마 정의
const registerSchema = toTypedSchema(
  z.object({
    name: z.string({
      required_error: '이름을 입력해주세요.',
    }),
    email: z
      .string({
        required_error: '이메일을 입력해주세요.',
      })
      .email('유효한 이메일 주소를 입력해주세요.'),
  })
);

const toast = useToast();
const router = useRouter();

const AUTH_REPOSITORY = container.resolve(AuthRepository);

async function handleRegister(values: Register) {
  await AUTH_REPOSITORY.register(values)
    .then(() => {
      toast.info('회원가입 성공', {
        description: '회원가입이 완료되었습니다. 이메일을 확인해주세요.',
        position: 'bottom-right',
      });
      router.push({ path: '/auths/login' });
    })
    .catch((e: HttpError) => {
      toast.error('회원가입 실패', { description: e.getMessage() });
    });
}
</script>

<style scoped></style>