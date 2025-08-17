<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        size="sm"
        class="h-8 gap-2"
        :class="[
          'justify-start text-left font-normal',
          !modelValue?.start && !modelValue?.end && 'text-muted-foreground'
        ]"
      >
        <CalendarIcon class="h-4 w-4" />
        <span class="hidden sm:inline">
          {{ formattedDateRange || placeholder }}
        </span>
        <span class="sm:hidden">
          {{ formattedDateRangeMobile || '날짜' }}
        </span>
      </Button>
    </PopoverTrigger>
    
    <PopoverContent class="w-auto p-0" align="start">
      <div class="flex flex-col">
        <!-- 프리셋 옵션 -->
        <div class="flex flex-col gap-1 p-3 border-b">
          <div class="text-sm font-medium mb-2">빠른 선택</div>
          <div class="grid grid-cols-2 gap-2">
            <Button
              v-for="preset in presets"
              :key="preset.label"
              variant="ghost"
              size="sm"
              class="h-8 justify-start"
              @click="selectPreset(preset)"
            >
              {{ preset.label }}
            </Button>
          </div>
        </div>
        
        <!-- 캘린더 -->
        <div class="p-3">
          <RangeCalendar
            v-model="calendarValue"
            class="rounded-md border"
          />
          
          <!-- 액션 버튼 -->
          <div class="flex items-center justify-end gap-2 mt-3 pt-3 border-t">
            <Button variant="outline" size="sm" @click="clearSelection">
              초기화
            </Button>
            <Button size="sm" @click="applySelection">
              적용
            </Button>
          </div>
        </div>
      </div>
    </PopoverContent>
  </Popover>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { CalendarIcon } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { RangeCalendar } from '@/components/ui/range-calendar';
import { CalendarDate, type DateValue, toCalendarDate, fromDate } from '@internationalized/date';

interface DateRange {
  start?: Date | string;
  end?: Date | string;
}

interface Preset {
  label: string;
  range: DateRange;
}

interface Props {
  modelValue?: DateRange | null;
  placeholder?: string;
  numberOfMonths?: number;
}

interface Emits {
  (e: 'update:modelValue', value: DateRange | null): void;
  (e: 'change', value: DateRange | null): void;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '날짜 범위 선택',
  numberOfMonths: 2,
});

const emit = defineEmits<Emits>();

// Internal date range state
const dateRange = ref<DateRange>({});

// Calendar value for RangeCalendar component
const calendarValue = ref<{ start: DateValue | undefined; end: DateValue | undefined }>({
  start: undefined,
  end: undefined,
});

// 프리셋 옵션들
const presets = computed<Preset[]>(() => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const last7Days = new Date(today);
  last7Days.setDate(last7Days.getDate() - 7);
  
  const last30Days = new Date(today);
  last30Days.setDate(last30Days.getDate() - 30);
  
  const thisMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
  
  const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);

  return [
    {
      label: '오늘',
      range: { start: today, end: today }
    },
    {
      label: '어제',
      range: { start: yesterday, end: yesterday }
    },
    {
      label: '지난 7일',
      range: { start: last7Days, end: today }
    },
    {
      label: '지난 30일',
      range: { start: last30Days, end: today }
    },
    {
      label: '이번 달',
      range: { start: thisMonthStart, end: today }
    },
    {
      label: '지난 달',
      range: { start: lastMonthStart, end: lastMonthEnd }
    }
  ];
});

// 포맷된 날짜 범위 표시
const formattedDateRange = computed(() => {
  if (!props.modelValue?.start || !props.modelValue?.end) return '';
  
  const start = typeof props.modelValue.start === 'string' 
    ? new Date(props.modelValue.start) 
    : props.modelValue.start;
  const end = typeof props.modelValue.end === 'string' 
    ? new Date(props.modelValue.end) 
    : props.modelValue.end;
    
  return `${formatDate(start)} ~ ${formatDate(end)}`;
});

// 모바일용 짧은 날짜 범위 표시
const formattedDateRangeMobile = computed(() => {
  if (!props.modelValue?.start || !props.modelValue?.end) return '';
  
  const start = typeof props.modelValue.start === 'string' 
    ? new Date(props.modelValue.start) 
    : props.modelValue.start;
  const end = typeof props.modelValue.end === 'string' 
    ? new Date(props.modelValue.end) 
    : props.modelValue.end;
    
  return `${formatDateShort(start)}~${formatDateShort(end)}`;
});

// 날짜 포맷팅 함수
function formatDate(date: Date | DateValue): string {
  if (date instanceof Date) {
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } else {
    // DateValue 객체인 경우
    return `${date.year}-${String(date.month).padStart(2, '0')}-${String(date.day).padStart(2, '0')}`;
  }
}

function formatDateShort(date: Date | DateValue): string {
  if (date instanceof Date) {
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric'
    });
  } else {
    // DateValue 객체인 경우
    return `${date.month}/${date.day}`;
  }
}

// Date를 DateValue로 변환하는 헬퍼 함수
function convertToDateValue(date: Date): DateValue {
  return toCalendarDate(fromDate(date, 'Asia/Seoul'));
}

// DateValue를 Date로 변환하는 헬퍼 함수
function convertToDate(dateValue: DateValue): Date {
  return new Date(dateValue.year, dateValue.month - 1, dateValue.day);
}

// 프리셋 선택
function selectPreset(preset: Preset) {
  dateRange.value = { ...preset.range };
  // RangeCalendar 값도 업데이트 - Date를 DateValue로 변환
  if (preset.range.start && preset.range.end) {
    const startDate = typeof preset.range.start === 'string' ? new Date(preset.range.start) : preset.range.start;
    const endDate = typeof preset.range.end === 'string' ? new Date(preset.range.end) : preset.range.end;
    
    calendarValue.value = {
      start: convertToDateValue(startDate),
      end: convertToDateValue(endDate),
    };
  }
  applySelection();
}

// 선택 적용
function applySelection() {
  const result = dateRange.value.start && dateRange.value.end ? dateRange.value : null;
  emit('update:modelValue', result);
  emit('change', result);
}

// 선택 초기화
function clearSelection() {
  dateRange.value = {};
  calendarValue.value = {
    start: undefined,
    end: undefined,
  };
  emit('update:modelValue', null);
  emit('change', null);
}

// Props 변경 감지하여 내부 상태 업데이트
watch(() => props.modelValue, (newValue) => {
  if (newValue && newValue.start && newValue.end) {
    dateRange.value = { ...newValue };
    
    // Date를 DateValue로 변환
    const startDate = typeof newValue.start === 'string' ? new Date(newValue.start) : newValue.start;
    const endDate = typeof newValue.end === 'string' ? new Date(newValue.end) : newValue.end;
    
    calendarValue.value = {
      start: convertToDateValue(startDate),
      end: convertToDateValue(endDate),
    };
  } else {
    dateRange.value = {};
    calendarValue.value = {
      start: undefined,
      end: undefined,
    };
  }
}, { immediate: true });

// RangeCalendar 값 변경 감지
watch(calendarValue, (newValue) => {
  if (newValue.start && newValue.end) {
    // DateValue를 Date로 변환
    dateRange.value = {
      start: convertToDate(newValue.start),
      end: convertToDate(newValue.end),
    };
  }
}, { deep: true });
</script>