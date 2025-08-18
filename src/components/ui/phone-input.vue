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
      class="text-left"
      v-bind="$attrs"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue';
import { Input } from '@/components/ui/input';

interface PhoneInputProps {
  modelValue?: string | null;
  placeholder?: string;
  disabled?: boolean;
  id?: string;
  name?: string;
}

interface PhoneInputEmits {
  'update:modelValue': [value: string | null];
  blur: [event: FocusEvent];
}

const props = withDefaults(defineProps<PhoneInputProps>(), {
  modelValue: null,
  placeholder: '010-0000-0000',
  disabled: false,
  name: '',
});

const emit = defineEmits<PhoneInputEmits>();

const inputRef = ref<HTMLInputElement>();
const isFocused = ref(false);
const internalValue = ref('');

// 전화번호를 하이픈 포함 형식으로 포맷팅
const formatPhoneNumber = (phone: string | null): string => {
  if (!phone || phone.trim() === '') return '';
  
  // 숫자만 추출
  const numbersOnly = phone.replace(/[^\d]/g, '');
  
  // 길이에 따라 다른 포맷팅 적용
  if (numbersOnly.length <= 3) {
    return numbersOnly;
  } else if (numbersOnly.length <= 7) {
    return `${numbersOnly.slice(0, 3)}-${numbersOnly.slice(3)}`;
  } else if (numbersOnly.length <= 11) {
    return `${numbersOnly.slice(0, 3)}-${numbersOnly.slice(3, 7)}-${numbersOnly.slice(7)}`;
  } else {
    // 11자리를 초과하는 경우 11자리까지만 사용
    const trimmed = numbersOnly.slice(0, 11);
    return `${trimmed.slice(0, 3)}-${trimmed.slice(3, 7)}-${trimmed.slice(7)}`;
  }
};

// 전화번호 유효성 검증
const isValidPhoneNumber = (phone: string): boolean => {
  if (!phone) return false;
  
  const numbersOnly = phone.replace(/[^\d]/g, '');
  
  // 한국 전화번호 패턴 검증
  const patterns = [
    /^010\d{8}$/, // 010-XXXX-XXXX (11자리)
    /^01[1-9]\d{7,8}$/, // 011, 016, 017, 018, 019 등 (10-11자리)
    /^02\d{7,8}$/, // 서울 지역번호 (9-10자리)
    /^0[3-6][1-4]\d{6,7}$/, // 지역번호 (9-10자리)
    /^070\d{8}$/, // 인터넷전화 (11자리)
    /^1588\d{4}$/, // 대표번호 (8자리)
    /^15\d{6}$/, // 대표번호 (8자리)
  ];
  
  return patterns.some(pattern => pattern.test(numbersOnly));
};

// 문자열에서 숫자만 추출하여 원본 값 반환
const parsePhoneNumber = (str: string): string | null => {
  if (!str || str.trim() === '') return null;
  
  // 숫자만 추출
  const numbersOnly = str.replace(/[^\d]/g, '');
  
  return numbersOnly || null;
};


// 입력 처리
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const inputValue = target.value;
  
  // 숫자만 허용 (백스페이스, 삭제 등 제어 문자 허용)
  const numericValue = inputValue.replace(/[^\d]/g, '');
  
  // 11자리 제한
  const limitedValue = numericValue.slice(0, 11);
  
  // 내부 값 업데이트 (포커스 중에는 숫자만)
  internalValue.value = limitedValue;
  
  // 모델 값 업데이트
  const parsedValue = parsePhoneNumber(limitedValue);
  emit('update:modelValue', parsedValue);
};

// 포커스 획득 시
const handleFocus = () => {
  isFocused.value = true;
  
  // 포커스 시 숫자만 표시
  const value = props.modelValue;
  if (!value || value.trim() === '') {
    internalValue.value = '';
  } else {
    internalValue.value = value.replace(/[^\d]/g, '');
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
  internalValue.value = formatPhoneNumber(props.modelValue);
  
  // 유효성 검증 (선택사항 - 경고만 표시)
  if (props.modelValue && !isValidPhoneNumber(props.modelValue)) {
    console.warn('유효하지 않은 전화번호 형식:', props.modelValue);
  }
  
  // Vee-Validate를 위해 blur 이벤트 전달
  emit('blur', event);
};

// modelValue 변경 감지
watch(() => props.modelValue, (newValue) => {
  // 포커스가 없을 때만 내부 값 업데이트
  if (!isFocused.value) {
    internalValue.value = formatPhoneNumber(newValue);
  }
}, { immediate: true });

// 메서드 노출
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
  isValid: () => props.modelValue ? isValidPhoneNumber(props.modelValue) : true,
});
</script>

<script lang="ts">
// attrs 상속 비활성화 (Input 컴포넌트에 직접 전달하기 위해)
export default {
  inheritAttrs: false,
};
</script>