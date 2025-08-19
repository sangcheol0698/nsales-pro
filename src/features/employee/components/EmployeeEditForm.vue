<template>
  <Form
    v-slot="{ handleSubmit, errors, values, resetForm }"
    :validation-schema="validationSchema"
    :initial-values="initialValues"
    :key="`employee-edit-form-${props.employee?.id || 'new'}`"
    ref="formRef"
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
                  @update:model-value="(value) => {
                    console.log('부서 선택 변경:', { value, type: typeof value, numericValue: Number(value) });
                    field.onChange(Number(value));
                  }"
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

          <!-- 퇴사일 (상태가 퇴사일 때만 표시) -->
          <FormField v-if="values.status === '퇴사'" v-slot="{ componentField }" name="leaveDate">
            <FormItem>
              <FormLabel>퇴사일</FormLabel>
              <FormControl>
                <DatePicker
                  v-bind="componentField"
                  placeholder="퇴사일을 선택하세요"
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
          구성원 수정
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
import { onMounted, ref, watch, nextTick } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { DatePicker } from '@/components/ui/date-picker';
import { Loader2 } from 'lucide-vue-next';
import EmployeeUpdate from '@/features/employee/entity/EmployeeUpdate';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch';
import OrganizationSelectDialog from '@/features/organization/components/OrganizationSelectDialog.vue';
import { useDepartments } from '@/core/composables';
import { Textarea } from '@/components/ui/textarea';

interface EmployeeEditFormProps {
  loading?: boolean;
  employee?: EmployeeSearch | null;
}

interface EmployeeEditFormEmits {
  submit: [employee: EmployeeUpdate];
  cancel: [];
}

const props = withDefaults(defineProps<EmployeeEditFormProps>(), {
  loading: false,
  employee: null,
});

const emit = defineEmits<EmployeeEditFormEmits>();

// 조직도 다이얼로그 상태
const orgDialogOpen = ref(false);
const currentFieldRef = ref<any>(null);
const formRef = ref<any>(null);

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
  leaveDate: z.date().optional(),
  comment: z.string().optional(),
}));

// 유효성 검증 스키마
const validationSchema = formSchema;

// 초기값
const initialValues = ref({
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
  leaveDate: undefined,
  comment: '',
});

// props.employee 변경 감지하여 초기값 업데이트
watch(() => props.employee, async (employee) => {
  if (employee) {
    console.log('EmployeeEditForm 초기값 설정:', {
      employeeData: employee,
      departmentId: employee.departmentId,
      departmentIdType: typeof employee.departmentId
    });

    // 부서 데이터가 아직 로드되지 않았다면 먼저 로드
    if (departmentOptions.value.length === 0) {
      try {
        await fetchDepartments();
        console.log('부서 데이터 미리 로드 완료:', departmentOptions.value);
      } catch (error) {
        console.error('부서 데이터 미리 로드 실패:', error);
      }
    }

    initialValues.value = {
      name: employee.name || '',
      email: employee.email || '',
      phone: employee.phone || '',
      departmentId: employee.departmentId || undefined,
      rank: employee.rank || '',
      grade: employee.grade || '',
      type: employee.type || '',
      birthDate: employee.birthDate ? new Date(employee.birthDate) : undefined,
      joinDate: employee.joinDate ? new Date(employee.joinDate) : undefined,
      status: employee.status || '재직',
      leaveDate: employee.leaveDate ? new Date(employee.leaveDate) : undefined,
      comment: '', // comment는 여전히 EmployeeSearch에 없으므로 빈 값
    };

    console.log('설정된 초기값:', initialValues.value);
    console.log('부서 옵션 확인:', departmentOptions.value);
    console.log('선택된 부서 ID로 찾은 부서:', departmentOptions.value.find(opt => opt.value === employee.departmentId));

    // 다음 틱에서 폼을 리셋하여 초기값이 올바르게 적용되도록 함
    await nextTick();
    if (formRef.value && formRef.value.resetForm) {
      formRef.value.resetForm({ values: initialValues.value });
      console.log('폼 리셋 완료');
    }
  }
}, { immediate: true });

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
  console.log('구성원 수정 폼 제출 시작:', values);

  if (!props.employee?.id) {
    console.error('Employee ID is missing');
    return;
  }

  // 날짜 필드를 문자열로 변환
  const employeeData = {
    id: props.employee.id,
    name: values.name,
    email: values.email,
    phone: values.phone,
    departmentId: values.departmentId,
    rank: values.rank,
    grade: values.grade,
    type: values.type,
    status: values.status,
    birthDate: formatDateForAPI(values.birthDate),
    joinDate: formatDateForAPI(values.joinDate),
    leaveDate: formatDateForAPI(values.leaveDate),
    comment: values.comment,
    modifiedDateTime: props.employee.modifiedDateTime, // 낙관적 동시성 제어용
  };

  console.log('변환된 구성원 데이터:', employeeData);
  console.log('전송할 departmentId:', employeeData.departmentId, 'type:', typeof employeeData.departmentId);
  console.log('낙관적 동시성 제어 - modifiedDateTime:', employeeData.modifiedDateTime);

  const employee = EmployeeUpdate.fromFormData(employeeData);
  console.log('생성된 구성원 수정 객체:', employee);

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
    console.log('현재 선택된 부서 ID:', initialValues.value.departmentId);
  } catch (error) {
    console.error('부서 데이터 로드 실패:', error);
  }
});
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>