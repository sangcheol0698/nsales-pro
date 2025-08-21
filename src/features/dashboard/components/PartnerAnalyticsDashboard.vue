<template>
  <div class="partner-dashboard space-y-6">
    <!-- 파트너 현황 개요 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ partnerStats.totalPartners }}</p>
            <p class="text-sm text-muted-foreground">전체 파트너</p>
            <div class="flex items-center justify-center mt-2">
              <TrendingUp class="h-4 w-4 text-primary mr-1" />
              <span class="text-sm text-primary">+{{ newPartners }}개</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ partnerStats.activePartners }}</p>
            <p class="text-sm text-muted-foreground">활성 파트너</p>
            <Progress :value="activePartnerRate" class="mt-2" />
            <p class="text-xs text-muted-foreground mt-1">{{ activePartnerRate.toFixed(1) }}%</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ partnerStats.averageGrade }}</p>
            <p class="text-sm text-muted-foreground">평균 등급</p>
            <Badge variant="default" class="mt-2">우수</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ formatCurrency(partnerStats.revenueContribution) }}</p>
            <p class="text-sm text-muted-foreground">매출 기여도</p>
            <div class="flex items-center justify-center mt-2">
              <DollarSign class="h-4 w-4 text-primary mr-1" />
              <span class="text-sm text-primary">+18%</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 파트너 등급별 분포 & 성과 분석 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>파트너 등급별 분포</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="grade in gradeDistribution" :key="grade.level"
                 class="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div class="flex items-center gap-3">
                <div class="h-4 w-4 rounded" :class="grade.color"></div>
                <div>
                  <p class="font-medium">{{ grade.level }}급</p>
                  <p class="text-sm text-muted-foreground">{{ grade.description }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="font-bold">{{ grade.count }}개</p>
                <Badge variant="outline">{{ grade.percentage }}%</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>월별 파트너 성과</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="perf in monthlyPerformance" :key="perf.month" class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="font-medium">{{ perf.month }}</span>
                <div class="flex items-center gap-2">
                  <span class="text-sm">{{ formatCurrency(perf.revenue) }}</span>
                  <Badge :variant="perf.growth > 0 ? 'default' : 'secondary'">
                    {{ perf.growth > 0 ? '+' : '' }}{{ perf.growth }}%
                  </Badge>
                </div>
              </div>
              <Progress :value="perf.performance" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- TOP 파트너 & 신규 파트너 현황 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <CardTitle>TOP 10 파트너</CardTitle>
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm">
                  <Crown class="h-4 w-4 mr-2" />
                  전체보기
                </Button>
              </SheetTrigger>
              <SheetContent side="right" class="w-[700px]">
                <SheetHeader>
                  <SheetTitle>전체 파트너 순위</SheetTitle>
                  <SheetDescription>
                    모든 파트너의 성과와 기여도를 확인하세요
                  </SheetDescription>
                </SheetHeader>
                <div class="mt-6">
                  <div class="h-96 bg-muted/20 rounded-lg flex items-center justify-center">
                    <div class="text-center">
                      <Crown class="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                      <p class="text-muted-foreground">전체 파트너 랭킹</p>
                      <p class="text-sm text-muted-foreground">DataTable 컴포넌트 연동 예정</p>
                    </div>
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            <div v-for="(partner, index) in topPartners" :key="partner.id"
                 class="flex items-center gap-3 p-3 bg-muted/50 rounded-lg hover:bg-muted/70 transition-colors">
              <div class="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-bold text-sm">
                {{ index + 1 }}
              </div>
              <div class="flex-1">
                <p class="font-medium">{{ partner.name }}</p>
                <p class="text-sm text-muted-foreground">{{ partner.category }}</p>
              </div>
              <div class="text-right">
                <p class="font-bold text-primary">{{ formatCurrency(partner.revenue) }}</p>
                <Badge :variant="getGradeBadgeVariant(partner.grade)">{{ partner.grade }}급</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>파트너십 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-6">
            <!-- 신규 파트너 -->
            <div>
              <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium">신규 파트너 (최근 3개월)</h4>
                <Badge variant="secondary">{{ newPartnersList.length }}개</Badge>
              </div>
              <div class="space-y-2">
                <div v-for="partner in newPartnersList" :key="partner.id"
                     class="flex items-center justify-between p-2 bg-muted/30 rounded">
                  <span class="text-sm font-medium">{{ partner.name }}</span>
                  <div class="flex items-center gap-2">
                    <Badge variant="outline" size="sm">{{ partner.joinDate }}</Badge>
                    <Badge size="sm" :variant="getGradeBadgeVariant(partner.grade)">{{ partner.grade }}급</Badge>
                  </div>
                </div>
              </div>
            </div>

            <Separator />

            <!-- 파트너 계약 현황 -->
            <div>
              <h4 class="font-medium mb-3">계약 갱신 현황</h4>
              <div class="grid grid-cols-3 gap-4">
                <div class="text-center p-3 bg-primary/10 rounded-lg">
                  <p class="text-lg font-bold text-primary">{{ contractStatus.renewed }}</p>
                  <p class="text-xs text-primary">갱신완료</p>
                </div>
                <div class="text-center p-3 bg-secondary/50 rounded-lg">
                  <p class="text-lg font-bold text-secondary-foreground">{{ contractStatus.pending }}</p>
                  <p class="text-xs text-secondary-foreground">갱신대기</p>
                </div>
                <div class="text-center p-3 bg-destructive/10 rounded-lg">
                  <p class="text-lg font-bold text-destructive">{{ contractStatus.expiring }}</p>
                  <p class="text-xs text-destructive">만료예정</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 파트너 관계 관리 & AI 인사이트 -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Brain class="h-5 w-5 text-primary" />
          AI 파트너 인사이트
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="flex items-start gap-3">
            <div class="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
              <TrendingUp class="h-5 w-5 text-primary" />
            </div>
            <div>
              <p class="font-medium text-sm">성장 파트너 예측</p>
              <p class="text-xs text-muted-foreground mb-2">향후 6개월 내 성장 가능성</p>
              <div class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span>테크솔루션</span>
                  <span class="font-medium text-primary">+45%</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span>디지털웨이브</span>
                  <span class="font-medium text-primary">+32%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div class="h-10 w-10 bg-destructive/10 rounded-full flex items-center justify-center">
              <AlertTriangle class="h-5 w-5 text-destructive" />
            </div>
            <div>
              <p class="font-medium text-sm">관계 개선 필요</p>
              <p class="text-xs text-muted-foreground mb-2">만족도 하락 파트너</p>
              <div class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span>스마트시스템즈</span>
                  <Badge variant="destructive" size="sm">긴급</Badge>
                </div>
                <div class="flex justify-between text-xs">
                  <span>클라우드플러스</span>
                  <Badge variant="default" size="sm">주의</Badge>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div class="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
              <Target class="h-5 w-5 text-primary" />
            </div>
            <div>
              <p class="font-medium text-sm">신규 기회</p>
              <p class="text-xs text-muted-foreground mb-2">잠재 파트너십 기회</p>
              <div class="space-y-1">
                <div class="flex justify-between text-xs">
                  <span>AI 솔루션 분야</span>
                  <span class="font-medium text-primary">3개사</span>
                </div>
                <div class="flex justify-between text-xs">
                  <span>클라우드 인프라</span>
                  <span class="font-medium text-primary">2개사</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { 
  TrendingUp,
  DollarSign,
  Crown,
  Brain,
  AlertTriangle,
  Target
} from 'lucide-vue-next'

// Mock 데이터
const partnerStats = ref({
  totalPartners: 32,
  activePartners: 28,
  averageGrade: 'A',
  revenueContribution: 1850000000
})

const newPartners = ref(5)

const gradeDistribution = ref([
  { level: 'A', count: 8, percentage: 25, description: 'VIP 파트너', color: 'bg-primary' },
  { level: 'B', count: 12, percentage: 37.5, description: '우수 파트너', color: 'bg-primary' },
  { level: 'C', count: 9, percentage: 28.1, description: '일반 파트너', color: 'bg-secondary' },
  { level: 'D', count: 3, percentage: 9.4, description: '신규 파트너', color: 'bg-muted' }
])

const monthlyPerformance = ref([
  { month: '3월', revenue: 520000000, performance: 95, growth: 18 },
  { month: '2월', revenue: 480000000, performance: 88, growth: 12 },
  { month: '1월', revenue: 450000000, performance: 82, growth: 8 },
  { month: '12월', revenue: 420000000, performance: 78, growth: -3 }
])

const topPartners = ref([
  { id: 1, name: '테크솔루션', category: 'IT 서비스', revenue: 285000000, grade: 'A' },
  { id: 2, name: '디지털웨이브', category: '소프트웨어', revenue: 240000000, grade: 'A' },
  { id: 3, name: '스마트시스템즈', category: '하드웨어', revenue: 195000000, grade: 'B' },
  { id: 4, name: '클라우드플러스', category: '클라우드', revenue: 175000000, grade: 'B' },
  { id: 5, name: '데이터랩', category: '빅데이터', revenue: 158000000, grade: 'A' },
  { id: 6, name: '모바일마스터', category: '모바일', revenue: 142000000, grade: 'B' },
  { id: 7, name: 'AI이노베이션', category: '인공지능', revenue: 128000000, grade: 'A' },
  { id: 8, name: '보안프로', category: '보안', revenue: 115000000, grade: 'B' }
])

const newPartnersList = ref([
  { id: 1, name: '넥스트젠', joinDate: '2024-01', grade: 'D' },
  { id: 2, name: '퓨처테크', joinDate: '2024-02', grade: 'C' },
  { id: 3, name: '이지솔루션', joinDate: '2024-03', grade: 'C' },
  { id: 4, name: '글로벌IT', joinDate: '2024-03', grade: 'D' }
])

const contractStatus = ref({
  renewed: 18,
  pending: 8,
  expiring: 6
})

// Computed 속성
const activePartnerRate = computed(() => 
  (partnerStats.value.activePartners / partnerStats.value.totalPartners) * 100
)

// 헬퍼 함수들
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    notation: 'compact',
    maximumFractionDigits: 1
  }).format(amount)
}

const getGradeBadgeVariant = (grade: string) => {
  const variants = {
    'A': 'default',
    'B': 'secondary',
    'C': 'outline',
    'D': 'secondary'
  }
  return variants[grade] || 'secondary'
}
</script>

<style scoped>
.partner-dashboard {
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