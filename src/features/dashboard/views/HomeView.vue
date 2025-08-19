<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-6 overflow-x-hidden">
      <div class="executive-dashboard space-y-8">
        <!-- Header -->
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">Executive Dashboard</h1>
            <p class="text-muted-foreground">전사 핵심 지표 및 비즈니스 인사이트</p>
          </div>
          <div class="flex items-center gap-2">
            <Badge :variant="loading ? 'secondary' : 'outline'" class="gap-1">
              <div v-if="loading" class="h-2 w-2 bg-current rounded-full animate-pulse"></div>
              {{ loading ? '로딩중' : '실시간' }}
            </Badge>
            <span class="text-sm text-muted-foreground">{{ lastUpdated }}</span>
          </div>
        </div>

        <!-- KPI Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- 매출 카드 -->
          <Card class="relative overflow-hidden">
            <CardContent class="p-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-muted-foreground">총 매출</p>
                  <p class="text-3xl font-bold">{{ formatCurrency(salesKPI.totalRevenue) }}</p>
                  <div class="flex items-center mt-2">
                    <TrendingUp v-if="salesKPI.trend > 0" class="h-4 w-4 text-green-500 mr-1" />
                    <TrendingDown v-else class="h-4 w-4 text-red-500 mr-1" />
                    <span :class="salesKPI.trend > 0 ? 'text-green-600' : 'text-red-600'" class="text-sm">
                      {{ salesKPI.trend > 0 ? '+' : '' }}{{ salesKPI.trend.toFixed(1) }}%
                    </span>
                  </div>
                </div>
                <div class="h-12 w-12 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center">
                  <DollarSign class="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 프로젝트 카드 -->
          <Card class="relative overflow-hidden">
            <CardContent class="p-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-muted-foreground">활성 프로젝트</p>
                  <p class="text-3xl font-bold">{{ projectKPI.activeProjects }}</p>
                  <Badge variant="secondary" class="mt-2">
                    완료율 {{ projectKPI.completionRate.toFixed(1) }}%
                  </Badge>
                </div>
                <div class="h-12 w-12 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center">
                  <FolderOpen class="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 직원 카드 -->
          <Card class="relative overflow-hidden">
            <CardContent class="p-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-muted-foreground">전체 직원</p>
                  <p class="text-3xl font-bold">{{ employeeKPI.totalEmployees }}</p>
                  <div class="flex items-center mt-2">
                    <UserPlus class="h-4 w-4 text-blue-500 mr-1" />
                    <span class="text-sm text-blue-600">신규 {{ employeeKPI.newHires }}명</span>
                  </div>
                </div>
                <div
                  class="h-12 w-12 bg-purple-100 dark:bg-purple-900/20 rounded-full flex items-center justify-center">
                  <Users class="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 파트너 카드 -->
          <Card class="relative overflow-hidden">
            <CardContent class="p-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-muted-foreground">비즈니스 파트너</p>
                  <p class="text-3xl font-bold">{{ partnerKPI.totalPartners }}</p>
                  <Badge variant="outline" class="mt-2">
                    평균 {{ partnerKPI.averageGrade }}
                  </Badge>
                </div>
                <div
                  class="h-12 w-12 bg-orange-100 dark:bg-orange-900/20 rounded-full flex items-center justify-center">
                  <Handshake class="h-6 w-6 text-orange-600 dark:text-orange-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Domain Analysis Tabs -->
        <Tabs v-model="activeTab" class="w-full">
          <TabsList class="grid w-full grid-cols-5 mb-8">
            <TabsTrigger value="sales" class="flex items-center gap-2">
              <DollarSign class="h-4 w-4" />
              매출분석
            </TabsTrigger>
            <TabsTrigger value="projects" class="flex items-center gap-2">
              <FolderOpen class="h-4 w-4" />
              프로젝트
            </TabsTrigger>
            <TabsTrigger value="employees" class="flex items-center gap-2">
              <Users class="h-4 w-4" />
              인력현황
            </TabsTrigger>
            <TabsTrigger value="partners" class="flex items-center gap-2">
              <Handshake class="h-4 w-4" />
              파트너
            </TabsTrigger>
            <TabsTrigger value="ai-insights" class="flex items-center gap-2">
              <Brain class="h-4 w-4" />
              AI인사이트
            </TabsTrigger>
          </TabsList>

          <TabsContent value="sales" class="mt-0">
            <SalesAnalyticsDashboard />
          </TabsContent>

          <TabsContent value="projects" class="mt-0">
            <ProjectAnalyticsDashboard />
          </TabsContent>

          <TabsContent value="employees" class="mt-0">
            <EmployeeAnalyticsDashboard />
          </TabsContent>

          <TabsContent value="partners" class="mt-0">
            <PartnerAnalyticsDashboard />
          </TabsContent>

          <TabsContent value="ai-insights" class="mt-0">
            <AIInsightsDashboard />
          </TabsContent>
        </Tabs>
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue';
import { SidebarLayout } from '@/components/layout';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Brain, DollarSign, FolderOpen, Handshake, TrendingDown, TrendingUp, UserPlus, Users } from 'lucide-vue-next';

// Stats 엔티티 imports
import EmployeeStats from '@/features/employee/entity/EmployeeStats';
import ProjectStats from '@/features/project/entity/ProjectStats';
import PartnerStats from '@/features/partner/entity/PartnerStats';
import SalesStats from '@/features/sales/entity/SalesStats';

// Repository imports (DI)
import { container } from 'tsyringe';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository';
import ProjectRepository from '@/features/project/repository/ProjectRepository';
import PartnerRepository from '@/features/partner/repository/PartnerRepository';
import SalesRepository from '@/features/sales/repository/SalesRepository';

// 대시보드 컴포넌트들
const SalesAnalyticsDashboard = defineAsyncComponent(() => import('../components/SalesAnalyticsDashboard.vue'));
const ProjectAnalyticsDashboard = defineAsyncComponent(() => import('../components/ProjectAnalyticsDashboard.vue'));
const EmployeeAnalyticsDashboard = defineAsyncComponent(() => import('../components/EmployeeAnalyticsDashboard.vue'));
const PartnerAnalyticsDashboard = defineAsyncComponent(() => import('../components/PartnerAnalyticsDashboard.vue'));
const AIInsightsDashboard = defineAsyncComponent(() => import('../components/AIInsightsDashboard.vue'));

// Repository 의존성 주입
const employeeRepository = container.resolve(EmployeeRepository);
const projectRepository = container.resolve(ProjectRepository);
const partnerRepository = container.resolve(PartnerRepository);
const salesRepository = container.resolve(SalesRepository);

// 상태 관리
const activeTab = ref('sales');
const lastUpdated = ref(new Date().toLocaleTimeString('ko-KR'));
const loading = ref(true);

// 실제 Stats 데이터
const employeeStats = ref<EmployeeStats | null>(null);
const projectStats = ref<ProjectStats | null>(null);
const partnerStats = ref<PartnerStats | null>(null);
const salesStats = ref<SalesStats | null>(null);

// KPI 계산된 데이터
const salesKPI = computed(() => ({
  totalRevenue: salesStats.value?.totalRevenue || 0,
  trend: calculateSalesTrend(),
}));

const projectKPI = computed(() => ({
  activeProjects: projectStats.value?.activeProjects || 0,
  completionRate: projectStats.value?.completionRate || 0,
}));

const employeeKPI = computed(() => ({
  totalEmployees: employeeStats.value?.totalEmployees || 0,
  newHires: employeeStats.value?.newHires || 0,
}));

const partnerKPI = computed(() => ({
  totalPartners: partnerStats.value?.totalPartners || 0,
  averageGrade: partnerStats.value?.averageGrade || 'N/A',
}));


// 헬퍼 함수들
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(amount);
};

const calculateSalesTrend = (): number => {
  // TODO: 실제 이전 기간 매출과 비교하여 트렌드 계산
  // 현재는 Mock 데이터로 대체
  return 12.5;
};

// 대시보드 데이터 로딩
const loadDashboardData = async () => {
  try {
    loading.value = true;

    // TODO: 실제 API가 구현되면 아래 주석을 해제하고 사용
    // const [employeeStatsData, projectStatsData, partnerStatsData, salesStatsData] = await Promise.allSettled([
    //   employeeRepository.getStats?.() || Promise.resolve(null),
    //   projectRepository.getStats?.() || Promise.resolve(null), 
    //   partnerRepository.getStats?.() || Promise.resolve(null),
    //   salesRepository.getStats?.() || Promise.resolve(null),
    // ]);

    // 현재는 Mock 데이터로 시작 (실제 API 연동 시 교체)
    await new Promise(resolve => setTimeout(resolve, 800)); // 로딩 시뮬레이션

    employeeStats.value = new EmployeeStats({
      totalEmployees: 156,
      activeEmployees: 148,
      newHires: 8,
      averageTenure: 28,
    });

    projectStats.value = new ProjectStats({
      totalProjects: 32,
      activeProjects: 24,
      totalValue: 4850000000,
      completionRate: 78.5,
    });

    partnerStats.value = new PartnerStats({
      totalPartners: 32,
      activePartners: 28,
      averageGrade: 'A',
      revenueContribution: 1850000000,
    });

    salesStats.value = new SalesStats({
      totalRevenue: 2450000000,
      collectedRevenue: 1980000000,
      outstandingAmount: 470000000,
      averageCollectionPeriod: 28,
    });

    console.log('Dashboard Mock 데이터 로드 완료:', {
      employee: employeeStats.value,
      project: projectStats.value,
      partner: partnerStats.value,
      sales: salesStats.value,
    });

  } catch (error) {
    console.error('Dashboard 데이터 로딩 실패:', error);
  } finally {
    loading.value = false;
    lastUpdated.value = new Date().toLocaleTimeString('ko-KR');
  }
};

// 실시간 데이터 업데이트
const setupRealTimeUpdates = () => {
  // 30초마다 타임스탬프 업데이트
  setInterval(() => {
    lastUpdated.value = new Date().toLocaleTimeString('ko-KR');
  }, 30000);

  // 5분마다 데이터 리프레시
  setInterval(async () => {
    await loadDashboardData();
  }, 300000);
};

// 데이터 로딩 및 초기화
onMounted(async () => {
  await loadDashboardData();
  setupRealTimeUpdates();
});
</script>

<style scoped>
.executive-dashboard {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>