<template>
  <div class="project-dashboard space-y-6">
    <!-- Project Status Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-blue-600">{{ projectStats.totalProjects }}</p>
            <p class="text-sm text-muted-foreground">전체 프로젝트</p>
            <div class="flex justify-center mt-2">
              <Badge variant="secondary">{{ new Date().getFullYear() }}년</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-green-600">{{ projectStats.activeProjects }}</p>
            <p class="text-sm text-muted-foreground">진행중</p>
            <Progress :value="projectProgressRate" class="mt-2" />
            <p class="text-xs text-muted-foreground mt-1">{{ projectProgressRate.toFixed(1) }}%</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-purple-600">{{ formatCurrency(projectStats.totalValue) }}</p>
            <p class="text-sm text-muted-foreground">총 프로젝트 가치</p>
            <div class="flex items-center justify-center mt-2">
              <TrendingUp class="h-4 w-4 text-green-500 mr-1" />
              <span class="text-sm text-green-600">+15.3%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-orange-600">{{ projectStats.completionRate.toFixed(1) }}%</p>
            <p class="text-sm text-muted-foreground">평균 완료율</p>
            <Progress :value="projectStats.completionRate" class="mt-2" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Project Status Distribution & Timeline -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 프로젝트 상태 분포 -->
      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <CardTitle>프로젝트 상태 분포</CardTitle>
            <Drawer>
              <DrawerTrigger asChild>
                <Button variant="ghost" size="sm">
                  <PieChart class="h-4 w-4 mr-2" />
                  상세보기
                </Button>
              </DrawerTrigger>
              <DrawerContent>
                <DrawerHeader class="text-center">
                  <DrawerTitle>프로젝트 상태별 상세 현황</DrawerTitle>
                  <DrawerDescription>
                    각 단계별 프로젝트 현황과 세부 정보
                  </DrawerDescription>
                </DrawerHeader>
                <div class="px-4 pb-4 space-y-4">
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div v-for="status in projectStatusDetail" :key="status.name"
                         class="text-center p-4 bg-muted/50 rounded-lg">
                      <p class="text-xl font-bold" :class="status.color">{{ status.count }}</p>
                      <p class="text-sm text-muted-foreground">{{ status.name }}</p>
                      <Progress :value="(status.count / projectStats.totalProjects) * 100" class="mt-2" />
                    </div>
                  </div>
                </div>
              </DrawerContent>
            </Drawer>
          </div>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="status in projectStatusDetail" :key="status.name"
                 class="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div class="flex items-center gap-3">
                <div class="h-3 w-3 rounded-full" :class="status.bgColor"></div>
                <span class="font-medium">{{ status.name }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="font-bold" :class="status.color">{{ status.count }}</span>
                <Badge variant="outline">{{ ((status.count / projectStats.totalProjects) * 100).toFixed(1) }}%</Badge>
              </div>
            </div>
          </div>

          <!-- 차트: 상태 분포 바 차트 -->
          <div class="h-64 mt-6">
            <BarChart :labels="statusLabels" :datasets="statusDatasets" />
          </div>
        </CardContent>
      </Card>

      <!-- 프로젝트 타임라인 -->
      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <CardTitle>진행 중인 프로젝트</CardTitle>
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm">
                  <Calendar class="h-4 w-4 mr-2" />
                  전체 일정
                </Button>
              </SheetTrigger>
              <SheetContent side="right" class="w-[700px]">
                <SheetHeader>
                  <SheetTitle>프로젝트 전체 일정</SheetTitle>
                  <SheetDescription>
                    모든 프로젝트의 일정과 마일스톤을 확인하세요
                  </SheetDescription>
                </SheetHeader>
                <div class="mt-6">
                  <div class="h-96 bg-muted/20 rounded-lg flex items-center justify-center">
                    <div class="text-center">
                      <Calendar class="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                      <p class="text-muted-foreground">Gantt Chart / Calendar View</p>
                      <p class="text-sm text-muted-foreground">프로젝트 일정 관리 시스템 연동 예정</p>
                    </div>
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            <div v-for="project in activeProjects" :key="project.id"
                 class="border rounded-lg p-3 hover:bg-muted/50 transition-colors">
              <div class="flex items-start justify-between mb-2">
                <div>
                  <p class="font-medium">{{ project.name }}</p>
                  <p class="text-sm text-muted-foreground">{{ project.client }}</p>
                </div>
                <Badge :variant="getProjectStatusVariant(project.status)">
                  {{ project.status }}
                </Badge>
              </div>
              <div class="space-y-2">
                <div class="flex items-center justify-between text-sm">
                  <span>진행률</span>
                  <span class="font-medium">{{ project.progress }}%</span>
                </div>
                <Progress :value="project.progress" />
                <div class="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{{ formatDate(project.startDate) }} ~ {{ formatDate(project.endDate) }}</span>
                  <span>{{ formatCurrency(project.value) }}</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Resource Utilization & Risk Analysis -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 리소스 활용도 -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Users class="h-5 w-5" />
            팀별 리소스 활용도
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="team in teamUtilization" :key="team.name" class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="font-medium">{{ team.name }}</span>
                <div class="flex items-center gap-2">
                  <span class="text-sm">{{ team.utilization }}%</span>
                  <Badge :variant="getUtilizationVariant(team.utilization)">
                    {{ getUtilizationStatus(team.utilization) }}
                  </Badge>
                </div>
              </div>
              <Progress :value="team.utilization" />
              <div class="flex items-center justify-between text-xs text-muted-foreground">
                <span>활성 프로젝트: {{ team.activeProjects }}개</span>
                <span>팀원: {{ team.members }}명</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- 리스크 분석 -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <AlertTriangle class="h-5 w-5 text-orange-500" />
            프로젝트 리스크 분석
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div class="grid grid-cols-3 gap-4 mb-4">
              <div class="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <p class="text-xl font-bold text-red-600">{{ riskAnalysis.high }}</p>
                <p class="text-xs text-red-600">고위험</p>
              </div>
              <div class="text-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <p class="text-xl font-bold text-orange-600">{{ riskAnalysis.medium }}</p>
                <p class="text-xs text-orange-600">중위험</p>
              </div>
              <div class="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p class="text-xl font-bold text-green-600">{{ riskAnalysis.low }}</p>
                <p class="text-xs text-green-600">저위험</p>
              </div>
            </div>

            <div class="space-y-3">
              <div v-for="risk in riskFactors" :key="risk.id"
                   class="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                <div class="h-2 w-2 rounded-full" :class="getRiskColor(risk.level)"></div>
                <div class="flex-1">
                  <p class="font-medium text-sm">{{ risk.project }}</p>
                  <p class="text-xs text-muted-foreground">{{ risk.issue }}</p>
                </div>
                <Badge :variant="getRiskVariant(risk.level)">{{ risk.level }}</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@/components/ui/drawer';
import { AlertTriangle, Calendar, PieChart, TrendingUp, Users } from 'lucide-vue-next';
// 차트 컴포넌트
import { BarChart } from '@/components/ui/chart';

// Mock 데이터
const projectStats = ref({
  totalProjects: 32,
  activeProjects: 24,
  totalValue: 4850000000,
  completionRate: 78.5,
});

const projectStatusDetail = ref([
  { name: '기획', count: 3, color: 'text-blue-600', bgColor: 'bg-blue-500' },
  { name: '개발', count: 12, color: 'text-green-600', bgColor: 'bg-green-500' },
  { name: '테스트', count: 6, color: 'text-orange-600', bgColor: 'bg-orange-500' },
  { name: '배포', count: 3, color: 'text-purple-600', bgColor: 'bg-purple-500' },
  { name: '완료', count: 8, color: 'text-gray-600', bgColor: 'bg-gray-500' },
]);

const activeProjects = ref([
  {
    id: 1,
    name: 'ERP 시스템 고도화',
    client: 'ABC 기업',
    status: '개발',
    progress: 65,
    startDate: '2024-01-15',
    endDate: '2024-04-30',
    value: 850000000,
  },
  {
    id: 2,
    name: '모바일 앱 개발',
    client: 'XYZ 회사',
    status: '테스트',
    progress: 85,
    startDate: '2024-02-01',
    endDate: '2024-03-15',
    value: 420000000,
  },
  {
    id: 3,
    name: 'AI 솔루션 구축',
    client: 'KLM 그룹',
    status: '개발',
    progress: 45,
    startDate: '2024-02-15',
    endDate: '2024-06-30',
    value: 680000000,
  },
  {
    id: 4,
    name: '클라우드 마이그레이션',
    client: 'DEF 코퍼레이션',
    status: '기획',
    progress: 25,
    startDate: '2024-03-01',
    endDate: '2024-07-15',
    value: 950000000,
  },
  {
    id: 5,
    name: 'IoT 플랫폼 구축',
    client: 'GHI 엔터프라이즈',
    status: '배포',
    progress: 95,
    startDate: '2024-01-01',
    endDate: '2024-03-31',
    value: 720000000,
  },
]);

const teamUtilization = ref([
  { name: '프론트엔드팀', utilization: 87, activeProjects: 8, members: 12 },
  { name: '백엔드팀', utilization: 92, activeProjects: 10, members: 15 },
  { name: 'DevOps팀', utilization: 78, activeProjects: 6, members: 8 },
  { name: 'QA팀', utilization: 85, activeProjects: 12, members: 10 },
  { name: 'AI팀', utilization: 95, activeProjects: 4, members: 6 },
]);

const riskAnalysis = ref({
  high: 3,
  medium: 7,
  low: 22,
});

const riskFactors = ref([
  { id: 1, project: 'ERP 시스템 고도화', issue: '일정 지연 위험', level: '고위험' },
  { id: 2, project: 'AI 솔루션 구축', issue: '기술적 복잡성', level: '중위험' },
  { id: 3, project: '클라우드 마이그레이션', issue: '리소스 부족', level: '중위험' },
  { id: 4, project: 'IoT 플랫폼 구축', issue: '고객 요구사항 변경', level: '저위험' },
]);

// Computed 속성들
const projectProgressRate = computed(() =>
  (projectStats.value.activeProjects / projectStats.value.totalProjects) * 100,
);

// 상태 분포 차트 데이터
const statusLabels = computed(() => projectStatusDetail.value.map(s => s.name));
const statusDatasets = computed(() => [
  {
    label: '프로젝트 수',
    data: projectStatusDetail.value.map(s => s.count),
    backgroundColor: [
      'rgba(59,130,246,0.7)',  // 기획 - blue
      'rgba(34,197,94,0.7)',   // 개발 - green
      'rgba(249,115,22,0.7)',  // 테스트 - orange
      'rgba(147,51,234,0.7)',  // 배포 - purple
      'rgba(107,114,128,0.7)', // 완료 - gray
    ],
    borderColor: 'rgba(0,0,0,0.05)',
    borderWidth: 1,
  },
]);

// 헬퍼 함수들
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(amount);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
  });
};

const getProjectStatusVariant = (status: string) => {
  const variants = {
    '기획': 'secondary',
    '개발': 'default',
    '테스트': 'outline',
    '배포': 'destructive',
  };
  return variants[status] || 'secondary';
};

const getUtilizationVariant = (utilization: number) => {
  if (utilization >= 95) return 'destructive';
  if (utilization >= 85) return 'default';
  return 'secondary';
};

const getUtilizationStatus = (utilization: number) => {
  if (utilization >= 95) return '과부하';
  if (utilization >= 85) return '적정';
  return '여유';
};

const getRiskColor = (level: string) => {
  const colors = {
    '고위험': 'bg-red-500',
    '중위험': 'bg-orange-500',
    '저위험': 'bg-green-500',
  };
  return colors[level] || 'bg-gray-500';
};

const getRiskVariant = (level: string) => {
  const variants = {
    '고위험': 'destructive',
    '중위험': 'default',
    '저위험': 'secondary',
  };
  return variants[level] || 'secondary';
};

// 데이터 로딩
onMounted(async () => {
  console.log('Project Analytics Dashboard 로드됨');
});
</script>

<style scoped>
.project-dashboard {
  animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>