<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        :class="cn(
          'w-full justify-start text-left font-normal',
          !value && 'text-muted-foreground',
          className
        )"
      >
        <CalendarIcon class="mr-2 h-4 w-4" />
        {{ value ? df.format(value.toDate(getLocalTimeZone())) : placeholder }}
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0" align="start">
      <CalendarRoot
        v-slot="{ date, grid, weekDays }"
        v-model:placeholder="placeholder"
        v-model="value"
        @update:model-value="handleDateSelect"
        :disabled="disabled"
        class="rounded-md border p-3"
        initial-focus
      >
        <CalendarHeader>
          <CalendarHeading class="flex w-full items-center justify-between gap-2">
            <Select
              :default-value="placeholder.month.toString()"
              @update:model-value="(v) => {
                if (!v || !placeholder) return;
                if (Number(v) === placeholder?.month) return;
                placeholder = placeholder.set({
                  month: Number(v),
                })
              }"
            >
              <SelectTrigger aria-label="월 선택" class="w-[60%]">
                <SelectValue placeholder="월 선택" />
              </SelectTrigger>
              <SelectContent class="max-h-[200px]">
                <SelectItem
                  v-for="month in createYear({ dateObj: date })"
                  :key="month.toString()"
                  :value="month.month.toString()"
                >
                  {{ formatter.custom(toDate(month), { month: 'long' }) }}
                </SelectItem>
              </SelectContent>
            </Select>

            <Select
              :default-value="placeholder.year.toString()"
              @update:model-value="(v) => {
                if (!v || !placeholder) return;
                if (Number(v) === placeholder?.year) return;
                placeholder = placeholder.set({
                  year: Number(v),
                })
              }"
            >
              <SelectTrigger aria-label="년도 선택" class="w-[40%]">
                <SelectValue placeholder="년도 선택" />
              </SelectTrigger>
              <SelectContent class="max-h-[200px]">
                <SelectItem
                  v-for="yearValue in createDecade({ dateObj: date, startIndex: -10, endIndex: 10 })"
                  :key="yearValue.toString()"
                  :value="yearValue.year.toString()"
                >
                  {{ yearValue.year }}
                </SelectItem>
              </SelectContent>
            </Select>
          </CalendarHeading>
        </CalendarHeader>

        <div class="flex flex-col space-y-4 pt-4 sm:flex-row sm:gap-x-4 sm:gap-y-0">
          <CalendarGrid v-for="month in grid" :key="month.value.toString()">
            <CalendarGridHead>
              <CalendarGridRow>
                <CalendarHeadCell
                  v-for="day in weekDays"
                  :key="day"
                >
                  {{ day }}
                </CalendarHeadCell>
              </CalendarGridRow>
            </CalendarGridHead>
            <CalendarGridBody class="grid">
              <CalendarGridRow v-for="(weekDates, index) in month.rows" :key="`weekDate-${index}`" class="mt-2 w-full">
                <CalendarCell
                  v-for="weekDate in weekDates"
                  :key="weekDate.toString()"
                  :date="weekDate"
                >
                  <CalendarCellTrigger
                    :day="weekDate"
                    :month="month.value"
                  />
                </CalendarCell>
              </CalendarGridRow>
            </CalendarGridBody>
          </CalendarGrid>
        </div>
      </CalendarRoot>
    </PopoverContent>
  </Popover>
</template>

<script setup lang="ts">
import type { DateValue } from '@internationalized/date';
import { DateFormatter, getLocalTimeZone, parseDate, today } from '@internationalized/date';
import { ref, watch } from 'vue';
import { CalendarIcon } from 'lucide-vue-next';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  CalendarCell,
  CalendarCellTrigger,
  CalendarGrid,
  CalendarGridBody,
  CalendarGridHead,
  CalendarGridRow,
  CalendarHeadCell,
  CalendarHeader,
  CalendarHeading,
} from '@/components/ui/calendar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarRoot, useDateFormatter } from 'reka-ui';
import { createDecade, createYear, toDate } from 'reka-ui/date';

interface DatePickerProps {
  modelValue?: Date | string | null;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

interface DatePickerEmits {
  'update:modelValue': [value: Date | null];
}

const props = withDefaults(defineProps<DatePickerProps>(), {
  placeholder: '날짜를 선택하세요',
  disabled: false,
});

const emit = defineEmits<DatePickerEmits>();

// 한국어 날짜 포맷터
const df = new DateFormatter('ko-KR', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
});

// reka-ui 포맷터 (월/년도 선택용)
const formatter = useDateFormatter('ko-KR');

const value = ref<DateValue | undefined>();
const placeholder = ref<DateValue>(today(getLocalTimeZone()));

// props.modelValue가 변경될 때 내부 value 동기화
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    value.value = undefined;
    return;
  }

  try {
    let dateToConvert: Date;
    if (typeof newValue === 'string') {
      dateToConvert = new Date(newValue);
    } else {
      dateToConvert = newValue;
    }

    // Date를 YYYY-MM-DD 형식으로 변환 후 DateValue로 파싱
    const year = dateToConvert.getFullYear();
    const month = String(dateToConvert.getMonth() + 1).padStart(2, '0');
    const day = String(dateToConvert.getDate()).padStart(2, '0');
    const dateString = `${year}-${month}-${day}`;

    const dateValue = parseDate(dateString);
    value.value = dateValue;
    // placeholder도 선택된 날짜로 업데이트 (월/년도 선택이 올바르게 표시되도록)
    placeholder.value = dateValue;
  } catch (error) {
    console.warn('Invalid date provided to DatePicker:', newValue);
    value.value = undefined;
  }
}, { immediate: true });

const handleDateSelect = (selectedValue: DateValue | undefined) => {
  value.value = selectedValue;

  if (!selectedValue) {
    emit('update:modelValue', null);
    return;
  }

  // placeholder도 선택된 날짜로 업데이트
  placeholder.value = selectedValue;

  // DateValue를 Date 객체로 변환
  try {
    const date = selectedValue.toDate(getLocalTimeZone());
    emit('update:modelValue', date);
  } catch (error) {
    console.warn('Error converting DateValue to Date:', error);
    emit('update:modelValue', null);
  }
};
</script>