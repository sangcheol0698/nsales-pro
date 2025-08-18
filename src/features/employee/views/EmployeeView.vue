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
          :fetchData="fetchEmployees"
          searchPlaceholder="구성원 검색..."
          searchColumnId="name"
          :getColumnLabel="getColumnLabel"
          emptyMessage="구성원이 없습니다"
          emptyDescription="새 구성원을 추가하거나 검색 조건을 변경해보세요"
          storageKey="employee-table-visibility"
        >
          <template #filters="{ table }">
            <DataTableFacetedFilter
              v-if="table.getColumn('status')"
              :column="table.getColumn('status')"
              title="상태"
              :options="statusOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('rank')"
              :column="table.getColumn('rank')"
              title="직급"
              :options="rankOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('grade')"
              :column="table.getColumn('grade')"
              title="등급"
              :options="gradeOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('type')"
              :column="table.getColumn('type')"
              title="유형"
              :options="typeOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('departmentId') && departmentFilterOptions.length > 0"
              :column="table.getColumn('departmentId')"
              title="부서"
              :options="departmentFilterOptions"
            />

            <!-- 조직도 기반 부서 선택 버튼 -->
            <Button variant="outline" size="sm" class="h-8" @click="openOrgDialog(table)">
              부서 선택(조직도)
            </Button>
          </template>

          <template #actions="{ table }">
            <div class="flex items-center gap-2">
              <!-- 모바일: 통합 액션 드롭다운 -->
              <MobileActionDropdown
                addButtonText="구성원 추가"
                :showSalaryUpload="false"
                @download-current="() => downloadCurrentData(table)"
                @download-sample="downloadSample"
                @download-all="downloadAllData"
                @upload-excel="openUploadDialog"
                @upload-salary="() => {}"
                @add-item="onAddEmployee"
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

                <!-- 구성원 추가 버튼 -->
                <Button size="sm" class="h-8" @click="onAddEmployee">
                  <UserPlus class="mr-2 h-4 w-4" />
                  구성원 추가
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
      title="구성원 엑셀 업로드"
      description="엑셀 파일을 업로드하여 구성원 정보를 일괄 등록하세요."
      :onUpload="handleExcelUpload"
      :onDownloadSample="downloadSample"
      @success="handleUploadSuccess"
      @error="handleUploadError"
    />

    <!-- 조직도 선택 다이얼로그 -->
    <OrganizationSelectDialog
      v-model:open="orgDialogOpen"
      :withMembers="false"
      @select="handleOrgSelected"
    />

    <!-- 구성원 추가 다이얼로그 -->
    <EmployeeAddDialog
      v-model:open="addDialogOpen"
      @success="handleAddSuccess"
    />
  </SidebarLayout>
</template>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table';
import { computed, h, onMounted, ref } from 'vue';
import { container } from 'tsyringe';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository.ts';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch.ts';
import EmployeeStats from '@/features/employee/entity/EmployeeStats.ts';
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
import OrganizationSelectDialog from '@/features/organization/components/OrganizationSelectDialog.vue';
import EmployeeAddDialog from '@/features/employee/components/EmployeeAddDialog.vue';
import { useDepartments, useToast } from '@/core/composables';

import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Award, Clock, Star, TrendingUp, Upload, User, UserCheck, UserPlus, Users, UserX } from 'lucide-vue-next';

const toast = useToast();
const EMPLOYEE_REPOSITORY = container.resolve(EmployeeRepository);
const { departmentOptions, fetchDepartments } = useDepartments();

// 부서 필터 옵션: value를 문자열로 매핑하여 필터 UI와 동기화되도록 함
const departmentFilterOptions = computed(() =>
  departmentOptions.value.map((opt: any) => ({ ...opt, value: String(opt.value) })),
);

// 요약 카드 데이터
const employeeStats = ref({
  totalEmployees: 0,
  activeEmployees: 0,
  newHires: 0,
  averageTenure: 0,
});

// 엑셀 업로드 상태
const uploadDialogOpen = ref(false);
// 조직도 선택 상태
const orgDialogOpen = ref(false);
// 구성원 추가 다이얼로그 상태
const addDialogOpen = ref(false);
const tableRef = ref<any>(null);

// 요약 카드 구성
const summaryCards = computed(() => [
  {
    title: '총 구성원 수',
    value: employeeStats.value.totalEmployees,
    previousValue: employeeStats.value.totalEmployees - 5, // 임시로 -5로 설정
    description: '전월 대비',
    icon: Users,
    formatType: 'number' as const,
  },
  {
    title: '재직자 수',
    value: employeeStats.value.activeEmployees,
    previousValue: employeeStats.value.activeEmployees - 2, // 임시로 -2로 설정
    description: '전월 대비',
    icon: UserCheck,
    formatType: 'number' as const,
  },
  {
    title: '신규 입사자',
    value: employeeStats.value.newHires,
    previousValue: employeeStats.value.newHires - 1, // 임시로 -1로 설정
    description: '이번 달',
    icon: TrendingUp,
    formatType: 'number' as const,
  },
  {
    title: '평균 근속 기간',
    value: employeeStats.value.averageTenure,
    previousValue: employeeStats.value.averageTenure - 0.2, // 임시로 -0.2로 설정
    description: '전체 평균',
    icon: Award,
    formatType: 'number' as const,
  },
]);

// Filter options (백엔드 enum에 맞춤)
const statusOptions = [
  { label: '재직', value: '재직', icon: UserCheck },
  { label: '휴직', value: '휴직', icon: Clock },
  { label: '퇴사', value: '퇴사', icon: UserX },
];

const rankOptions = [
  { label: '사원', value: '사원' },
  { label: '선임', value: '선임' },
  { label: '책임', value: '책임' },
  { label: '팀장', value: '팀장' },
  { label: '수석', value: '수석' },
  { label: '이사', value: '이사' },
  { label: '기술이사', value: '기술이사' },
  { label: '상무', value: '상무' },
  { label: '부사장', value: '부사장' },
  { label: '사장', value: '사장' },
];

const gradeOptions = [
  { label: '초급', value: '초급', icon: Star },
  { label: '중급', value: '중급', icon: Star },
  { label: '고급', value: '고급', icon: Star },
  { label: '특급', value: '특급', icon: Star },
];

const typeOptions = [
  { label: '정직원', value: '정직원', icon: User },
  { label: '프리랜서', value: '프리랜서', icon: UserCheck },
  { label: '외주', value: '외주', icon: Users },
];

// departmentOptions는 이제 useDepartments composable에서 제공됨

const columns: ColumnDef<EmployeeSearch>[] = [
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
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '이름' }),
    cell: ({ row }) => {
      const joinDate = new Date(row.original.joinDate);
      const leaveDate = row.original.leaveDate ? new Date(row.original.leaveDate) : null;
      const today = new Date();

      let tenureText = '';

      if (leaveDate) {
        // 퇴사한 경우
        const workingTime = leaveDate.getTime() - joinDate.getTime();
        const workingDays = Math.floor(workingTime / (1000 * 60 * 60 * 24));

        if (workingDays < 365) {
          tenureText = `근무 ${workingDays}일`;
        } else {
          const years = Math.floor(workingDays / 365);
          const months = Math.floor((workingDays % 365) / 30);
          if (months > 0) {
            tenureText = `근무 ${years}년 ${months}개월`;
          } else {
            tenureText = `근무 ${years}년`;
          }
        }
      } else {
        // 재직 중인 경우
        const diffTime = today.getTime() - joinDate.getTime();
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays < 365) {
          tenureText = `재직 ${diffDays}일`;
        } else {
          const years = Math.floor(diffDays / 365);
          const months = Math.floor((diffDays % 365) / 30);
          if (months > 0) {
            tenureText = `재직 ${years}년 ${months}개월`;
          } else {
            tenureText = `재직 ${years}년`;
          }
        }
      }

      return h('div', { class: 'flex flex-col w-32' }, [
        h(TruncatedCell, { text: String(row.getValue('name') ?? ''), maxWidth: '8rem', className: 'font-medium' }),
        h(TruncatedCell, {
          text: tenureText,
          maxWidth: '8rem',
          className: `text-xs ${leaveDate ? 'text-gray-500' : 'text-muted-foreground'}`,
        }),
      ]);
    },
    enableHiding: true,
    size: 140,
    meta: { skeleton: 'title-subtitle' },
  },
  {
    accessorKey: 'teamName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '부서' }),
    cell: ({ row }) => h(TruncatedCell, { text: String(row.getValue('teamName') ?? ''), maxWidth: '8rem' }),
    enableHiding: true,
    size: 140,
  },
  {
    accessorKey: 'departmentId',
    header: () => null,
    cell: () => null,
    filterFn: (row, _id, value) => {
      return value.includes(row.original.departmentId?.toString() || '');
    },
    enableHiding: false,
    enableSorting: false,
    size: 0,
    meta: {
      isFilterOnly: true, // 필터링 전용 컬럼 표시
    },
  },
  {
    accessorKey: 'rank',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '직급' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('rank') ?? ''),
      maxWidth: '5rem',
      className: 'text-left',
    }),
    filterFn: (row, _id, value) => {
      return value.includes(row.getValue('rank'));
    },
    enableHiding: true,
    size: 100,
  },
  {
    accessorKey: 'joinDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '입사일' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('joinDate') ?? ''),
      maxWidth: '7rem',
      className: 'text-left',
    }),
    enableHiding: true,
    size: 120,
  },
  {
    accessorKey: 'grade',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '등급' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('grade') ?? ''),
      maxWidth: '4rem',
      className: 'text-left',
    }),
    filterFn: (row, _id, value) => {
      return value.includes(row.getValue('grade'));
    },
    enableHiding: true,
    size: 80,
  },
  {
    accessorKey: 'type',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '유형' }),
    cell: ({ row }) => h(TruncatedCell, {
      text: String(row.getValue('type') ?? ''),
      maxWidth: '5rem',
      className: 'text-left',
    }),
    filterFn: (row, _id, value) => {
      return value.includes(row.getValue('type'));
    },
    enableHiding: true,
    size: 100,
  },
  {
    accessorKey: 'status',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '상태' }),
    cell: ({ row }) => {
      const status = row.getValue('status') as string;
      return h(StatusBadge, {
        status: status || '퇴사',
        type: 'employee',
      });
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id));
    },
    enableHiding: true,
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      return h(DataTableRowActions, {
        row: row.original,
        onEdit: (employee) => onEditEmployee(employee),
        onView: (employee) => onViewEmployee(employee),
        onDuplicate: (employee) => onDuplicateEmployee(employee),
        onDelete: (employee) => onDeleteEmployee(employee),
      });
    },
  },
];

function getColumnLabel(columnId: string): string {
  switch (columnId) {
    case 'name':
      return '이름';
    case 'email':
      return '이메일';
    case 'teamName':
      return '부서';
    case 'rank':
      return '직급';
    case 'grade':
      return '등급';
    case 'type':
      return '유형';
    case 'joinDate':
      return '입사일';
    case 'status':
      return '재직상태';
    case 'code':
      return '사번';
    default:
      return columnId;
  }
}

// fetchDepartments는 이제 useDepartments composable에서 제공됨

// Function to fetch employee statistics
async function fetchEmployeeStats() {
  try {
    // 새로운 통계 API 사용
    const stats: EmployeeStats = await EMPLOYEE_REPOSITORY.getEmployeeStats();

    employeeStats.value.totalEmployees = stats.totalEmployees;
    employeeStats.value.activeEmployees = stats.activeEmployees;
    employeeStats.value.newHires = stats.newHires;
    employeeStats.value.averageTenure = stats.averageTenure;
  } catch (error) {
    console.error('Error loading employee statistics:', error);

    // API 실패 시 가데이터 설정
    employeeStats.value.totalEmployees = 25; // 가데이터
    employeeStats.value.activeEmployees = 23; // 가데이터
    employeeStats.value.newHires = 3; // 가데이터
    employeeStats.value.averageTenure = 3.2; // 가데이터 (년 단위)

    // 에러 토스트는 개발 중에만 표시 (실제 서비스에서는 제거)
    // toast.error('구성원 통계 로드 실패', {
    //   description: '구성원 통계를 불러오는 중 오류가 발생했습니다.',
    //   position: 'bottom-right',
    // });
  }
}

// Function to fetch employees data
async function fetchEmployees(params: Record<string, any>): Promise<PageResponse<EmployeeSearch>> {
  try {
    console.log('Fetching employees with params:', params);
    const response = await EMPLOYEE_REPOSITORY.getEmployees(params);
    console.log('Employees loaded:', response.content);
    return response;
  } catch (error) {
    console.error('Error loading employees:', error);
    toast.error('구성원 로드 실패', {
      description: '구성원을 불러오는 중 오류가 발생했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
    throw error;
  }
}

// 컴포넌트 마운트 시 데이터 로드
onMounted(() => {
  fetchEmployeeStats();
  fetchDepartments();
});

// Action handlers
function onAddEmployee() {
  addDialogOpen.value = true;
}

function onViewEmployee(employee: EmployeeSearch) {
  console.log('View employee:', employee);
  toast.info('구성원 상세보기', {
    description: `${employee.name}의 상세 정보를 확인합니다.`,
    position: 'bottom-right',
  });
}

function onEditEmployee(employee: EmployeeSearch) {
  console.log('Edit employee:', employee);
  toast.info('구성원 편집', {
    description: `${employee.name}의 정보를 편집합니다.`,
    position: 'bottom-right',
  });
}

function onDuplicateEmployee(employee: EmployeeSearch) {
  console.log('Duplicate employee:', employee);
  toast.info('구성원 복제', {
    description: `${employee.name}의 정보를 복제합니다.`,
    position: 'bottom-right',
  });
}

function onDeleteEmployee(employee: EmployeeSearch) {
  console.log('Delete employee:', employee);
  toast.warning('구성원 삭제', {
    description: `${employee.name}을(를) 삭제하시겠습니까?`,
    position: 'bottom-right',
  });
}

// 엑셀 관련 함수들
function openUploadDialog() {
  uploadDialogOpen.value = true;
}

async function downloadCurrentData(table: any) {
  try {
    // 현재 테이블의 필터 및 검색 조건을 가져와서 전달
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

    await EMPLOYEE_REPOSITORY.downloadExcel(params);
  } catch (error) {
    console.error('Excel download error:', error);
    throw error;
  }
}

async function downloadSample() {
  try {
    await EMPLOYEE_REPOSITORY.downloadSample();
  } catch (error) {
    console.error('Sample download error:', error);
    throw error;
  }
}

async function downloadAllData() {
  try {
    await EMPLOYEE_REPOSITORY.downloadExcel({});
  } catch (error) {
    console.error('All data download error:', error);
    throw error;
  }
}

async function handleExcelUpload(file: File, onProgress: (progress: number) => void) {
  try {
    await EMPLOYEE_REPOSITORY.uploadExcel(file, onProgress);
  } catch (error) {
    console.error('Excel upload error:', error);
    throw error;
  }
}

function handleUploadSuccess() {
  toast.success('엑셀 업로드 완료', {
    description: '구성원 정보가 성공적으로 업로드되었습니다.',
    position: 'bottom-right',
  });

  // 통계 및 테이블 데이터 새로고침
  fetchEmployeeStats();
  // 테이블 새로고침은 DataTableWithUrl에서 자동으로 처리됨
}

function handleUploadError(error: string) {
  toast.error('엑셀 업로드 실패', {
    description: error,
    position: 'bottom-right',
  });
}

function handleAddSuccess() {
  toast.success('구성원 추가 완료', {
    description: '구성원이 성공적으로 추가되었습니다.',
    position: 'bottom-right',
  });

  // 통계 및 테이블 데이터 새로고침
  fetchEmployeeStats();
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

// 조직도 다이얼로그 열기 (filters 슬롯의 table을 보관)
function openOrgDialog(table: any) {
  tableRef.value = { table };
  orgDialogOpen.value = true;
}

// 조직도에서 부서 선택 시 컬럼 필터에 적용
function handleOrgSelected(node: { departmentId?: number }) {
  if (!node?.departmentId) return;
  const table = tableRef.value?.table;
  if (!table) return;
  const currentFilters = table.getState().columnFilters.filter((f: any) => f.id !== 'departmentId');
  const newFilters = [
    ...currentFilters,
    { id: 'departmentId', value: [String(node.departmentId)] },
  ];
  table.setColumnFilters(newFilters);
}
</script>

<style scoped></style>