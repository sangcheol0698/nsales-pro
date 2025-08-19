<template>
  <Form
    v-slot="{ handleSubmit, errors, values }"
    :validation-schema="validationSchema"
    :initial-values="initialValues"
    :key="`project-edit-form-${props.project?.id || 'new'}`"
    ref="formRef"
  >
    <form @submit.prevent="handleSubmit(onSubmit)" class="space-y-6">
      <!-- 기본 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">기본 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 프로젝트 코드 -->
          <FormField v-slot="{ componentField }" name="code">
            <FormItem>
              <FormLabel>프로젝트 코드 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="예: PRJ-2024-001"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 프로젝트명 -->
          <FormField v-slot="{ componentField }" name="name">
            <FormItem>
              <FormLabel>프로젝트명 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="프로젝트명을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 프로젝트 유형 -->
          <FormField v-slot="{ componentField }" name="type">
            <FormItem>
              <FormLabel>프로젝트 유형 <span class="text-red-500">*</span></FormLabel>
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="유형을 선택하세요" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="SI">SI (System Integration)</SelectItem>
                  <SelectItem value="SM">SM (System Maintenance)</SelectItem>
                </SelectContent>
              </Select>
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

      <!-- 일정 및 금액 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">일정 및 금액 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 계약일 -->
          <FormField v-slot="{ componentField }" name="contractDate">
            <FormItem>
              <FormLabel>계약일 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <DatePicker
                  v-bind="componentField"
                  placeholder="계약일을 선택하세요"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 시작일 -->
          <FormField v-slot="{ componentField }" name="startDate">
            <FormItem>
              <FormLabel>시작일</FormLabel>
              <FormControl>
                <DatePicker
                  v-bind="componentField"
                  placeholder="시작일을 선택하세요"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 종료일 -->
          <FormField v-slot="{ componentField }" name="endDate">
            <FormItem>
              <FormLabel>종료일</FormLabel>
              <FormControl>
                <DatePicker
                  v-bind="componentField"
                  placeholder="종료일을 선택하세요"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 예상 금액 -->
          <FormField v-slot="{ componentField }" name="expectedAmount">
            <FormItem>
              <FormLabel>예상 금액</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  placeholder="0"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 계약 금액 -->
          <FormField v-slot="{ componentField }" name="contractAmount">
            <FormItem>
              <FormLabel>계약 금액</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  placeholder="0"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- PM 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">PM 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- PM 이름 -->
          <FormField v-slot="{ componentField }" name="pmName">
            <FormItem>
              <FormLabel>PM 이름</FormLabel>
              <FormControl>
                <Input
                  placeholder="PM 이름을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- PM 연락처 -->
          <FormField v-slot="{ componentField }" name="pmPhone">
            <FormItem>
              <FormLabel>PM 연락처</FormLabel>
              <FormControl>
                <Input
                  placeholder="010-0000-0000"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- 주관사 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">주관사 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 주관사명 -->
          <FormField v-slot="{ componentField }" name="mainCompany">
            <FormItem>
              <FormLabel>주관사명 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="주관사명을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 주관사 담당자 -->
          <FormField v-slot="{ componentField }" name="mainCompanyRep">
            <FormItem>
              <FormLabel>주관사 담당자</FormLabel>
              <FormControl>
                <Input
                  placeholder="담당자명을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 주관사 담당자 연락처 -->
          <FormField v-slot="{ componentField }" name="mainCompanyRepPhone">
            <FormItem>
              <FormLabel>주관사 담당자 연락처</FormLabel>
              <FormControl>
                <Input
                  placeholder="010-0000-0000"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </div>
      </div>

      <!-- 고객사 정보 섹션 -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-foreground">고객사 정보</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 고객사명 -->
          <FormField v-slot="{ componentField }" name="clientCompany">
            <FormItem>
              <FormLabel>고객사명 <span class="text-red-500">*</span></FormLabel>
              <FormControl>
                <Input
                  placeholder="고객사명을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 고객사 담당자 -->
          <FormField v-slot="{ componentField }" name="clientCompanyRep">
            <FormItem>
              <FormLabel>고객사 담당자</FormLabel>
              <FormControl>
                <Input
                  placeholder="담당자명을 입력하세요"
                  v-bind="componentField"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <!-- 고객사 담당자 연락처 -->
          <FormField v-slot="{ componentField }" name="clientCompanyRepPhone">
            <FormItem>
              <FormLabel>고객사 담당자 연락처</FormLabel>
              <FormControl>
                <Input
                  placeholder="010-0000-0000"
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
          프로젝트 수정
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
import ProjectUpdate from '@/features/project/entity/ProjectUpdate';
import ProjectDetail from '@/features/project/entity/ProjectDetail';
import OrganizationSelectDialog from '@/features/organization/components/OrganizationSelectDialog.vue';
import { useDepartments } from '@/core/composables';

interface ProjectEditFormProps {
  loading?: boolean;
  project?: ProjectDetail | null;
}

interface ProjectEditFormEmits {
  submit: [project: ProjectUpdate];
  cancel: [];
}

const props = withDefaults(defineProps<ProjectEditFormProps>(), {
  loading: false,
  project: null,
});

const emit = defineEmits<ProjectEditFormEmits>();

// 조직도 다이얼로그 상태
const orgDialogOpen = ref(false);
const currentFieldRef = ref<any>(null);
const formRef = ref<any>(null);

// 부서 정보
const { departmentOptions, fetchDepartments, loading: departmentsLoading, error: departmentsError } = useDepartments();

// Zod 스키마
const formSchema = toTypedSchema(z.object({
  code: z.string().min(1, '프로젝트 코드는 필수입니다.'),
  name: z.string().min(1, '프로젝트명은 필수입니다.'),
  type: z.enum(['SI', 'SM'], { required_error: '프로젝트 유형을 선택해주세요.' }),
  contractDate: z.date({ required_error: '계약일은 필수입니다.' }),
  departmentId: z.number({ required_error: '담당 부서를 선택해주세요.' }).min(1, '담당 부서를 선택해주세요.'),
  mainCompany: z.string().min(1, '주관사명은 필수입니다.'),
  clientCompany: z.string().min(1, '고객사명은 필수입니다.'),
  // 선택적 필드들
  expectedAmount: z.number().optional(),
  contractAmount: z.number().optional(),
  pmName: z.string().optional(),
  pmPhone: z.string().optional(),
  startDate: z.date().optional(),
  endDate: z.date().optional(),
  mainCompanyRep: z.string().optional(),
  mainCompanyRepPhone: z.string().optional(),
  clientCompanyRep: z.string().optional(),
  clientCompanyRepPhone: z.string().optional(),
}));

// 유효성 검증 스키마
const validationSchema = formSchema;

// 초기값
const initialValues = ref({
  code: '',
  name: '',
  type: 'SI' as 'SI' | 'SM',
  contractDate: undefined,
  departmentId: undefined,
  mainCompany: '',
  clientCompany: '',
  expectedAmount: undefined,
  contractAmount: undefined,
  pmName: '',
  pmPhone: '',
  startDate: undefined,
  endDate: undefined,
  mainCompanyRep: '',
  mainCompanyRepPhone: '',
  clientCompanyRep: '',
  clientCompanyRepPhone: '',
});

// props.project 변경 감지하여 초기값 업데이트
watch(() => props.project, async (project) => {
  if (project) {
    console.log('ProjectEditForm 초기값 설정:', project);

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
      code: project.code || '',
      name: project.name || '',
      type: project.type || 'SI',
      contractDate: project.contractDate ? new Date(project.contractDate) : undefined,
      departmentId: project.department?.id, // ProjectDetail에서 department.id 사용
      mainCompany: project.mainCompany || '',
      clientCompany: project.clientCompany || '',
      expectedAmount: project.expectedAmount || undefined,
      contractAmount: project.contractAmount || undefined,
      pmName: project.pmName || '',
      pmPhone: project.pmPhone || '',
      startDate: project.startDate ? new Date(project.startDate) : undefined,
      endDate: project.endDate ? new Date(project.endDate) : undefined,
      mainCompanyRep: project.mainCompanyRep || '',
      mainCompanyRepPhone: project.mainCompanyRepPhone || '',
      clientCompanyRep: project.clientCompanyRep || '',
      clientCompanyRepPhone: project.clientCompanyRepPhone || '',
    };

    console.log('설정된 초기값:', initialValues.value);

    // 다음 틱에서 폼을 리셋하여 초기값이 올바르게 적용되도록 함
    await nextTick();
    if (formRef.value && formRef.value.resetForm) {
      formRef.value.resetForm({ values: initialValues.value });
      console.log('프로젝트 수정 폼 리셋 완료');
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
  console.log('프로젝트 수정 폼 제출 시작:', values);

  if (!props.project?.id) {
    console.error('Project ID is missing');
    return;
  }

  // 날짜 필드를 문자열로 변환
  const projectData = {
    id: props.project.id,
    code: values.code,
    name: values.name,
    type: values.type,
    contractDate: formatDateForAPI(values.contractDate),
    departmentId: values.departmentId,
    mainCompany: values.mainCompany,
    clientCompany: values.clientCompany,
    expectedAmount: values.expectedAmount || undefined,
    contractAmount: values.contractAmount || undefined,
    pmName: values.pmName || undefined,
    pmPhone: values.pmPhone || undefined,
    startDate: formatDateForAPI(values.startDate),
    endDate: formatDateForAPI(values.endDate),
    mainCompanyRep: values.mainCompanyRep || undefined,
    mainCompanyRepPhone: values.mainCompanyRepPhone || undefined,
    clientCompanyRep: values.clientCompanyRep || undefined,
    clientCompanyRepPhone: values.clientCompanyRepPhone || undefined,
    modifiedDateTime: props.project.modifiedDateTime, // 낙관적 동시성 제어용
  };

  console.log('변환된 프로젝트 수정 데이터:', projectData);
  console.log('낙관적 동시성 제어 - modifiedDateTime:', projectData.modifiedDateTime);

  const project = ProjectUpdate.fromFormData(projectData);
  console.log('생성된 프로젝트 수정 객체:', project);

  emit('submit', project);
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