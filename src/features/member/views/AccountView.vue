<template>
  <MyPageLayout :loading="loading">
    <div class="space-y-6">
      <div class="space-y-2">
        <h3 class="text-lg font-medium">계정 정보</h3>
        <p class="text-sm text-muted-foreground">계정 정보를 확인하고 관리할 수 있습니다.</p>
      </div>

      <div class="space-y-6">
        <div class="space-y-4">
          <h4 class="text-sm font-medium">개인 정보</h4>

          <div class="grid gap-4">
            <div class="grid grid-cols-4 items-center gap-4">
              <Label class="text-right">이름</Label>
              <div class="col-span-3">
                <Input disabled :value="member?.name" />
              </div>
            </div>

            <div class="grid grid-cols-4 items-center gap-4">
              <Label class="text-right">이메일</Label>
              <div class="col-span-3">
                <Input disabled :value="member?.username" />
              </div>
            </div>

            <div class="grid grid-cols-4 items-center gap-4">
              <Label class="text-right">전화번호</Label>
              <div class="col-span-3">
                <Input
                  disabled
                  :value="employeeInfo?.phone"
                  placeholder="등록된 전화번호가 없습니다"
                />
              </div>
            </div>

            <div class="grid grid-cols-4 items-center gap-4">
              <Label class="text-right">생년월일</Label>
              <div class="col-span-3">
                <Input
                  disabled
                  :value="employeeInfo?.birthDate"
                  placeholder="등록된 생년월일이 없습니다"
                />
              </div>
            </div>
          </div>
        </div>

        <Separator />

        <div class="space-y-4">
          <h4 class="text-sm font-medium">직원 정보</h4>

          <div class="grid gap-4">
            <div class="grid grid-cols-4 items-center gap-4">
              <Label class="text-right">부서</Label>
              <div class="col-span-3">
                <Input
                  disabled
                  :value="employeeInfo?.teamName"
                  placeholder="등록된 부서가 없습니다"
                />
              </div>
            </div>

            <div class="grid grid-cols-4 items-center gap-4">
              <Label class="text-right">입사일</Label>
              <div class="col-span-3">
                <Input
                  disabled
                  :value="employeeInfo?.joinDate"
                  placeholder="등록된 입사일이 없습니다"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MyPageLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import Input from '@/core/components/ui/input/Input.vue';
import Label from '@/core/components/ui/label/Label.vue';
import Separator from '@/core/components/ui/separator/Separator.vue';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import MemberRepository from '@/features/member/repository/MemberRepository.ts';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository.ts';
import Member from '@/features/member/entity/Member';
import EmployeeMyInfo from '@/features/employee/entity/EmployeeMyInfo';
import MyPageLayout from '@/features/member/layouts/MyPageLayout.vue';

const toast = useToast();
const MEMBER_REPOSITORY = container.resolve(MemberRepository);
const EMPLOYEE_REPOSITORY = container.resolve(EmployeeRepository);

const member = ref<Member | null>(null);
const employeeInfo = ref<EmployeeMyInfo | null>(null);
const loading = ref(false);

// 사용자 정보 로드 함수
async function loadUserInfo() {
  loading.value = true;
  try {
    // API에서 계정 정보 가져오기
    const [memberData, employeeData] = await Promise.all([
      MEMBER_REPOSITORY.getMyInfo(),
      EMPLOYEE_REPOSITORY.getMyEmployee(),
    ]);

    member.value = memberData;
    employeeInfo.value = employeeData;

    // 로컬 스토리지 업데이트 (계정 정보만)
    localStorage.setItem('user', JSON.stringify(memberData));
  } catch (error) {
    toast.error('계정 정보 로드 실패', {
      description: '계정 정보를 불러오는데 실패했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
    console.error('Error loading user info:', error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadUserInfo();
});
</script>

<style scoped></style>
