<template>
  <Badge :variant="variant" :class="cn('capitalize', badgeClass)">
    <component v-if="icon" :is="icon" class="mr-1 h-3 w-3" />
    {{ label }}
  </Badge>
</template>

<script setup lang="ts">
import { type Component, computed } from 'vue';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle, Clock, UserCheck, UserX, XCircle, Star, Award, Shield, CircleDot, Circle } from 'lucide-vue-next';

interface StatusBadgeProps {
  status: string;
  type?: 'default' | 'employee' | 'project' | 'task' | 'sales' | 'partner';
  customLabel?: string;
}

const props = withDefaults(defineProps<StatusBadgeProps>(), {
  type: 'default',
});

const statusConfig = computed(() => {
  const configs = {
    employee: {
      '재직': {
        variant: 'default',
        label: '재직',
        icon: UserCheck,
        class: 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
      },
      '휴직': {
        variant: 'secondary',
        label: '휴직',
        icon: Clock,
        class: 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800',
      },
      '퇴사': {
        variant: 'outline',
        label: '퇴사',
        icon: UserX,
        class: 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/30 dark:text-gray-400 dark:border-gray-800',
      },
    },
    project: {
      'ACTIVE': {
        variant: 'default',
        label: '진행중',
        icon: CheckCircle,
        class: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      },
      'COMPLETED': {
        variant: 'default',
        label: '완료',
        icon: CheckCircle,
        class: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      },
      'ON_HOLD': {
        variant: 'secondary',
        label: '보류',
        icon: Clock,
        class: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      },
      'CANCELLED': {
        variant: 'destructive',
        label: '취소',
        icon: XCircle,
        class: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      },
      // Korean project statuses
      '진행중': {
        variant: 'default',
        label: '진행중',
        icon: Clock,
        class: 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800',
      },
      '완료': {
        variant: 'default',
        label: '완료',
        icon: CheckCircle,
        class: 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
      },
      '예약': {
        variant: 'secondary',
        label: '예약',
        icon: Clock,
        class: 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800',
      },
    },
    task: {
      'TODO': {
        variant: 'outline',
        label: '할 일',
        icon: Clock,
        class: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
      },
      'IN_PROGRESS': {
        variant: 'default',
        label: '진행중',
        icon: AlertCircle,
        class: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      },
      'DONE': {
        variant: 'default',
        label: '완료',
        icon: CheckCircle,
        class: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      },
      'CANCELLED': {
        variant: 'destructive',
        label: '취소',
        icon: XCircle,
        class: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      },
    },
    sales: {
      '미수금': {
        variant: 'secondary',
        label: '미수금',
        icon: Clock,
        class: 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800',
      },
      '수금완료': {
        variant: 'default',
        label: '수금완료',
        icon: CheckCircle,
        class: 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
      },
      '취소': {
        variant: 'destructive',
        label: '취소',
        icon: XCircle,
        class: 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800',
      },
    },
    partner: {
      'A': {
        variant: 'default',
        label: 'A등급',
        icon: Star,
        class: 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800',
      },
      'B': {
        variant: 'default',
        label: 'B등급',
        icon: Award,
        class: 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800',
      },
      'C': {
        variant: 'secondary',
        label: 'C등급',
        icon: Shield,
        class: 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
      },
      'D': {
        variant: 'outline',
        label: 'D등급',
        icon: CircleDot,
        class: 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800',
      },
      'E': {
        variant: 'destructive',
        label: 'E등급',
        icon: Circle,
        class: 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800',
      },
    },
    default: {
      'ACTIVE': { variant: 'default', label: '활성', icon: CheckCircle },
      'INACTIVE': { variant: 'secondary', label: '비활성', icon: XCircle },
      'PENDING': { variant: 'outline', label: '대기', icon: Clock },
      'COMPLETED': { variant: 'default', label: '완료', icon: CheckCircle },
      'CANCELLED': { variant: 'destructive', label: '취소', icon: XCircle },
      // 직원 상태 기본값들
      '재직': { variant: 'default', label: '재직', icon: UserCheck },
      '휴직': { variant: 'secondary', label: '휴직', icon: Clock },
      '퇴사': { variant: 'outline', label: '퇴사', icon: UserX },
    },
  };

  const config = configs[props.type as keyof typeof configs];
  return config?.[props.status as keyof typeof config] || {
    variant: 'secondary',
    label: props.status,
    icon: AlertCircle,
  };
});

const variant = computed(() => statusConfig.value.variant);
const label = computed(() => props.customLabel || statusConfig.value.label);
const icon = computed(() => statusConfig.value.icon as Component);
const badgeClass = computed(() => statusConfig.value.class || '');
</script>