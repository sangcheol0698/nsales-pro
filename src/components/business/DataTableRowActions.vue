<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        variant="ghost"
        size="sm"
        class="h-8 w-8 p-0 data-[state=open]:bg-muted"
      >
        <MoreHorizontal class="h-4 w-4" />
        <span class="sr-only">메뉴 열기</span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-[160px]">
      <DropdownMenuItem @click="copyToClipboard">
        <Copy class="mr-2 h-4 w-4" />
        ID 복사
      </DropdownMenuItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem @click="$emit('edit', row)">
        <Edit class="mr-2 h-4 w-4" />
        편집
      </DropdownMenuItem>
      <DropdownMenuItem @click="$emit('view', row)">
        <Eye class="mr-2 h-4 w-4" />
        상세보기
      </DropdownMenuItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem 
        @click="$emit('duplicate', row)"
        class="text-muted-foreground"
      >
        <Copy class="mr-2 h-4 w-4" />
        복제
      </DropdownMenuItem>
      <DropdownMenuItem 
        @click="$emit('delete', row)"
        class="text-destructive"
      >
        <Trash class="mr-2 h-4 w-4" />
        삭제
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup lang="ts">
import { Copy, Edit, Eye, MoreHorizontal, Trash } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/core/composables';

interface DataTableRowActionsProps {
  row: any;
}

const props = defineProps<DataTableRowActionsProps>();

const emit = defineEmits<{
  edit: [row: any];
  view: [row: any];
  duplicate: [row: any];
  delete: [row: any];
}>();

const toast = useToast();

function copyToClipboard() {
  const id = props.row.id || props.row.code || 'N/A';
  navigator.clipboard.writeText(id).then(() => {
    toast.success('복사 완료', {
      description: `ID ${id}가 클립보드에 복사되었습니다.`,
      position: 'bottom-right',
    });
  });
}
</script>