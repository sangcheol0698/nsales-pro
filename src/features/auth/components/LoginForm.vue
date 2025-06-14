<template>
  <div class="flex flex-col gap-6">
    <Card>
      <CardHeader class="flex flex-col gap-1">
        <CardTitle class="text-xl"> 로그인</CardTitle>
        <CardDescription> 이메일과 비밀번호를 입력하세요.</CardDescription>
      </CardHeader>
      <CardContent>
        <Form :validation-schema="loginSchema" @submit="handleLogin" v-slot="{ errors }">
          <div class="grid gap-6">
            <div class="grid gap-6">
              <FormField name="username" v-slot="{ field }">
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
              <FormField name="password" v-slot="{ field }">
                <FormItem>
                  <div class="flex items-center">
                    <FormLabel>비밀번호</FormLabel>
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
              <FormField name="remember">
                <FormItem>
                  <div class="flex justify-end space-x-2">
                    <FormControl>
                      <Checkbox id="remember" type="checkbox" v-model="remember" />
                      <Label for="remember">로그인 상태 유지</Label>
                    </FormControl>
                  </div>
                </FormItem>
              </FormField>
              <Button class="w-full" type="submit" :disabled="Object.keys(errors).length > 0">
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
import type Login from '@/features/auth/entity/Login.ts';
import { useRouter } from 'vue-router';
import type HttpError from '@/core/http/HttpError.ts';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import AuthRepository from '@/features/auth/repository/AuthRepository.ts';
import MemberRepository from '@/features/member/repository/MemberRepository.ts';
import { Label } from '@/core/components/ui/label';
import { Checkbox } from '@/core/components/ui/checkbox';
import { ref, onMounted } from 'vue';

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

const toast = useToast();
const router = useRouter();

const remember = ref(false);

// 컴포넌트 마운트 시 세션 만료 확인
onMounted(() => {
  // URL 쿼리 파라미터에서 세션 만료 여부 확인
  const expired = router.currentRoute.value.query.expired === 'true';

  // 세션 만료로 인한 리다이렉트인 경우 메시지 표시
  if (expired) {
    toast.error('세션 만료', {
      description: '로그인 세션이 만료되었습니다. 다시 로그인해주세요.',
      position: 'bottom-right',
    });

    // 쿼리 파라미터 제거 (새로고침 시 메시지가 다시 표시되지 않도록)
    router.replace({ name: 'login', query: {} });
  }
});

const AUTH_REPOSITORY = container.resolve(AuthRepository);
const MEMBER_REPOSITORY = container.resolve(MemberRepository);

async function handleLogin(values: Login) {
  try {
    // 로그인 시도
    await AUTH_REPOSITORY.login(values, remember.value);

    // 로그인 성공 후 사용자 정보 가져오기
    const myInfo = await MEMBER_REPOSITORY.getMyInfo();

    // 사용자 정보를 localStorage에 저장
    localStorage.setItem('user', JSON.stringify(myInfo));

    toast.info('로그인 성공', {
      description: '환영합니다! 로그인에 성공했습니다.',
      position: 'bottom-right',
    });

    router.push({ path: '/' });
  } catch (e) {
    toast.error('로그인 실패', { description: (e as HttpError).getMessage() });
  }
}
</script>
