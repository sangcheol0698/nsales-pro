<template>
  <Card class="relative overflow-hidden">
    <CardContent>
      <div>
        <div class="flex items-center justify-between mb-1">
          <h3 class="text-sm font-medium text-muted-foreground mb-3">
            {{ title }}
          </h3>
          <span
            :class="trendBadgeClass"
            class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
          >
            {{ trendText }}
          </span>
        </div>

        <div class="text-2xl font-bold text-foreground">
          {{ formatAnimatedValue(animatedValue) }}
        </div>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { Card, CardContent } from '@/components/ui/card';
import { type LucideIcon, Minus, TrendingDown, TrendingUp } from 'lucide-vue-next';

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

// 애니메이션용 값
const animatedValue = ref(0);

// 숫자 애니메이션 함수
function animateValue(start: number, end: number, duration: number = 1500) {
  if (start === end) {
    animatedValue.value = end;
    return;
  }

  const startTime = Date.now();
  const difference = end - start;

  const updateValue = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // easeOutCubic 이징 함수 적용
    const easing = 1 - Math.pow(1 - progress, 3);
    const currentValue = start + (difference * easing);

    animatedValue.value = currentValue;

    if (progress < 1) {
      requestAnimationFrame(updateValue);
    } else {
      animatedValue.value = end;
    }
  };

  requestAnimationFrame(updateValue);
}

// 애니메이션된 값 포맷팅
function formatAnimatedValue(value: number): string {
  if (props.formatType === 'text') {
    return String(props.value);
  }

  const numValue = Math.round(value);

  switch (props.formatType) {
    case 'currency':
      return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW',
        maximumFractionDigits: 0,
      }).format(numValue);
    case 'percentage':
      return `${(value).toFixed(1)}%`;
    case 'number':
    default:
      return new Intl.NumberFormat('ko-KR').format(numValue);
  }
}

// 값 포맷팅 (트렌드 계산용)
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

// 트렌드 배지 클래스 (shadcn-vue 스타일)
const trendBadgeClass = computed(() => {
  if (trend.value.isNeutral) {
    return 'bg-secondary text-secondary-foreground';
  }
  return trend.value.isPositive
    ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
    : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
});

// 트렌드 텍스트
const trendText = computed(() => {
  if (trend.value.isNeutral) return '변화없음';
  const sign = trend.value.isPositive ? '+' : '-';
  return `${sign}${trend.value.percentage.toFixed(1)}%`;
});

// 컴포넌트 마운트 시 애니메이션 시작
onMounted(() => {
  if (props.formatType !== 'text' && typeof props.value === 'number') {
    // 약간의 지연을 두고 애니메이션 시작 (순차적 효과)
    const delay = Math.random() * 200;
    setTimeout(() => {
      animateValue(0, props.value, 1500);
    }, delay);
  } else {
    animatedValue.value = typeof props.value === 'number' ? props.value : 0;
  }
});

// 값 변경 시 애니메이션 다시 시작
watch(() => props.value, (newValue, oldValue) => {
  if (props.formatType !== 'text' && typeof newValue === 'number' && typeof oldValue === 'number') {
    animateValue(oldValue, newValue, 800);
  } else {
    animatedValue.value = typeof newValue === 'number' ? newValue : 0;
  }
});
</script>