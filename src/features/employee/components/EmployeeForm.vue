<template>
  <Form
    v-slot="{ handleSubmit, errors, values }"
    :validation-schema="validationSchema"
    :initial-values="initialValues"
  >
    <form @submit.prevent="handleSubmit(onSubmit)" class="space-y-6">
      <!-- 기본 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">기본 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 이름 -->
          <FormField v-slot="{ componentField }" name="name">
            <FormItem>
              <FormLabel>이름 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="이름을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 이메일 -->
          <FormField v-slot="{ componentField }" name="email">
            <FormItem>
              <FormLabel>이메일 <span class="text-red-500">*</span></FormLabel>
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

          <!-- 전화번호 -->
          <FormField v-slot="{ componentField }" name="phone">
            <FormItem>
              <FormLabel>전화번호 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="010-0000-0000"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 담당 부서 -->
          <FormField v-slot="{ field }" name="departmentId">
            <FormItem>
              <FormLabel>담당 부서 <span class="text-red-500">*</span></FormLabel>
              <div class="flex gap-2">
                <Select
                  :model-value="field.value ? String(field.value) : ''"
                  @update:model-value="(value) => field.onChange(Number(value))"
                  @blur="field.onBlur"
                  :name="field.name"
                  :disabled="departmentsLoading"
                >
                  <FormControl>
                    <SelectTrigger class="flex-1">
                      <SelectValue
                        :placeholder="departmentsLoading ? '부서 정보 로딩 중...' : departmentsError ? '부서 정보 로드 실패' : '부서를 선택하세요'"
                      />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem
                      v-for="dept in departmentOptions"
                      :key="dept.value"
                      :value="String(dept.value)"
                    >
                      {{ dept.label }}
                    </SelectItem>
                    <SelectItem v-if="departmentOptions.length === 0 && !departmentsLoading" value="" disabled>
                      부서 정보가 없습니다
                    </SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  variant="outline"
                  @click="openOrgDialog(field)"
                  class="whitespace-nowrap h-9 w-15"
                >
                  조직도
                </Button>
              </div>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- 직무 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">직무 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 직급 -->
          <FormField v-slot="{ componentField }" name="rank">
            <FormItem>
              <FormLabel>직급 <span class="text-red-500">*</span></FormLabel>
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="직급을 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="사원">사원</SelectItem>
                  <SelectItem value="선임">선임</SelectItem>
                  <SelectItem value="책임">책임</SelectItem>
                  <SelectItem value="팀장">팀장</SelectItem>
                  <SelectItem value="수석">수석</SelectItem>
                  <SelectItem value="이사">이사</SelectItem>
                  <SelectItem value="기술이사">기술이사</SelectItem>
                  <SelectItem value="상무">상무</SelectItem>
                  <SelectItem value="부사장">부사장</SelectItem>
                  <SelectItem value="사장">사장</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 등급 -->
          <FormField v-slot="{ componentField }" name="grade">
            <FormItem>
              <FormLabel>등급 <span class="text-red-500">*</span></FormLabel>
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="등급을 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="초급">초급</SelectItem>
                  <SelectItem value="중급">중급</SelectItem>
                  <SelectItem value="고급">고급</SelectItem>
                  <SelectItem value="특급">특급</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 유형 -->
          <FormField v-slot="{ componentField }" name="type">
            <FormItem>
              <FormLabel>유형 <span class="text-red-500">*</span></FormLabel>
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="유형을 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="정직원">정직원</SelectItem>
                  <SelectItem value="프리랜서">프리랜서</SelectItem>
                  <SelectItem value="외주">외주</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 상태 -->
          <FormField v-slot="{ componentField }" name="status">
            <FormItem>
              <FormLabel>상태</FormLabel>
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="상태를 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="재직">재직</SelectItem>
                  <SelectItem value="휴직">휴직</SelectItem>
                  <SelectItem value="퇴사">퇴사</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- 날짜 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">날짜 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 생년월일 -->
          <FormField v-slot="{ componentField }" name="birthDate">
            <FormItem>
              <FormLabel>생년월일 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <DatePicker
                  v-bind="componentField"
                  placeholder="생년월일을 선택하세요"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 입사일 -->
          <FormField v-slot="{ componentField }" name="joinDate">
            <FormItem>
              <FormLabel>입사일 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <DatePicker
                  v-bind="componentField"
                  placeholder="입사일을 선택하세요"
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
          구성원 생성
        </Button>
      </div>

      <!-- 조직도 선택 다이얼로그 -->
      <OrganizationSelectDialog
        v-model:open="orgDialogOpen"
        :withMembers="false"
        @select="handleOrgSelected"
      />
    </form>
  </Form>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { DatePicker } from '@/components/ui/date-picker';
import { Loader2 } from 'lucide-vue-next';
import EmployeeCreate from '@/features/employee/entity/EmployeeCreate';
import OrganizationSelectDialog from '@/features/organization/components/OrganizationSelectDialog.vue';
import { useDepartments } from '@/core/composables';
import { Textarea } from '@/components/ui/textarea';

interface EmployeeFormProps {
  loading?: boolean;
}

interface EmployeeFormEmits {
  submit: [employee: EmployeeCreate];
  cancel: [];
}

const props = withDefaults(defineProps<EmployeeFormProps>(), {
  loading: false,
});

const emit = defineEmits<EmployeeFormEmits>();

// 조직도 다이얼로그 상태
const orgDialogOpen = ref(false);
const currentFieldRef = ref<any>(null);

// 부서 정보
const { departmentOptions, fetchDepartments, loading: departmentsLoading, error: departmentsError } = useDepartments();

// Zod 스키마
const formSchema = toTypedSchema(z.object({
  name: z.string().min(1, '이름은 필수입니다.'),
  email: z.string().email('올바른 이메일 형식이 아닙니다.').min(1, '이메일은 필수입니다.'),
  phone: z.string().min(1, '전화번호는 필수입니다.'),
  departmentId: z.number({ required_error: '담당 부서를 선택해주세요.' }).min(1, '담당 부서를 선택해주세요.'),
  rank: z.string().min(1, '직급을 선택해주세요.'),
  grade: z.string().min(1, '등급을 선택해주세요.'),
  type: z.string().min(1, '유형을 선택해주세요.'),
  birthDate: z.date({ required_error: '생년월일은 필수입니다.' }),
  joinDate: z.date({ required_error: '입사일은 필수입니다.' }),
  // 선택적 필드들
  status: z.string().optional(),
  comment: z.string().optional(),
}));

// 유효성 검증 스키마
const validationSchema = formSchema;

// 초기값
const initialValues = {
  name: '',
  email: '',
  phone: '',
  departmentId: undefined,
  rank: '',
  grade: '',
  type: '',
  birthDate: undefined,
  joinDate: undefined,
  status: '재직',
  comment: '',
};

// 조직도에서 부서 선택
const openOrgDialog = (field: any) => {
  currentFieldRef.value = field;
  orgDialogOpen.value = true;
};

const handleOrgSelected = (node: { departmentId?: number }) => {
  if (node?.departmentId && currentFieldRef.value) {
    currentFieldRef.value.onChange(node.departmentId);
    currentFieldRef.value = null;
    orgDialogOpen.value = false;
  }
};

// 날짜를 API 형식 문자열로 변환
const formatDateForAPI = (date: Date | null): string => {
  if (!date) return '';
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// 폼 제출
const onSubmit = (values: any) => {
  console.log('구성원 폼 제출 시작:', values);

  // 날짜 필드를 문자열로 변환
  const employeeData = {
    ...values,
    birthDate: formatDateForAPI(values.birthDate),
    joinDate: formatDateForAPI(values.joinDate),
  };

  console.log('변환된 구성원 데이터:', employeeData);

  const employee = new EmployeeCreate(employeeData);
  console.log('생성된 구성원 객체:', employee);

  emit('submit', employee);
};

// 폼 취소
const onCancel = () => {
  emit('cancel');
};

// 컴포넌트 마운트 시 부서 데이터 로드
onMounted(async () => {
  try {
    await fetchDepartments();
    console.log('부서 데이터 로드 완료:', departmentOptions.value);
  } catch (error) {
    console.error('부서 데이터 로드 실패:', error);
  }
});
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>