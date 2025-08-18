<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full max-w-4xl mx-auto">
        <!-- 로딩 상태 -->
        <div v-if="loading" class="flex justify-center items-center h-64">
          <Loader2 class="h-8 w-8 animate-spin" />
        </div>

        <!-- 에러 상태 -->
        <div v-else-if="error" class="text-center p-8">
          <AlertCircle class="h-12 w-12 text-destructive mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-foreground mb-2">구성원 정보를 불러올 수 없습니다</h3>
          <p class="text-muted-foreground mb-4">{{ error }}</p>
          <div class="flex gap-2 justify-center">
            <Button variant="outline" @click="$router.go(-1)">
              <ArrowLeft class="mr-2 h-4 w-4" />
              이전으로
            </Button>
            <Button @click="loadEmployee">
              <RefreshCw class="mr-2 h-4 w-4" />
              다시 시도
            </Button>
          </div>
        </div>

        <!-- 구성원 정보 -->
        <div v-else-if="employee" class="space-y-6">
          <!-- 헤더 -->
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-foreground">{{ employee.name }}</h1>
              <p class="text-muted-foreground">{{ employee.code }}</p>
            </div>
            <div class="flex gap-2">
              <Button variant="outline" @click="onEditEmployee">
                <Edit3 class="mr-2 h-4 w-4" />
                수정
              </Button>
              <Button variant="destructive" @click="onDeleteEmployee">
                <Trash2 class="mr-2 h-4 w-4" />
                삭제
              </Button>
            </div>
          </div>

          <!-- 기본 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <User class="h-5 w-5" />
                기본 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">이름</Label>
                  <p class="font-medium">{{ employee.name }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">사원코드</Label>
                  <p class="font-medium">{{ employee.code }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">이메일</Label>
                  <p class="font-medium">{{ employee.email }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">생년월일</Label>
                  <p class="font-medium">{{ employee.birthDate || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">전화번호</Label>
                  <p class="font-medium">{{ employee.phone || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">상태</Label>
                  <StatusBadge :status="employee.status" type="employee" />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 조직 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Building2 class="h-5 w-5" />
                조직 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">소속 부서</Label>
                  <p class="font-medium">{{ employee.teamName || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">직급</Label>
                  <p class="font-medium">{{ employee.rank || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">등급</Label>
                  <p class="font-medium">{{ employee.grade || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">유형</Label>
                  <p class="font-medium">{{ employee.type || '-' }}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 근무 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Calendar class="h-5 w-5" />
                근무 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">입사일</Label>
                  <p class="font-medium">{{ employee.joinDate || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">퇴사일</Label>
                  <p class="font-medium">{{ employee.leaveDate || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">근무 기간</Label>
                  <p class="font-medium">{{ workPeriod }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">근무 상태</Label>
                  <p class="font-medium">{{ employee.status === '퇴사' ? '퇴사' : '재직중' }}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 시스템 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Clock class="h-5 w-5" />
                시스템 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">등록일시</Label>
                  <p class="font-medium">{{ formatDateTime(employee.createdAt) }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">수정일시</Label>
                  <p class="font-medium">{{ formatDateTime(employee.updatedAt) }}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>

    <!-- 구성원 수정 다이얼로그 -->
    <EmployeeEditDialog
      v-model:open="editDialogOpen"
      :loading="editLoading"
      :employee="employee"
      @submit="handleEditSubmit"
    />

    <!-- 구성원 삭제 다이얼로그 -->
    <EmployeeDeleteDialog
      v-model:open="deleteDialogOpen"
      :loading="deleteLoading"
      :employee="employee"
      @confirm="handleDeleteConfirm"
    />
  </SidebarLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { container } from 'tsyringe';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository.ts';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch.ts';
import EmployeeUpdate from '@/features/employee/entity/EmployeeUpdate.ts';
import EmployeeEditDialog from '@/features/employee/components/EmployeeEditDialog.vue';
import EmployeeDeleteDialog from '@/features/employee/components/EmployeeDeleteDialog.vue';
import { SidebarLayout } from '@/components/layout';
import { StatusBadge } from '@/components/business';
import { useToast } from '@/core/composables';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  AlertCircle,
  ArrowLeft,
  Building2,
  Calendar,
  Clock,
  Edit3,
  Loader2,
  RefreshCw,
  Trash2,
  User,
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const EMPLOYEE_REPOSITORY = container.resolve(EmployeeRepository);

// 상태 관리
const loading = ref(true);
const error = ref<string | null>(null);
const employee = ref<EmployeeSearch | null>(null);

// 수정/삭제 다이얼로그 상태
const editDialogOpen = ref(false);
const editLoading = ref(false);
const deleteDialogOpen = ref(false);
const deleteLoading = ref(false);

// 근무 기간 계산
const workPeriod = computed(() => {
  if (!employee.value?.joinDate) return '-';
  
  const joinDate = new Date(employee.value.joinDate);
  const endDate = employee.value.leaveDate ? new Date(employee.value.leaveDate) : new Date();
  
  const diffTime = endDate.getTime() - joinDate.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  const diffYears = Math.floor(diffDays / 365);
  const remainingDays = diffDays % 365;
  
  if (diffYears > 0) {
    return `${diffYears}년 ${remainingDays}일`;
  } else {
    return `${diffDays}일`;
  }
});

// 구성원 정보 로드
async function loadEmployee() {
  const employeeId = route.params.id as string;
  
  if (!employeeId || isNaN(Number(employeeId))) {
    error.value = '잘못된 구성원 ID입니다.';
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;
    
    employee.value = await EMPLOYEE_REPOSITORY.getEmployee(Number(employeeId));
    console.log('구성원 상세 정보 로드 완료:', employee.value);
    
  } catch (err: any) {
    console.error('구성원 정보 로드 실패:', err);
    error.value = err.message || '구성원 정보를 불러오는데 실패했습니다.';
    employee.value = null;
  } finally {
    loading.value = false;
  }
}

// 날짜시간 포맷팅
function formatDateTime(dateTimeString: string | undefined): string {
  if (!dateTimeString) return '-';
  
  try {
    const date = new Date(dateTimeString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateTimeString;
  }
}

// 수정 버튼 핸들러
function onEditEmployee() {
  if (!employee.value) return;
  editDialogOpen.value = true;
}

// 삭제 버튼 핸들러
function onDeleteEmployee() {
  if (!employee.value) return;
  deleteDialogOpen.value = true;
}

// 구성원 수정 처리
async function handleEditSubmit(employeeData: EmployeeUpdate) {
  editLoading.value = true;

  try {
    console.log('구성원 수정 요청:', employeeData);

    await EMPLOYEE_REPOSITORY.updateEmployee(employeeData);

    toast.success('구성원 수정 완료', {
      description: `${employeeData.name}의 정보가 성공적으로 수정되었습니다.`,
      position: 'bottom-right',
    });

    // 다이얼로그 닫기
    editDialogOpen.value = false;

    // 구성원 정보 새로고침
    await loadEmployee();

  } catch (error: any) {
    console.error('구성원 수정 실패:', error);

    let errorMessage = '구성원 수정 중 오류가 발생했습니다.';
    if (error?.message?.includes('modifiedDateTime')) {
      errorMessage = '다른 사용자가 이미 수정했습니다. 새로고침 후 다시 시도해주세요.';
    }

    toast.error('구성원 수정 실패', {
      description: errorMessage,
      position: 'bottom-right',
    });
  } finally {
    editLoading.value = false;
  }
}

// 구성원 삭제 처리
async function handleDeleteConfirm(employeeId: number) {
  deleteLoading.value = true;

  try {
    console.log('구성원 삭제 요청:', employeeId);

    const employeeName = employee.value?.name || '';

    await EMPLOYEE_REPOSITORY.deleteEmployee(employeeId);

    toast.success('구성원 삭제 완료', {
      description: `${employeeName}이(가) 성공적으로 삭제되었습니다.`,
      position: 'bottom-right',
    });

    // 목록으로 이동
    router.push('/employees');

  } catch (error: any) {
    console.error('구성원 삭제 실패:', error);

    toast.error('구성원 삭제 실패', {
      description: '구성원 삭제 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  } finally {
    deleteLoading.value = false;
  }
}

// 컴포넌트 마운트 시 구성원 정보 로드
onMounted(() => {
  loadEmployee();
});
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>