<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-5xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>구성원 추가</DialogTitle>
        <DialogDescription>
          새로운 구성원을 추가합니다. 필수 정보를 입력해주세요.
        </DialogDescription>
      </DialogHeader>

      <EmployeeForm
        :loading="loading"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { container } from 'tsyringe';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import EmployeeForm from './EmployeeForm.vue';
import EmployeeCreate from '@/features/employee/entity/EmployeeCreate';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository';
import { useToast } from '@/core/composables';

interface EmployeeAddDialogProps {
  open: boolean;
}

interface EmployeeAddDialogEmits {
  'update:open': [open: boolean];
  success: [];
}

defineProps<EmployeeAddDialogProps>();
const emit = defineEmits<EmployeeAddDialogEmits>();

const toast = useToast();
const EMPLOYEE_REPOSITORY = container.resolve(EmployeeRepository);

const loading = ref(false);

const handleSubmit = async (employee: EmployeeCreate) => {
  try {
    loading.value = true;
    console.log('구성원 생성 요청:', employee);
    
    await EMPLOYEE_REPOSITORY.createEmployee(employee);
    
    toast.success('구성원 생성 완료', {
      description: `${employee.name}님이 성공적으로 추가되었습니다.`,
      position: 'bottom-right',
    });
    
    emit('success');
    emit('update:open', false);
  } catch (error) {
    console.error('구성원 생성 실패:', error);
    
    toast.error('구성원 생성 실패', {
      description: '구성원을 생성하는 중 오류가 발생했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  emit('update:open', false);
};
</script>