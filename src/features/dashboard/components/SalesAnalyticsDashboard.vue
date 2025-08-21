<template>
  <div class="sales-dashboard space-y-6">
    <!-- Quick Metrics Row -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ formatCurrency(salesStats.collectedRevenue) }}</p>
            <p class="text-sm text-muted-foreground">수금완료</p>
            <Progress :value="collectionRate" class="mt-2" />
            <p class="text-xs text-muted-foreground mt-1">{{ collectionRate.toFixed(1) }}% 달성</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-secondary-foreground">{{ formatCurrency(salesStats.outstandingAmount) }}</p>
            <p class="text-sm text-muted-foreground">미수금</p>
            <Badge variant="secondary" class="mt-2">{{ salesStats.averageCollectionPeriod }}일</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">
              {{ salesStats.totalRevenue - salesStats.collectedRevenue > 0 ? '+' : ''
              }}{{ formatCurrency(salesStats.totalRevenue - salesStats.collectedRevenue) }}</p>
            <p class="text-sm text-muted-foreground">수주예정</p>
            <div class="flex items-center justify-center mt-2">
              <TrendingUp class="h-4 w-4 text-primary mr-1" />
              <span class="text-sm text-primary">+8.2%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">
              {{ Math.round((salesStats.collectedRevenue / salesStats.totalRevenue) * 100) }}%</p>
            <p class="text-sm text-muted-foreground">수금률</p>
            <Progress :value="(salesStats.collectedRevenue / salesStats.totalRevenue) * 100" class="mt-2" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Charts and Tables Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 매출 트렌드 차트 -->
      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <CardTitle>월별 매출 트렌드</CardTitle>
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm">
                  <TrendingUp class="h-4 w-4 mr-2" />
                  상세보기
                </Button>
              </SheetTrigger>
              <SheetContent side="right" class="w-[600px]">
                <SheetHeader>
                  <SheetTitle>매출 트렌드 상세 분석</SheetTitle>
                  <SheetDescription>
                    월별 매출 현황과 예측 데이터를 확인하세요
                  </SheetDescription>
                </SheetHeader>
                <div class="mt-6 space-y-4">
                  <div class="grid grid-cols-2 gap-4">
                    <div class="text-center p-4 bg-muted/50 rounded-lg">
                      <p class="text-2xl font-bold">{{ formatCurrency(2450000000) }}</p>
                      <p class="text-sm text-muted-foreground">이번달 매출</p>
                    </div>
                    <div class="text-center p-4 bg-muted/50 rounded-lg">
                      <p class="text-2xl font-bold">{{ formatCurrency(2800000000) }}</p>
                      <p class="text-sm text-muted-foreground">예상 매출</p>
                    </div>
                  </div>
                  <!-- 차트 영역 -->
                  <div class="h-64 bg-muted/20 rounded-lg flex items-center justify-center">
                    <p class="text-muted-foreground">상세 차트 영역</p>
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </CardHeader>
        <CardContent>
          <!-- 차트 컨테이너 -->
          <div class="h-64">
            <LineChart :labels="revenueLabels" :datasets="revenueDatasets" />
          </div>
        </CardContent>
      </Card>

      <!-- 미수금 현황 -->
      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <CardTitle>미수금 TOP 10</CardTitle>
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm">
                  <FileText class="h-4 w-4 mr-2" />
                  전체보기
                </Button>
              </SheetTrigger>
              <SheetContent side="right" class="w-[800px]">
                <SheetHeader>
                  <SheetTitle>전체 미수금 현황</SheetTitle>
                  <SheetDescription>
                    모든 미수금 항목을 확인하고 관리하세요
                  </SheetDescription>
                </SheetHeader>
                <div class="mt-6">
                  <div class="space-y-4">
                    <div class="flex items-center gap-4 p-3 bg-muted/50 rounded-lg">
                      <div class="flex-1">
                        <p class="font-medium">전체 미수금 데이터</p>
                        <p class="text-sm text-muted-foreground">DataTable 컴포넌트 연동 예정</p>
                      </div>
                      <Badge variant="outline">{{ mockOutstanding.length }}건</Badge>
                    </div>
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            <div v-for="item in topOutstanding" :key="item.id"
                 class="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted/70 transition-colors">
              <div>
                <p class="font-medium">{{ item.clientName }}</p>
                <p class="text-sm text-muted-foreground">{{ item.projectName }}</p>
              </div>
              <div class="text-right">
                <p class="font-bold text-secondary-foreground">{{ formatCurrency(item.amount) }}</p>
                <Badge variant="outline"
                       :class="item.daysPast > 30 ? 'border-destructive text-destructive' : 'border-secondary text-secondary-foreground'">
                  {{ item.daysPast }}일
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- AI Insights Card -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Brain class="h-5 w-5 text-primary" />
          AI 매출 분석 인사이트
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="flex items-start gap-3">
            <div class="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
              <TrendingUp class="h-5 w-5 text-primary" />
            </div>
            <div>
              <p class="font-medium text-sm">수금 예측</p>
              <p class="text-xs text-muted-foreground mb-2">다음 주 예상 수금액</p>
              <p class="text-lg font-bold text-primary">{{ formatCurrency(predictedCollection) }}</p>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div class="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
              <Target class="h-5 w-5 text-primary" />
            </div>
            <div>
              <p class="font-medium text-sm">목표 달성률</p>
              <p class="text-xs text-muted-foreground mb-2">월간 매출 목표 대비</p>
              <div class="flex items-center gap-2">
                <Progress :value="85.5" class="flex-1" />
                <span class="text-sm font-medium">85.5%</span>
              </div>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div class="h-10 w-10 bg-destructive/10 rounded-full flex items-center justify-center">
              <AlertTriangle class="h-5 w-5 text-destructive" />
            </div>
            <div>
              <p class="font-medium text-sm">주의 항목</p>
              <p class="text-xs text-muted-foreground mb-2">60일 이상 미수금</p>
              <div class="flex items-center gap-2">
                <Badge variant="destructive">긴급</Badge>
                <span class="text-sm font-medium">{{ criticalOutstanding }}건</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { AlertTriangle, Brain, FileText, Target, TrendingUp } from 'lucide-vue-next';
// 차트 컴포넌트
import { LineChart } from '@/components/ui/chart';

// Mock 데이터 (추후 실제 API 연동)
const salesStats = ref({
  totalRevenue: 2450000000,
  collectedRevenue: 1980000000,
  outstandingAmount: 470000000,
  averageCollectionPeriod: 28,
});

const mockOutstanding = ref([
  { id: 1, clientName: 'ABC 기업', projectName: 'ERP 구축', amount: 85000000, daysPast: 45 },
  { id: 2, clientName: 'XYZ 회사', projectName: '모바일 앱 개발', amount: 62000000, daysPast: 32 },
  { id: 3, clientName: 'KLM 그룹', projectName: '시스템 통합', amount: 58000000, daysPast: 28 },
  { id: 4, clientName: 'DEF 코퍼레이션', projectName: 'AI 솔루션', amount: 47000000, daysPast: 18 },
  { id: 5, clientName: 'GHI 엔터프라이즈', projectName: '클라우드 마이그레이션', amount: 41000000, daysPast: 12 },
  { id: 6, clientName: 'JNP 테크', projectName: 'IoT 플랫폼', amount: 38000000, daysPast: 67 },
  { id: 7, clientName: 'QRS 솔루션', projectName: '빅데이터 분석', amount: 34000000, daysPast: 21 },
  { id: 8, clientName: 'TUV 시스템즈', projectName: '웹 포털 구축', amount: 29000000, daysPast: 8 },
  { id: 9, clientName: 'WXY 인더스트리', projectName: '보안 솔루션', amount: 25000000, daysPast: 55 },
  { id: 10, clientName: 'ZAB 네트웍스', projectName: '네트워크 구축', amount: 22000000, daysPast: 14 },
]);

// Computed 속성들
const collectionRate = computed(() =>
  (salesStats.value.collectedRevenue / salesStats.value.totalRevenue) * 100,
);

const topOutstanding = computed(() =>
  mockOutstanding.value.slice(0, 7),
);

const predictedCollection = computed(() => 125000000);

const criticalOutstanding = computed(() =>
  mockOutstanding.value.filter(item => item.daysPast > 60).length,
);

// 헬퍼 함수
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(amount);
};

// 월별 매출 트렌드용 라벨/데이터 (데모용)
const revenueLabels = computed(() => ['10월', '11월', '12월', '1월', '2월', '3월']);
const revenueDatasets = computed(() => [
  {
    label: '총 매출',
    data: [380, 420, 460, 510, 540, 600],
    // 색상/배경은 LineChart에서 테마 기준으로 자동 설정
    fill: true,
  },
  {
    label: '수금액',
    data: [320, 360, 400, 455, 490, 530],
    fill: true,
  },
]);

// 데이터 로딩
onMounted(async () => {
  // TODO: 실제 SalesRepository를 통한 데이터 로딩
  console.log('Sales Analytics Dashboard 로드됨');
});
</script>

<style scoped>
.sales-dashboard {
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