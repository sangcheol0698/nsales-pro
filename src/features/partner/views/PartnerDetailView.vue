<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full max-w-4xl mx-auto">
        <!-- 로딩 상태 -->
        <div v-if="loading" class="flex justify-center items-center h-64">
          <Loader2 class="h-8 w-8 animate-spin" />
        </div>

        <!-- 에러 상태 -->
        <div v-else-if="error" class="text-center p-8">
          <AlertCircle class="h-12 w-12 text-destructive mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-foreground mb-2">협력사 정보를 불러올 수 없습니다</h3>
          <p class="text-muted-foreground mb-4">{{ error }}</p>
          <div class="flex gap-2 justify-center">
            <Button variant="outline" @click="$router.go(-1)">
              <ArrowLeft class="mr-2 h-4 w-4" />
              이전으로
            </Button>
            <Button @click="loadPartner">
              <RefreshCw class="mr-2 h-4 w-4" />
              다시 시도
            </Button>
          </div>
        </div>

        <!-- 협력사 정보 -->
        <div v-else-if="partner" class="space-y-6">
          <!-- 헤더 -->
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-foreground">{{ partner.name }}</h1>
              <div class="flex items-center gap-2 mt-1">
                <StatusBadge :status="partner.grade" type="partner" />
              </div>
            </div>
            <div class="flex gap-2">
              <Button variant="outline" @click="onEditPartner">
                <Edit3 class="mr-2 h-4 w-4" />
                수정
              </Button>
              <Button variant="destructive" @click="onDeletePartner">
                <Trash2 class="mr-2 h-4 w-4" />
                삭제
              </Button>
            </div>
          </div>

          <!-- 기본 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Building2 class="h-5 w-5" />
                기본 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">업체명</Label>
                  <p class="font-medium">{{ partner.name }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">대표자</Label>
                  <p class="font-medium">{{ partner.ceoName || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">등급</Label>
                  <StatusBadge :status="partner.grade" type="partner" />
                </div>
                <div class="space-y-1 md:col-span-2 lg:col-span-3">
                  <Label class="text-muted-foreground">주소</Label>
                  <p class="font-medium">{{ partner.address || '-' }}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 영업 담당자 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <User class="h-5 w-5" />
                영업 담당자 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">담당자명</Label>
                  <p class="font-medium">{{ partner.salesRepName || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">연락처</Label>
                  <p class="font-medium font-mono">{{ partner.salesRepPhone || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">이메일</Label>
                  <p class="font-medium font-mono">{{ partner.salesRepEmail || '-' }}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 시스템 정보 카드 -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Clock class="h-5 w-5" />
                시스템 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1">
                  <Label class="text-muted-foreground">등록일시</Label>
                  <p class="font-medium">{{ formatDateTime(partner.createdAt) }}</p>
                </div>
                <div class="space-y-1">
                  <Label class="text-muted-foreground">수정일시</Label>
                  <p class="font-medium">{{ formatDateTime(partner.updatedAt) }}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>

    <!-- 협력사 수정 다이얼로그 -->
    <PartnerEditDialog
      v-model:open="editDialogOpen"
      :loading="editLoading"
      :partner="partner"
      @submit="handleEditSubmit"
    />

    <!-- 협력사 삭제 다이얼로그 -->
    <PartnerDeleteDialog
      v-model:open="deleteDialogOpen"
      :loading="deleteLoading"
      :partner="partner"
      @confirm="handleDeleteConfirm"
    />
  </SidebarLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { container } from 'tsyringe';
import PartnerRepository from '@/features/partner/repository/PartnerRepository.ts';
import PartnerSearch from '@/features/partner/entity/PartnerSearch.ts';
import PartnerUpdate from '@/features/partner/entity/PartnerUpdate.ts';
import PartnerEditDialog from '@/features/partner/components/PartnerEditDialog.vue';
import PartnerDeleteDialog from '@/features/partner/components/PartnerDeleteDialog.vue';
import { SidebarLayout } from '@/components/layout';
import { StatusBadge } from '@/components/business';
import { useToast } from '@/core/composables';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  AlertCircle,
  ArrowLeft,
  Building2,
  Clock,
  Edit3,
  Loader2,
  RefreshCw,
  Trash2,
  User,
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const PARTNER_REPOSITORY = container.resolve(PartnerRepository);

// 상태 관리
const loading = ref(true);
const error = ref<string | null>(null);
const partner = ref<PartnerSearch | null>(null);

// 수정/삭제 다이얼로그 상태
const editDialogOpen = ref(false);
const editLoading = ref(false);
const deleteDialogOpen = ref(false);
const deleteLoading = ref(false);

// 협력사 정보 로드
async function loadPartner() {
  const partnerId = route.params.id as string;
  
  if (!partnerId || isNaN(Number(partnerId))) {
    error.value = '잘못된 협력사 ID입니다.';
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;
    
    partner.value = await PARTNER_REPOSITORY.getPartner(Number(partnerId));
    console.log('협력사 상세 정보 로드 완료:', partner.value);
    
  } catch (err: any) {
    console.error('협력사 정보 로드 실패:', err);
    error.value = err.message || '협력사 정보를 불러오는데 실패했습니다.';
    partner.value = null;
  } finally {
    loading.value = false;
  }
}

// 날짜시간 포맷팅
function formatDateTime(dateTimeString: string | undefined): string {
  if (!dateTimeString) return '-';
  
  try {
    const date = new Date(dateTimeString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateTimeString;
  }
}

// 수정 버튼 핸들러
function onEditPartner() {
  if (!partner.value) return;
  editDialogOpen.value = true;
}

// 삭제 버튼 핸들러
function onDeletePartner() {
  if (!partner.value) return;
  deleteDialogOpen.value = true;
}

// 협력사 수정 처리
async function handleEditSubmit(partnerData: PartnerUpdate) {
  editLoading.value = true;

  try {
    console.log('협력사 수정 요청:', partnerData);

    await PARTNER_REPOSITORY.updatePartner(partnerData);

    toast.success('협력사 수정 완료', {
      description: `${partnerData.name}의 정보가 성공적으로 수정되었습니다.`,
      position: 'bottom-right',
    });

    // 다이얼로그 닫기
    editDialogOpen.value = false;

    // 협력사 정보 새로고침
    await loadPartner();

  } catch (error: any) {
    console.error('협력사 수정 실패:', error);

    let errorMessage = '협력사 수정 중 오류가 발생했습니다.';
    if (error?.message?.includes('modifiedDateTime')) {
      errorMessage = '다른 사용자가 이미 수정했습니다. 새로고침 후 다시 시도해주세요.';
    }

    toast.error('협력사 수정 실패', {
      description: errorMessage,
      position: 'bottom-right',
    });
  } finally {
    editLoading.value = false;
  }
}

// 협력사 삭제 처리
async function handleDeleteConfirm(partnerId: number) {
  deleteLoading.value = true;

  try {
    console.log('협력사 삭제 요청:', partnerId);

    const partnerName = partner.value?.name || '';

    await PARTNER_REPOSITORY.deletePartner(partnerId);

    toast.success('협력사 삭제 완료', {
      description: `${partnerName}이(가) 성공적으로 삭제되었습니다.`,
      position: 'bottom-right',
    });

    // 목록으로 이동
    router.push('/partners');

  } catch (error: any) {
    console.error('협력사 삭제 실패:', error);

    toast.error('협력사 삭제 실패', {
      description: '협력사 삭제 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  } finally {
    deleteLoading.value = false;
  }
}

// 컴포넌트 마운트 시 협력사 정보 로드
onMounted(() => {
  loadPartner();
});
</script>

<style scoped>
/* 추가 스타일링이 필요한 경우 여기에 작성 */
</style>