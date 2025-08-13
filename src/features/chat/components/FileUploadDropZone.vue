<template>
  <div class="relative">
    <!-- 메인 드롭존 -->
    <div
      ref="dropZoneRef"
      class="relative border-2 border-dashed rounded-lg transition-all duration-300 group"
      :class="{
        'border-primary bg-primary/5 scale-105': isDragOver,
        'border-muted-foreground/30 hover:border-muted-foreground/50 hover:bg-muted/10': !isDragOver,
        'cursor-pointer': !disabled
      }"
      @click="!disabled && triggerFileInput()"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <!-- 배경 패턴 (드래그 중일 때만 표시) -->
      <div v-if="isDragOver" class="absolute inset-0 opacity-20 rounded-lg overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary/5"></div>
        <div class="absolute inset-0" 
             style="background-image: radial-gradient(circle at 1px 1px, rgba(var(--primary),0.15) 1px, transparent 0); background-size: 20px 20px;">
        </div>
      </div>

      <!-- 업로드 영역 내용 -->
      <div class="relative p-6 text-center">
        <div v-if="!isDragOver" class="space-y-3">
          <div class="mx-auto w-12 h-12 bg-muted/50 rounded-full flex items-center justify-center group-hover:bg-primary/10 transition-colors">
            <Upload class="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
          </div>
          <div>
            <h4 class="text-sm font-medium mb-1">파일을 드래그하거나 클릭하여 업로드</h4>
            <p class="text-xs text-muted-foreground">
              📷 이미지, 📄 PDF, 📝 DOCX 파일 (최대 10MB)
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
              🧠 지식 베이스에 자동 추가
            </Label>
          </div>
        </div>

        <div v-else class="space-y-3">
          <div class="mx-auto w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center animate-pulse">
            <Download class="h-8 w-8 text-primary animate-bounce" />
          </div>
          <div>
            <p class="text-sm font-medium text-primary">파일을 여기에 놓으세요</p>
            <p class="text-xs text-primary/70">{{ draggedFileCount }}개 파일</p>
          </div>
        </div>
      </div>

      <!-- 로딩 오버레이 -->
      <div v-if="isUploading" class="absolute inset-0 bg-background/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
        <BlurFade :show="isUploading" :delay="0" :duration="200">
          <div class="text-center space-y-3">
            <div class="relative">
              <Loader class="h-8 w-8 animate-spin mx-auto text-primary" />
              <div class="absolute inset-0 animate-ping h-8 w-8 mx-auto border border-primary/20 rounded-full"></div>
            </div>
            <p class="text-sm font-medium">업로드 중...</p>
            <div v-if="uploadProgress > 0" class="w-40 bg-muted rounded-full h-2 overflow-hidden">
              <div 
                class="bg-gradient-to-r from-primary via-primary/80 to-primary/60 h-2 rounded-full transition-all duration-500 ease-out relative"
                :style="{ width: `${uploadProgress}%` }"
              >
                <!-- 진행률 바 위에 반짝이는 효과 -->
                <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
              </div>
            </div>
            <p class="text-xs text-muted-foreground font-mono">{{ Math.round(uploadProgress) }}%</p>
          </div>
        </BlurFade>
      </div>
    </div>

    <!-- 업로드된 파일 목록 -->
    <div v-if="uploadedFiles.length > 0" class="mt-6 space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Label class="text-sm font-medium">업로드된 파일</Label>
          <Badge variant="secondary" class="text-xs">{{ uploadedFiles.length }}</Badge>
        </div>
        <Button
          variant="ghost"
          size="sm"
          @click="clearAll"
          class="h-6 text-xs text-muted-foreground hover:text-foreground"
        >
          <X class="h-3 w-3 mr-1" />
          모두 지우기
        </Button>
      </div>
      
      <!-- 이미지 파일들 (그리드 레이아웃) -->
      <div v-if="imageFiles.length > 0" class="space-y-2">
        <Label class="text-xs text-muted-foreground">📷 이미지 파일</Label>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <BlurFade
            v-for="(file, index) in imageFiles"
            :key="file.id"
            :delay="index * 100"
            :duration="300"
            direction="up"
          >
            <div
              class="relative group aspect-square rounded-lg overflow-hidden border border-muted bg-muted/30 hover:bg-muted/50 transition-all duration-200"
            >
            <!-- 이미지 썸네일 -->
            <div v-if="file.thumbnail" class="w-full h-full">
              <img
                :src="file.thumbnail"
                :alt="file.name"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                @click="openImageModal(file)"
              />
            </div>
            
            <!-- 이미지 로딩 중 -->
            <div v-else class="w-full h-full flex items-center justify-center">
              <div class="text-center space-y-2">
                <Image class="h-6 w-6 text-muted-foreground mx-auto" />
                <div v-if="file.status === 'processing'" class="w-8 h-1 bg-muted rounded-full overflow-hidden">
                  <div class="h-full bg-primary animate-pulse"></div>
                </div>
              </div>
            </div>
            
            <!-- 오버레이 정보 -->
            <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200 flex items-end">
              <div class="w-full p-2 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <p class="text-white text-xs font-medium truncate">{{ file.name }}</p>
                <p class="text-white/70 text-xs">{{ formatFileSize(file.size) }}</p>
              </div>
            </div>
            
            <!-- 상태 배지 -->
            <div class="absolute top-2 right-2">
              <Badge
                :variant="file.status === 'completed' ? 'default' : 
                         file.status === 'processing' ? 'secondary' : 'destructive'"
                class="text-xs h-5 px-2 shadow-lg"
              >
                {{ getStatusText(file.status) }}
              </Badge>
            </div>
            
            <!-- 삭제 버튼 -->
            <Button
              variant="ghost"
              size="sm"
              @click="removeFile(file.id)"
              class="absolute top-2 left-2 h-6 w-6 p-0 bg-black/20 hover:bg-red-500/80 text-white opacity-0 group-hover:opacity-100 transition-all duration-200"
            >
              <X class="h-3 w-3" />
            </Button>
            </div>
          </BlurFade>
        </div>
      </div>
      
      <!-- 문서 파일들 (리스트 레이아웃) -->
      <div v-if="documentFiles.length > 0" class="space-y-2">
        <Label class="text-xs text-muted-foreground">📄 문서 파일</Label>
        <div class="space-y-2">
          <BlurFade
            v-for="(file, index) in documentFiles"
            :key="file.id"
            :delay="(imageFiles.length + index) * 100"
            :duration="300"
            direction="left"
          >
            <div
              class="flex items-center gap-3 p-3 bg-muted/30 rounded-lg group hover:bg-muted/50 transition-all duration-200"
            >
            <!-- 파일 아이콘 -->
            <div class="flex-shrink-0 w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <FileText class="h-5 w-5 text-blue-600" />
            </div>
            
            <!-- 파일 정보 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-sm font-medium truncate">{{ file.name }}</span>
                <Badge
                  :variant="file.status === 'completed' ? 'default' : 
                           file.status === 'processing' ? 'secondary' : 'destructive'"
                  class="text-xs h-4 px-2"
                >
                  {{ getStatusText(file.status) }}
                </Badge>
              </div>
              <div class="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{{ formatFileSize(file.size) }}</span>
                <span>•</span>
                <span>{{ file.addedToVectorStore ? '🧠 지식 베이스 포함' : '📎 일반 업로드' }}</span>
              </div>
            </div>
            
            <!-- 액션 버튼들 -->
            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <Button
                v-if="file.status === 'completed'"
                variant="ghost"
                size="sm"
                @click="previewFile(file)"
                class="h-8 w-8 p-0"
                title="미리보기"
              >
                <Eye class="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click="removeFile(file.id)"
                class="h-8 w-8 p-0 hover:bg-destructive/20 hover:text-destructive"
                title="삭제"
              >
                <X class="h-4 w-4" />
              </Button>
            </div>
            </div>
          </BlurFade>
        </div>
      </div>
    </div>
    
    <!-- 이미지 확대 모달 -->
    <div v-if="selectedImage" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click="closeImageModal">
      <div class="relative max-w-4xl max-h-full">
        <img
          :src="selectedImage.thumbnail"
          :alt="selectedImage.name"
          class="max-w-full max-h-full rounded-lg shadow-2xl"
          @click.stop
        />
        <Button
          variant="ghost"
          size="sm"
          @click="closeImageModal"
          class="absolute top-4 right-4 h-8 w-8 p-0 bg-black/20 hover:bg-black/40 text-white"
        >
          <X class="h-4 w-4" />
        </Button>
        <div class="absolute bottom-4 left-4 bg-black/60 rounded-lg p-3 text-white">
          <p class="font-medium">{{ selectedImage.name }}</p>
          <p class="text-sm text-white/70">{{ formatFileSize(selectedImage.size) }}</p>
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
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import BlurFade from '@/components/ui/BlurFade.vue'
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
  thumbnail?: string
  file?: File
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
const draggedFileCount = ref(0)
const selectedImage = ref<UploadedFile | null>(null)

// 참조
const dropZoneRef = ref<HTMLDivElement>()
const fileInputRef = ref<HTMLInputElement>()

// 계산된 속성
const imageFiles = computed(() => uploadedFiles.value.filter(file => file.type === 'image'))
const documentFiles = computed(() => uploadedFiles.value.filter(file => file.type === 'document' || file.type === 'other'))

// 드래그 앤 드롭 핸들러
const handleDragOver = (event: DragEvent) => {
  if (props.disabled) return
  isDragOver.value = true
  
  // 드래그된 파일 개수 확인
  const files = event.dataTransfer?.files
  if (files) {
    draggedFileCount.value = files.length
  }
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
    addedToVectorStore: addToVectorStore.value,
    file: file
  }

  // 이미지 파일인 경우 썸네일 생성
  if (uploadedFile.type === 'image') {
    try {
      uploadedFile.thumbnail = await generateImageThumbnail(file)
    } catch (error) {
      console.error('Thumbnail generation failed:', error)
    }
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

// 이미지 썸네일 생성 함수
const generateImageThumbnail = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        
        if (!ctx) {
          reject(new Error('Canvas context not available'))
          return
        }
        
        // 썸네일 크기 설정 (최대 300x300)
        const maxSize = 300
        let { width, height } = img
        
        if (width > height) {
          if (width > maxSize) {
            height = (height * maxSize) / width
            width = maxSize
          }
        } else {
          if (height > maxSize) {
            width = (width * maxSize) / height
            height = maxSize
          }
        }
        
        canvas.width = width
        canvas.height = height
        
        // 이미지 그리기
        ctx.drawImage(img, 0, 0, width, height)
        
        // base64로 변환
        const thumbnail = canvas.toDataURL('image/jpeg', 0.8)
        resolve(thumbnail)
      }
      img.onerror = () => reject(new Error('Image loading failed'))
      img.src = e.target?.result as string
    }
    reader.onerror = () => reject(new Error('File reading failed'))
    reader.readAsDataURL(file)
  })
}

// 이미지 모달 함수들
const openImageModal = (file: UploadedFile) => {
  selectedImage.value = file
}

const closeImageModal = () => {
  selectedImage.value = null
}
</script>

<style scoped>
.border-dashed {
  border-style: dashed;
}
</style>