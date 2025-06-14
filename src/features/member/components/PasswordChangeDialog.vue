<template>
  <Dialog :open="open" @update:open="updateOpen">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>비밀번호 변경</DialogTitle>
        <DialogDescription>
          새로운 비밀번호를 설정합니다. 비밀번호는 8-20자 사이이며, 대문자, 소문자, 특수문자를 포함해야 합니다.
        </DialogDescription>
      </DialogHeader>
      <Form :validation-schema="passwordChangeSchema" @submit="handlePasswordChange" v-slot="{ errors }">
        <div class="grid gap-4 py-4">
          <FormField name="password" v-slot="{ field }">
            <FormItem>
              <FormLabel>현재 비밀번호</FormLabel>
              <FormControl>
                <Input type="password" placeholder="현재 비밀번호" v-bind="field" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
          <FormField name="newPassword" v-slot="{ field }">
            <FormItem>
              <FormLabel>새 비밀번호</FormLabel>
              <FormControl>
                <Input type="password" placeholder="새 비밀번호" v-bind="field" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
          <FormField name="newPasswordConfirm" v-slot="{ field }">
            <FormItem>
              <FormLabel>비밀번호 확인</FormLabel>
              <FormControl>
                <Input type="password" placeholder="새 비밀번호 확인" v-bind="field" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" @click="updateOpen(false)">취소</Button>
          <Button type="submit" :disabled="Object.keys(errors).length > 0 || isSubmitting">변경하기</Button>
        </DialogFooter>
      </Form>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import MemberRepository from '@/features/member/repository/MemberRepository';
import type PasswordChange from '@/features/member/entity/PasswordChange';
import type HttpError from '@/core/http/HttpError';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/core/components/ui/dialog';
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

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  'update:open': [value: boolean];
  'password-changed': [];
}>();

const updateOpen = (value: boolean) => {
  emit('update:open', value);
};

const toast = useToast();
const MEMBER_REPOSITORY = container.resolve(MemberRepository);
const isSubmitting = ref(false);

// 비밀번호 변경 폼 검증 스키마 정의
const passwordChangeSchema = toTypedSchema(
  z.object({
    password: z.string({
      required_error: '현재 비밀번호를 입력해주세요.',
    }),
    newPassword: z
      .string({
        required_error: '새 비밀번호를 입력해주세요.',
      })
      .min(8, '비밀번호는 최소 8자 이상이어야 합니다.')
      .max(20, '비밀번호는 최대 20자 이하이어야 합니다.')
      .regex(/[A-Z]/, '비밀번호에는 최소 1개의 대문자가 포함되어야 합니다.')
      .regex(/[a-z]/, '비밀번호에는 최소 1개의 소문자가 포함되어야 합니다.')
      .regex(/[!@#$%^&*()]/, '비밀번호에는 최소 1개의 특수문자가 포함되어야 합니다.'),
    newPasswordConfirm: z.string({
      required_error: '비밀번호 확인을 입력해주세요.',
    }),
  }).refine((data) => data.newPassword === data.newPasswordConfirm, {
    message: '비밀번호가 일치하지 않습니다.',
    path: ['newPasswordConfirm'],
  }).refine((data) => data.password !== data.newPassword, {
    message: '새 비밀번호는 현재 비밀번호와 달라야 합니다.',
    path: ['newPassword'],
  })
);

async function handlePasswordChange(values: PasswordChange) {
  isSubmitting.value = true;
  try {
    await MEMBER_REPOSITORY.changePassword(values);
    toast.success('비밀번호 변경 성공', {
      description: '비밀번호가 성공적으로 변경되었습니다.',
      position: 'bottom-right',
    });
    emit('password-changed');
    updateOpen(false);
  } catch (e) {
    toast.error('비밀번호 변경 실패', { 
      description: (e as HttpError).getMessage(),
      position: 'bottom-right',
    });
  } finally {
    isSubmitting.value = false;
  }
}
</script>