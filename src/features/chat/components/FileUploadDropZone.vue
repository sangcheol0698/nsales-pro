<template>
  <div class="relative">
    <!-- 메인 드롭존 -->
    <div
      ref="dropZoneRef"
      class="relative border-2 border-dashed rounded-lg transition-all duration-200"
      :class="{
        'border-primary bg-primary/5': isDragOver,
        'border-muted-foreground/30 hover:border-muted-foreground/50': !isDragOver,
        'cursor-pointer': !disabled
      }"
      @click="!disabled && triggerFileInput()"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <!-- 업로드 영역 내용 -->
      <div class="p-6 text-center">
        <div v-if="!isDragOver" class="space-y-3">
          <div class="mx-auto w-12 h-12 bg-muted/50 rounded-full flex items-center justify-center">
            <Upload class="h-6 w-6 text-muted-foreground" />
          </div>
          <div>
            <h4 class="text-sm font-medium mb-1">파일을 드래그하거나 클릭하여 업로드</h4>
            <p class="text-xs text-muted-foreground">
              PDF, DOCX, 이미지 파일 (최대 10MB)
            </p>
          </div>
          <div class="flex items-center justify-center gap-2">
            <Switch
              v-model:checked="addToVectorStore"
              :disabled="disabled"
              id="vector-store-toggle"
            />
            <Label 
              for="vector-store-toggle" 
              class="text-xs text-muted-foreground cursor-pointer"
            >
              지식 베이스에 자동 추가
            </Label>
          </div>
        </div>

        <div v-else class="space-y-2">
          <div class="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
            <Download class="h-6 w-6 text-primary" />
          </div>
          <p class="text-sm font-medium text-primary">파일을 여기에 놓으세요</p>
        </div>
      </div>

      <!-- 로딩 오버레이 -->
      <div v-if="isUploading" class="absolute inset-0 bg-background/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
        <div class="text-center space-y-2">
          <Loader class="h-6 w-6 animate-spin mx-auto text-primary" />
          <p class="text-sm font-medium">업로드 중...</p>
          <div v-if="uploadProgress > 0" class="w-32 bg-muted rounded-full h-2">
            <div 
              class="bg-primary h-2 rounded-full transition-all duration-300"
              :style="{ width: `${uploadProgress}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 업로드된 파일 목록 -->
    <div v-if="uploadedFiles.length > 0" class="mt-4 space-y-2">
      <div class="flex items-center justify-between">
        <Label class="text-sm font-medium">업로드된 파일</Label>
        <Button
          variant="ghost"
          size="sm"
          @click="clearAll"
          class="h-6 text-xs text-muted-foreground hover:text-foreground"
        >
          모두 지우기
        </Button>
      </div>
      
      <div class="space-y-1">
        <div
          v-for="file in uploadedFiles"
          :key="file.id"
          class="flex items-center gap-3 p-3 bg-muted/30 rounded-lg group"
        >
          <!-- 파일 아이콘 -->
          <div class="flex-shrink-0">
            <FileText v-if="file.type === 'document'" class="h-4 w-4 text-blue-600" />
            <Image v-else-if="file.type === 'image'" class="h-4 w-4 text-green-600" />
            <FileIcon v-else class="h-4 w-4 text-gray-600" />
          </div>
          
          <!-- 파일 정보 -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-sm font-medium truncate">{{ file.name }}</span>
              <Badge
                :variant="file.status === 'completed' ? 'default' : 
                         file.status === 'processing' ? 'secondary' : 'destructive'"
                class="text-xs h-4 px-1"
              >
                {{ getStatusText(file.status) }}
              </Badge>
            </div>
            <div class="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{{ formatFileSize(file.size) }}</span>
              <span>•</span>
              <span>{{ file.addedToVectorStore ? '지식 베이스 포함' : '일반 업로드' }}</span>
            </div>
          </div>
          
          <!-- 액션 버튼들 -->
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              v-if="file.status === 'completed'"
              variant="ghost"
              size="sm"
              @click="previewFile(file)"
              class="h-6 w-6 p-0"
            >
              <Eye class="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              @click="removeFile(file.id)"
              class="h-6 w-6 p-0 hover:bg-destructive/20 hover:text-destructive"
            >
              <X class="h-3 w-3" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- 숨겨진 파일 입력 -->
    <input
      ref="fileInputRef"
      type="file"
      multiple
      accept="image/*,text/*,.pdf,.doc,.docx"
      @change="handleFileSelect"
      class="hidden"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  Upload, 
  Download, 
  Loader,
  FileText,
  Image,
  FileIcon,
  Eye,
  X
} from 'lucide-vue-next'
import { Button } from '@/core/components/ui/button'
import { Label } from '@/core/components/ui/label'
import { Badge } from '@/core/components/ui/badge'
import { Switch } from '@/core/components/ui/switch'
import { useToast } from '@/core/composables'

interface Props {
  disabled?: boolean
  sessionId?: string
}

interface UploadedFile {
  id: string
  name: string
  size: number
  type: 'document' | 'image' | 'other'
  status: 'processing' | 'completed' | 'failed'
  addedToVectorStore: boolean
  content?: string
  url?: string
}

interface Emits {
  fileUploaded: [file: UploadedFile]
  filesCleared: []
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<Emits>()
const toast = useToast()

// 상태
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const addToVectorStore = ref(true)
const uploadedFiles = ref<UploadedFile[]>([])

// 참조
const dropZoneRef = ref<HTMLDivElement>()
const fileInputRef = ref<HTMLInputElement>()

// 드래그 앤 드롭 핸들러
const handleDragOver = (event: DragEvent) => {
  if (props.disabled) return
  isDragOver.value = true
}

const handleDragLeave = (event: DragEvent) => {
  if (props.disabled) return
  // 드롭존 밖으로 나갔을 때만 isDragOver를 false로 설정
  const rect = dropZoneRef.value?.getBoundingClientRect()
  if (rect) {
    const { clientX, clientY } = event
    if (
      clientX < rect.left ||
      clientX > rect.right ||
      clientY < rect.top ||
      clientY > rect.bottom
    ) {
      isDragOver.value = false
    }
  }
}

const handleDrop = (event: DragEvent) => {
  if (props.disabled) return
  isDragOver.value = false
  
  const files = event.dataTransfer?.files
  if (files) {
    processFiles(Array.from(files))
  }
}

// 파일 처리 함수들
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    processFiles(Array.from(files))
    // 입력 필드 초기화
    target.value = ''
  }
}

const processFiles = async (files: File[]) => {
  if (props.disabled || files.length === 0) return

  // 파일 검증
  const validFiles = files.filter(file => {
    // 파일 크기 제한 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('파일 크기 제한', {
        description: `${file.name}은 10MB를 초과합니다.`
      })
      return false
    }
    return true
  })

  if (validFiles.length === 0) return

  try {
    isUploading.value = true
    uploadProgress.value = 0

    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i]
      await uploadSingleFile(file)
      uploadProgress.value = Math.round(((i + 1) / validFiles.length) * 100)
    }

    toast.success('업로드 완료', {
      description: `${validFiles.length}개 파일이 성공적으로 업로드되었습니다.`
    })
  } catch (error) {
    console.error('Upload error:', error)
    toast.error('업로드 실패', {
      description: '파일 업로드 중 오류가 발생했습니다.'
    })
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

const uploadSingleFile = async (file: File): Promise<void> => {
  const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  
  // 파일 타입 결정
  const getFileType = (file: File): 'document' | 'image' | 'other' => {
    if (file.type.startsWith('image/')) return 'image'
    if (
      file.type === 'application/pdf' ||
      file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
      file.type === 'text/plain'
    ) return 'document'
    return 'other'
  }

  // 업로드된 파일 객체 생성
  const uploadedFile: UploadedFile = {
    id: fileId,
    name: file.name,
    size: file.size,
    type: getFileType(file),
    status: 'processing',
    addedToVectorStore: addToVectorStore.value
  }

  // 파일 목록에 추가
  uploadedFiles.value.push(uploadedFile)

  try {
    // FormData 생성
    const formData = new FormData()
    formData.append('content', '') // 빈 메시지로 파일만 업로드
    formData.append('sessionId', props.sessionId || 'default')
    formData.append('files', file)

    // 서버에 업로드
    const response = await fetch('/api/v1/chat/messages/with-files', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      const result = await response.json()
      
      // 업로드 성공
      uploadedFile.status = 'completed'
      uploadedFile.content = result.aiMessage?.content || '파일이 성공적으로 처리되었습니다.'
      
      emit('fileUploaded', uploadedFile)
    } else {
      throw new Error('Upload failed')
    }
  } catch (error) {
    console.error('Single file upload error:', error)
    uploadedFile.status = 'failed'
  }
}

// 유틸리티 함수들
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const getStatusText = (status: string): string => {
  switch (status) {
    case 'processing': return '처리중'
    case 'completed': return '완료'
    case 'failed': return '실패'
    default: return status
  }
}

const previewFile = (file: UploadedFile) => {
  // 파일 미리보기 로직
  toast.info('파일 내용', {
    description: file.content || '파일 내용을 미리볼 수 없습니다.'
  })
}

const removeFile = (fileId: string) => {
  uploadedFiles.value = uploadedFiles.value.filter(file => file.id !== fileId)
}

const clearAll = () => {
  uploadedFiles.value = []
  emit('filesCleared')
}
</script>

<style scoped>
.border-dashed {
  border-style: dashed;
}
</style>