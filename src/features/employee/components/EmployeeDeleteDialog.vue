<template>
  <AlertDialog v-model:open="dialogOpen">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>구성원 삭제</AlertDialogTitle>
        <AlertDialogDescription>
          정말로 <strong>{{ employeeName }}</strong> 구성원을 삭제하시겠습니까?
          <br />
          이 작업은 되돌릴 수 없습니다.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>취소</AlertDialogCancel>
        <AlertDialogAction
          @click="handleDelete"
          :disabled="loading"
          class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
        >
          <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
          삭제
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Loader2 } from 'lucide-vue-next';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository';
import { container } from 'tsyringe';
import { toast } from 'vue-sonner';

interface EmployeeDeleteDialogProps {
  open: boolean;
  employeeId?: number | null;
  employeeName?: string;
}

interface EmployeeDeleteDialogEmits {
  'update:open': [value: boolean];
  success: [];
}

const props = withDefaults(defineProps<EmployeeDeleteDialogProps>(), {
  open: false,
  employeeId: null,
  employeeName: '',
});

const emit = defineEmits<EmployeeDeleteDialogEmits>();

// Repository
const employeeRepository = container.resolve(EmployeeRepository);

// 상태 관리
const dialogOpen = ref(props.open);
const loading = ref(false);

// Dialog 열림/닫힘 상태 동기화
watch(() => props.open, (newValue) => {
  dialogOpen.value = newValue;
});

watch(dialogOpen, (newValue) => {
  emit('update:open', newValue);
});

// 삭제 처리
const handleDelete = async () => {
  if (!props.employeeId) {
    console.error('Employee ID is required for deletion');
    return;
  }

  loading.value = true;

  try {
    console.log('구성원 삭제 시작:', props.employeeId);
    await employeeRepository.deleteEmployee(props.employeeId);
    console.log('구성원 삭제 완료');
    
    toast.success(`${props.employeeName} 구성원이 성공적으로 삭제되었습니다.`);
    emit('success');
    dialogOpen.value = false;
  } catch (err) {
    console.error('구성원 삭제 실패:', err);
    toast.error('구성원 삭제에 실패했습니다.');
  } finally {
    loading.value = false;
  }
};
</script>