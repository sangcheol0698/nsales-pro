<template>
  <div class="ai-insights-dashboard space-y-6">
    <!-- AI 상태 및 성능 지표 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <div class="h-12 w-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-2">
              <Brain class="h-6 w-6 text-primary" />
            </div>
            <p class="text-2xl font-bold text-primary">활성</p>
            <p class="text-sm text-muted-foreground">AI 시스템 상태</p>
            <Badge variant="secondary" class="mt-2">99.8% 가동률</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ aiMetrics.totalQueries }}</p>
            <p class="text-sm text-muted-foreground">오늘 AI 질의</p>
            <div class="flex items-center justify-center mt-2">
              <TrendingUp class="h-4 w-4 text-primary mr-1" />
              <span class="text-sm text-primary">+23%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ aiMetrics.accuracy }}%</p>
            <p class="text-sm text-muted-foreground">예측 정확도</p>
            <Progress :value="aiMetrics.accuracy" class="mt-2" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ aiMetrics.responseTime }}ms</p>
            <p class="text-sm text-muted-foreground">평균 응답시간</p>
            <Badge variant="outline" class="mt-2">최적화됨</Badge>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- AI 인사이트 & 예측 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 비즈니스 인사이트 -->
      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <CardTitle class="flex items-center gap-2">
              <Lightbulb class="h-5 w-5 text-primary" />
              AI 비즈니스 인사이트
            </CardTitle>
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal class="h-4 w-4 mr-2" />
                  더보기
                </Button>
              </SheetTrigger>
              <SheetContent side="right" class="w-[600px]">
                <SheetHeader>
                  <SheetTitle>상세 AI 분석 리포트</SheetTitle>
                  <SheetDescription>
                    AI가 분석한 비즈니스 트렌드와 개선 제안사항
                  </SheetDescription>
                </SheetHeader>
                <div class="mt-6 space-y-6">
                  <div class="space-y-4">
                    <h4 class="font-medium">매출 최적화 제안</h4>
                    <div class="p-4 bg-muted/50 rounded-lg">
                      <p class="text-sm">ABC 기업과의 계약 갱신 확률이 87%로 예측됩니다. 3월 중 적극적인 영업 활동을 권장합니다.</p>
                    </div>
                  </div>
                  <div class="space-y-4">
                    <h4 class="font-medium">리스크 관리</h4>
                    <div class="p-4 bg-muted/50 rounded-lg">
                      <p class="text-sm">프로젝트 지연 위험이 높은 상위 3개 프로젝트에 대한 리소스 재배치를 검토해보세요.</p>
                    </div>
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="insight in businessInsights" :key="insight.id" 
                 class="flex items-start gap-3 p-4 bg-muted/30 rounded-lg border-l-4" :class="insight.borderColor">
              <div class="h-8 w-8 rounded-full flex items-center justify-center" :class="insight.iconBg">
                <component :is="insight.icon" class="h-4 w-4" :class="insight.iconColor" />
              </div>
              <div class="flex-1">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-sm">{{ insight.title }}</p>
                    <p class="text-xs text-muted-foreground mt-1">{{ insight.description }}</p>
                  </div>
                  <Badge :variant="insight.badgeVariant">{{ insight.priority }}</Badge>
                </div>
                <div class="mt-2 flex items-center gap-2">
                  <div class="flex items-center text-xs text-muted-foreground">
                    <Clock class="h-3 w-3 mr-1" />
                    {{ insight.timeAgo }}
                  </div>
                  <div class="flex items-center text-xs" :class="insight.impactColor">
                    <TrendingUp class="h-3 w-3 mr-1" />
                    {{ insight.impact }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- 예측 및 트렌드 -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <BarChart3 class="h-5 w-5 text-primary" />
            AI 예측 분석
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-6">
            <!-- 매출 예측 -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <h4 class="font-medium text-sm">다음 분기 매출 예측</h4>
                <Badge variant="outline">92% 정확도</Badge>
              </div>
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span>보수적 예측</span>
                  <span class="font-medium">{{ formatCurrency(predictions.revenue.conservative) }}</span>
                </div>
                <Progress :value="75" class="bg-destructive/20" />
                
                <div class="flex justify-between text-sm">
                  <span>현실적 예측</span>
                  <span class="font-medium text-primary">{{ formatCurrency(predictions.revenue.realistic) }}</span>
                </div>
                <Progress :value="85" class="bg-primary/20" />
                
                <div class="flex justify-between text-sm">
                  <span>낙관적 예측</span>
                  <span class="font-medium">{{ formatCurrency(predictions.revenue.optimistic) }}</span>
                </div>
                <Progress :value="95" class="bg-primary/20" />
              </div>
            </div>

            <Separator />

            <!-- 프로젝트 성공률 예측 -->
            <div class="space-y-3">
              <h4 class="font-medium text-sm">프로젝트 성공률 예측</h4>
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-3 bg-primary/10 rounded-lg">
                  <p class="text-xl font-bold text-primary">{{ predictions.project.successRate }}%</p>
                  <p class="text-xs text-primary">성공률</p>
                </div>
                <div class="text-center p-3 bg-secondary/50 rounded-lg">
                  <p class="text-xl font-bold text-secondary-foreground">{{ predictions.project.riskProjects }}</p>
                  <p class="text-xs text-secondary-foreground">리스크 프로젝트</p>
                </div>
              </div>
            </div>

            <Separator />

            <!-- 시장 트렌드 -->
            <div class="space-y-3">
              <h4 class="font-medium text-sm">시장 트렌드 분석</h4>
              <div class="space-y-2">
                <div v-for="trend in marketTrends" :key="trend.category" 
                     class="flex items-center justify-between">
                  <span class="text-sm">{{ trend.category }}</span>
                  <div class="flex items-center gap-2">
                    <component :is="trend.icon" class="h-4 w-4" :class="trend.color" />
                    <span class="text-sm font-medium" :class="trend.color">{{ trend.change }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- AI 채팅 위젯 통합 -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <MessageCircle class="h-5 w-5 text-primary" />
          AI 비서와 대화하기
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="bg-muted/20 rounded-lg p-6 text-center">
          <div class="space-y-4">
            <div class="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
              <Bot class="h-8 w-8 text-primary" />
            </div>
            <div>
              <p class="font-medium">비즈니스 데이터에 대해 궁금한 것이 있나요?</p>
              <p class="text-sm text-muted-foreground mt-1">AI가 대시보드 데이터를 기반으로 답변해드립니다</p>
            </div>
            <div class="flex gap-2 justify-center flex-wrap">
              <Button variant="outline" size="sm" @click="askQuestion('이번 달 매출 전망은?')">
                "이번 달 매출 전망은?"
              </Button>
              <Button variant="outline" size="sm" @click="askQuestion('지연 위험이 높은 프로젝트는?')">
                "지연 위험이 높은 프로젝트는?"
              </Button>
              <Button variant="outline" size="sm" @click="askQuestion('리소스 최적화 방법은?')">
                "리소스 최적화 방법은?"
              </Button>
            </div>
            <Sheet>
              <SheetTrigger asChild>
                <Button class="mt-4">
                  <MessageCircle class="h-4 w-4 mr-2" />
                  AI와 채팅 시작하기
                </Button>
              </SheetTrigger>
              <SheetContent side="right" class="w-[500px]">
                <SheetHeader>
                  <SheetTitle>AI 비서 채팅</SheetTitle>
                  <SheetDescription>
                    비즈니스 데이터에 대한 질문을 자유롭게 하세요
                  </SheetDescription>
                </SheetHeader>
                <div class="mt-6 h-96 bg-muted/20 rounded-lg flex items-center justify-center">
                  <div class="text-center">
                    <MessageCircle class="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                    <p class="text-muted-foreground">AI 채팅 위젯</p>
                    <p class="text-sm text-muted-foreground">기존 Chat 컴포넌트 통합 예정</p>
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- 자동화 및 알림 설정 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Zap class="h-5 w-5 text-primary" />
            AI 자동화 현황
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="automation in automationStatus" :key="automation.id"
                 class="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div class="flex items-center gap-3">
                <div class="h-2 w-2 rounded-full" :class="automation.active ? 'bg-primary' : 'bg-muted-foreground'"></div>
                <div>
                  <p class="font-medium text-sm">{{ automation.name }}</p>
                  <p class="text-xs text-muted-foreground">{{ automation.description }}</p>
                </div>
              </div>
              <Badge :variant="automation.active ? 'default' : 'secondary'">
                {{ automation.active ? '활성' : '비활성' }}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Bell class="h-5 w-5 text-primary" />
            스마트 알림
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="alert in smartAlerts" :key="alert.id"
                 class="flex items-start gap-3 p-3 border rounded-lg" :class="getAlertBorderClass(alert.severity)">
              <div class="h-2 w-2 rounded-full mt-2" :class="getAlertDotClass(alert.severity)"></div>
              <div class="flex-1">
                <p class="font-medium text-sm">{{ alert.title }}</p>
                <p class="text-xs text-muted-foreground mt-1">{{ alert.message }}</p>
                <div class="flex items-center gap-2 mt-2">
                  <Badge variant="outline" size="sm">{{ alert.category }}</Badge>
                  <span class="text-xs text-muted-foreground">{{ alert.timeAgo }}</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { 
  Brain,
  TrendingUp, 
  TrendingDown,
  Lightbulb,
  MoreHorizontal,
  BarChart3,
  Clock,
  MessageCircle,
  Bot,
  Zap,
  Bell,
  Target,
  AlertTriangle,
  DollarSign
} from 'lucide-vue-next'

// Mock 데이터
const aiMetrics = ref({
  totalQueries: 247,
  accuracy: 94.2,
  responseTime: 125
})

const businessInsights = ref([
  {
    id: 1,
    title: '매출 증가 기회 발견',
    description: 'ABC 기업의 프로젝트 확장 가능성이 높음 (87% 확률)',
    priority: '높음',
    impact: '+15% 매출 예상',
    timeAgo: '2시간 전',
    icon: DollarSign,
    iconBg: 'bg-primary/10',
    iconColor: 'text-primary',
    borderColor: 'border-l-primary',
    badgeVariant: 'destructive',
    impactColor: 'text-primary'
  },
  {
    id: 2,
    title: '프로젝트 지연 위험',
    description: 'ERP 시스템 고도화 프로젝트의 일정 준수 확률 62%',
    priority: '중간',
    impact: '-5일 지연 예상',
    timeAgo: '4시간 전',
    icon: AlertTriangle,
    iconBg: 'bg-destructive/10',
    iconColor: 'text-destructive',
    borderColor: 'border-l-destructive',
    badgeVariant: 'default',
    impactColor: 'text-destructive'
  },
  {
    id: 3,
    title: '리소스 최적화 제안',
    description: '백엔드팀 업무 부하 95% - 다른 팀으로 일부 업무 분산 권장',
    priority: '중간',
    impact: '+20% 효율성',
    timeAgo: '6시간 전',
    icon: Target,
    iconBg: 'bg-primary/10',
    iconColor: 'text-primary',
    borderColor: 'border-l-primary',
    badgeVariant: 'secondary',
    impactColor: 'text-primary'
  }
])

const predictions = ref({
  revenue: {
    conservative: 2800000000,
    realistic: 3200000000,
    optimistic: 3600000000
  },
  project: {
    successRate: 87.5,
    riskProjects: 3
  }
})

const marketTrends = ref([
  { category: 'AI/ML 솔루션', change: '+24%', icon: TrendingUp, color: 'text-primary' },
  { category: '클라우드 서비스', change: '+18%', icon: TrendingUp, color: 'text-primary' },
  { category: '레거시 시스템', change: '-8%', icon: TrendingDown, color: 'text-destructive' },
  { category: '모바일 앱', change: '+12%', icon: TrendingUp, color: 'text-primary' }
])

const automationStatus = ref([
  { id: 1, name: '매출 예측 자동 업데이트', description: '매일 오전 9시 자동 분석', active: true },
  { id: 2, name: '프로젝트 리스크 모니터링', description: '실시간 위험 요소 감지', active: true },
  { id: 3, name: '고객 만족도 분석', description: '월 1회 자동 리포트 생성', active: false },
  { id: 4, name: '리소스 최적화 제안', description: '주 1회 팀별 업무 분석', active: true }
])

const smartAlerts = ref([
  {
    id: 1,
    title: '임계 미수금 알림',
    message: 'ABC 기업의 미수금이 60일을 초과했습니다.',
    category: '재무',
    severity: 'high',
    timeAgo: '30분 전'
  },
  {
    id: 2,
    title: '프로젝트 마일스톤 도달',
    message: 'AI 솔루션 구축 프로젝트가 50% 완료되었습니다.',
    category: '프로젝트',
    severity: 'low',
    timeAgo: '2시간 전'
  },
  {
    id: 3,
    title: '리소스 부족 예상',
    message: '다음 주 백엔드팀의 업무량이 한계치에 근접할 예정입니다.',
    category: '인력',
    severity: 'medium',
    timeAgo: '4시간 전'
  }
])

// 헬퍼 함수들
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    notation: 'compact',
    maximumFractionDigits: 1
  }).format(amount)
}

const getAlertBorderClass = (severity: string) => {
  const classes = {
    'high': 'border-destructive/20 bg-destructive/10',
    'medium': 'border-secondary/50 bg-secondary/20',
    'low': 'border-primary/20 bg-primary/10'
  }
  return classes[severity] || classes['low']
}

const getAlertDotClass = (severity: string) => {
  const classes = {
    'high': 'bg-destructive',
    'medium': 'bg-secondary', 
    'low': 'bg-primary'
  }
  return classes[severity] || classes['low']
}

const askQuestion = (question: string) => {
  console.log('AI에게 질문:', question)
  // TODO: AI 채팅 기능 연동
}

// 데이터 로딩
onMounted(async () => {
  console.log('AI Insights Dashboard 로드됨')
})
</script>

<style scoped>
.ai-insights-dashboard {
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