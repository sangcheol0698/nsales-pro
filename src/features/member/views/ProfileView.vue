<template>
  <MyPageLayout :loading="loading">
    <div class="space-y-6">
      <div class="space-y-2">
        <h3 class="text-lg font-medium">프로필</h3>
        <p class="text-sm text-muted-foreground">사이트에서 다른 사용자에게 보여지는 정보입니다.</p>
      </div>

      <div class="space-y-6">
        <div class="space-y-4">
          <div class="grid w-full items-center gap-1.5">
            <Label htmlFor="username">사용자 이름</Label>
            <Input id="username" v-model="profileForm.username" placeholder="이름" />
            <p class="text-sm text-muted-foreground mt-1">
              공개적으로 표시되는 이름입니다. 실명이나 가명을 사용할 수 있습니다. 30일에 한 번만
              변경할 수 있습니다.
            </p>
          </div>

          <div class="grid w-full items-center gap-1.5">
            <Label htmlFor="email">이메일</Label>
            <Input
              id="email"
              v-model="profileForm.email"
              placeholder="표시할 인증된 이메일 선택"
              disabled
            />
            <p class="text-sm text-muted-foreground mt-1">
              이메일 설정에서 인증된 이메일 주소를 관리할 수 있습니다.
            </p>
          </div>

          <div class="grid w-full items-center gap-1.5">
            <Label htmlFor="bio">자기소개</Label>
            <textarea
              id="bio"
              v-model="profileForm.bio"
              placeholder="여기에 메시지를 입력하세요."
              class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            ></textarea>
            <p class="text-sm text-muted-foreground mt-1">
              @멘션을 사용하여 다른 사용자나 조직을 언급할 수 있습니다.
            </p>
          </div>
        </div>
        <Button @click="updateProfile">프로필 업데이트</Button>
      </div>
    </div>
  </MyPageLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Label from '@/components/ui/label/Label.vue';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import MemberRepository from '@/features/member/repository/MemberRepository.ts';
import type Member from '@/features/member/entity/Member';
import MyPageLayout from '@/features/member/layouts/MyPageLayout.vue';

const toast = useToast();
const MEMBER_REPOSITORY = container.resolve(MemberRepository);

const member = ref<Member | null>(null);
const loading = ref(false);

const profileForm = ref({
  username: '', // "Name" placeholder below it
  email: '', // "Select a verified email to display"
  bio: '',
});

// 사용자 정보 로드 함수
async function loadUserInfo() {
  loading.value = true;
  try {
    // 로컬 스토리지에서 사용자 정보 가져오기
    const userStr = localStorage.getItem('user');
    if (userStr) {
      member.value = JSON.parse(userStr);
    }

    // API에서 최신 사용자 정보 가져오기
    const myInfo = await MEMBER_REPOSITORY.getMyInfo();
    member.value = myInfo;

    // 로컬 스토리지 업데이트
    localStorage.setItem('user', JSON.stringify(myInfo));

    // ProfileForm에 초기 데이터 설정
    profileForm.value.username = myInfo.name || ''; // Use name for username field as per image's description
    profileForm.value.email = myInfo.username || ''; // Use username for email field as per original code's email
    // URLs will remain hardcoded from the image for now, or fetched if part of Member entity
  } catch (error) {
    toast.error('프로필 정보 로드 실패', {
      description: '사용자 정보를 불러오는데 실패했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadUserInfo();
});

// 프로필 업데이트 함수 (Profile 섹션의 "Update Profile" 버튼)
function updateProfile() {
  console.log('Updating profile with:', profileForm.value);
  toast.success('프로필 업데이트 완료', {
    description: '프로필 정보가 성공적으로 업데이트되었습니다.',
    position: 'bottom-right',
  });
  // 실제 API 호출 로직 추가
}
</script>

<style scoped></style>
