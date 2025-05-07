<template>
  <div class="flex flex-col gap-6">
    <Card>
      <CardHeader class="flex flex-col gap-1">
        <CardTitle class="text-xl"> 회원 등록</CardTitle>
        <CardDescription> 이름과 회사 이메일을 입력하세요.</CardDescription>
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
                이메일 링크 발송
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
</template>

<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useRouter } from 'vue-router';
import { useToast } from '@/composables';
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
import AuthRepository from '@/repository/AuthRepository.ts';
import type Register from '@/enity/auth/Register.ts';
import { container } from 'tsyringe';

// 회원 등록 폼 검증 스키마 정의
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

const router = useRouter();
const toast = useToast();

const AUTH_REPOSITORY = container.resolve(AuthRepository);

async function handleRegister(values: Register) {
  await AUTH_REPOSITORY.register(values)
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
