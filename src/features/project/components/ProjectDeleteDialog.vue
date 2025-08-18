<template>
  <AlertDialog :open="open" @update:open="$emit('update:open', $event)">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>프로젝트 삭제 확인</AlertDialogTitle>
        <AlertDialogDescription class="space-y-2">
          <p>정말로 이 프로젝트를 삭제하시겠습니까?</p>
          <div v-if="project" class="bg-muted p-3 rounded-md">
            <p class="font-medium">{{ project.name }}</p>
            <p class="text-sm text-muted-foreground">
              코드: {{ project.code }} | 유형: {{ project.type }}
            </p>
            <p class="text-sm text-muted-foreground">
              주관사: {{ project.mainCompany }} | 고객사: {{ project.clientCompany }}
            </p>
          </div>
          <p class="text-red-600 font-medium">이 작업은 되돌릴 수 없습니다.</p>
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel @click="handleCancel">
          취소
        </AlertDialogCancel>
        <AlertDialogAction 
          @click="handleConfirm"
          :disabled="loading"
          class="bg-destructive hover:bg-destructive/90"
        >
          <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
          삭제
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>

<script setup lang="ts">
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
import ProjectSearch from '@/features/project/entity/ProjectSearch';

interface ProjectDeleteDialogProps {
  open: boolean;
  loading?: boolean;
  project?: ProjectSearch | null;
}

interface ProjectDeleteDialogEmits {
  'update:open': [value: boolean];
  confirm: [projectId: number];
}

const props = withDefaults(defineProps<ProjectDeleteDialogProps>(), {
  loading: false,
  project: null,
});

const emit = defineEmits<ProjectDeleteDialogEmits>();

const handleConfirm = () => {
  if (props.project?.id) {
    console.log('ProjectDeleteDialog - 삭제 확인:', props.project.id);
    emit('confirm', props.project.id);
  }
};

const handleCancel = () => {
  console.log('ProjectDeleteDialog - 삭제 취소');
  emit('update:open', false);
};
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>