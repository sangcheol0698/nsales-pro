<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent
      class="w-[85vw] sm:w-[80vw] md:w-[75vw] lg:w-[70vw] xl:w-[65vw] 2xl:w-[60vw] !max-w-[900px] sm:!max-w-[80vw] md:!max-w-[75vw] lg:!max-w-[70vw] xl:!max-w-[65vw] 2xl:!max-w-[60vw] h-[95vh] sm:h-[90vh] md:h-[85vh] flex flex-col p-0">
      <DialogHeader class="px-6 sm:px-8 lg:px-10 xl:px-12 pt-6 sm:pt-8 pb-6 border-b flex-shrink-0">
        <DialogTitle class="text-xl sm:text-2xl">설정</DialogTitle>
        <DialogDescription class="text-sm sm:text-base">
          계정 설정 및 이메일 환경설정을 관리합니다.
        </DialogDescription>
      </DialogHeader>

      <div v-if="loading" class="flex justify-center items-center flex-1 p-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>

      <div v-else class="flex flex-col lg:flex-row gap-4 lg:gap-6 flex-1 overflow-hidden">
        <!-- Mobile: Horizontal tabs, Desktop: Vertical sidebar -->
        <aside class="lg:w-48 xl:w-52 2xl:w-56 flex-shrink-0 px-4 sm:px-6 lg:px-0 lg:pl-6">
          <!-- Mobile horizontal scrollable tabs -->
          <nav class="lg:hidden">
            <div class="flex space-x-1 overflow-x-auto pb-2 mb-4">
              <button
                v-for="category in categories"
                :key="category.key"
                @click="selectedCategory = category.key"
                :class="[
                  'flex-shrink-0 rounded-full px-4 py-2 text-sm font-medium whitespace-nowrap transition-colors',
                  selectedCategory === category.key
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
                ]"
              >
                {{ category.name }}
              </button>
            </div>
          </nav>

          <!-- Desktop vertical navigation -->
          <nav class="hidden lg:block lg:sticky lg:top-0">
            <div class="space-y-1">
              <button
                v-for="category in categories"
                :key="category.key"
                @click="selectedCategory = category.key"
                :class="[
                  'block w-full text-left rounded-md px-3 py-2.5 text-sm font-medium transition-colors',
                  selectedCategory === category.key
                    ? 'bg-secondary text-secondary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                ]"
              >
                {{ category.name }}
              </button>
            </div>
          </nav>
        </aside>

        <div class="flex-1 min-w-0 overflow-y-auto px-4 sm:px-6 lg:px-8 xl:px-10 pb-8">
          <!-- Profile Tab -->
          <div v-if="selectedCategory === 'profile'" class="space-y-6">
            <div class="space-y-2">
              <h3 class="text-lg sm:text-xl font-medium">프로필</h3>
              <p class="text-sm sm:text-base text-muted-foreground">
                사이트에서 다른 사용자에게 보여지는 정보입니다.
              </p>
            </div>

            <div class="space-y-6">
              <!-- Profile form with better spacing -->
              <div class="space-y-4">
                <div class="space-y-2">
                  <Label htmlFor="username" class="text-sm font-medium">사용자 이름</Label>
                  <Input
                    id="username"
                    v-model="profileForm.username"
                    placeholder="이름"
                    class="h-10 sm:h-11 text-sm sm:text-base"
                  />
                  <p class="text-xs sm:text-sm text-muted-foreground">
                    공개적으로 표시되는 이름입니다. 실명이나 가명을 사용할 수 있습니다.
                  </p>
                </div>

                <div class="space-y-2">
                  <Label htmlFor="email" class="text-sm font-medium">이메일</Label>
                  <Input
                    id="email"
                    v-model="profileForm.email"
                    placeholder="표시할 인증된 이메일 선택"
                    class="h-10 sm:h-11 text-sm sm:text-base"
                    disabled
                  />
                  <p class="text-xs sm:text-sm text-muted-foreground">
                    이메일 설정에서 인증된 이메일 주소를 관리할 수 있습니다.
                  </p>
                </div>

                <div class="space-y-2">
                  <Label htmlFor="bio" class="text-sm font-medium">자기소개</Label>
                  <Textarea
                    id="bio"
                    v-model="profileForm.bio"
                    placeholder="여기에 메시지를 입력하세요."
                    class="min-h-[100px] sm:min-h-[120px] text-sm sm:text-base resize-none"
                  />
                  <p class="text-xs sm:text-sm text-muted-foreground">
                    @멘션을 사용하여 다른 사용자나 조직을 언급할 수 있습니다.
                  </p>
                </div>

                <div class="pt-2">
                  <Button
                    @click="updateProfile"
                    class="w-full sm:w-auto h-10 sm:h-11 text-sm sm:text-base"
                  >
                    프로필 업데이트
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <!-- Account Tab -->
          <div v-else-if="selectedCategory === 'account'" class="space-y-6">
            <div class="space-y-2">
              <h3 class="text-lg sm:text-xl font-medium">내 계정 정보</h3>
              <p class="text-sm sm:text-base text-muted-foreground">
                내 계정 정보를 확인하고 관리할 수 있습니다.
              </p>
            </div>

            <div class="space-y-6">
              <div class="space-y-4">
                <h4 class="text-base sm:text-lg font-medium">개인 정보</h4>
                <div class="space-y-4">
                  <!-- Responsive grid: mobile stacked, desktop side-by-side -->
                  <div class="flex flex-col sm:grid sm:grid-cols-4 gap-2 sm:gap-4 items-start sm:items-center">
                    <Label class="text-sm font-medium sm:text-right">이름</Label>
                    <div class="col-span-3 w-full">
                      <Input
                        disabled
                        :value="employee?.name || member?.name"
                        class="h-10 sm:h-11 text-sm sm:text-base bg-muted"
                      />
                    </div>
                  </div>
                  <div class="flex flex-col sm:grid sm:grid-cols-4 gap-2 sm:gap-4 items-start sm:items-center">
                    <Label class="text-sm font-medium sm:text-right">이메일</Label>
                    <div class="col-span-3 w-full">
                      <Input
                        disabled
                        :value="employee?.email || member?.username"
                        class="h-10 sm:h-11 text-sm sm:text-base bg-muted"
                      />
                    </div>
                  </div>

                  <div class="flex flex-col sm:grid sm:grid-cols-4 gap-2 sm:gap-4 items-start sm:items-center">
                    <Label class="text-sm font-medium sm:text-right">전화번호</Label>
                    <div class="col-span-3 w-full">
                      <Input
                        disabled
                        :value="employee?.phone"
                        placeholder="등록된 전화번호가 없습니다"
                        class="h-10 sm:h-11 text-sm sm:text-base bg-muted"
                      />
                    </div>
                  </div>

                  <div class="flex flex-col sm:grid sm:grid-cols-4 gap-2 sm:gap-4 items-start sm:items-center">
                    <Label class="text-sm font-medium sm:text-right">생년월일</Label>
                    <div class="col-span-3 w-full">
                      <Input
                        disabled
                        :value="employee?.birthDate"
                        placeholder="등록된 생년월일이 없습니다"
                        class="h-10 sm:h-11 text-sm sm:text-base bg-muted"
                      />
                    </div>
                  </div>
                  
                  <div class="flex flex-col sm:grid sm:grid-cols-4 gap-2 sm:gap-4 items-start sm:items-center">
                    <Label class="text-sm font-medium sm:text-right">입사일</Label>
                    <div class="col-span-3 w-full">
                      <Input
                        disabled
                        :value="employee?.joinDate"
                        placeholder="등록된 입사일이 없습니다"
                        class="h-10 sm:h-11 text-sm sm:text-base bg-muted"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <div class="space-y-4">
                <h4 class="text-base sm:text-lg font-medium">직원 정보</h4>
                <div class="space-y-4">
                  <div class="flex flex-col sm:grid sm:grid-cols-4 gap-2 sm:gap-4 items-start sm:items-center">
                    <Label class="text-sm font-medium sm:text-right">부서</Label>
                    <div class="col-span-3 w-full">
                      <Input
                        disabled
                        :value="employee?.teamName"
                        placeholder="등록된 부서가 없습니다"
                        class="h-10 sm:h-11 text-sm sm:text-base bg-muted"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Appearance Tab -->
          <div v-else-if="selectedCategory === 'appearance'" class="space-y-6">
            <div class="space-y-2">
              <h3 class="text-lg sm:text-xl font-medium">환경 설정</h3>
              <p class="text-sm sm:text-base text-muted-foreground">
                앱의 테마 및 폰트 설정을 관리합니다.
              </p>
            </div>

            <div class="space-y-6">
              <div class="space-y-4">
                <h4 class="text-base sm:text-lg font-medium">테마</h4>
                <p class="text-sm sm:text-base text-muted-foreground">
                  인터페이스 테마를 선택하세요.
                </p>
                <!-- Responsive grid: 1 column on mobile, 2 on tablet, 3 on desktop -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  <div
                    v-for="themeOption in themeOptions"
                    :key="themeOption.value"
                    @click="setTheme(themeOption.value)"
                    :class="[
                      'border rounded-lg p-3 sm:p-4 cursor-pointer transition-all hover:scale-105',
                      theme === themeOption.value 
                        ? 'border-primary bg-primary/10 ring-2 ring-primary/20' 
                        : 'border-border hover:border-primary/50 hover:bg-accent/50'
                    ]"
                  >
                    <div class="flex items-center space-x-2 sm:space-x-3">
                      <component :is="themeOption.icon" class="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" />
                      <div class="min-w-0">
                        <span class="text-sm sm:text-base font-medium block">{{ themeOption.name }}</span>
                        <p class="text-xs sm:text-sm text-muted-foreground mt-0.5">
                          {{ themeOption.description }}
                        </p>
                      </div>
                      <!-- Selection indicator -->
                      <div v-if="theme === themeOption.value" class="flex-shrink-0">
                        <div class="w-2 h-2 bg-primary rounded-full"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <div class="space-y-4">
                <h4 class="text-base sm:text-lg font-medium">폰트</h4>
                <p class="text-sm sm:text-base text-muted-foreground">
                  인터페이스에 사용할 폰트를 선택하세요.
                </p>
                <!-- Responsive grid: 1 column on mobile, 2 on tablet, 2 on desktop for fonts -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                  <div 
                    v-for="fontOption in fontOptions"
                    :key="fontOption.value"
                    @click="changeFont(fontOption.value)"
                    :class="[
                      'border rounded-lg p-3 sm:p-4 cursor-pointer transition-all hover:scale-105',
                      font === fontOption.value 
                        ? 'border-primary bg-primary/10 ring-2 ring-primary/20' 
                        : 'border-border hover:border-primary/50 hover:bg-accent/50'
                    ]"
                  >
                    <div class="flex items-center space-x-2 sm:space-x-3">
                      <div class="min-w-0 flex-1">
                        <span class="text-sm sm:text-base font-medium block" :style="{ fontFamily: fontOption.value }">{{ fontOption.name }}</span>
                        <p class="text-xs sm:text-sm text-muted-foreground mt-0.5">
                          {{ fontOption.description }}
                        </p>
                        <!-- Font sample -->
                        <p class="text-xs text-muted-foreground mt-1 truncate" :style="{ fontFamily: fontOption.value }">
                          가나다라 ABCD 1234
                        </p>
                      </div>
                      <!-- Selection indicator -->
                      <div v-if="font === fontOption.value" class="flex-shrink-0">
                        <div class="w-2 h-2 bg-primary rounded-full"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Security Tab -->
          <div v-else-if="selectedCategory === 'security'" class="space-y-6">
            <div class="space-y-2">
              <h3 class="text-lg sm:text-xl font-medium">보안 설정</h3>
              <p class="text-sm sm:text-base text-muted-foreground">계정 보안 관련 설정을 관리합니다.</p>
            </div>

            <div class="space-y-6">
              <div class="space-y-4">
                <h4 class="text-base sm:text-lg font-medium">비밀번호 변경</h4>
                <div class="space-y-4">
                  <div class="flex flex-col sm:grid sm:grid-cols-4 gap-2 sm:gap-4 items-start sm:items-center">
                    <Label class="text-sm font-medium sm:text-right">비밀번호</Label>
                    <div class="col-span-3 w-full flex flex-col sm:flex-row gap-2 sm:gap-3">
                      <Input
                        disabled
                        type="password"
                        model-value="********"
                        class="flex-1 h-10 sm:h-11 text-sm sm:text-base bg-muted"
                      />
                      <Button
                        variant="outline"
                        @click="handleChangePassword"
                        class="w-full sm:w-auto h-10 sm:h-11 text-sm sm:text-base"
                      >
                        변경
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <div class="space-y-4">
                <h4 class="text-base sm:text-lg font-medium">로그인 세션 관리</h4>
                <p class="text-sm sm:text-base text-muted-foreground">
                  현재 활성화된 로그인 세션을 관리합니다.
                </p>
                <div class="space-y-2">
                  <Button
                    variant="outline"
                    disabled
                    class="w-full sm:w-auto h-10 sm:h-11 text-sm sm:text-base"
                  >
                    다른 기기에서 로그아웃
                  </Button>
                  <p class="text-xs sm:text-sm text-muted-foreground">이 기능은 현재 개발 중입니다.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Password Change Dialog -->
      <PasswordChangeDialog
        :open="isPasswordDialogOpen"
        @update:open="isPasswordDialogOpen = $event"
        @password-changed="handlePasswordChanged"
      />
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Monitor, Moon, Sun } from 'lucide-vue-next';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { useTheme, useToast, useFont } from '@/core/composables';
import { container } from 'tsyringe';
import MemberRepository from '@/features/member/repository/MemberRepository';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository';
import type Member from '@/features/member/entity/Member';
import type EmployeeMyInfo from '@/features/employee/entity/EmployeeMyInfo';
import PasswordChangeDialog from '@/features/member/components/PasswordChangeDialog.vue';

interface Props {
  open: boolean;
}

defineProps<Props>();
defineEmits<{
  'update:open': [value: boolean];
}>();

const toast = useToast();
const { theme, setTheme } = useTheme();
const { font, setFont, availableFonts } = useFont();
const MEMBER_REPOSITORY = container.resolve(MemberRepository);
const EMPLOYEE_REPOSITORY = container.resolve(EmployeeRepository);

const member = ref<Member | null>(null);
const employee = ref<EmployeeMyInfo | null>(null);
const loading = ref(true);
const isPasswordDialogOpen = ref(false);
const selectedCategory = ref('profile');

const categories = [
  { key: 'profile', name: '프로필' },
  { key: 'account', name: '내 계정 정보' },
  { key: 'appearance', name: '환경 설정' },
  { key: 'security', name: '보안설정' },
];

const themeOptions = [
  {
    value: 'light',
    name: '라이트',
    description: '밝은 테마',
    icon: Sun,
  },
  {
    value: 'dark',
    name: '다크',
    description: '어두운 테마',
    icon: Moon,
  },
  {
    value: 'system',
    name: '시스템',
    description: '시스템 설정 따름',
    icon: Monitor,
  },
];

const fontOptions = [
  {
    value: 'Pretendard',
    name: 'Pretendard',
    description: '기본 한글 폰트',
  },
  {
    value: 'D2Coding',
    name: 'D2Coding',
    description: '개발자 전용 폰트',
  },
  {
    value: 'IBM Plex Mono',
    name: 'IBM Plex Mono',
    description: 'IBM 모노스페이스 폰트',
  },
  {
    value: 'Roboto Mono',
    name: 'Roboto Mono',
    description: 'Google 모노스페이스 폰트',
  },
  {
    value: 'Courier New',
    name: 'Courier New',
    description: '시스템 모노스페이스 폰트',
  },
];

const profileForm = ref({
  username: '',
  email: '',
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

    // Employee 정보도 가져오기 (있는 경우에만)
    try {
      const myEmployee = await EMPLOYEE_REPOSITORY.getMyEmployee();
      employee.value = myEmployee;
      localStorage.setItem('employee', JSON.stringify(myEmployee));
    } catch (employeeError) {
      console.log('Employee info not available:', employeeError);
      // Employee 정보가 없어도 계속 진행
    }

    // 로컬 스토리지 업데이트
    localStorage.setItem('user', JSON.stringify(myInfo));

    // ProfileForm에 초기 데이터 설정
    profileForm.value.username = myInfo.name || '';
    profileForm.value.email = myInfo.username || '';
  } catch (error) {
    console.error('Error loading user info:', error);
    toast.error('프로필 정보 로드 실패', {
      description: '사용자 정보를 불러오는데 실패했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
  } finally {
    loading.value = false;
  }
}

// 프로필 업데이트 함수
function updateProfile() {
  console.log('Updating profile with:', profileForm.value);
  toast.success('프로필 업데이트 완료', {
    description: '프로필 정보가 성공적으로 업데이트되었습니다.',
    position: 'bottom-right',
  });
  // 실제 API 호출 로직 추가
}

// 비밀번호 변경 다이얼로그 열기
function handleChangePassword() {
  isPasswordDialogOpen.value = true;
}

// 폰트 변경 함수
function changeFont(fontValue: string) {
  const selectedFontOption = fontOptions.find(f => f.value === fontValue);
  if (selectedFontOption) {
    // useFont composable을 사용하여 폰트 변경
    setFont(fontValue as any);
    
    toast.success('폰트 변경 완료', {
      description: `${selectedFontOption.name} 폰트로 변경되었습니다.`,
      position: 'bottom-right',
    });
  }
}

// 비밀번호 변경 완료 후 처리
function handlePasswordChanged() {
  loadUserInfo();
}

onMounted(() => {
  loadUserInfo();
  // useFont composable이 이미 폰트를 처리하므로 별도 처리 불필요
});
</script>

<style scoped>
/* Force override shadcn-vue dialog max-width constraints */
:deep([data-slot="dialog-content"]) {
  max-width: min(80vw, 900px) !important;
  width: 80vw !important;
}

@media (min-width: 640px) {
  :deep([data-slot="dialog-content"]) {
    max-width: min(75vw, 900px) !important;
    width: 75vw !important;
  }
}

@media (min-width: 768px) {
  :deep([data-slot="dialog-content"]) {
    max-width: min(70vw, 900px) !important;
    width: 70vw !important;
  }
}

@media (min-width: 1024px) {
  :deep([data-slot="dialog-content"]) {
    max-width: min(65vw, 900px) !important;
    width: 65vw !important;
  }
}

@media (min-width: 1280px) {
  :deep([data-slot="dialog-content"]) {
    max-width: min(60vw, 900px) !important;
    width: 60vw !important;
  }
}
</style>