<template>
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button
        variant="outline"
        size="sm"
        class="h-8 md:hidden"
      >
        <MoreVertical class="h-4 w-4" />
        <span class="sr-only">액션 메뉴</span>
      </Button>
    </DropdownMenuTrigger>
    
    <DropdownMenuContent align="end" class="w-48">
      <DropdownMenuLabel>액션</DropdownMenuLabel>
      <DropdownMenuSeparator />
      
      <!-- 엑셀 다운로드 서브메뉴 -->
      <DropdownMenuSub>
        <DropdownMenuSubTrigger>
          <Download class="mr-2 h-4 w-4" />
          엑셀 다운로드
        </DropdownMenuSubTrigger>
        <DropdownMenuSubContent>
          <DropdownMenuItem @click="$emit('download-current')">
            <FileSpreadsheet class="mr-2 h-4 w-4" />
            현재 데이터
          </DropdownMenuItem>
          <DropdownMenuItem @click="$emit('download-sample')">
            <FileText class="mr-2 h-4 w-4" />
            샘플 파일
          </DropdownMenuItem>
          <DropdownMenuItem @click="$emit('download-all')">
            <Database class="mr-2 h-4 w-4" />
            전체 데이터
          </DropdownMenuItem>
        </DropdownMenuSubContent>
      </DropdownMenuSub>
      
      <DropdownMenuSeparator />
      
      <!-- 엑셀 업로드 -->
      <DropdownMenuItem @click="$emit('upload-excel')">
        <Upload class="mr-2 h-4 w-4" />
        엑셀 업로드
      </DropdownMenuItem>
      
      <!-- 급여 업로드 (Employee용, 선택적) -->
      <DropdownMenuItem 
        v-if="showSalaryUpload"
        @click="$emit('upload-salary')"
      >
        <TrendingUp class="mr-2 h-4 w-4" />
        급여 업로드
      </DropdownMenuItem>
      
      <DropdownMenuSeparator />
      
      <!-- 추가 버튼 -->
      <DropdownMenuItem @click="$emit('add-item')">
        <Plus class="mr-2 h-4 w-4" />
        {{ addButtonText }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup lang="ts">
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { 
  MoreVertical,
  Download,
  Upload,
  Plus,
  FileSpreadsheet,
  FileText,
  Database,
  TrendingUp
} from 'lucide-vue-next';

interface Props {
  addButtonText: string;
  showSalaryUpload?: boolean;
}

interface Emits {
  (e: 'download-current'): void;
  (e: 'download-sample'): void;
  (e: 'download-all'): void;
  (e: 'upload-excel'): void;
  (e: 'upload-salary'): void;
  (e: 'add-item'): void;
}

const props = withDefaults(defineProps<Props>(), {
  showSalaryUpload: false,
});

const emit = defineEmits<Emits>();
</script>