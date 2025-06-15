<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="max-w-4xl mx-auto w-full">
        <Card>
          <CardHeader class="flex flex-col gap-1">
            <CardTitle class="text-xl">설정</CardTitle>
            <CardDescription>계정 설정 및 이메일 환경설정을 관리합니다.</CardDescription>
          </CardHeader>
          <CardContent>
            <div v-if="loading" class="flex justify-center items-center p-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
            <div v-else class="flex gap-8">
              <aside class="w-48 flex-shrink-0">
                <nav class="space-y-1">
                  <a
                    href="#"
                    @click.prevent="selectedCategory = 'profile'"
                    :class="[
                      'block rounded-md px-3 py-2 text-sm font-medium',
                      selectedCategory === 'profile'
                        ? 'bg-secondary text-secondary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                    ]"
                  >
                    프로필
                  </a>
                  <a
                    href="#"
                    @click.prevent="selectedCategory = 'account'"
                    :class="[
                      'block rounded-md px-3 py-2 text-sm font-medium',
                      selectedCategory === 'account'
                        ? 'bg-secondary text-secondary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                    ]"
                  >
                    내 계정 정보
                  </a>
                  <a
                    href="#"
                    @click.prevent="selectedCategory = 'appearance'"
                    :class="[
                      'block rounded-md px-3 py-2 text-sm font-medium',
                      selectedCategory === 'appearance'
                        ? 'bg-secondary text-secondary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                    ]"
                  >
                    환경 설정
                  </a>
                  <a
                    href="#"
                    @click.prevent="selectedCategory = 'notifications'"
                    :class="[
                      'block rounded-md px-3 py-2 text-sm font-medium',
                      selectedCategory === 'notifications'
                        ? 'bg-secondary text-secondary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                    ]"
                  >
                    보안설정
                  </a>
                  <a
                    href="#"
                    @click.prevent="selectedCategory = 'display'"
                    :class="[
                      'block rounded-md px-3 py-2 text-sm font-medium',
                      selectedCategory === 'display'
                        ? 'bg-secondary text-secondary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                    ]"
                  >
                    활동 내역
                  </a>
                </nav>
              </aside>

              <div class="flex-1">
                <div v-if="selectedCategory === 'profile'" class="space-y-6">
                  <div class="space-y-2">
                    <h3 class="text-lg font-medium">프로필</h3>
                    <p class="text-sm text-muted-foreground">
                      사이트에서 다른 사용자에게 보여지는 정보입니다.
                    </p>
                  </div>

                  <div class="space-y-6">
                    <div class="space-y-4">
                      <div class="grid w-full items-center gap-1.5">
                        <Label htmlFor="username">사용자 이름</Label>
                        <Input id="username" v-model="profileForm.username" placeholder="이름" />
                        <p class="text-sm text-muted-foreground mt-1">
                          공개적으로 표시되는 이름입니다. 실명이나 가명을 사용할 수 있습니다. 30일에
                          한 번만 변경할 수 있습니다.
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

                        <div class="grid grid-cols-4 items-center gap-4">
                          <Label class="text-right">고용 형태</Label>
                          <div class="col-span-3">
                            <Input
                              disabled
                              :value="member?.type"
                              placeholder="등록된 고용 형태가 없습니다"
                            />
                          </div>
                        </div>

                        <div class="grid grid-cols-4 items-center gap-4">
                          <Label class="text-right">입사일</Label>
                          <div class="col-span-3">
                            <Input
                              disabled
                              :value="member?.joinDate"
                              placeholder="등록된 입사일이 없습니다"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else-if="selectedCategory === 'appearance'" class="space-y-6">
                  <div class="space-y-2">
                    <h3 class="text-lg font-medium">환경 설정</h3>
                    <p class="text-sm text-muted-foreground">
                      앱의 테마 및 폰트 설정을 관리합니다.
                    </p>
                  </div>

                  <div class="space-y-6">
                    <AppearanceForm />
                  </div>
                </div>

                <div v-else-if="selectedCategory === 'notifications'" class="space-y-6">
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
                            <Button variant="outline" @click="handleChangePassword"> 변경</Button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div class="space-y-4">
                      <div class="flex items-center justify-between">
                        <div>
                          <h4 class="text-sm font-medium">2단계 인증</h4>
                          <p class="text-sm text-muted-foreground">
                            계정 보안을 강화하기 위한 2단계 인증을 설정합니다.
                          </p>
                        </div>
                        <Switch disabled />
                      </div>
                      <p class="text-xs text-muted-foreground">이 기능은 현재 개발 중입니다.</p>
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

                <div v-else-if="selectedCategory === 'display'" class="space-y-6">
                  <div class="space-y-2">
                    <h3 class="text-lg font-medium">활동 내역</h3>
                    <p class="text-sm text-muted-foreground">최근 계정 활동 내역을 확인합니다.</p>
                  </div>
                  <div class="space-y-4">
                    <div class="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>활동</TableHead>
                            <TableHead>날짜</TableHead>
                            <TableHead>IP 주소</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow>
                            <TableCell>로그인</TableCell>
                            <TableCell>2023-06-01 09:30:45</TableCell>
                            <TableCell>192.168.1.1</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>비밀번호 변경</TableCell>
                            <TableCell>2023-05-15 14:22:10</TableCell>
                            <TableCell>192.168.1.1</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>
                    <p class="text-xs text-muted-foreground">
                      이 기능은 현재 개발 중이며, 샘플 데이터만 표시됩니다.
                    </p>
                  </div>
                </div>

                <div v-else class="space-y-6">
                  <div class="space-y-2">
                    <h3 class="text-lg font-medium">{{ selectedCategory }}</h3>
                    <p class="text-sm text-muted-foreground">
                      {{ selectedCategory }} 설정을 관리합니다.
                    </p>
                  </div>
                  <div class="text-center p-4 border rounded-md bg-muted/10">
                    <p>{{ selectedCategory }} 설정 내용이 여기에 표시됩니다.</p>
                    <p class="text-sm text-muted-foreground mt-2">이 기능은 현재 개발 중입니다.</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>

    <PasswordChangeDialog
      :open="isPasswordDialogOpen"
      @update:open="isPasswordDialogOpen = $event"
      @password-changed="handlePasswordChanged"
    />
  </SidebarLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { SidebarLayout } from '@/shared/components/sidebar';
import Card from '@/core/components/ui/card/Card.vue';
import CardContent from '@/core/components/ui/card/CardContent.vue';
import CardDescription from '@/core/components/ui/card/CardDescription.vue';
import CardHeader from '@/core/components/ui/card/CardHeader.vue';
import CardTitle from '@/core/components/ui/card/CardTitle.vue';
import Button from '@/core/components/ui/button/Button.vue';
import Input from '@/core/components/ui/input/Input.vue';
import Label from '@/core/components/ui/label/Label.vue';
import Separator from '@/core/components/ui/separator/Separator.vue';
import Switch from '@/core/components/ui/switch/Switch.vue';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/core/components/ui/table';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import MemberRepository from '@/features/member/repository/MemberRepository.ts';
import type Member from '@/features/member/entity/Member';
import PasswordChangeDialog from '@/features/member/components/PasswordChangeDialog.vue';
import AppearanceForm from '@/features/member/components/AppearanceForm.vue';

const toast = useToast();
const MEMBER_REPOSITORY = container.resolve(MemberRepository);

const member = ref<Member | null>(null);
const loading = ref(true);
const isPasswordDialogOpen = ref(false);

// 현재 선택된 설정 카테고리 (기본값 'profile'로 설정)
const selectedCategory = ref('profile');

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

// 비밀번호 변경 다이얼로그 열기
function handleChangePassword() {
  isPasswordDialogOpen.value = true;
}

// 비밀번호 변경 완료 후 처리
function handlePasswordChanged() {
  // 사용자 정보 다시 로드
  loadUserInfo();
}

// 프로필 사진 업로드 완료 후 처리
function handleProfilePictureUploaded() {
  // 사용자 정보 다시 로드
  loadUserInfo();

  // 실제 API가 구현되면 아래 주석 해제
  // profileImageUrl.value = 업로드된 이미지 URL;

  // 현재는 임시로 성공 메시지만 표시
  toast.success('프로필 사진 변경 완료', {
    description: '프로필 사진이 성공적으로 변경되었습니다.',
    position: 'bottom-right',
  });
}
</script>

<style scoped></style>
