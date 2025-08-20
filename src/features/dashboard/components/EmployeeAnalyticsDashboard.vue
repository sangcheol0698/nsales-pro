<template>
  <div class="employee-dashboard space-y-6">
    <!-- 직원 현황 개요 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ employeeStats.totalEmployees }}</p>
            <p class="text-sm text-muted-foreground">전체 직원</p>
            <div class="flex items-center justify-center mt-2">
              <UserPlus class="h-4 w-4 text-primary mr-1" />
              <span class="text-sm text-primary">+{{ employeeStats.newHires }}명</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ employeeStats.activeEmployees }}</p>
            <p class="text-sm text-muted-foreground">활성 직원</p>
            <Progress :value="(employeeStats.activeEmployees / employeeStats.totalEmployees) * 100" class="mt-2" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-primary">{{ employeeStats.averageTenure }}</p>
            <p class="text-sm text-muted-foreground">평균 재직기간 (개월)</p>
            <Badge variant="outline" class="mt-2">안정적</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-secondary-foreground">{{ turnoverRate.toFixed(1) }}%</p>
            <p class="text-sm text-muted-foreground">이직률</p>
            <Badge :variant="turnoverRate > 10 ? 'destructive' : 'secondary'" class="mt-2">
              {{ turnoverRate > 10 ? '주의' : '양호' }}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 부서별 현황 & 직급별 분포 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>부서별 인력 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="dept in departmentStats" :key="dept.name"
                 class="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div>
                <p class="font-medium">{{ dept.name }}</p>
                <p class="text-sm text-muted-foreground">{{ dept.projects }}개 프로젝트 참여</p>
              </div>
              <div class="text-right">
                <p class="font-bold">{{ dept.members }}명</p>
                <Badge :variant="getUtilizationVariant(dept.utilization)">{{ dept.utilization }}%</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>직급별 분포</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            <div v-for="rank in rankDistribution" :key="rank.level"
                 class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="font-medium">{{ rank.level }}</span>
                <span class="text-sm">{{ rank.count }}명 ({{ rank.percentage }}%)</span>
              </div>
              <Progress :value="rank.percentage" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 성과 지표 & 스킬 매트릭스 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>팀별 성과 지표</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="performance in teamPerformance" :key="performance.team">
              <div class="flex items-center justify-between mb-2">
                <span class="font-medium">{{ performance.team }}</span>
                <Badge :variant="getPerformanceVariant(performance.score)">
                  {{ performance.score.toFixed(1) }}점
                </Badge>
              </div>
              <Progress :value="performance.score * 10" />
              <div class="flex justify-between text-xs text-muted-foreground mt-1">
                <span>목표 달성률: {{ performance.goalAchievement }}%</span>
                <span>만족도: {{ performance.satisfaction }}/5</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>핵심 스킬 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            <div v-for="skill in skillMatrix" :key="skill.name">
              <div class="flex items-center justify-between mb-1">
                <span class="text-sm font-medium">{{ skill.name }}</span>
                <div class="flex items-center gap-2">
                  <Badge variant="outline">{{ skill.experts }}명 전문가</Badge>
                  <span class="text-xs text-muted-foreground">{{ skill.average }}/5</span>
                </div>
              </div>
              <Progress :value="skill.average * 20" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 채용 & 개발 계획 -->
    <Card>
      <CardHeader>
        <CardTitle>인력 개발 현황</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center p-4 bg-primary/10 rounded-lg">
            <Calendar class="h-8 w-8 text-primary mx-auto mb-2" />
            <p class="text-2xl font-bold text-primary">{{ trainingStats.ongoing }}</p>
            <p class="text-sm text-muted-foreground">진행중인 교육</p>
          </div>
          
          <div class="text-center p-4 bg-primary/10 rounded-lg">
            <GraduationCap class="h-8 w-8 text-primary mx-auto mb-2" />
            <p class="text-2xl font-bold text-primary">{{ trainingStats.completed }}</p>
            <p class="text-sm text-muted-foreground">완료된 교육 (이번 달)</p>
          </div>
          
          <div class="text-center p-4 bg-primary/10 rounded-lg">
            <Target class="h-8 w-8 text-primary mx-auto mb-2" />
            <p class="text-2xl font-bold text-primary">{{ trainingStats.planned }}</p>
            <p class="text-sm text-muted-foreground">계획된 교육</p>
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
import { Progress } from '@/components/ui/progress'
import { UserPlus, Calendar, GraduationCap, Target } from 'lucide-vue-next'

// Mock 데이터
const employeeStats = ref({
  totalEmployees: 156,
  activeEmployees: 148,
  newHires: 8,
  averageTenure: 28
})

const departmentStats = ref([
  { name: '개발팀', members: 45, projects: 12, utilization: 87 },
  { name: '디자인팀', members: 18, projects: 8, utilization: 82 },
  { name: '기획팀', members: 22, projects: 15, utilization: 78 },
  { name: '영업팀', members: 28, projects: 20, utilization: 92 },
  { name: '인사팀', members: 12, projects: 5, utilization: 65 },
  { name: '재무팀', members: 15, projects: 7, utilization: 71 },
  { name: 'QA팀', members: 16, projects: 10, utilization: 88 }
])

const rankDistribution = ref([
  { level: '임원', count: 8, percentage: 5.1 },
  { level: '부장/팀장', count: 18, percentage: 11.5 },
  { level: '과장/선임', count: 35, percentage: 22.4 },
  { level: '대리/주임', count: 42, percentage: 26.9 },
  { level: '사원/인턴', count: 53, percentage: 34.0 }
])

const teamPerformance = ref([
  { team: '프론트엔드팀', score: 8.7, goalAchievement: 95, satisfaction: 4.2 },
  { team: '백엔드팀', score: 8.4, goalAchievement: 88, satisfaction: 4.0 },
  { team: 'DevOps팀', score: 8.9, goalAchievement: 92, satisfaction: 4.5 },
  { team: 'AI팀', score: 9.1, goalAchievement: 97, satisfaction: 4.3 },
  { team: '모바일팀', score: 8.2, goalAchievement: 85, satisfaction: 3.9 }
])

const skillMatrix = ref([
  { name: 'JavaScript/TypeScript', experts: 28, average: 4.2 },
  { name: 'Python', experts: 15, average: 3.8 },
  { name: 'React/Vue.js', experts: 22, average: 4.0 },
  { name: 'Node.js', experts: 18, average: 3.9 },
  { name: 'DevOps/Cloud', experts: 12, average: 3.6 },
  { name: 'AI/ML', experts: 8, average: 3.4 }
])

const trainingStats = ref({
  ongoing: 12,
  completed: 28,
  planned: 15
})

// Computed 속성
const turnoverRate = computed(() => 8.5) // Mock 데이터

// 헬퍼 함수들
const getUtilizationVariant = (utilization: number) => {
  if (utilization >= 90) return 'destructive'
  if (utilization >= 80) return 'default'
  return 'secondary'
}

const getPerformanceVariant = (score: number) => {
  if (score >= 8.5) return 'default'
  if (score >= 7.5) return 'secondary'
  return 'outline'
}
</script>

<style scoped>
.employee-dashboard {
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