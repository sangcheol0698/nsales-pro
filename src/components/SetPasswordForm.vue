<template>
  <div class="flex flex-col gap-6">
    <Card>
      <CardHeader class="flex flex-col gap-1">
        <CardTitle class="text-xl"> 비밀번호 설정 </CardTitle>
        <CardDescription> 새 비밀번호를 입력하세요. </CardDescription>
      </CardHeader>
      <CardContent>
        <Form :validation-schema="passwordSchema" @submit="handleSetPassword" v-slot="{ errors }">
          <div class="grid gap-6">
            <div class="grid gap-6">
              <FormField name="newPassword" v-slot="{ field }">
                <FormItem>
                  <FormLabel>비밀번호</FormLabel>
                  <FormDescription>
                    비밀번호는 대문자, 소문자, 숫자를 포함하여 8자 이상이어야 합니다.
                  </FormDescription>
                  <FormControl>
                    <Input
                      id="password"
                      type="password"
                      placeholder="새 비밀번호"
                      v-bind="field"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>
              <FormField name="newPasswordConfirm" v-slot="{ field }">
                <FormItem>
                  <FormLabel>비밀번호 확인</FormLabel>
                  <FormControl>
                    <Input
                      id="confirmPassword"
                      type="password"
                      placeholder="비밀번호 확인"
                      v-bind="field"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              </FormField>
              <Button class="w-full" type="submit" :disabled="Object.keys(errors).length > 0"> 비밀번호 설정 </Button>
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
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from '@/composables';
import type HttpError from '@/http/HttpError.ts';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import AuthRepository from '@/repository/AuthRepository.ts';
import type SetPassword from '@/enity/auth/SetPassword.ts';

// 토큰 상태 관리
const token = ref('');

const router = useRouter();
const route = useRoute();
const toast = useToast();

const AUTH_REPOSITORY = new AuthRepository();

// 비밀번호 설정 폼 검증 스키마 정의
const passwordSchema = toTypedSchema(
  z.object({
    newPassword: z.string({
      required_error: '비밀번호를 입력해주세요.',
    })
    .min(8, '비밀번호는 최소 8자 이상이어야 합니다.')
    .regex(/[A-Z]/, '비밀번호에는 대문자가 포함되어야 합니다.')
    .regex(/[a-z]/, '비밀번호에는 소문자가 포함되어야 합니다.')
    .regex(/[0-9]/, '비밀번호에는 숫자가 포함되어야 합니다.'),
    newPasswordConfirm: z.string({
      required_error: '비밀번호 확인을 입력해주세요.',
    }),
  })
  .refine((data) => data.newPassword === data.newPasswordConfirm, {
    message: '비밀번호와 비밀번호 확인이 일치하지 않습니다.',
    path: ['newPasswordConfirm'],
  })
);

onMounted(() => {
  // Get token from route params
  const routeToken = route.query.token as string;
  if (!routeToken) {
    toast.error('유효하지 않은 링크', { description: '비밀번호 설정 링크가 유효하지 않습니다.' });
    router.push('/auths/login');
    return;
  }

  token.value = routeToken;
});

async function handleSetPassword(values: SetPassword) {
  values.token = token.value;
  await AUTH_REPOSITORY.setPassword(values)
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
