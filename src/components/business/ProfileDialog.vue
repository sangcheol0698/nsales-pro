<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>설정</DialogTitle>
        <DialogDescription>
          계정 설정 및 이메일 환경설정을 관리합니다.
        </DialogDescription>
      </DialogHeader>

      <div v-if="loading" class="flex justify-center items-center p-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
      
      <div v-else class="flex gap-6">
        <aside class="w-48 flex-shrink-0">
          <nav class="space-y-1">
            <button
              v-for="category in categories"
              :key="category.key"
              @click="selectedCategory = category.key"
              :class="[
                'block w-full text-left rounded-md px-3 py-2 text-sm font-medium transition-colors',
                selectedCategory === category.key
                  ? 'bg-secondary text-secondary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground',
              ]"
            >
              {{ category.name }}
            </button>
          </nav>
        </aside>

        <div class="flex-1 min-w-0">
          <!-- Profile Tab -->
          <div v-if="selectedCategory === 'profile'" class="space-y-6">
            <div class="space-y-2">
              <h3 class="text-lg font-medium">프로필</h3>
              <p class="text-sm text-muted-foreground">
                사이트에서 다른 사용자에게 보여지는 정보입니다.
              </p>
            </div>

            <div class="space-y-4">
              <div class="grid w-full items-center gap-1.5">
                <Label htmlFor="username">사용자 이름</Label>
                <Input id="username" v-model="profileForm.username" placeholder="이름" />
                <p class="text-sm text-muted-foreground">
                  공개적으로 표시되는 이름입니다. 실명이나 가명을 사용할 수 있습니다.
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
                <p class="text-sm text-muted-foreground">
                  이메일 설정에서 인증된 이메일 주소를 관리할 수 있습니다.
                </p>
              </div>

              <div class="grid w-full items-center gap-1.5">
                <Label htmlFor="bio">자기소개</Label>
                <Textarea
                  id="bio"
                  v-model="profileForm.bio"
                  placeholder="여기에 메시지를 입력하세요."
                  class="min-h-[100px]"
                />
                <p class="text-sm text-muted-foreground">
                  @멘션을 사용하여 다른 사용자나 조직을 언급할 수 있습니다.
                </p>
              </div>

              <Button @click="updateProfile">프로필 업데이트</Button>
            </div>
          </div>

          <!-- Account Tab -->
          <div v-else-if="selectedCategory === 'account'" class="space-y-6">
            <div class="space-y-2">
              <h3 class="text-lg font-medium">내 계정 정보</h3>
              <p class="text-sm text-muted-foreground">
                내 계정 정보를 확인하고 관리할 수 있습니다.
              </p>
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
                        :value="member?.phone"
                        placeholder="등록된 전화번호가 없습니다"
                      />
                    </div>
                  </div>
                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">생년월일</Label>
                    <div class="col-span-3">
                      <Input
                        disabled
                        :value="member?.birthDate"
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
                        :value="member?.departmentName"
                        placeholder="등록된 부서가 없습니다"
                      />
                    </div>
                  </div>
                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">직급</Label>
                    <div class="col-span-3">
                      <Input
                        disabled
                        :value="member?.rank"
                        placeholder="등록된 직급이 없습니다"
                      />
                    </div>
                  </div>
                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">등급</Label>
                    <div class="col-span-3">
                      <Input
                        disabled
                        :value="member?.grade"
                        placeholder="등록된 등급이 없습니다"
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
              <h3 class="text-lg font-medium">환경 설정</h3>
              <p class="text-sm text-muted-foreground">
                앱의 테마 및 폰트 설정을 관리합니다.
              </p>
            </div>

            <div class="space-y-6">
              <div class="space-y-4">
                <h4 class="text-sm font-medium">테마</h4>
                <p class="text-sm text-muted-foreground">
                  인터페이스 테마를 선택하세요.
                </p>
                <div class="grid grid-cols-3 gap-4">
                  <div 
                    v-for="themeOption in themeOptions"
                    :key="themeOption.value"
                    @click="setTheme(themeOption.value)"
                    :class="[
                      'border rounded-lg p-4 cursor-pointer transition-colors',
                      theme === themeOption.value 
                        ? 'border-primary bg-primary/10' 
                        : 'border-border hover:border-primary/50'
                    ]"
                  >
                    <div class="flex items-center space-x-2">
                      <component :is="themeOption.icon" class="h-4 w-4" />
                      <span class="text-sm font-medium">{{ themeOption.name }}</span>
                    </div>
                    <p class="text-xs text-muted-foreground mt-1">
                      {{ themeOption.description }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Security Tab -->
          <div v-else-if="selectedCategory === 'security'" class="space-y-6">
            <div class="space-y-2">
              <h3 class="text-lg font-medium">보안 설정</h3>
              <p class="text-sm text-muted-foreground">계정 보안 관련 설정을 관리합니다.</p>
            </div>
            
            <div class="space-y-6">
              <div class="space-y-4">
                <h4 class="text-sm font-medium">비밀번호 변경</h4>
                <div class="grid gap-4">
                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label class="text-right">비밀번호</Label>
                    <div class="col-span-3 flex items-center gap-2">
                      <Input disabled type="password" model-value="********" />
                      <Button variant="outline" @click="handleChangePassword">변경</Button>
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <div class="space-y-4">
                <h4 class="text-sm font-medium">로그인 세션 관리</h4>
                <p class="text-sm text-muted-foreground">
                  현재 활성화된 로그인 세션을 관리합니다.
                </p>
                <Button variant="outline" disabled>다른 기기에서 로그아웃</Button>
                <p class="text-xs text-muted-foreground">이 기능은 현재 개발 중입니다.</p>
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
import { Sun, Moon, Monitor } from 'lucide-vue-next';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/core/composables';
import { useTheme } from '@/core/composables';
import { container } from 'tsyringe';
import MemberRepository from '@/features/member/repository/MemberRepository';
import type Member from '@/features/member/entity/Member';
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
const MEMBER_REPOSITORY = container.resolve(MemberRepository);

const member = ref<Member | null>(null);
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

    // 로컬 스토리지 업데이트
    localStorage.setItem('user', JSON.stringify(myInfo));

    // ProfileForm에 초기 데이터 설정
    profileForm.value.username = myInfo.name || '';
    profileForm.value.email = myInfo.username || '';
  } catch (error) {
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

// 비밀번호 변경 완료 후 처리
function handlePasswordChanged() {
  loadUserInfo();
}

onMounted(() => {
  loadUserInfo();
});
</script>