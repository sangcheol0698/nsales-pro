<template>
  <SidebarLayout>
    <div class="container mx-auto p-6">
      <!-- 헤더 -->
      <div class="mb-6">
        <div class="flex items-center gap-2 mb-4">
          <Button variant="ghost" size="sm" @click="router.back()">
            <ArrowLeft class="h-4 w-4" />
          </Button>
          <h1 class="text-3xl font-bold tracking-tight">
            {{ isEditMode ? '공지사항 수정' : '공지사항 작성' }}
          </h1>
        </div>
        <p class="text-muted-foreground">
          {{ isEditMode ? '공지사항 내용을 수정하세요.' : '새로운 공지사항을 작성하세요.' }}
        </p>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="space-y-6">
        <Card>
          <CardContent class="p-6">
            <div class="space-y-4">
              <Skeleton class="h-4 w-20" />
              <Skeleton class="h-10 w-full" />
              <Skeleton class="h-4 w-20" />
              <Skeleton class="h-64 w-full" />
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 폼 -->
      <form v-else @submit.prevent="handleSubmit" class="space-y-6">
        <Card>
          <CardContent class="p-6">
            <div class="space-y-6">
              <!-- 제목 입력 -->
              <div class="space-y-2">
                <Label htmlFor="title">제목 *</Label>
                <Input
                  id="title"
                  v-model="form.title"
                  placeholder="공지사항 제목을 입력하세요"
                  required
                  :class="{ 'border-red-500': errors.title }"
                />
                <p v-if="errors.title" class="text-sm text-red-500">{{ errors.title }}</p>
              </div>

              <!-- 작성자 (읽기 전용) -->
              <div class="space-y-2">
                <Label htmlFor="author">작성자</Label>
                <Input
                  id="author"
                  :value="user?.name || ''"
                  readonly
                  disabled
                  class="bg-muted"
                />
              </div>

              <!-- 내용 입력 (Rich Text Editor) -->
              <div class="space-y-2">
                <Label htmlFor="content">내용 *</Label>
                <div :class="{ 'ring-2 ring-destructive': errors.content }">
                  <RichTextEditor
                    v-model="form.content"
                    placeholder="공지사항 내용을 작성하세요..."
                  />
                </div>
                <p v-if="errors.content" class="text-sm text-red-500">{{ errors.content }}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 액션 버튼들 -->
        <div class="flex items-center justify-between">
          <Button type="button" variant="outline" @click="router.back()">
            취소
          </Button>

          <div class="flex items-center gap-2">
            <!-- 미리보기 버튼 -->
            <Button
              type="button"
              variant="outline"
              @click="showPreview = true"
              :disabled="!form.title || !form.content"
            >
              미리보기
            </Button>

            <!-- 저장 버튼 -->
            <Button
              type="submit"
              :disabled="isSubmitting || !form.title || !form.content"
            >
              <Loader2 v-if="isSubmitting" class="h-4 w-4 mr-2 animate-spin" />
              {{ isEditMode ? '수정' : '등록' }}
            </Button>
          </div>
        </div>
      </form>

      <!-- 미리보기 다이얼로그 -->
      <Dialog :open="showPreview" @update:open="showPreview = $event">
        <DialogContent class="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>공지사항 미리보기</DialogTitle>
            <DialogDescription>
              작성한 내용이 어떻게 표시되는지 확인하세요.
            </DialogDescription>
          </DialogHeader>

          <div class="space-y-4">
            <div>
              <h3 class="text-2xl font-bold">{{ form.title }}</h3>
              <div class="flex items-center gap-4 text-sm text-muted-foreground mt-2">
                <span>작성자: {{ user?.name }}</span>
                <span>작성일: {{ new Date().toLocaleDateString('ko-KR') }}</span>
              </div>
            </div>

            <Separator />

            <div class="prose prose-sm max-w-none min-h-[200px] p-4 border rounded-md bg-muted/20"
                 v-html="sanitizedPreviewContent"></div>
          </div>

          <DialogFooter>
            <Button @click="showPreview = false">확인</Button>
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

import { ArrowLeft, Loader2 } from 'lucide-vue-next';

import { SidebarLayout } from '@/components/layout';
import { RichTextEditor } from '@/components/ui/rich-text-editor';
import NoticeRepository from '@/features/notice/repository/NoticeRepository';
import { useAuth } from '@/core/composables/useAuth';

const router = useRouter();
const route = useRoute();
const noticeRepository = container.resolve(NoticeRepository);
const { user, canCreateNotice, canEditNotice } = useAuth();

const isEditMode = computed(() => !!route.params.id);
const noticeId = computed(() => route.params.id as string);

const form = ref({
  title: '',
  content: '',
});

const errors = ref({
  title: '',
  content: '',
});

const isLoading = ref(false);
const isSubmitting = ref(false);
const showPreview = ref(false);

// Tiptap 에디터는 RichTextEditor 컴포넌트 내부에서 설정됨

const sanitizedPreviewContent = computed(() => {
  if (!form.value.content) return '<p class="text-muted-foreground">내용을 입력하면 여기에 미리보기가 표시됩니다.</p>';

  // echo-editor가 출력하는 HTML은 이미 안전하게 처리된 것이므로 그대로 사용
  return form.value.content || '<p class="text-muted-foreground">내용을 입력하세요.</p>';
});

const validateForm = () => {
  errors.value = {
    title: '',
    content: '',
  };

  let isValid = true;

  if (!form.value.title.trim()) {
    errors.value.title = '제목을 입력해주세요.';
    isValid = false;
  } else if (form.value.title.length > 100) {
    errors.value.title = '제목은 100자 이하로 입력해주세요.';
    isValid = false;
  }

  if (!form.value.content.trim()) {
    errors.value.content = '내용을 입력해주세요.';
    isValid = false;
  }

  return isValid;
};

const loadNotice = async () => {
  if (!isEditMode.value) return;

  try {
    isLoading.value = true;
    const notice = await noticeRepository.getNotice(noticeId.value);
    form.value = {
      title: notice.title,
      content: notice.content,
    };
  } catch (error) {
    console.error('Failed to load notice:', error);
    toast.error('공지사항을 불러오는데 실패했습니다.');
    router.back();
  } finally {
    isLoading.value = false;
  }
};

const handleSubmit = async () => {
  if (!validateForm()) return;

  try {
    isSubmitting.value = true;

    const noticeData = {
      title: form.value.title.trim(),
      content: form.value.content.trim(),
      author: user.value?.name || '',
    };

    if (isEditMode.value) {
      await noticeRepository.updateNotice(noticeId.value, noticeData);
      toast.success('공지사항이 수정되었습니다.');
      router.push(`/notices/${noticeId.value}`);
    } else {
      const notice = await noticeRepository.createNotice(noticeData);
      toast.success('공지사항이 등록되었습니다.');
      router.push(`/notices/${notice.id}`);
    }
  } catch (error) {
    console.error('Failed to save notice:', error);
    toast.error(`공지사항 ${isEditMode.value ? '수정' : '등록'}에 실패했습니다.`);
  } finally {
    isSubmitting.value = false;
  }
};

// 권한 체크
onMounted(() => {
  // if (isEditMode.value && !canEditNotice.value) {
  //   toast.error('공지사항을 수정할 권한이 없습니다.');
  //   router.replace('/notices');
  //   return;
  // }
  //
  // if (!isEditMode.value && !canCreateNotice.value) {
  //   toast.error('공지사항을 작성할 권한이 없습니다.');
  //   router.replace('/notices');
  //   return;
  // }

  loadNotice();
});
</script>

<style scoped>
/* 미리보기 다이얼로그 prose 스타일 */
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
  color: hsl(var(--primary));
  text-decoration: underline;
  text-underline-offset: 2px;
}

.prose code {
  color: inherit;
  background-color: hsl(var(--muted));
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
  font-family: ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
}

.prose pre {
  background-color: hsl(var(--muted));
  color: inherit;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

.prose blockquote {
  border-left: 4px solid hsl(var(--border));
  padding-left: 1rem;
  margin: 1.5rem 0;
  color: hsl(var(--muted-foreground));
  font-style: italic;
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
  border: 1px solid hsl(var(--border));
  padding: 0.75rem;
  text-align: left;
}

.prose th {
  background-color: hsl(var(--muted));
  font-weight: 600;
}
</style>