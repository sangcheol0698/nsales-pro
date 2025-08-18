<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <!-- 요약 카드 -->
        <SummaryCards :cards="summaryCards" />

        <!-- 데이터 테이블 -->
        <DataTableWithUrl
          ref="tableRef"
          :columns="columns"
          :fetchData="fetchPartners"
          searchPlaceholder="협력사 검색..."
          searchColumnId="name"
          :getColumnLabel="getColumnLabel"
          emptyMessage="협력사가 없습니다"
          emptyDescription="새 협력사를 추가하거나 검색 조건을 변경해보세요"
          storageKey="partner-table-visibility"
        >
          <template #filters="{ table }">
            <DataTableFacetedFilter
              v-if="table.getColumn('grade')"
              :column="table.getColumn('grade')"
              title="등급"
              :options="gradeOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('ceoName') && ceoNameOptions.length > 0"
              :column="table.getColumn('ceoName')"
              title="대표자"
              :options="ceoNameOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('salesRepName') && salesRepNameOptions.length > 0"
              :column="table.getColumn('salesRepName')"
              title="영업대표"
              :options="salesRepNameOptions"
            />
          </template>

          <template #actions="{ table }">
            <div class="flex items-center gap-2">
              <!-- 모바일: 통합 액션 드롭다운 -->
              <MobileActionDropdown
                addButtonText="협력사 추가"
                @download-current="() => downloadCurrentData(table)"
                @download-sample="downloadSample"
                @download-all="downloadAllData"
                @upload-excel="openUploadDialog"
                @add-item="onAddPartner"
              />

              <!-- 데스크톱: 개별 버튼들 -->
              <div class="hidden md:flex items-center gap-2">
                <!-- 엑셀 다운로드 버튼 -->
                <ExcelDownloadButton
                  :onDownloadData="() => downloadCurrentData(table)"
                  :onDownloadSample="downloadSample"
                  :onDownloadAll="downloadAllData"
                  @download-start="handleDownloadStart"
                  @download-complete="handleDownloadComplete"
                  @download-error="handleDownloadError"
                />

                <!-- 엑셀 업로드 버튼 -->
                <Button
                  variant="outline"
                  size="sm"
                  class="h-8"
                  @click="openUploadDialog"
                >
                  <Upload class="mr-2 h-4 w-4" />
                  엑셀 업로드
                </Button>

                <!-- 협력사 추가 버튼 -->
                <Button size="sm" class="h-8" @click="onAddPartner" data-testid="add-partner-btn">
                  <Plus class="mr-2 h-4 w-4" />
                  협력사 추가
                </Button>
              </div>
            </div>
          </template>
        </DataTableWithUrl>
      </div>
    </main>

    <!-- 엑셀 업로드 다이얼로그 -->
    <ExcelUploadDialog
      v-model:open="uploadDialogOpen"
      title="협력사 엑셀 업로드"
      description="엑셀 파일을 업로드하여 협력사 정보를 일괄 등록하세요."
      :onUpload="handleExcelUpload"
      :onDownloadSample="downloadSample"
      @success="handleUploadSuccess"
      @error="handleUploadError"
    />

    <!-- 협력사 추가 다이얼로그 -->
    <PartnerAddDialog
      v-model:open="addDialogOpen"
      @success="handleAddSuccess"
    />

    <!-- 협력사 수정 다이얼로그 -->
    <PartnerEditDialog
      v-model:open="editDialogOpen"
      :loading="editLoading"
      :partner="selectedPartner"
      @submit="handleEditSubmit"
    />

    <!-- 협력사 삭제 다이얼로그 -->
    <PartnerDeleteDialog
      v-model:open="deleteDialogOpen"
      :loading="deleteLoading"
      :partner="selectedPartner"
      @confirm="handleDeleteConfirm"
    />
  </SidebarLayout>
</template>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table';
import { computed, h, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { container } from 'tsyringe';
import PartnerRepository from '@/features/partner/repository/PartnerRepository.ts';
import PartnerSearch from '@/features/partner/entity/PartnerSearch.ts';
import PartnerStats from '@/features/partner/entity/PartnerStats.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/components/layout';
import {
  DataTableColumnHeader,
  DataTableFacetedFilter,
  DataTableRowActions,
  DataTableWithUrl,
  ExcelDownloadButton,
  ExcelUploadDialog,
  MobileActionDropdown,
  StatusBadge,
  SummaryCards,
  TruncatedCell,
} from '@/components/business';
import PartnerAddDialog from '@/features/partner/components/PartnerAddDialog.vue';
import PartnerEditDialog from '@/features/partner/components/PartnerEditDialog.vue';
import PartnerDeleteDialog from '@/features/partner/components/PartnerDeleteDialog.vue';
import PartnerUpdate from '@/features/partner/entity/PartnerUpdate.ts';
import { useToast } from '@/core/composables';

import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import {
  Award,
  Building2,
  Circle,
  CircleDot,
  Percent,
  Plus,
  Shield,
  Star,
  TrendingUp,
  Upload,
  Users,
} from 'lucide-vue-next';

const router = useRouter();
const toast = useToast();
const PARTNER_REPOSITORY = container.resolve(PartnerRepository);

// 요약 카드 데이터
const partnerStats = ref({
  totalPartners: 0,
  activePartners: 0,
  averageGrade: '',
  revenueContribution: 0,
});

// 엑셀 업로드 상태
const uploadDialogOpen = ref(false);
// 협력사 추가 다이얼로그 상태
const addDialogOpen = ref(false);
// 협력사 수정 관련 상태
const editDialogOpen = ref(false);
const editLoading = ref(false);
const selectedPartner = ref<PartnerSearch | null>(null);
// 협력사 삭제 관련 상태
const deleteDialogOpen = ref(false);
const deleteLoading = ref(false);

// 테이블 참조 (새로고침용)
const tableRef = ref<any>(null);

// 요약 카드 구성
const summaryCards = computed(() => [
  {
    title: '총 협력사 수',
    value: partnerStats.value.totalPartners,
    previousValue: partnerStats.value.totalPartners - 2,
    description: '전월 대비',
    icon: Building2,
    formatType: 'number' as const,
  },
  {
    title: '활성 협력사',
    value: partnerStats.value.activePartners,
    previousValue: partnerStats.value.activePartners - 1,
    description: '전월 대비',
    icon: TrendingUp,
    formatType: 'number' as const,
  },
  {
    title: '평균 등급',
    value: partnerStats.value.averageGrade,
    description: '전체 평균',
    icon: Award,
    formatType: 'text' as const,
  },
  {
    title: '매출 기여도',
    value: partnerStats.value.revenueContribution,
    previousValue: partnerStats.value.revenueContribution - 3,
    description: '전체 매출 대비',
    icon: Percent,
    formatType: 'percentage' as const,
  },
]);

// Filter options
const gradeOptions = [
  { label: 'A등급', value: 'A', icon: Star },
  { label: 'B등급', value: 'B', icon: Award },
  { label: 'C등급', value: 'C', icon: Shield },
  { label: 'D등급', value: 'D', icon: CircleDot },
  { label: 'E등급', value: 'E', icon: Circle },
];

// CEO 이름 및 영업대표 이름은 동적으로 로드된 데이터에서 추출
const partnerData = ref<PartnerSearch[]>([]);

// 동적으로 계산되는 CEO 및 영업대표 옵션
const ceoNameOptions = computed(() => {
  const uniqueCeoNames = [...new Set(partnerData.value.map(p => p.ceoName).filter(Boolean))];
  return uniqueCeoNames.map(name => ({
    label: name,
    value: name,
    icon: Users,
  }));
});

const salesRepNameOptions = computed(() => {
  const uniqueSalesRepNames = [...new Set(partnerData.value.map(p => p.salesRepName).filter(Boolean))];
  return uniqueSalesRepNames.map(name => ({
    label: name,
    value: name,
    icon: Users,
  }));
});

const columns: ColumnDef<PartnerSearch>[] = [
  {
    id: 'select',
    header: ({ table }) =>
      h(Checkbox, {
        modelValue:
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && 'indeterminate'),
        'onUpdate:modelValue': (value) => table.toggleAllPageRowsSelected(!!value),
        ariaLabel: '모두 선택',
      }),
    cell: ({ row }) =>
      h(Checkbox, {
        modelValue: row.getIsSelected(),
        'onUpdate:modelValue': (value) => row.toggleSelected(!!value),
        ariaLabel: '행 선택',
      }),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'name',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '협력사명' }),
    cell: ({ row }) => {
      return h('div', { class: 'flex flex-col w-96' }, [
        h('button', {
          class: 'font-medium text-left text-primary hover:text-primary/80 hover:underline transition-all duration-200 truncate max-w-96 cursor-pointer',
          onClick: () => onViewPartner(row.original),
        }, String(row.getValue('name') ?? '')),
        h('div', {
          class: 'text-xs text-muted-foreground truncate max-w-96',
        }, String(row.original.address ?? '')),
      ]);
    },
    enableHiding: true,
    size: 500,
    meta: { skeleton: 'title-subtitle' },
  },
  {
    accessorKey: 'ceoName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '대표자' }),
    cell: ({ row }) => h(TruncatedCell, { text: String(row.getValue('ceoName') ?? ''), maxWidth: '6rem' }),
    filterFn: (row, _id, value) => {
      return value.includes(String(row.getValue('ceoName') ?? ''));
    },
    enableHiding: true,
    size: 110,
  },
  {
    accessorKey: 'salesRepName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업대표' }),
    cell: ({ row }) => h(TruncatedCell, { text: String(row.getValue('salesRepName') ?? ''), maxWidth: '6rem' }),
    filterFn: (row, _id, value) => {
      return value.includes(String(row.getValue('salesRepName') ?? ''));
    },
    enableHiding: true,
    size: 120,
  },
  {
    accessorKey: 'salesRepPhone',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업대표 연락처' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('salesRepPhone') ?? ''),
      maxWidth: '8rem',
      className: 'text-left font-mono',
    }),
    enableHiding: true,
    size: 140,
  },
  {
    accessorKey: 'salesRepEmail',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업대표 이메일' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('salesRepEmail') ?? ''),
      maxWidth: '10rem',
      className: 'font-mono',
    }),
    enableHiding: true,
    size: 200,
  },
  {
    accessorKey: 'grade',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '등급' }),
    cell: ({ row }) => {
      const grade = row.getValue('grade') as string;
      return h(StatusBadge, {
        status: grade || 'C',
        type: 'partner',
      });
    },
    filterFn: (row, _id, value) => {
      return value.includes(String(row.getValue('grade') ?? ''));
    },
    enableHiding: true,
    size: 90,
    meta: { skeleton: 'enum-badge' },
  },
  {
    id: 'actions',
    enableHiding: false,
    size: 44,
    cell: ({ row }) => {
      return h(DataTableRowActions, {
        row: row.original,
        onEdit: (partner) => onEditPartner(partner),
        onView: (partner) => onViewPartner(partner),
        onDuplicate: (partner) => onDuplicatePartner(partner),
        onDelete: (partner) => onDeletePartner(partner),
      });
    },
  },
];

function getColumnLabel(columnId: string): string {
  switch (columnId) {
    case 'name':
      return '협력사명';
    case 'ceoName':
      return '대표자';
    case 'salesRepName':
      return '영업대표';
    case 'salesRepPhone':
      return '영업대표 연락처';
    case 'salesRepEmail':
      return '영업대표 이메일';
    case 'grade':
      return '등급';
    case 'address':
      return '주소';
    default:
      return columnId;
  }
}

// Function to fetch partner statistics
async function fetchPartnerStats() {
  try {
    // 새로운 통계 API 사용
    const stats: PartnerStats = await PARTNER_REPOSITORY.getPartnerStats();

    partnerStats.value.totalPartners = stats.totalPartners;
    partnerStats.value.activePartners = stats.activePartners;
    partnerStats.value.averageGrade = stats.averageGrade;
    partnerStats.value.revenueContribution = stats.revenueContribution;
  } catch (error) {
    console.error('Error loading partner statistics:', error);

    // API 실패 시 가데이터 설정
    partnerStats.value.totalPartners = 15; // 가데이터
    partnerStats.value.activePartners = 12; // 가데이터
    partnerStats.value.averageGrade = 'B+'; // 가데이터
    partnerStats.value.revenueContribution = 68; // 가데이터

    toast.error('협력사 통계 로드 실패', {
      description: '협력사 통계를 불러오는 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  }
}

// Function to fetch partners data
async function fetchPartners(params: Record<string, any>): Promise<PageResponse<PartnerSearch>> {
  try {
    console.log('Fetching partners with params:', params);
    const response = await PARTNER_REPOSITORY.getPartners(params);
    console.log('Partners loaded:', response.content);

    // 필터 옵션을 위해 모든 파트너 데이터를 저장
    // 페이지네이션된 데이터이므로 전체 데이터는 별도 요청이 필요하지만, 
    // 현재 페이지의 데이터라도 필터 옵션에 포함
    if (response.content && response.content.length > 0) {
      // 기존 데이터와 새 데이터를 합쳐서 중복 제거
      const existingIds = new Set(partnerData.value.map(p => p.id));
      const newPartners = response.content.filter(p => !existingIds.has(p.id));
      partnerData.value = [...partnerData.value, ...newPartners];
    }

    return response;
  } catch (error) {
    console.error('Error loading partners:', error);
    toast.error('협력사 로드 실패', {
      description: '협력사를 불러오는 중 오류가 발생했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
    throw error;
  }
}

// 필터 옵션용 전체 파트너 데이터 로드
async function loadAllPartnersForFilters() {
  try {
    // 필터 옵션을 위해 전체 데이터를 한 번에 로드 (size=1000으로 충분히 큰 값)
    const response = await PARTNER_REPOSITORY.getPartners({ size: 1000, page: 0 });
    partnerData.value = response.content || [];
  } catch (error) {
    console.error('Error loading partners for filters:', error);
    // 에러가 발생해도 필터는 계속 작동하도록 빈 배열 유지
    partnerData.value = [];
  }
}

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  fetchPartnerStats();
  loadAllPartnersForFilters();
});

// Action handlers
function onAddPartner() {
  addDialogOpen.value = true;
}

function onViewPartner(partner: PartnerSearch) {
  console.log('View partner:', partner);
  router.push(`/partners/${partner.id}`);
}

async function onEditPartner(partner: PartnerSearch) {
  try {
    console.log('Edit partner:', partner);

    // 서버에서 상세 데이터 가져오기
    const detailPartner = await PARTNER_REPOSITORY.getPartner(partner.id);
    console.log('Loaded detailed partner data:', detailPartner);

    // 상세 데이터를 상태에 저장
    selectedPartner.value = detailPartner;
    editDialogOpen.value = true;
  } catch (error) {
    console.error('협력사 정보 로드 실패:', error);
    toast.error('협력사 정보 로드 실패', {
      description: '협력사 정보를 불러오는 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  }
}

function onDuplicatePartner(partner: PartnerSearch) {
  console.log('Duplicate partner:', partner);
  toast.info('협력사 복제', {
    description: `${partner.name}의 정보를 복제합니다.`,
    position: 'bottom-right',
  });
}

function onDeletePartner(partner: PartnerSearch) {
  console.log('Delete partner:', partner);

  // 선택된 협력사 정보를 상태에 저장
  selectedPartner.value = partner;
  deleteDialogOpen.value = true;
}

// 엑셀 관련 함수들
function openUploadDialog() {
  uploadDialogOpen.value = true;
}

async function downloadCurrentData(table: any) {
  try {
    const filters = table.getState().columnFilters;
    const search = table.getState().globalFilter;

    const params: any = {};

    // 필터 조건 처리
    filters.forEach((filter: any) => {
      if (filter.value !== undefined && filter.value !== null && filter.value !== '') {
        // 배열 형태의 값 처리 (다중 선택 필터)
        if (Array.isArray(filter.value) && filter.value.length > 0) {
          // 배열의 첫 번째 값만 사용 (백엔드가 단일 값을 받을 때)
          params[filter.id] = filter.value[0];
        } else {
          params[filter.id] = filter.value;
        }
      }
    });

    // 검색 조건 추가 (name 필드로 전달)
    if (search) {
      params.name = search;
    }

    await PARTNER_REPOSITORY.downloadExcel(params);
  } catch (error) {
    console.error('Excel download error:', error);
    throw error;
  }
}

async function downloadSample() {
  try {
    await PARTNER_REPOSITORY.downloadSample();
  } catch (error) {
    console.error('Sample download error:', error);
    throw error;
  }
}

async function downloadAllData() {
  try {
    await PARTNER_REPOSITORY.downloadExcel({});
  } catch (error) {
    console.error('All data download error:', error);
    throw error;
  }
}

async function handleExcelUpload(file: File, onProgress: (progress: number) => void) {
  try {
    await PARTNER_REPOSITORY.uploadExcel(file, onProgress);
  } catch (error) {
    console.error('Excel upload error:', error);
    throw error;
  }
}

function handleUploadSuccess() {
  toast.success('엑셀 업로드 완료', {
    description: '협력사 정보가 성공적으로 업로드되었습니다.',
    position: 'bottom-right',
  });

  fetchPartnerStats();
}

function handleUploadError(error: string) {
  toast.error('엑셀 업로드 실패', {
    description: error,
    position: 'bottom-right',
  });
}

function handleAddSuccess() {
  toast.success('협력사 추가 완료', {
    description: '협력사가 성공적으로 추가되었습니다.',
    position: 'bottom-right',
  });

  // 통계 새로고침
  fetchPartnerStats();
  // 필터 옵션을 위한 전체 데이터 새로고침
  loadAllPartnersForFilters();
  // 테이블 새로고침은 DataTableWithUrl에서 자동으로 처리됨
}

function handleDownloadStart() {
  toast.info('다운로드 시작', {
    description: '엑셀 파일을 준비하고 있습니다...',
    position: 'bottom-right',
  });
}

function handleDownloadComplete() {
  toast.success('다운로드 완료', {
    description: '엑셀 파일이 성공적으로 다운로드되었습니다.',
    position: 'bottom-right',
  });
}

function handleDownloadError(error: string) {
  toast.error('다운로드 실패', {
    description: error,
    position: 'bottom-right',
  });
}

// 협력사 수정 처리
async function handleEditSubmit(partner: PartnerUpdate) {
  editLoading.value = true;

  try {
    console.log('협력사 수정 요청:', partner);

    await PARTNER_REPOSITORY.updatePartner(partner);

    toast.success('협력사 수정 완료', {
      description: `${partner.name}의 정보가 성공적으로 수정되었습니다.`,
      position: 'bottom-right',
    });

    // 다이얼로그 닫기
    editDialogOpen.value = false;
    selectedPartner.value = null;

    // 통계 새로고침
    fetchPartnerStats();

    // 테이블 데이터 새로고침
    if (tableRef.value && tableRef.value.loadData) {
      console.log('협력사 수정 완료 - 테이블 새로고침 중...');
      tableRef.value.loadData();
    }

    // 필터 옵션을 위한 전체 데이터 새로고침
    loadAllPartnersForFilters();

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

    const partnerName = selectedPartner.value?.name || '';

    await PARTNER_REPOSITORY.deletePartner(partnerId);

    toast.success('협력사 삭제 완료', {
      description: `${partnerName}이(가) 성공적으로 삭제되었습니다.`,
      position: 'bottom-right',
    });

    // 다이얼로그 닫기
    deleteDialogOpen.value = false;
    selectedPartner.value = null;

    // 통계 새로고침
    fetchPartnerStats();

    // 테이블 데이터 새로고침
    if (tableRef.value && tableRef.value.loadData) {
      console.log('협력사 삭제 완료 - 테이블 새로고침 중...');
      tableRef.value.loadData();
    }

    // 필터 옵션을 위한 전체 데이터 새로고침
    loadAllPartnersForFilters();

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
</script>

<style scoped></style>
