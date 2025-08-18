<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>협력사 추가</DialogTitle>
        <DialogDescription>
          새로운 협력사를 추가합니다. 필수 정보를 입력해주세요.
        </DialogDescription>
      </DialogHeader>

      <PartnerForm
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
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import PartnerForm from './PartnerForm.vue';
import PartnerCreate from '@/features/partner/entity/PartnerCreate';
import PartnerRepository from '@/features/partner/repository/PartnerRepository';
import { useToast } from '@/core/composables';
import type HttpError from '@/core/http/HttpError.ts';

interface PartnerAddDialogProps {
  open: boolean;
}

interface PartnerAddDialogEmits {
  'update:open': [open: boolean];
  success: [];
}

defineProps<PartnerAddDialogProps>();
const emit = defineEmits<PartnerAddDialogEmits>();

const toast = useToast();
const PARTNER_REPOSITORY = container.resolve(PartnerRepository);

const loading = ref(false);

const handleSubmit = async (partner: PartnerCreate) => {
  try {
    loading.value = true;
    console.log('협력사 생성 요청:', partner);

    await PARTNER_REPOSITORY.createPartner(partner);

    toast.success('협력사 생성 완료', {
      description: `${partner.name}이(가) 성공적으로 추가되었습니다.`,
      position: 'bottom-right',
    });

    emit('success');
    emit('update:open', false);
  } catch (error) {
    console.error('협력사 생성 실패:', error);

    toast.error('협력사 생성 실패', {
      description: (error as HttpError).getMessage?.() ?? '협력사를 생성하는 중 오류가 발생했습니다. 다시 시도해주세요.',
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