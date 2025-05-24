<template>
  <AuthLayout logoHref="/auths/initialize">
    <div class="flex flex-col gap-6">
      <Card>
        <CardHeader class="flex flex-col gap-1">
          <CardTitle class="text-xl">비밀번호 설정</CardTitle>
          <CardDescription>새로운 비밀번호를 설정해주세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form
            :validation-schema="setPasswordSchema"
            @submit="handleSetPassword"
            v-slot="{ errors }"
          >
            <div class="grid gap-6">
              <div class="grid gap-6">
                <FormField name="newPassword" v-slot="{ field }">
                  <FormItem>
                    <FormLabel>새 비밀번호</FormLabel>
                    <FormControl>
                      <Input id="newPassword" type="password" v-bind="field" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                </FormField>
                <FormField name="newPasswordConfirm" v-slot="{ field }">
                  <FormItem>
                    <FormLabel>새 비밀번호 확인</FormLabel>
                    <FormControl>
                      <Input id="newPasswordConfirm" type="password" v-bind="field" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                </FormField>
                <Button class="w-full" type="submit" :disabled="Object.keys(errors).length > 0">
                  비밀번호 설정
                </Button>
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
import type SetPassword from '@/features/auth/entity/SetPassword.ts';
import { useRoute, useRouter } from 'vue-router';
import type HttpError from '@/core/http/HttpError.ts';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import AuthRepository from '@/features/auth/repository/AuthRepository.ts';
import AuthLayout from '@/core/layouts/AuthLayout.vue';
import { onMounted, ref } from 'vue';

// 비밀번호 설정 폼 검증 스키마 정의
const setPasswordSchema = toTypedSchema(
  z
    .object({
      newPassword: z
        .string({
          required_error: '비밀번호를 입력해주세요.',
        })
        .min(8, '비밀번호는 최소 8자 이상이어야 합니다.'),
      newPasswordConfirm: z.string({
        required_error: '비밀번호 확인을 입력해주세요.',
      }),
      token: z.string(),
    })
    .refine((data) => data.newPassword === data.newPasswordConfirm, {
      message: '비밀번호가 일치하지 않습니다.',
      path: ['newPasswordConfirm'],
    })
);

const toast = useToast();
const router = useRouter();
const route = useRoute();
const token = ref('');

const AUTH_REPOSITORY = container.resolve(AuthRepository);

async function handleSetPassword(values: SetPassword) {
  values.token = token.value;
  await AUTH_REPOSITORY.setPassword(values)
    .then(() => {
      toast.info('비밀번호 설정 성공', {
        description: '비밀번호가 성공적으로 설정되었습니다. 로그인해주세요.',
        position: 'bottom-right',
      });
      router.push({ path: '/auths/login' });
    })
    .catch((e: HttpError) => {
      toast.error('비밀번호 설정 실패', { description: e.getMessage() });
    });
}

onMounted(() => {
  // URL에서 토큰 추출
  const queryToken = route.query.token as string;
  if (queryToken) {
    token.value = queryToken;
  } else {
    toast.error('유효하지 않은 접근', {
      description: '유효한 토큰이 없습니다. 비밀번호 찾기를 다시 시도해주세요.',
      position: 'bottom-right',
    });
    router.push({ path: '/auths/forgot-password' });
  }
});
</script>

<style scoped></style>