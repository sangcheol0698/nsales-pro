<template>
  <SidebarLayout>
    <div class="container mx-auto p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">공지사항</h1>
        <p class="text-muted-foreground mt-2">중요한 공지사항을 확인하세요</p>
      </div>
      
      <!-- 관리자만 공지사항 작성 버튼 표시 -->
      <Button 
        v-if="canCreateNotice" 
        @click="router.push('/notices/new')"
        class="gap-2"
      >
        <Plus class="h-4 w-4" />
        공지사항 작성
      </Button>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="space-y-4">
      <Card v-for="i in 3" :key="i">
        <CardContent class="p-6">
          <div class="space-y-3">
            <Skeleton class="h-6 w-3/4" />
            <Skeleton class="h-4 w-1/2" />
            <Skeleton class="h-4 w-full" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 공지사항 목록 -->
    <div v-else-if="notices.length > 0" class="space-y-4">
      <Card 
        v-for="notice in notices" 
        :key="notice.id"
        class="hover:shadow-md transition-shadow cursor-pointer"
        @click="router.push(`/notices/${notice.id}`)"
      >
        <CardContent class="p-6">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-xl font-semibold mb-2 hover:text-primary transition-colors">
                {{ notice.title }}
              </h3>
              
              <div class="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                <div class="flex items-center gap-1">
                  <User class="h-4 w-4" />
                  {{ notice.author }}
                </div>
                <div class="flex items-center gap-1">
                  <Calendar class="h-4 w-4" />
                  {{ formatDate(notice.createdAt) }}
                </div>
              </div>
              
              <!-- 내용 미리보기 -->
              <p class="text-muted-foreground line-clamp-2">
                {{ getPreviewText(notice.content) }}
              </p>
            </div>
            
            <!-- 관리자 액션 버튼들 -->
            <div v-if="canEditNotice" class="flex items-center gap-2 ml-4">
              <Button 
                variant="outline" 
                size="sm"
                @click.stop="router.push(`/notices/${notice.id}/edit`)"
                class="gap-1"
              >
                <Edit class="h-3 w-3" />
                수정
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                @click.stop="handleDeleteNotice(notice.id)"
                class="gap-1 text-destructive hover:text-destructive"
              >
                <Trash2 class="h-3 w-3" />
                삭제
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 빈 상태 -->
    <div v-else class="text-center py-12">
      <div class="mx-auto w-24 h-24 bg-muted rounded-full flex items-center justify-center mb-4">
        <MessageSquare class="h-10 w-10 text-muted-foreground" />
      </div>
      <h3 class="text-lg font-medium mb-2">아직 공지사항이 없습니다</h3>
      <p class="text-muted-foreground mb-4">
        {{ canCreateNotice ? '첫 번째 공지사항을 작성해보세요.' : '공지사항이 등록되면 여기에 표시됩니다.' }}
      </p>
      <Button 
        v-if="canCreateNotice" 
        @click="router.push('/notices/new')"
        class="gap-2"
      >
        <Plus class="h-4 w-4" />
        공지사항 작성
      </Button>
    </div>

    <!-- 삭제 확인 다이얼로그 -->
    <AlertDialog :open="showDeleteDialog" @update:open="showDeleteDialog = $event">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>공지사항 삭제</AlertDialogTitle>
          <AlertDialogDescription>
            정말로 이 공지사항을 삭제하시겠습니까? 삭제된 공지사항은 복구할 수 없습니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel @click="showDeleteDialog = false">취소</AlertDialogCancel>
          <AlertDialogAction @click="confirmDelete" class="bg-destructive text-destructive-foreground hover:bg-destructive/90">
            삭제
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
    </div>
  </SidebarLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { container } from 'tsyringe';
import { toast } from 'vue-sonner';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
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

import { Plus, Edit, Trash2, User, Calendar, MessageSquare } from 'lucide-vue-next';

import { SidebarLayout } from '@/components/layout';
import Notice from '@/features/notice/entity/Notice';
import NoticeRepository from '@/features/notice/repository/NoticeRepository';
import { useAuth } from '@/core/composables/useAuth';

const router = useRouter();
const noticeRepository = container.resolve(NoticeRepository);
const { canCreateNotice, canEditNotice, canDeleteNotice } = useAuth();

const notices = ref<Notice[]>([]);
const isLoading = ref(true);
const showDeleteDialog = ref(false);
const deleteTargetId = ref<string>('');

const loadNotices = async () => {
  try {
    isLoading.value = true;
    const response = await noticeRepository.getNotices();
    notices.value = response.content;
  } catch (error) {
    console.error('Failed to load notices:', error);
    toast.error('공지사항을 불러오는데 실패했습니다.');
  } finally {
    isLoading.value = false;
  }
};

const handleDeleteNotice = (noticeId: string) => {
  deleteTargetId.value = noticeId;
  showDeleteDialog.value = true;
};

const confirmDelete = async () => {
  try {
    await noticeRepository.deleteNotice(deleteTargetId.value);
    notices.value = notices.value.filter(notice => notice.id !== deleteTargetId.value);
    toast.success('공지사항이 삭제되었습니다.');
    showDeleteDialog.value = false;
  } catch (error) {
    console.error('Failed to delete notice:', error);
    toast.error('공지사항 삭제에 실패했습니다.');
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const getPreviewText = (content: string) => {
  // HTML 태그 제거하고 텍스트만 추출
  const div = document.createElement('div');
  div.innerHTML = content;
  const text = div.textContent || div.innerText || '';
  return text.length > 100 ? text.substring(0, 100) + '...' : text;
};

onMounted(() => {
  loadNotices();
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>