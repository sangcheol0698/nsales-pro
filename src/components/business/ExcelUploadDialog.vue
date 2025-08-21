<template>
  <Dialog v-model:open="isOpen">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>엑셀 파일 업로드</DialogTitle>
        <DialogDescription>
          {{ description }}
        </DialogDescription>
      </DialogHeader>

      <div class="grid gap-4 py-4">
        <!-- 샘플 다운로드 섹션 -->
        <div class="border-2 border-dashed rounded-lg p-4">
          <div class="text-center">
            <FileSpreadsheet class="mx-auto h-8 w-8 text-gray-400 mb-2" />
            <h4 class="text-sm font-medium mb-1">샘플 파일 다운로드</h4>
            <p class="text-xs text-gray-500 mb-3">업로드 형식에 맞는 샘플 파일을 다운로드하세요</p>
            <Button variant="outline" size="sm" @click="downloadSample" :disabled="isDownloading">
              <Download class="h-4 w-4 mr-2" />
              {{ isDownloading ? '다운로드 중...' : '샘플 다운로드' }}
            </Button>
          </div>
        </div>

        <!-- 파일 업로드 섹션 -->
        <div
          ref="dropZoneRef"
          class="rounded-lg p-4 transition-colors"
          :class="[
            'border-2 border-dashed',
            isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-200',
          ]"
          @dragover.prevent="onDragOver"
          @dragleave.prevent="onDragLeave"
          @drop.prevent="onDrop"
        >
          <div class="text-center">
            <Upload class="mx-auto h-8 w-8 text-gray-400 mb-2" />
            <div class="space-y-2">
              <input
                ref="fileInput"
                type="file"
                accept=".xlsx,.xls"
                @change="handleFileSelect"
                class="hidden"
              />
              <Button
                variant="outline"
                @click="triggerFileSelect"
                :disabled="isUploading"
                class="w-full"
              >
                <Upload class="h-4 w-4 mr-2" />
                파일 선택
              </Button>

              <p class="text-xs text-gray-500">
                또는 이 영역에 파일을 끌어다 놓으세요 (.xlsx, .xls, 최대 10MB)
              </p>

              <!-- 선택된 파일 정보 -->
              <div v-if="selectedFile" class="text-sm text-gray-600">
                <div class="flex items-center justify-center gap-2">
                  <FileSpreadsheet class="h-4 w-4" />
                  <span>{{ selectedFile.name }}</span>
                  <Button variant="ghost" size="sm" @click="clearFile" class="h-6 w-6 p-0">
                    <X class="h-3 w-3" />
                  </Button>
                </div>
                <div class="text-xs text-gray-400">
                  {{ formatFileSize(selectedFile.size) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 업로드 진행률 -->
        <div v-if="isUploading" class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span>업로드 중...</span>
            <span>{{ Math.round(uploadProgress) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${uploadProgress}%` }"
            ></div>
          </div>
        </div>

        <!-- 에러 메시지 -->
        <div v-if="errorMessage" class="text-red-600 text-sm p-3 bg-red-50 rounded-lg">
          <div class="flex items-center gap-2">
            <AlertCircle class="h-4 w-4" />
            <span>{{ errorMessage }}</span>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="closeDialog" :disabled="isUploading"> 취소 </Button>
        <Button @click="uploadFile" :disabled="!selectedFile || isUploading">
          <Upload class="h-4 w-4 mr-2" />
          {{ isUploading ? '업로드 중...' : '업로드' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AlertCircle, Download, FileSpreadsheet, Upload, X } from 'lucide-vue-next';

interface Props {
  open: boolean;
  title?: string;
  description?: string;
  onUpload: (file: File, onProgress: (progress: number) => void) => Promise<void>;
  onDownloadSample: () => Promise<void>;
}

interface Emits {
  (e: 'update:open', value: boolean): void;

  (e: 'success'): void;

  (e: 'error', error: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  title: '엑셀 파일 업로드',
  description: '업로드할 엑셀 파일을 선택하세요.',
});

const emit = defineEmits<Emits>();

// Reactive state
const fileInput = ref<HTMLInputElement>();
const selectedFile = ref<File | null>(null);
const isUploading = ref(false);
const isDownloading = ref(false);
const uploadProgress = ref(0);
const errorMessage = ref('');

// Drag & Drop state
const dropZoneRef = ref<HTMLElement | null>(null);
const isDragging = ref(false);

// Computed
const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value),
});

// Methods
function triggerFileSelect() {
  fileInput.value?.click();
}

function validateAndSetFile(file: File) {
  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
  ];

  if (!allowedTypes.includes(file.type)) {
    errorMessage.value = '엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.';
    return false;
  }

  if (file.size > 10 * 1024 * 1024) {
    errorMessage.value = '파일 크기는 10MB를 초과할 수 없습니다.';
    return false;
  }

  selectedFile.value = file;
  errorMessage.value = '';
  return true;
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) validateAndSetFile(file);
}

function clearFile() {
  selectedFile.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

// Drag & Drop handlers
function onDragOver() {
  isDragging.value = true;
}

function onDragLeave() {
  isDragging.value = false;
}

function onDrop(e: DragEvent) {
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (!files || files.length === 0) return;
  const file = files[0];
  validateAndSetFile(file);
}

async function uploadFile() {
  if (!selectedFile.value) return;

  isUploading.value = true;
  uploadProgress.value = 0;
  errorMessage.value = '';

  try {
    await props.onUpload(selectedFile.value, (progress) => {
      uploadProgress.value = progress;
    });

    emit('success');
    closeDialog();
  } catch (error) {
    const message = error instanceof Error ? error.message : '업로드 중 오류가 발생했습니다.';
    errorMessage.value = message;
    emit('error', message);
  } finally {
    isUploading.value = false;
    uploadProgress.value = 0;
  }
}

async function downloadSample() {
  isDownloading.value = true;
  errorMessage.value = '';

  try {
    await props.onDownloadSample();
  } catch (error) {
    const message =
      error instanceof Error ? error.message : '샘플 다운로드 중 오류가 발생했습니다.';
    errorMessage.value = message;
    emit('error', message);
  } finally {
    isDownloading.value = false;
  }
}

function closeDialog() {
  isOpen.value = false;
  clearFile();
  errorMessage.value = '';
  uploadProgress.value = 0;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
</script>
