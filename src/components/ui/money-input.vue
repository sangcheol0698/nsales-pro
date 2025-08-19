<template>
  <div class="relative">
    <Input
      :id="id"
      ref="inputRef"
      :value="internalValue"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
      :placeholder="placeholder"
      :disabled="disabled"
      :name="name"
      class="text-right pr-8"
      v-bind="$attrs"
    />
    <div class="absolute inset-y-0 right-3 flex items-center text-sm text-muted-foreground pointer-events-none">
      원
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue';
import { Input } from '@/components/ui/input';

interface MoneyInputProps {
  modelValue?: number | null;
  placeholder?: string;
  disabled?: boolean;
  id?: string;
  name?: string;
}

interface MoneyInputEmits {
  'update:modelValue': [value: number | null];
  blur: [event: FocusEvent];
}

const props = withDefaults(defineProps<MoneyInputProps>(), {
  modelValue: null,
  placeholder: '0',
  disabled: false,
  name: '',
});

const emit = defineEmits<MoneyInputEmits>();

const inputRef = ref<HTMLInputElement>();
const isFocused = ref(false);
const internalValue = ref('');

// 숫자를 천 단위 콤마 형식으로 포맷팅
const formatNumber = (num: number | null): string => {
  if (num === null || num === undefined || isNaN(num)) return '';
  return num.toLocaleString('ko-KR');
};

// 문자열에서 숫자만 추출
const parseNumber = (str: string): number | null => {
  if (!str || str.trim() === '') return null;
  
  // 콤마와 공백 제거, 숫자만 추출
  const cleanStr = str.replace(/[,\s]/g, '');
  const num = parseInt(cleanStr, 10);
  
  return isNaN(num) ? null : num;
};


// 입력 처리
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const inputValue = target.value;
  
  // 숫자만 허용 (백스페이스, 삭제 등 제어 문자 허용)
  const numericValue = inputValue.replace(/[^\d]/g, '');
  
  // 내부 값 업데이트 (포커스 중에는 숫자만)
  internalValue.value = numericValue;
  
  // 모델 값 업데이트
  const parsedValue = parseNumber(numericValue);
  emit('update:modelValue', parsedValue);
};

// 포커스 획득 시
const handleFocus = () => {
  isFocused.value = true;
  
  // 포커스 시 숫자만 표시
  const value = props.modelValue;
  if (value === null || value === undefined || isNaN(value)) {
    internalValue.value = '';
  } else {
    internalValue.value = value.toString();
  }
  
  // 다음 틱에서 전체 선택
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.select(); // 전체 선택으로 편의성 향상
    }
  });
};

// 포커스 잃을 시
const handleBlur = (event: FocusEvent) => {
  isFocused.value = false;
  
  // 포커스 해제 시 포맷된 값으로 표시
  internalValue.value = formatNumber(props.modelValue);
  
  // Vee-Validate를 위해 blur 이벤트 전달
  emit('blur', event);
};

// modelValue 변경 감지
watch(() => props.modelValue, (newValue) => {
  // 포커스가 없을 때만 내부 값 업데이트
  if (!isFocused.value) {
    internalValue.value = formatNumber(newValue);
  }
}, { immediate: true });

// 메서드 노출
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
});
</script>

<script lang="ts">
// attrs 상속 비활성화 (Input 컴포넌트에 직접 전달하기 위해)
export default {
  inheritAttrs: false,
};
</script>