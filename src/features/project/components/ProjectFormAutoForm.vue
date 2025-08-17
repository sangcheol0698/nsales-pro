<template>
  <div class="space-y-6">
    <AutoForm
      :schema="projectSchema"
      :field-config="fieldConfig"
      @submit="handleSubmit"
    >
      <template #customAutoForm="{ fields }">
        <!-- 기본 정보 섹션 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-foreground">기본 정보</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- 프로젝트 코드 -->
            <AutoFormField
              :config="fieldConfig.code"
              field-name="code"
              :shape="fields.code.shape"
            />

            <!-- 프로젝트명 -->
            <AutoFormField
              :config="fieldConfig.name"
              field-name="name"
              :shape="fields.name.shape"
            />

            <!-- 프로젝트 유형 -->
            <AutoFormField
              :config="fieldConfig.type"
              field-name="type"
              :shape="fields.type.shape"
            />

            <!-- 담당 부서 -->
            <div class="space-y-2">
              <AutoFormField
                :config="fieldConfig.departmentId"
                field-name="departmentId"
                :shape="fields.departmentId.shape"
              />
              <Button 
                type="button" 
                variant="outline" 
                size="sm" 
                @click="openOrgDialog"
                class="w-full mt-2"
              >
                조직도에서 선택
              </Button>
            </div>
          </div>
        </div>

        <!-- 일정 및 금액 정보 섹션 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-foreground">일정 및 금액 정보</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- 계약일 -->
            <AutoFormField
              :config="fieldConfig.contractDate"
              field-name="contractDate"
              :shape="fields.contractDate.shape"
            />

            <!-- 시작일 -->
            <AutoFormField
              :config="fieldConfig.startDate"
              field-name="startDate"
              :shape="fields.startDate.shape"
            />

            <!-- 종료일 -->
            <AutoFormField
              :config="fieldConfig.endDate"
              field-name="endDate"
              :shape="fields.endDate.shape"
            />

            <!-- 예상 금액 -->
            <AutoFormField
              :config="fieldConfig.expectedAmount"
              field-name="expectedAmount"
              :shape="fields.expectedAmount.shape"
            />

            <!-- 계약 금액 -->
            <AutoFormField
              :config="fieldConfig.contractAmount"
              field-name="contractAmount"
              :shape="fields.contractAmount.shape"
            />
          </div>
        </div>

        <!-- PM 정보 섹션 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-foreground">PM 정보</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- PM 이름 -->
            <AutoFormField
              :config="fieldConfig.pmName"
              field-name="pmName"
              :shape="fields.pmName.shape"
            />

            <!-- PM 연락처 -->
            <AutoFormField
              :config="fieldConfig.pmPhone"
              field-name="pmPhone"
              :shape="fields.pmPhone.shape"
            />
          </div>
        </div>

        <!-- 주관사 정보 섹션 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-foreground">주관사 정보</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- 주관사명 -->
            <AutoFormField
              :config="fieldConfig.mainCompany"
              field-name="mainCompany"
              :shape="fields.mainCompany.shape"
            />

            <!-- 주관사 담당자 -->
            <AutoFormField
              :config="fieldConfig.mainCompanyRep"
              field-name="mainCompanyRep"
              :shape="fields.mainCompanyRep.shape"
            />

            <!-- 주관사 담당자 연락처 -->
            <AutoFormField
              :config="fieldConfig.mainCompanyRepPhone"
              field-name="mainCompanyRepPhone"
              :shape="fields.mainCompanyRepPhone.shape"
            />
          </div>
        </div>

        <!-- 고객사 정보 섹션 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-foreground">고객사 정보</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- 고객사명 -->
            <AutoFormField
              :config="fieldConfig.clientCompany"
              field-name="clientCompany"
              :shape="fields.clientCompany.shape"
            />

            <!-- 고객사 담당자 -->
            <AutoFormField
              :config="fieldConfig.clientCompanyRep"
              field-name="clientCompanyRep"
              :shape="fields.clientCompanyRep.shape"
            />

            <!-- 고객사 담당자 연락처 -->
            <AutoFormField
              :config="fieldConfig.clientCompanyRepPhone"
              field-name="clientCompanyRepPhone"
              :shape="fields.clientCompanyRepPhone.shape"
            />
          </div>
        </div>
      </template>

      <!-- 폼 액션 버튼 -->
      <div class="flex justify-end gap-2 pt-4 border-t">
        <Button type="button" variant="outline" @click="onCancel">
          취소
        </Button>
        <Button type="submit" :disabled="loading">
          <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
          프로젝트 생성
        </Button>
      </div>
    </AutoForm>

    <!-- 조직도 선택 다이얼로그 -->
    <OrganizationSelectDialog
      v-model:open="orgDialogOpen"
      :withMembers="false"
      @select="handleOrgSelected"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-vue-next';
import { AutoForm, AutoFormField, type Config } from '@/components/ui/auto-form';
import ProjectCreate from '@/features/project/entity/ProjectCreate';
import OrganizationSelectDialog from '@/features/organization/components/OrganizationSelectDialog.vue';
import { useDepartments } from '@/core/composables';

interface ProjectFormAutoFormProps {
  loading?: boolean;
}

interface ProjectFormAutoFormEmits {
  submit: [project: ProjectCreate];
  cancel: [];
}

const props = withDefaults(defineProps<ProjectFormAutoFormProps>(), {
  loading: false,
});

const emit = defineEmits<ProjectFormAutoFormEmits>();

// 조직도 다이얼로그 상태
const orgDialogOpen = ref(false);

// 부서 정보
const { departmentOptions, fetchDepartments } = useDepartments();

// Zod 스키마 정의
const projectSchema = z.object({
  code: z.string().min(1, '프로젝트 코드는 필수입니다.'),
  name: z.string().min(1, '프로젝트명은 필수입니다.'),
  type: z.enum(['SI', 'SM'], { required_error: '프로젝트 유형을 선택해주세요.' }),
  contractDate: z.string().min(1, '계약일은 필수입니다.'),
  departmentId: z.string().min(1, '담당 부서를 선택해주세요.'), // string으로 변경하여 AutoForm에서 처리하기 쉽게
  mainCompany: z.string().min(1, '주관사명은 필수입니다.'),
  clientCompany: z.string().min(1, '고객사명은 필수입니다.'),
  // 선택적 필드들
  expectedAmount: z.number().optional(),
  contractAmount: z.number().optional(),
  pmName: z.string().optional(),
  pmPhone: z.string().optional(),
  startDate: z.string().optional(),
  endDate: z.string().optional(),
  mainCompanyRep: z.string().optional(),
  mainCompanyRepPhone: z.string().optional(),
  clientCompanyRep: z.string().optional(),
  clientCompanyRepPhone: z.string().optional(),
});

// AutoForm 필드 설정
const fieldConfig: Config<z.infer<typeof projectSchema>> = {
  code: {
    label: '프로젝트 코드',
    description: '예: PRJ-2024-001',
    inputProps: {
      placeholder: '예: PRJ-2024-001',
    },
  },
  name: {
    label: '프로젝트명',
    inputProps: {
      placeholder: '프로젝트명을 입력하세요',
    },
  },
  type: {
    label: '프로젝트 유형',
    inputProps: {
      placeholder: '유형을 선택하세요',
    },
  },
  contractDate: {
    label: '계약일',
    fieldType: 'date',
  },
  departmentId: {
    label: '담당 부서',
    fieldType: 'select',
    inputProps: {
      placeholder: '부서를 선택하세요',
    },
  },
  mainCompany: {
    label: '주관사명',
    inputProps: {
      placeholder: '주관사명을 입력하세요',
    },
  },
  clientCompany: {
    label: '고객사명',
    inputProps: {
      placeholder: '고객사명을 입력하세요',
    },
  },
  expectedAmount: {
    label: '예상 금액 (원)',
    fieldType: 'number',
    inputProps: {
      placeholder: '0',
    },
  },
  contractAmount: {
    label: '계약 금액 (원)',
    fieldType: 'number',
    inputProps: {
      placeholder: '0',
    },
  },
  pmName: {
    label: 'PM 이름',
    inputProps: {
      placeholder: 'PM 이름을 입력하세요',
    },
  },
  pmPhone: {
    label: 'PM 연락처',
    inputProps: {
      placeholder: '010-0000-0000',
    },
  },
  startDate: {
    label: '시작일',
    fieldType: 'date',
  },
  endDate: {
    label: '종료일',
    fieldType: 'date',
  },
  mainCompanyRep: {
    label: '주관사 담당자',
    inputProps: {
      placeholder: '담당자명을 입력하세요',
    },
  },
  mainCompanyRepPhone: {
    label: '주관사 담당자 연락처',
    inputProps: {
      placeholder: '010-0000-0000',
    },
  },
  clientCompanyRep: {
    label: '고객사 담당자',
    inputProps: {
      placeholder: '담당자명을 입력하세요',
    },
  },
  clientCompanyRepPhone: {
    label: '고객사 담당자 연락처',
    inputProps: {
      placeholder: '010-0000-0000',
    },
  },
};

// 조직도에서 부서 선택
const openOrgDialog = () => {
  orgDialogOpen.value = true;
};

const handleOrgSelected = (node: { departmentId?: number }) => {
  if (node?.departmentId) {
    // AutoForm에서 값 설정하는 방법은 form context를 통해야 합니다
    // 현재는 조직도 선택 기능을 비활성화하고 드롭다운만 사용
    console.log('Department selected:', node.departmentId);
  }
};

// 폼 제출
const handleSubmit = (value: z.infer<typeof projectSchema>) => {
  // departmentId를 숫자로 변환
  const projectData = {
    ...value,
    departmentId: Number(value.departmentId),
  };
  
  const project = new ProjectCreate(projectData);
  emit('submit', project);
};

// 폼 취소
const onCancel = () => {
  emit('cancel');
};

// 컴포넌트 마운트 시 부서 데이터 로드
onMounted(() => {
  fetchDepartments();
});
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>