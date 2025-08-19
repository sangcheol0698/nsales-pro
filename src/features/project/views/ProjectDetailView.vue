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
          <h3 class="text-lg font-semibold text-foreground mb-2">프로젝트 정보를 불러올 수 없습니다</h3>
          <p class="text-muted-foreground mb-4">{{ error }}</p>
          <div class="flex gap-2 justify-center">
            <Button variant="outline" @click="$router.go(-1)">
              <ArrowLeft class="mr-2 h-4 w-4" />
              이전으로
            </Button>
            <Button @click="loadProject">
              <RefreshCw class="mr-2 h-4 w-4" />
              다시 시도
            </Button>
          </div>
        </div>

        <!-- 프로젝트 정보 -->
        <div v-else-if="project" class="space-y-6">
          <!-- 헤더 -->
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-foreground">{{ project.name }}</h1>
              <div class="flex items-center gap-2 mt-1">
                <Badge variant="outline">{{ project.code }}</Badge>
                <StatusBadge :status="project.status" type="project" />
              </div>
            </div>
            <div class="flex gap-2">
              <Button variant="outline" @click="onEditProject">
                <Edit3 class="mr-2 h-4 w-4" />
                수정
              </Button>
              <Button variant="destructive" @click="onDeleteProject">
                <Trash2 class="mr-2 h-4 w-4" />
                삭제
              </Button>
            </div>
          </div>

          <!-- 기본 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <FolderOpen class="h-5 w-5" />
                프로젝트 기본 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">프로젝트명</Label>
                  <p class="font-medium">{{ project.name }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">프로젝트 코드</Label>
                  <p class="font-medium font-mono">{{ project.code }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">유형</Label>
                  <Badge variant="secondary">{{ project.type }}</Badge>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">상태</Label>
                  <StatusBadge :status="project.status" type="project" />
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">계약일</Label>
                  <p class="font-medium">{{ formatDate(project.contractDate) }}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 일정 및 금액 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Calendar class="h-5 w-5" />
                일정 및 금액 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">시작일</Label>
                  <p class="font-medium">{{ formatDate(project.startDate) }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">종료일</Label>
                  <p class="font-medium">{{ formatDate(project.endDate) }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">프로젝트 기간</Label>
                  <p class="font-medium">{{ projectDuration }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">계약 금액</Label>
                  <p class="font-medium text-lg">{{ formatAmount(project.contractAmount) }}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 관련 회사 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Building2 class="h-5 w-5" />
                관련 회사 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">주관사</Label>
                  <p class="font-medium">{{ project.mainCompany || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">고객사</Label>
                  <p class="font-medium">{{ project.clientCompany || '-' }}</p>
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
                  <p class="font-medium">{{ formatDateTime(project.createdAt) }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">수정일시</Label>
                  <p class="font-medium">{{ formatDateTime(project.updatedAt) }}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>

    <!-- 프로젝트 수정 다이얼로그 -->
    <ProjectEditDialog
      v-model:open="editDialogOpen"
      :loading="editLoading"
      :project="project"
      @submit="handleEditSubmit"
    />

    <!-- 프로젝트 삭제 다이얼로그 -->
    <ProjectDeleteDialog
      v-model:open="deleteDialogOpen"
      :loading="deleteLoading"
      :project="project"
      @confirm="handleDeleteConfirm"
    />
  </SidebarLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { container } from 'tsyringe';
import ProjectRepository from '@/features/project/repository/ProjectRepository.ts';
import ProjectSearch from '@/features/project/entity/ProjectSearch.ts';
import ProjectUpdate from '@/features/project/entity/ProjectUpdate.ts';
import ProjectEditDialog from '@/features/project/components/ProjectEditDialog.vue';
import ProjectDeleteDialog from '@/features/project/components/ProjectDeleteDialog.vue';
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
import { Badge } from '@/components/ui/badge';
import {
  AlertCircle,
  ArrowLeft,
  Building2,
  Calendar,
  Clock,
  Edit3,
  FolderOpen,
  Loader2,
  RefreshCw,
  Trash2,
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const PROJECT_REPOSITORY = container.resolve(ProjectRepository);

// 상태 관리
const loading = ref(true);
const error = ref<string | null>(null);
const project = ref<ProjectSearch | null>(null);

// 수정/삭제 다이얼로그 상태
const editDialogOpen = ref(false);
const editLoading = ref(false);
const deleteDialogOpen = ref(false);
const deleteLoading = ref(false);

// 프로젝트 기간 계산
const projectDuration = computed(() => {
  if (!project.value?.startDate || !project.value?.endDate) return '-';
  
  const startDate = new Date(project.value.startDate);
  const endDate = new Date(project.value.endDate);
  
  const diffTime = endDate.getTime() - startDate.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays <= 0) return '-';
  
  const months = Math.floor(diffDays / 30);
  const remainingDays = diffDays % 30;
  
  if (months > 0) {
    return `${months}개월 ${remainingDays}일`;
  } else {
    return `${diffDays}일`;
  }
});

// 프로젝트 정보 로드
async function loadProject() {
  const projectId = route.params.id as string;
  
  if (!projectId || isNaN(Number(projectId))) {
    error.value = '잘못된 프로젝트 ID입니다.';
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;
    
    project.value = await PROJECT_REPOSITORY.getProject(Number(projectId));
    console.log('프로젝트 상세 정보 로드 완료:', project.value);
    
  } catch (err: any) {
    console.error('프로젝트 정보 로드 실패:', err);
    error.value = err.message || '프로젝트 정보를 불러오는데 실패했습니다.';
    project.value = null;
  } finally {
    loading.value = false;
  }
}

// 날짜 포맷팅
function formatDate(dateString: string | undefined): string {
  if (!dateString) return '-';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  } catch {
    return dateString;
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

// 금액 포맷팅
function formatAmount(amount: number | undefined): string {
  if (!amount || amount === 0) return '-';
  
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
  }).format(amount);
}

// 수정 버튼 핸들러
function onEditProject() {
  if (!project.value) return;
  editDialogOpen.value = true;
}

// 삭제 버튼 핸들러
function onDeleteProject() {
  if (!project.value) return;
  deleteDialogOpen.value = true;
}

// 프로젝트 수정 처리
async function handleEditSubmit(projectData: ProjectUpdate) {
  editLoading.value = true;

  try {
    console.log('프로젝트 수정 요청:', projectData);

    await PROJECT_REPOSITORY.updateProject(projectData);

    toast.success('프로젝트 수정 완료', {
      description: `${projectData.name}의 정보가 성공적으로 수정되었습니다.`,
      position: 'bottom-right',
    });

    // 다이얼로그 닫기
    editDialogOpen.value = false;

    // 프로젝트 정보 새로고침
    await loadProject();

  } catch (error: any) {
    console.error('프로젝트 수정 실패:', error);

    let errorMessage = '프로젝트 수정 중 오류가 발생했습니다.';
    if (error?.message?.includes('modifiedDateTime')) {
      errorMessage = '다른 사용자가 이미 수정했습니다. 새로고침 후 다시 시도해주세요.';
    }

    toast.error('프로젝트 수정 실패', {
      description: errorMessage,
      position: 'bottom-right',
    });
  } finally {
    editLoading.value = false;
  }
}

// 프로젝트 삭제 처리
async function handleDeleteConfirm(projectId: number) {
  deleteLoading.value = true;

  try {
    console.log('프로젝트 삭제 요청:', projectId);

    const projectName = project.value?.name || '';

    await PROJECT_REPOSITORY.deleteProject(projectId);

    toast.success('프로젝트 삭제 완료', {
      description: `${projectName}이(가) 성공적으로 삭제되었습니다.`,
      position: 'bottom-right',
    });

    // 목록으로 이동
    router.push('/projects');

  } catch (error: any) {
    console.error('프로젝트 삭제 실패:', error);

    toast.error('프로젝트 삭제 실패', {
      description: '프로젝트 삭제 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  } finally {
    deleteLoading.value = false;
  }
}

// 컴포넌트 마운트 시 프로젝트 정보 로드
onMounted(() => {
  loadProject();
});
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>