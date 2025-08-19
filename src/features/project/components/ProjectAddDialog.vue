<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-4xl max-h-[90vh] overflow-auto">
      <DialogHeader>
        <DialogTitle>프로젝트 추가</DialogTitle>
        <DialogDescription>
          새로운 프로젝트를 추가합니다. * 표시된 항목은 필수 입력 사항입니다.
        </DialogDescription>
      </DialogHeader>

      <div class="mt-4">
        <ProjectForm
          :loading="loading"
          @submit="handleSubmit"
          @cancel="handleCancel"
        />
      </div>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import ProjectForm from './ProjectForm.vue';
import ProjectCreate from '@/features/project/entity/ProjectCreate';

interface ProjectAddDialogProps {
  open: boolean;
}

interface ProjectAddDialogEmits {
  'update:open': [value: boolean];
  'success': [project: ProjectCreate];
}

defineProps<ProjectAddDialogProps>();
const emit = defineEmits<ProjectAddDialogEmits>();

const loading = ref(false);

const handleSubmit = async (project: ProjectCreate) => {
  loading.value = true;
  try {
    emit('success', project);
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  emit('update:open', false);
};
</script>

<style scoped>
/* 다이얼로그 내 스크롤을 위한 스타일 */
:deep(.scroll-area) {
  max-height: calc(90vh - 120px);
}
</style>