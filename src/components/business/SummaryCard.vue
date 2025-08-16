<template>
  <Card class="relative overflow-hidden">
    <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle class="text-sm font-medium">
        {{ title }}
      </CardTitle>
      <component 
        :is="icon" 
        class="h-4 w-4 text-muted-foreground"
      />
    </CardHeader>
    <CardContent>
      <div class="text-2xl font-bold">
        {{ formattedValue }}
      </div>
      <div class="flex items-center pt-1 text-xs text-muted-foreground">
        <component 
          :is="trendIcon" 
          :class="trendColorClass"
          class="h-4 w-4 mr-1"
        />
        <span :class="trendColorClass">
          {{ trendText }}
        </span>
        <span class="ml-1">
          {{ description }}
        </span>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { 
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  type LucideIcon
} from 'lucide-vue-next';

interface SummaryCardProps {
  title: string;
  value: number | string;
  previousValue?: number;
  description?: string;
  icon: LucideIcon;
  formatType?: 'number' | 'currency' | 'percentage' | 'text';
  showTrend?: boolean;
}

const props = withDefaults(defineProps<SummaryCardProps>(), {
  description: '전월 대비',
  formatType: 'number',
  showTrend: true,
});

// 값 포맷팅
const formattedValue = computed(() => {
  if (props.formatType === 'text') {
    return props.value;
  }
  
  const numValue = typeof props.value === 'string' ? parseFloat(props.value) : props.value;
  
  switch (props.formatType) {
    case 'currency':
      return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        maximumFractionDigits: 0,
      }).format(numValue);
    case 'percentage':
      return `${numValue.toFixed(1)}%`;
    case 'number':
    default:
      return new Intl.NumberFormat('ko-KR').format(numValue);
  }
});

// 트렌드 계산
const trend = computed(() => {
  if (!props.showTrend || !props.previousValue || typeof props.value !== 'number') {
    return { percentage: 0, isPositive: null, isNeutral: true };
  }
  
  const currentValue = props.value;
  const prevValue = props.previousValue;
  
  if (prevValue === 0) {
    return { percentage: 0, isPositive: null, isNeutral: true };
  }
  
  const percentage = ((currentValue - prevValue) / prevValue) * 100;
  const isPositive = percentage > 0;
  const isNeutral = Math.abs(percentage) < 0.1;
  
  return { percentage: Math.abs(percentage), isPositive, isNeutral };
});

// 트렌드 아이콘
const trendIcon = computed(() => {
  if (trend.value.isNeutral) return Minus;
  return trend.value.isPositive ? TrendingUp : TrendingDown;
});

// 트렌드 색상
const trendColorClass = computed(() => {
  if (trend.value.isNeutral) return 'text-muted-foreground';
  return trend.value.isPositive 
    ? 'text-green-600 dark:text-green-400' 
    : 'text-red-600 dark:text-red-400';
});

// 트렌드 텍스트
const trendText = computed(() => {
  if (trend.value.isNeutral) return '변화없음';
  const sign = trend.value.isPositive ? '+' : '-';
  return `${sign}${trend.value.percentage.toFixed(1)}%`;
});
</script>