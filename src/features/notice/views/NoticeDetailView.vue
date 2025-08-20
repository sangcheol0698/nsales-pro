<template>
  <SidebarLayout>
    <div class="container mx-auto p-6">
      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="space-y-6">
        <Card>
          <CardContent class="p-6">
            <div class="space-y-4">
              <Skeleton class="h-8 w-96" />
              <div class="flex gap-4">
                <Skeleton class="h-4 w-20" />
                <Skeleton class="h-4 w-20" />
              </div>
              <Skeleton class="h-64 w-full" />
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 공지사항 상세 -->
      <div v-else-if="notice" class="space-y-6">
        <!-- 헤더 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Button variant="ghost" size="sm" @click="router.back()">
              <ArrowLeft class="h-4 w-4" />
            </Button>
            <h1 class="text-3xl font-bold tracking-tight">{{ notice.title }}</h1>
          </div>

          <!-- 관리자만 수정/삭제 버튼 표시 -->
          <div v-if="canEditNotice || canDeleteNotice" class="flex items-center gap-2">
            <Button
              v-if="canEditNotice"
              variant="outline"
              size="sm"
              @click="router.push(`/notices/${notice.id}/edit`)"
            >
              <Edit class="h-4 w-4 mr-2" />
              수정
            </Button>
            <Button
              v-if="canDeleteNotice"
              variant="destructive"
              size="sm"
              @click="handleDelete"
            >
              <Trash2 class="h-4 w-4 mr-2" />
              삭제
            </Button>
          </div>
        </div>

        <!-- 메타 정보 -->
        <div class="flex items-center gap-4 text-sm text-gray-600 border-b border-gray-200 pb-4 dark:text-gray-400 dark:border-gray-700">
          <div class="flex items-center gap-1">
            <User class="h-4 w-4" />
            <span>{{ notice.author }}</span>
          </div>
          <div class="flex items-center gap-1">
            <Calendar class="h-4 w-4" />
            <span>{{ formatDate(notice.createdAt) }}</span>
          </div>
          <div v-if="notice.updatedAt && notice.updatedAt !== notice.createdAt" class="flex items-center gap-1">
            <Clock class="h-4 w-4" />
            <span>수정: {{ formatDate(notice.updatedAt) }}</span>
          </div>
        </div>

        <!-- 내용 -->
        <Card>
          <CardContent class="p-6">
            <div 
              class="prose prose-sm max-w-none min-h-[200px]"
              v-html="sanitizedContent"
            ></div>
          </CardContent>
        </Card>

        <!-- 목록으로 돌아가기 -->
        <div class="flex justify-center">
          <Button variant="outline" @click="router.push('/notices')">
            <List class="h-4 w-4 mr-2" />
            목록으로 돌아가기
          </Button>
        </div>
      </div>

      <!-- 공지사항을 찾을 수 없음 -->
      <div v-else class="text-center py-12">
        <h2 class="text-2xl font-bold text-gray-600 mb-4 dark:text-gray-400">공지사항을 찾을 수 없습니다</h2>
        <Button variant="outline" @click="router.push('/notices')">
          <List class="h-4 w-4 mr-2" />
          목록으로 돌아가기
        </Button>
      </div>

      <!-- 삭제 확인 다이얼로그 -->
      <Dialog :open="showDeleteDialog" @update:open="showDeleteDialog = $event">
        <DialogContent>
          <DialogHeader>
            <DialogTitle>공지사항 삭제</DialogTitle>
            <DialogDescription>
              정말로 이 공지사항을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" @click="showDeleteDialog = false">취소</Button>
            <Button variant="destructive" @click="confirmDelete" :disabled="isDeleting">
              <Loader2 v-if="isDeleting" class="h-4 w-4 mr-2 animate-spin" />
              삭제
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { container } from 'tsyringe';
import { toast } from 'vue-sonner';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

import {
  ArrowLeft,
  Edit,
  Trash2,
  User,
  Calendar,
  Clock,
  List,
  Loader2,
} from 'lucide-vue-next';

import { SidebarLayout } from '@/components/layout';
import NoticeRepository from '@/features/notice/repository/NoticeRepository';
import { useAuth } from '@/core/composables/useAuth';
import type { Notice } from '@/features/notice/entity/Notice';

const router = useRouter();
const route = useRoute();
const noticeRepository = container.resolve(NoticeRepository);
const { canEditNotice, canDeleteNotice } = useAuth();

const noticeId = computed(() => route.params.id as string);

const notice = ref<Notice | null>(null);
const isLoading = ref(false);
const showDeleteDialog = ref(false);
const isDeleting = ref(false);

const sanitizedContent = computed(() => {
  if (!notice.value?.content) return '';
  
  // 기본적인 HTML 콘텐츠를 안전하게 표시
  // 실제 프로덕션에서는 DOMPurify 등을 사용하는 것이 좋습니다
  return notice.value.content;
});

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const loadNotice = async () => {
  try {
    isLoading.value = true;
    notice.value = await noticeRepository.getNotice(noticeId.value);
  } catch (error) {
    console.error('Failed to load notice:', error);
    toast.error('공지사항을 불러오는데 실패했습니다.');
    router.push('/notices');
  } finally {
    isLoading.value = false;
  }
};

const handleDelete = () => {
  showDeleteDialog.value = true;
};

const confirmDelete = async () => {
  try {
    isDeleting.value = true;
    await noticeRepository.deleteNotice(noticeId.value);
    toast.success('공지사항이 삭제되었습니다.');
    router.push('/notices');
  } catch (error) {
    console.error('Failed to delete notice:', error);
    toast.error('공지사항 삭제에 실패했습니다.');
  } finally {
    isDeleting.value = false;
    showDeleteDialog.value = false;
  }
};

onMounted(() => {
  loadNotice();
});
</script>

<style scoped>
/* 공지사항 내용 스타일링 */
.prose {
  color: inherit;
}

.prose h1,
.prose h2,
.prose h3,
.prose h4,
.prose h5,
.prose h6 {
  color: inherit;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.prose h1 {
  font-size: 2rem;
  line-height: 1.2;
}

.prose h2 {
  font-size: 1.5rem;
  line-height: 1.3;
}

.prose h3 {
  font-size: 1.25rem;
  line-height: 1.4;
}

.prose p {
  margin-bottom: 1.25rem;
}

.prose strong {
  color: inherit;
  font-weight: 600;
}

.prose em {
  font-style: italic;
}

.prose a {
  color: #2563eb;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.dark .prose a {
  color: #3b82f6;
}

.prose code {
  color: inherit;
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
  font-family: ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
}

.dark .prose code {
  background-color: #1f2937;
}

.prose pre {
  background-color: #f3f4f6;
  color: inherit;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

.dark .prose pre {
  background-color: #1f2937;
}

.prose blockquote {
  border-left: 4px solid #e5e7eb;
  padding-left: 1rem;
  margin: 1.5rem 0;
  color: #6b7280;
  font-style: italic;
}

.dark .prose blockquote {
  border-color: #374151;
  color: #9ca3af;
}

.prose ul,
.prose ol {
  margin: 1.25rem 0;
  padding-left: 1.5rem;
}

.prose li {
  margin: 0.5rem 0;
}

.prose table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
}

.prose th,
.prose td {
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  text-align: left;
}

.dark .prose th,
.dark .prose td {
  border-color: #374151;
}

.prose th {
  background-color: #f3f4f6;
  font-weight: 600;
}

.dark .prose th {
  background-color: #1f2937;
}
</style>