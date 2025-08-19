<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>협력사 정보 수정</DialogTitle>
        <DialogDescription>
          협력사 정보를 수정합니다.
        </DialogDescription>
      </DialogHeader>
      
      <PartnerEditForm
        :loading="loading"
        :partner="partner"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import PartnerEditForm from './PartnerEditForm.vue';
import PartnerUpdate from '@/features/partner/entity/PartnerUpdate';
import PartnerSearch from '@/features/partner/entity/PartnerSearch';

interface PartnerEditDialogProps {
  open: boolean;
  loading?: boolean;
  partner?: PartnerSearch | null;
}

interface PartnerEditDialogEmits {
  'update:open': [value: boolean];
  submit: [partner: PartnerUpdate];
}

const props = withDefaults(defineProps<PartnerEditDialogProps>(), {
  loading: false,
  partner: null,
});

const emit = defineEmits<PartnerEditDialogEmits>();

const handleSubmit = (partner: PartnerUpdate) => {
  console.log('PartnerEditDialog - 수정 요청:', partner);
  emit('submit', partner);
};

const handleCancel = () => {
  console.log('PartnerEditDialog - 취소');
  emit('update:open', false);
};
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>