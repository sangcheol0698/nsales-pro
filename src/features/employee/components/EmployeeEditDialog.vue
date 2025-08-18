<template>
  <Dialog v-model:open="dialogOpen">
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>구성원 수정</DialogTitle>
        <DialogDescription>
          구성원 정보를 수정합니다.
        </DialogDescription>
      </DialogHeader>

      <div v-if="loading" class="flex items-center justify-center py-8">
        <Loader2 class="h-8 w-8 animate-spin" />
        <span class="ml-2">구성원 정보를 불러오는 중...</span>
      </div>

      <div v-else-if="error" class="flex items-center justify-center py-8 text-red-500">
        <AlertCircle class="h-5 w-5 mr-2" />
        <span>구성원 정보를 불러오는데 실패했습니다.</span>
      </div>

      <EmployeeEditForm
        v-else
        :loading="submitting"
        :employee="employee"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Loader2, AlertCircle } from 'lucide-vue-next';
import EmployeeEditForm from './EmployeeEditForm.vue';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch';
import EmployeeUpdate from '@/features/employee/entity/EmployeeUpdate';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository';
import { container } from 'tsyringe';
import { toast } from 'vue-sonner';

interface EmployeeEditDialogProps {
  open: boolean;
  employeeId?: number | null;
}

interface EmployeeEditDialogEmits {
  'update:open': [value: boolean];
  success: [];
}

const props = withDefaults(defineProps<EmployeeEditDialogProps>(), {
  open: false,
  employeeId: null,
});

const emit = defineEmits<EmployeeEditDialogEmits>();

// Repository
const employeeRepository = container.resolve(EmployeeRepository);

// 상태 관리
const dialogOpen = ref(props.open);
const loading = ref(false);
const submitting = ref(false);
const error = ref(false);
const employee = ref<EmployeeSearch | null>(null);

// Dialog 열림/닫힘 상태 동기화
watch(() => props.open, (newValue) => {
  dialogOpen.value = newValue;
  if (newValue && props.employeeId) {
    loadEmployee();
  }
});

watch(dialogOpen, (newValue) => {
  emit('update:open', newValue);
  if (!newValue) {
    // 다이얼로그가 닫힐 때 상태 초기화
    employee.value = null;
    error.value = false;
  }
});

// 구성원 정보 로드
const loadEmployee = async () => {
  if (!props.employeeId) {
    console.error('Employee ID is required');
    return;
  }

  loading.value = true;
  error.value = false;

  try {
    console.log('구성원 정보 로딩 시작:', props.employeeId);
    const rawResponse = await employeeRepository.getEmployee(props.employeeId);
    console.log('구성원 API 응답 (Raw):', rawResponse);
    employee.value = rawResponse;
    console.log('구성원 정보 로드 완료 - phone:', employee.value.phone, 'birthDate:', employee.value.birthDate, 'departmentId:', employee.value.departmentId);
  } catch (err) {
    console.error('구성원 정보 로드 실패:', err);
    error.value = true;
    toast.error('구성원 정보를 불러오는데 실패했습니다.');
  } finally {
    loading.value = false;
  }
};

// 폼 제출 처리
const handleSubmit = async (employeeUpdate: EmployeeUpdate) => {
  submitting.value = true;

  try {
    console.log('구성원 수정 시작:', employeeUpdate);
    await employeeRepository.updateEmployee(employeeUpdate);
    console.log('구성원 수정 완료');
    
    toast.success('구성원 정보가 성공적으로 수정되었습니다.');
    emit('success');
    dialogOpen.value = false;
  } catch (err) {
    console.error('구성원 수정 실패:', err);
    toast.error('구성원 수정에 실패했습니다.');
  } finally {
    submitting.value = false;
  }
};

// 폼 취소 처리
const handleCancel = () => {
  dialogOpen.value = false;
};
</script>