<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>프로젝트 정보 수정</DialogTitle>
        <DialogDescription>
          프로젝트 정보를 수정합니다.
        </DialogDescription>
      </DialogHeader>
      
      <ProjectEditForm
        :loading="loading"
        :project="project"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import ProjectEditForm from './ProjectEditForm.vue';
import ProjectUpdate from '@/features/project/entity/ProjectUpdate';
import ProjectSearch from '@/features/project/entity/ProjectSearch';

interface ProjectEditDialogProps {
  open: boolean;
  loading?: boolean;
  project?: ProjectSearch | null;
}

interface ProjectEditDialogEmits {
  'update:open': [value: boolean];
  submit: [project: ProjectUpdate];
}

const props = withDefaults(defineProps<ProjectEditDialogProps>(), {
  loading: false,
  project: null,
});

const emit = defineEmits<ProjectEditDialogEmits>();

const handleSubmit = (project: ProjectUpdate) => {
  console.log('ProjectEditDialog - 수정 요청:', project);
  emit('submit', project);
};

const handleCancel = () => {
  console.log('ProjectEditDialog - 취소');
  emit('update:open', false);
};
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>