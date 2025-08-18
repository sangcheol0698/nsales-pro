<template>
  <Form
    v-slot="{ handleSubmit, errors, values }"
    :validation-schema="validationSchema"
    :initial-values="initialValues"
    :key="`partner-edit-form-${props.partner?.id || 'new'}`"
    ref="formRef"
  >
    <form @submit.prevent="handleSubmit(onSubmit)" class="space-y-6">
      <!-- 기본 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">기본 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 협력사명 -->
          <FormField v-slot="{ componentField }" name="name">
            <FormItem>
              <FormLabel>협력사명 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="협력사명을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 대표자명 -->
          <FormField v-slot="{ componentField }" name="ceoName">
            <FormItem>
              <FormLabel>대표자명 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="대표자명을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 등급 -->
          <FormField v-slot="{ componentField }" name="grade">
            <FormItem>
              <FormLabel>등급</FormLabel>
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="등급을 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="A">A등급</SelectItem>
                  <SelectItem value="B">B등급</SelectItem>
                  <SelectItem value="C">C등급</SelectItem>
                  <SelectItem value="D">D등급</SelectItem>
                  <SelectItem value="E">E등급</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 수수료율 -->
          <FormField v-slot="{ componentField }" name="commissionRate">
            <FormItem>
              <FormLabel>수수료율 (%)</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  placeholder="0"
                  min="0"
                  max="100"
                  step="0.1"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- 영업대표 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">영업대표 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 영업대표명 -->
          <FormField v-slot="{ componentField }" name="salesRepName">
            <FormItem>
              <FormLabel>영업대표명 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="영업대표명을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 영업대표 연락처 -->
          <FormField v-slot="{ componentField }" name="salesRepPhone">
            <FormItem>
              <FormLabel>영업대표 연락처 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="010-0000-0000"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 영업대표 이메일 -->
          <FormField v-slot="{ componentField }" name="salesRepEmail">
            <FormItem>
              <FormLabel>영업대표 이메일</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="email@example.com"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- 주소 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">주소 정보</h3>
        <div class="grid grid-cols-1 gap-4">
          <!-- 우편번호 -->
          <FormField v-slot="{ componentField }" name="zipcode">
            <FormItem>
              <FormLabel>우편번호</FormLabel>
              <FormControl>
                <Input
                  placeholder="우편번호를 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 도로명 주소 -->
          <FormField v-slot="{ componentField }" name="street">
            <FormItem>
              <FormLabel>도로명 주소</FormLabel>
              <FormControl>
                <Input
                  placeholder="도로명 주소를 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 상세 주소 -->
          <FormField v-slot="{ componentField }" name="detail">
            <FormItem>
              <FormLabel>상세 주소</FormLabel>
              <FormControl>
                <Input
                  placeholder="상세 주소를 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- 추가 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">추가 정보</h3>
        <div class="grid grid-cols-1 gap-4">
          <!-- 메모 -->
          <FormField v-slot="{ componentField }" name="comment">
            <FormItem>
              <FormLabel>메모</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="추가 메모를 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- 폼 액션 버튼 -->
      <div class="flex justify-end gap-2 pt-4 border-t">
        <Button type="button" variant="outline" @click="onCancel">
          취소
        </Button>
        <Button type="submit" :disabled="loading">
          <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
          협력사 수정
        </Button>
      </div>
    </form>
  </Form>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Loader2 } from 'lucide-vue-next';
import PartnerUpdate from '@/features/partner/entity/PartnerUpdate';
import PartnerSearch from '@/features/partner/entity/PartnerSearch';
import { Textarea } from '@/components/ui/textarea';

interface PartnerEditFormProps {
  loading?: boolean;
  partner?: PartnerSearch | null;
}

interface PartnerEditFormEmits {
  submit: [partner: PartnerUpdate];
  cancel: [];
}

const props = withDefaults(defineProps<PartnerEditFormProps>(), {
  loading: false,
  partner: null,
});

const emit = defineEmits<PartnerEditFormEmits>();

const formRef = ref<any>(null);

// Zod 스키마
const formSchema = toTypedSchema(z.object({
  name: z.string().min(1, '협력사명은 필수입니다.'),
  ceoName: z.string().min(1, '대표자명은 필수입니다.'),
  salesRepName: z.string().min(1, '영업대표명은 필수입니다.'),
  salesRepPhone: z.string().min(1, '영업대표 연락처는 필수입니다.'),
  // 선택적 필드들
  salesRepEmail: z.string().email('올바른 이메일 형식이 아닙니다.').optional().or(z.literal('')),
  commissionRate: z.number().min(0, '수수료율은 0 이상이어야 합니다.').max(100, '수수료율은 100 이하여야 합니다.').optional(),
  street: z.string().optional(),
  detail: z.string().optional(),
  zipcode: z.string().optional(),
  grade: z.string().optional(),
  comment: z.string().optional(),
}));

// 유효성 검증 스키마
const validationSchema = formSchema;

// 초기값
const initialValues = ref({
  name: '',
  ceoName: '',
  salesRepName: '',
  salesRepPhone: '',
  salesRepEmail: '',
  commissionRate: undefined,
  street: '',
  detail: '',
  zipcode: '',
  grade: '',
  comment: '',
});

// props.partner 변경 감지하여 초기값 업데이트
watch(() => props.partner, async (partner) => {
  if (partner) {
    console.log('PartnerEditForm 초기값 설정:', partner);

    // 주소에서 우편번호, 도로명, 상세 주소 추출 (간단한 방식)
    const addressParts = partner.address.split(' ');
    const zipcode = addressParts.length > 0 && /^\d{5}$/.test(addressParts[0]) ? addressParts[0] : '';
    const street = zipcode ? addressParts.slice(1, -1).join(' ') : addressParts.slice(0, -1).join(' ');
    const detail = addressParts.length > 0 ? addressParts[addressParts.length - 1] : '';

    initialValues.value = {
      name: partner.name || '',
      ceoName: partner.ceoName || '',
      salesRepName: partner.salesRepName || '',
      salesRepPhone: partner.salesRepPhone || '',
      salesRepEmail: partner.salesRepEmail || '',
      commissionRate: undefined, // PartnerSearch에는 commissionRate가 없으므로 undefined
      street: street || '',
      detail: detail || '',
      zipcode: zipcode || '',
      grade: partner.grade || '',
      comment: '', // PartnerSearch에는 comment가 없으므로 빈 값
    };

    console.log('설정된 초기값:', initialValues.value);

    // 다음 틱에서 폼을 리셋하여 초기값이 올바르게 적용되도록 함
    await nextTick();
    if (formRef.value && formRef.value.resetForm) {
      formRef.value.resetForm({ values: initialValues.value });
      console.log('협력사 수정 폼 리셋 완료');
    }
  }
}, { immediate: true });

// 폼 제출
const onSubmit = (values: any) => {
  console.log('협력사 수정 폼 제출 시작:', values);

  if (!props.partner?.id) {
    console.error('Partner ID is missing');
    return;
  }

  const partnerData = {
    id: props.partner.id,
    name: values.name,
    ceoName: values.ceoName,
    salesRepName: values.salesRepName,
    salesRepPhone: values.salesRepPhone,
    salesRepEmail: values.salesRepEmail || undefined,
    commissionRate: values.commissionRate || undefined,
    street: values.street || undefined,
    detail: values.detail || undefined,
    zipcode: values.zipcode || undefined,
    grade: values.grade || undefined,
    comment: values.comment || undefined,
    modifiedDateTime: props.partner.modifiedDateTime, // 낙관적 동시성 제어용
  };

  console.log('변환된 협력사 수정 데이터:', partnerData);
  console.log('낙관적 동시성 제어 - modifiedDateTime:', partnerData.modifiedDateTime);

  const partner = PartnerUpdate.fromFormData(partnerData);
  console.log('생성된 협력사 수정 객체:', partner);

  emit('submit', partner);
};

// 폼 취소
const onCancel = () => {
  emit('cancel');
};
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>