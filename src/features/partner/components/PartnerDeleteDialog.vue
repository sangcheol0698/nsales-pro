<template>
  <AlertDialog :open="open" @update:open="$emit('update:open', $event)">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>협력사 삭제 확인</AlertDialogTitle>
        <AlertDialogDescription class="space-y-2">
          <p>정말로 이 협력사를 삭제하시겠습니까?</p>
          <div v-if="partner" class="bg-muted p-3 rounded-md">
            <p class="font-medium">{{ partner.name }}</p>
            <p class="text-sm text-muted-foreground">
              대표자: {{ partner.ceoName }} | 영업대표: {{ partner.salesRepName }}
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
import PartnerSearch from '@/features/partner/entity/PartnerSearch';

interface PartnerDeleteDialogProps {
  open: boolean;
  loading?: boolean;
  partner?: PartnerSearch | null;
}

interface PartnerDeleteDialogEmits {
  'update:open': [value: boolean];
  confirm: [partnerId: number];
}

const props = withDefaults(defineProps<PartnerDeleteDialogProps>(), {
  loading: false,
  partner: null,
});

const emit = defineEmits<PartnerDeleteDialogEmits>();

const handleConfirm = () => {
  if (props.partner?.id) {
    console.log('PartnerDeleteDialog - 삭제 확인:', props.partner.id);
    emit('confirm', props.partner.id);
  }
};

const handleCancel = () => {
  console.log('PartnerDeleteDialog - 삭제 취소');
  emit('update:open', false);
};
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>