<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <div class="flex items-center justify-between py-4">
          <h2 class="text-2xl font-bold">프로젝트 상세</h2>
          <Button variant="outline" @click="goBack">
            <ArrowLeft class="mr-2 h-4 w-4" />
            돌아가기
          </Button>
        </div>
        <div v-if="loading" class="flex justify-center items-center p-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        <div v-else-if="project" class="grid gap-6">
          <!-- 프로젝트 기본 정보 -->
          <Card>
            <CardHeader>
              <CardTitle>기본 정보</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">프로젝트명</span>
                  <span class="font-medium">{{ project.name }}</span>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">코드</span>
                  <span class="font-medium">{{ project.code }}</span>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">유형</span>
                  <span class="font-medium">{{ project.type }}</span>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">상태</span>
                  <span class="font-medium">{{ project.status }}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 프로젝트 계약 정보 -->
          <Card>
            <CardHeader>
              <CardTitle>계약 정보</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">계약일</span>
                  <span class="font-medium">{{ project.contractDate }}</span>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">계약금액</span>
                  <span class="font-medium">{{ formatCurrency(project.contractAmount) }}</span>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">시작일</span>
                  <span class="font-medium">{{ project.startDate }}</span>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">종료일</span>
                  <span class="font-medium">{{ project.endDate }}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 프로젝트 관련 회사 정보 -->
          <Card>
            <CardHeader>
              <CardTitle>관련 회사</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">주관사</span>
                  <span class="font-medium">{{ project.mainCompany }}</span>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm text-muted-foreground">고객사</span>
                  <span class="font-medium">{{ project.clientCompany }}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <div v-else class="flex flex-col items-center justify-center p-8">
          <p class="text-lg font-medium">프로젝트를 찾을 수 없습니다</p>
          <p class="text-sm text-muted-foreground">
            요청하신 프로젝트가 존재하지 않거나 접근 권한이 없습니다
          </p>
        </div>
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { SidebarLayout } from '@/shared/components/sidebar';
import { Button } from '@/core/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/core/components/ui/card';
import { ArrowLeft } from 'lucide-vue-next';
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { container } from 'tsyringe';
import ProjectRepository from '@/features/project/repository/ProjectRepository';
import type { ProjectSearch } from '@/features/project/entity/ProjectSearch';
import { useToast } from '@/core/composables';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const PROJECT_REPOSITORY = container.resolve(ProjectRepository);

const project = ref<ProjectSearch | null>(null);
const loading = ref(true);

// 프로젝트 ID 가져오기
const projectId = computed(() => {
  return Number(route.params.id);
});

// 프로젝트 상세 정보 가져오기
const fetchProject = async () => {
  loading.value = true;
  try {
    // 실제 API가 구현되면 아래 주석을 해제하고 사용
    // const response = await PROJECT_REPOSITORY.getProject(projectId.value);
    // project.value = response;

    // 목업 데이터 (API 구현 전까지 사용)
    // API 호출을 시뮬레이션하기 위해 setTimeout 사용
    setTimeout(() => {
      // 실제로는 API에서 받아온 데이터를 사용
      project.value = {
        id: projectId.value,
        code: 'PRJ-' + projectId.value.toString().padStart(4, '0'),
        name: '샘플 프로젝트 ' + projectId.value,
        type: '개발',
        startDate: '2023-01-01',
        endDate: '2023-12-31',
        contractDate: '2022-12-15',
        contractAmount: 50000000,
        mainCompany: '아바커스',
        clientCompany: '클라이언트 회사',
        status: '진행중',
        createdAt: '2022-12-15',
        updatedAt: '2023-01-01',
      };
      loading.value = false;
    }, 1000);
  } catch (error) {
    toast.error('프로젝트 정보 로드 실패', {
      description: '프로젝트 정보를 불러오는 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
    loading.value = false;
  }
};

// 이전 페이지로 돌아가기
const goBack = () => {
  router.push('/projects');
};

// 금액 포맷팅
const formatCurrency = (amount: number) => {
  return amount ? amount.toLocaleString() + '원' : '-';
};

onMounted(() => {
  fetchProject();
});
</script>

<style scoped></style>
