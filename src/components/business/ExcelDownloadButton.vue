<template>
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button
        variant="outline"
        size="sm"
        :disabled="isLoading"
        class="h-8 gap-2"
      >
        <Download class="h-4 w-4" />
        <span class="hidden sm:inline">{{ isLoading ? '다운로드 중...' : '엑셀 다운로드' }}</span>
        <span class="sm:hidden">{{ isLoading ? '다운로드...' : '엑셀' }}</span>
        <ChevronDown class="h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    
    <DropdownMenuContent align="end" class="w-48">
      <DropdownMenuItem @click="downloadData" :disabled="isLoading">
        <FileSpreadsheet class="h-4 w-4 mr-2" />
        현재 데이터 다운로드
      </DropdownMenuItem>
      
      <DropdownMenuItem @click="downloadSample" :disabled="isLoading">
        <FileText class="h-4 w-4 mr-2" />
        샘플 파일 다운로드
      </DropdownMenuItem>
      
      <DropdownMenuSeparator />
      
      <DropdownMenuItem @click="downloadAll" :disabled="isLoading">
        <Database class="h-4 w-4 mr-2" />
        전체 데이터 다운로드
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { 
  Download, 
  ChevronDown, 
  FileSpreadsheet, 
  FileText, 
  Database 
} from 'lucide-vue-next';

interface Props {
  onDownloadData: () => Promise<void>;
  onDownloadSample: () => Promise<void>;
  onDownloadAll?: () => Promise<void>;
}

interface Emits {
  (e: 'download-start'): void;
  (e: 'download-complete'): void;
  (e: 'download-error', error: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const isLoading = ref(false);

async function downloadData() {
  await executeDownload('data', props.onDownloadData);
}

async function downloadSample() {
  await executeDownload('sample', props.onDownloadSample);
}

async function downloadAll() {
  if (props.onDownloadAll) {
    await executeDownload('all', props.onDownloadAll);
  }
}

async function executeDownload(type: string, downloadFn: () => Promise<void>) {
  isLoading.value = true;
  emit('download-start');

  try {
    await downloadFn();
    emit('download-complete');
  } catch (error) {
    const message = error instanceof Error ? error.message : `${type} 다운로드 중 오류가 발생했습니다.`;
    emit('download-error', message);
  } finally {
    isLoading.value = false;
  }
}
</script>