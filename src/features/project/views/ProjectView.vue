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
          :fetchData="fetchProjects"
          searchPlaceholder="프로젝트 검색..."
          searchColumnId="name"
          :getColumnLabel="getColumnLabel"
          emptyMessage="프로젝트가 없습니다"
          emptyDescription="새 프로젝트를 추가하거나 검색 조건을 변경해보세요"
          storageKey="project-table-visibility"
        >
          <template #filters="{ table }">
            <!-- 날짜 검색 유형 선택 -->
            <Select v-model="searchType">
              <SelectTrigger class="w-32 h-8">
                <SelectValue placeholder="날짜 유형" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="option in searchTypeOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </SelectItem>
              </SelectContent>
            </Select>

            <!-- 날짜 범위 필터 -->
            <DateRangeFilter
              v-model="dateRange"
              placeholder="날짜 범위 선택"
            />

            <DataTableFacetedFilter
              v-if="table.getColumn('type')"
              :column="table.getColumn('type')"
              title="프로젝트 유형"
              :options="typeOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('status')"
              :column="table.getColumn('status')"
              title="상태"
              :options="statusOptions"
            />
          </template>

          <template #actions="{ table }">
            <div class="flex items-center gap-2">
              <!-- 모바일: 통합 액션 드롭다운 -->
              <MobileActionDropdown
                addButtonText="프로젝트 추가"
                @download-current="() => downloadCurrentData(table)"
                @download-sample="downloadSample"
                @download-all="downloadAllData"
                @upload-excel="openUploadDialog"
                @add-item="onAddProject"
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

                <!-- 프로젝트 추가 버튼 -->
                <Button size="sm" class="h-8" @click="onAddProject">
                  <Plus class="mr-2 h-4 w-4" />
                  프로젝트 추가
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
      title="프로젝트 엑셀 업로드"
      description="엑셀 파일을 업로드하여 프로젝트 정보를 일괄 등록하세요."
      :onUpload="handleExcelUpload"
      :onDownloadSample="downloadSample"
      @success="handleUploadSuccess"
      @error="handleUploadError"
    />

    <!-- 프로젝트 추가 다이얼로그 -->
    <ProjectAddDialog
      v-model:open="addDialogOpen"
      @success="handleProjectCreateSuccess"
    />

    <!-- 프로젝트 수정 다이얼로그 -->
    <ProjectEditDialog
      v-model:open="editDialogOpen"
      :project-id="selectedProjectId"
      @submit="handleEditSubmit"
    />

    <!-- 프로젝트 삭제 다이얼로그 -->
    <ProjectDeleteDialog
      v-model:open="deleteDialogOpen"
      :loading="deleteLoading"
      :project="selectedProject"
      @confirm="handleDeleteConfirm"
    />
  </SidebarLayout>
</template>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table';
import { computed, h, nextTick, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { container } from 'tsyringe';
import ProjectRepository from '@/features/project/repository/ProjectRepository.ts';
import ProjectSearch from '@/features/project/entity/ProjectSearch.ts';
import ProjectStats from '@/features/project/entity/ProjectStats.ts';
import ProjectCreate from '@/features/project/entity/ProjectCreate.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import ProjectAddDialog from '@/features/project/components/ProjectAddDialog.vue';
import ProjectEditDialog from '@/features/project/components/ProjectEditDialog.vue';
import ProjectDeleteDialog from '@/features/project/components/ProjectDeleteDialog.vue';
import ProjectUpdate from '@/features/project/entity/ProjectUpdate.ts';
import { SidebarLayout } from '@/components/layout';
import {
  DataTableColumnHeader,
  DataTableFacetedFilter,
  DataTableRowActions,
  DataTableWithUrl,
  DateRangeFilter,
  ExcelDownloadButton,
  ExcelUploadDialog,
  MobileActionDropdown,
  StatusBadge,
  SummaryCards,
  TruncatedCell,
} from '@/components/business';
import { useToast } from '@/core/composables';

import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import {
  Briefcase,
  CalendarClock,
  CheckCircle,
  Clock,
  DollarSign,
  Factory,
  FolderOpen,
  Plus,
  TrendingUp,
  Upload,
} from 'lucide-vue-next';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const router = useRouter();
const toast = useToast();
const PROJECT_REPOSITORY = container.resolve(ProjectRepository);

// 요약 카드 데이터
const projectStats = ref({
  totalProjects: 0,
  activeProjects: 0,
  totalValue: 0,
  completionRate: 0,
});

// 엑셀 업로드 상태
const uploadDialogOpen = ref(false);

// 프로젝트 추가 다이얼로그 상태
const addDialogOpen = ref(false);
// 프로젝트 수정 관련 상태
const editDialogOpen = ref(false);
const selectedProjectId = ref<number | null>(null);
// 프로젝트 삭제 관련 상태
const deleteDialogOpen = ref(false);
const deleteLoading = ref(false);
const selectedProject = ref<ProjectSearch | null>(null);

// 날짜 필터 상태
const searchType = ref('계약일자');
const dateRange = ref<{ start?: Date; end?: Date } | null>(null);

// 날짜 검색 유형 옵션
const searchTypeOptions = [
  { label: '계약일자', value: '계약일자' },
  { label: '시작일자', value: '시작일자' },
  { label: '종료일자', value: '종료일자' },
];

// 요약 카드 구성
const summaryCards = computed(() => [
  {
    title: '총 프로젝트 수',
    value: projectStats.value.totalProjects,
    previousValue: projectStats.value.totalProjects - 3,
    description: '전월 대비',
    icon: FolderOpen,
    formatType: 'number' as const,
  },
  {
    title: '진행중 프로젝트',
    value: projectStats.value.activeProjects,
    previousValue: projectStats.value.activeProjects - 1,
    description: '전월 대비',
    icon: TrendingUp,
    formatType: 'number' as const,
  },
  {
    title: '총 프로젝트 가치',
    value: projectStats.value.totalValue,
    previousValue: projectStats.value.totalValue * 0.9,
    description: '전월 대비',
    icon: DollarSign,
    formatType: 'currency' as const,
  },
  {
    title: '완료율',
    value: projectStats.value.completionRate,
    previousValue: projectStats.value.completionRate - 5,
    description: '전체 평균',
    icon: CheckCircle,
    formatType: 'percentage' as const,
  },
]);

// Function to fetch project statistics
async function fetchProjectStats() {
  try {
    // 새로운 통계 API 사용
    const stats: ProjectStats = await PROJECT_REPOSITORY.getProjectStats();

    projectStats.value.totalProjects = stats.totalProjects;
    projectStats.value.activeProjects = stats.activeProjects;
    projectStats.value.totalValue = stats.totalValue;
    projectStats.value.completionRate = stats.completionRate;
  } catch (error) {
    console.error('Error loading project statistics:', error);

    // API 실패 시 가데이터 설정
    projectStats.value.totalProjects = 12; // 가데이터
    projectStats.value.activeProjects = 8; // 가데이터
    projectStats.value.totalValue = 3500000000; // 가데이터
    projectStats.value.completionRate = 85; // 가데이터

    toast.error('프로젝트 통계 로드 실패', {
      description: '프로젝트 통계를 불러오는 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  }
}

// Filter options
const typeOptions = [
  { label: 'SI', value: 'SI', icon: Briefcase },
  { label: 'SM', value: 'SM', icon: Factory },
];

const statusOptions = [
  { label: '진행중', value: '진행중', icon: Clock },
  { label: '완료', value: '완료', icon: CheckCircle },
  { label: '예약', value: '예약', icon: CalendarClock },
];

const columns: ColumnDef<ProjectSearch>[] = [
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
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '프로젝트' }),
    cell: ({ row }) => {
      return h('div', { class: 'flex flex-col w-96' }, [
        h('button', {
          class: 'font-medium text-left text-primary hover:text-primary/80 hover:underline transition-all duration-200 truncate max-w-96 cursor-pointer',
          onClick: () => onViewProject(row.original),
        }, String(row.getValue('name') ?? '')),
        h('div', {
          class: 'text-xs text-muted-foreground truncate max-w-96',
        }, String(row.original.code ?? '')),
      ]);
    },
    enableHiding: true,
    enableSorting: true, // 프로젝트명은 정렬 가능
    size: 500,
    meta: { skeleton: 'title-subtitle' },
  },
  {
    accessorKey: 'type',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '유형' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('type') ?? ''),
      maxWidth: '5rem',
      className: 'font-medium text-left',
    }),
    filterFn: (row, _id, value) => {
      return value.includes(String(row.getValue('type') ?? ''));
    },
    enableHiding: true,
    enableSorting: true, // 유형은 정렬 가능
    size: 90,
  },
  {
    accessorKey: 'period',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '기간' }),
    cell: ({ row }) => {
      const startDate = row.original.startDate || '-';
      const endDate = row.original.endDate || '';
      const separator = startDate !== '-' && endDate ? ' ~ ' : '';
      const periodText = String(startDate) + separator + String(endDate);

      return h(TruncatedCell, { text: periodText, maxWidth: '14rem', className: 'text-left' });
    },
    enableHiding: true,
    enableSorting: false, // 복합 필드는 정렬 불가
    size: 240,
  },
  {
    accessorKey: 'contractDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '계약일' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('contractDate') ?? ''),
      maxWidth: '7rem',
      className: 'text-left',
    }),
    enableHiding: true,
    enableSorting: true, // 계약일은 정렬 가능
    size: 120,
  },
  {
    accessorKey: 'contractAmount',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '계약금액', align: 'right' }),
    cell: ({ row }) => {
      const amount = row.getValue('contractAmount') as number;
      const formattedAmount = amount ? amount.toLocaleString() + '원' : '-';

      return h(TruncatedCell, { text: formattedAmount, maxWidth: '8rem', className: 'text-right' });
    },
    enableHiding: true,
    enableSorting: true, // 계약금액은 정렬 가능
    size: 140,
  },
  {
    accessorKey: 'mainCompany',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '주관사' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('mainCompany') ?? ''),
      maxWidth: '10rem',
      className: 'text-left',
    }),
    enableHiding: true,
    enableSorting: true, // 주관사는 정렬 가능
    size: 160,
  },
  {
    accessorKey: 'clientCompany',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '고객사' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('clientCompany') ?? ''),
      maxWidth: '10rem',
      className: 'text-left',
    }),
    enableHiding: true,
    enableSorting: true, // 고객사는 정렬 가능
    size: 160,
  },
  {
    accessorKey: 'status',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '상태' }),
    cell: ({ row }) => {
      const status = row.getValue('status') as string;
      return h(StatusBadge, {
        status: status || '진행중',
        type: 'project',
      });
    },
    filterFn: (row, _id, value) => {
      return value.includes(String(row.getValue('status') ?? ''));
    },
    enableHiding: true,
    enableSorting: false, // 상태는 정렬 불가
    size: 100,
    meta: { skeleton: 'enum-badge' },
  },
  {
    id: 'actions',
    enableHiding: false,
    enableSorting: false, // 액션 버튼은 정렬 불가
    size: 44,
    cell: ({ row }) => {
      return h(DataTableRowActions, {
        row: row.original,
        onEdit: (project) => onEditProject(project),
        onView: (project) => onViewProject(project),
        onDuplicate: (project) => onDuplicateProject(project),
        onDelete: (project) => onDeleteProject(project),
      });
    },
  },
];

function getColumnLabel(columnId: string): string {
  switch (columnId) {
    case 'name':
      return '프로젝트';
    case 'type':
      return '유형';
    case 'period':
      return '기간';
    case 'contractDate':
      return '계약일';
    case 'contractAmount':
      return '계약금액';
    case 'mainCompany':
      return '주관사';
    case 'clientCompany':
      return '고객사';
    case 'status':
      return '상태';
    default:
      return columnId;
  }
}

// 테이블 인스턴스 참조
const tableRef = ref<any>(null);

// 날짜 범위 변경 핸들러
function handleDateRangeChange(range: any) {
  dateRange.value = range as { start?: Date; end?: Date } | null;

  // 테이블의 컬럼 필터로 날짜 범위 설정
  if (tableRef.value?.table) {
    const table = tableRef.value.table;

    // 기존 날짜 관련 필터 제거
    const currentFilters = table.getState().columnFilters.filter((filter: any) =>
      !['dateRange', 'searchType'].includes(filter.id),
    );

    // 새로운 필터 추가
    const newFilters = [...currentFilters];

    if (range && range.start && range.end) {
      newFilters.push({
        id: 'dateRange',
        value: range,
      });
    }

    if (searchType.value) {
      newFilters.push({
        id: 'searchType',
        value: searchType.value,
      });
    }

    table.setColumnFilters(newFilters);
  }
}

// Function to fetch projects data
async function fetchProjects(params: Record<string, any>): Promise<PageResponse<ProjectSearch>> {
  try {
    console.log('Fetching projects with params:', params);
    const response = await PROJECT_REPOSITORY.getProjects(params);
    console.log('Projects loaded:', response.content);
    return response;
  } catch (error) {
    console.error('Error loading projects:', error);
    toast.error('프로젝트 로드 실패', {
      description: '프로젝트를 불러오는 중 오류가 발생했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
    throw error;
  }
}

// 테이블 필터에서 UI 상태 복원
function restoreUIStateFromTable() {
  if (!tableRef.value?.table) return;

  const table = tableRef.value.table;
  const columnFilters = table.getState().columnFilters;

  // dateRange 필터 복원
  const dateRangeFilter = columnFilters.find((f: any) => f.id === 'dateRange');
  if (dateRangeFilter && dateRangeFilter.value) {
    dateRange.value = dateRangeFilter.value;
  } else {
    // 필터가 없으면 초기화
    dateRange.value = null;
  }

  // searchType 필터 복원
  const searchTypeFilter = columnFilters.find((f: any) => f.id === 'searchType');
  if (searchTypeFilter && searchTypeFilter.value) {
    searchType.value = searchTypeFilter.value;
  } else {
    // 필터가 없으면 기본값으로 초기화
    searchType.value = '계약일자';
  }
}

// searchType 변경 감지
watch(searchType, () => {
  if (dateRange.value && tableRef.value?.table) {
    handleDateRangeChange(dateRange.value);
  }
});

// 날짜 범위 변경 감지하여 필터 적용
watch(dateRange, (val) => {
  handleDateRangeChange(val);
});

// 테이블 필터 변경 감지하여 UI 상태 동기화
watch(() => tableRef.value?.table?.getState().columnFilters, () => {
  restoreUIStateFromTable();
}, { deep: true });

// 컴포넌트 마운트 시 통계 데이터 로드
onMounted(() => {
  fetchProjectStats();

  // 테이블이 준비되면 UI 상태 복원
  nextTick(() => {
    setTimeout(() => {
      restoreUIStateFromTable();
    }, 100);
  });
});

// Action handlers
function onAddProject() {
  addDialogOpen.value = true;
}

function onViewProject(project: ProjectSearch) {
  console.log('View project:', project);
  router.push(`/projects/${project.id}`);
}

function onEditProject(project: ProjectSearch) {
  console.log('Edit project:', project);
  selectedProjectId.value = project.id;
  editDialogOpen.value = true;
}

function onDuplicateProject(project: ProjectSearch) {
  console.log('Duplicate project:', project);
  toast.info('프로젝트 복제', {
    description: `${project.name}의 정보를 복제합니다.`,
    position: 'bottom-right',
  });
}

function onDeleteProject(project: ProjectSearch) {
  console.log('Delete project:', project);

  // 선택된 프로젝트 정보를 상태에 저장
  selectedProject.value = project;
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

    // 필터 조건 처리 (DataTableWithUrl과 동일한 로직 사용)
    filters.forEach((filter: any) => {
      if (filter.value !== undefined && filter.value !== null && filter.value !== '') {
        // 배열 형태의 값 처리 (다중 선택 필터)
        if (Array.isArray(filter.value) && filter.value.length > 0) {
          params[filter.id] = filter.value.join(',');
        }
        // 날짜 범위 값 처리 
        else if (typeof filter.value === 'object' && filter.value.start) {
          if (filter.id === 'dateRange') {
            params.startDate = formatDateForAPI(filter.value.start);
            if (filter.value.end) {
              params.endDate = formatDateForAPI(filter.value.end);
            }
          }
        }
        // 일반 값 처리
        else {
          params[filter.id] = filter.value;
        }
      }
    });

    // 검색 조건 추가 (name 필드로 전달)
    if (search) {
      params.name = search;
    }

    await PROJECT_REPOSITORY.downloadExcel(params);
  } catch (error) {
    console.error('Excel download error:', error);
    throw error;
  }
}

async function downloadSample() {
  try {
    await PROJECT_REPOSITORY.downloadSample();
  } catch (error) {
    console.error('Sample download error:', error);
    throw error;
  }
}

async function downloadAllData() {
  try {
    await PROJECT_REPOSITORY.downloadExcel({});
  } catch (error) {
    console.error('All data download error:', error);
    throw error;
  }
}

async function handleExcelUpload(file: File, onProgress: (progress: number) => void) {
  try {
    await PROJECT_REPOSITORY.uploadExcel(file, onProgress);
  } catch (error) {
    console.error('Excel upload error:', error);
    throw error;
  }
}

function handleUploadSuccess() {
  toast.success('엑셀 업로드 완료', {
    description: '프로젝트 정보가 성공적으로 업로드되었습니다.',
    position: 'bottom-right',
  });

  fetchProjectStats();
}

function handleUploadError(error: string) {
  toast.error('엑셀 업로드 실패', {
    description: error,
    position: 'bottom-right',
  });
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

// 프로젝트 생성 성공 핸들러
async function handleProjectCreateSuccess(project: ProjectCreate) {
  try {
    await PROJECT_REPOSITORY.createProject(project);

    toast.success('프로젝트 생성 완료', {
      description: `${project.name} 프로젝트가 성공적으로 생성되었습니다.`,
      position: 'bottom-right',
    });

    // 다이얼로그 닫기
    addDialogOpen.value = false;

    // 통계 및 테이블 데이터 새로고침
    fetchProjectStats();
    // 테이블 새로고침은 DataTableWithUrl에서 자동으로 처리됨
  } catch (error) {
    console.error('Project creation error:', error);
    toast.error('프로젝트 생성 실패', {
      description: '프로젝트 생성 중 오류가 발생했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
  }
}

// API용 날짜 포맷팅 함수
function formatDateForAPI(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// 프로젝트 수정 처리
const editLoading = ref(false);

async function handleEditSubmit(project: ProjectUpdate) {
  editLoading.value = true;

  try {
    console.log('프로젝트 수정 요청:', project);

    await PROJECT_REPOSITORY.updateProject(project);

    toast.success('프로젝트 수정 완료', {
      description: `${project.name}의 정보가 성공적으로 수정되었습니다.`,
      position: 'bottom-right',
    });

    // 다이얼로그 닫기
    editDialogOpen.value = false;
    selectedProjectId.value = null;

    // 통계 새로고침
    fetchProjectStats();

    // 테이블 데이터 새로고침
    if (tableRef.value && tableRef.value.loadData) {
      console.log('프로젝트 수정 완료 - 테이블 새로고침 중...');
      tableRef.value.loadData();
    }

  } catch (error: any) {
    console.error('프로젝트 수정 실패:', error);

    let errorMessage = '프로젝트 수정 중 오류가 발생했습니다.';
    if (error?.message?.includes('modifiedDateTime')) {
      errorMessage = '다른 사용자가 이미 수정했습니다. 새로고침 후 다시 시도해주세요.';
    }

    toast.error('프로젝트 수정 실패', {
      description: errorMessage,
      position: 'bottom-right',
    });
  } finally {
    editLoading.value = false;
  }
}

// 프로젝트 삭제 처리
async function handleDeleteConfirm(projectId: number) {
  deleteLoading.value = true;

  try {
    console.log('프로젝트 삭제 요청:', projectId);

    const projectName = selectedProject.value?.name || '';

    await PROJECT_REPOSITORY.deleteProject(projectId);

    toast.success('프로젝트 삭제 완료', {
      description: `${projectName}이(가) 성공적으로 삭제되었습니다.`,
      position: 'bottom-right',
    });

    // 다이얼로그 닫기
    deleteDialogOpen.value = false;
    selectedProject.value = null;

    // 통계 새로고침
    fetchProjectStats();

    // 테이블 데이터 새로고침
    if (tableRef.value && tableRef.value.loadData) {
      console.log('프로젝트 삭제 완료 - 테이블 새로고침 중...');
      tableRef.value.loadData();
    }

  } catch (error: any) {
    console.error('프로젝트 삭제 실패:', error);

    toast.error('프로젝트 삭제 실패', {
      description: '프로젝트 삭제 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  } finally {
    deleteLoading.value = false;
  }
}
</script>

<style scoped></style>
