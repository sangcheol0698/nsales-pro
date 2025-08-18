<template>
  <Dialog v-model:open="dialogOpen">
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>프로젝트 정보 수정</DialogTitle>
        <DialogDescription>
          프로젝트 정보를 수정합니다.
        </DialogDescription>
      </DialogHeader>

      <div v-if="loading" class="flex items-center justify-center py-8">
        <Loader2 class="h-8 w-8 animate-spin" />
        <span class="ml-2">프로젝트 정보를 불러오는 중...</span>
      </div>

      <div v-else-if="error" class="flex items-center justify-center py-8 text-red-500">
        <AlertCircle class="h-5 w-5 mr-2" />
        <span>프로젝트 정보를 불러오는데 실패했습니다.</span>
      </div>
      
      <ProjectEditForm
        v-else
        :loading="submitting"
        :project="project"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Loader2, AlertCircle } from 'lucide-vue-next';
import ProjectEditForm from './ProjectEditForm.vue';
import ProjectUpdate from '@/features/project/entity/ProjectUpdate';
import ProjectDetail from '@/features/project/entity/ProjectDetail';
import ProjectRepository from '@/features/project/repository/ProjectRepository';
import { container } from 'tsyringe';
import { toast } from 'vue-sonner';

interface ProjectEditDialogProps {
  open: boolean;
  projectId?: number | null;
}

interface ProjectEditDialogEmits {
  'update:open': [value: boolean];
  submit: [project: ProjectUpdate];
}

const props = withDefaults(defineProps<ProjectEditDialogProps>(), {
  open: false,
  projectId: null,
});

const emit = defineEmits<ProjectEditDialogEmits>();

// Repository
const projectRepository = container.resolve(ProjectRepository);

// 상태 관리
const dialogOpen = ref(props.open);
const loading = ref(false);
const submitting = ref(false);
const error = ref(false);
const project = ref<ProjectDetail | null>(null);

const handleSubmit = (projectData: ProjectUpdate) => {
  console.log('ProjectEditDialog - 수정 요청:', projectData);
  emit('submit', projectData);
};

const handleCancel = () => {
  console.log('ProjectEditDialog - 취소');
  emit('update:open', false);
};

// Dialog 열림/닫힘 상태 동기화
watch(() => props.open, (newValue) => {
  dialogOpen.value = newValue;
  if (newValue && props.projectId) {
    loadProject();
  }
});

watch(dialogOpen, (newValue) => {
  emit('update:open', newValue);
  if (!newValue) {
    // 다이얼로그가 닫힐 때 상태 초기화
    project.value = null;
    error.value = false;
  }
});

// 프로젝트 정보 로드
const loadProject = async () => {
  if (!props.projectId) {
    console.error('Project ID is required');
    return;
  }

  loading.value = true;
  error.value = false;

  try {
    console.log('프로젝트 정보 로딩 시작:', props.projectId);
    const rawResponse = await projectRepository.getProject(props.projectId);
    console.log('프로젝트 상세 데이터 로드 완료:', rawResponse);
    
    project.value = rawResponse;
  } catch (err: any) {
    console.error('프로젝트 정보 로드 실패:', err);
    error.value = true;
    toast.error('프로젝트 정보 로드 실패', {
      description: '프로젝트 정보를 불러오는 중 오류가 발생했습니다.',
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>