<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <!-- 요약 카드 -->
        <SummaryCards :cards="summaryCards" />

        <!-- 데이터 테이블 -->
        <DataTableWithUrl
          :columns="columns"
          :fetchData="fetchSales"
          searchPlaceholder="프로젝트명 검색..."
          searchColumnId="projectName"
          :getColumnLabel="getColumnLabel"
          emptyMessage="매출 데이터가 없습니다"
          emptyDescription="새 매출을 추가하거나 검색 조건을 변경해보세요"
          storageKey="sales-table-visibility"
        >
          <template #filters="{ table }">
            <DataTableFacetedFilter
              v-if="table.getColumn('year')"
              :column="table.getColumn('year')"
              title="연도"
              :options="yearOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('departmentType')"
              :column="table.getColumn('departmentType')"
              title="부서 타입"
              :options="departmentTypeOptions"
            />
          </template>

        </DataTableWithUrl>
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table';
import { computed, h, onMounted, ref } from 'vue';
import { container } from 'tsyringe';
import SalesRepository from '@/features/sales/repository/SalesRepository.ts';
import type { SalesSearch } from '@/features/sales/entity/SalesSearch.ts';
import SalesStats from '@/features/sales/entity/SalesStats.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/components/layout';
import {
  DataTableColumnHeader,
  DataTableFacetedFilter,
  DataTableRowActions,
  DataTableWithUrl,
  SummaryCards,
  TruncatedCell,
} from '@/components/business';
import { useToast } from '@/core/composables';

import { Checkbox } from '@/components/ui/checkbox';
import { AlertCircle, Building2, Calendar, CheckCircle, Clock, DollarSign, User, Users } from 'lucide-vue-next';

const toast = useToast();
const SALES_REPOSITORY = container.resolve(SalesRepository);

// 요약 카드 데이터
const salesStats = ref({
  totalRevenue: 0,
  collectedRevenue: 0,
  outstandingAmount: 0,
  averageCollectionPeriod: 0,
});

// 요약 카드 구성
const summaryCards = computed(() => [
  {
    title: '총 매출액',
    value: salesStats.value.totalRevenue,
    previousValue: salesStats.value.totalRevenue * 0.9, // 임시로 10% 증가로 설정
    description: '전월 대비',
    icon: DollarSign,
    formatType: 'currency' as const,
  },
  {
    title: '수금완료 매출',
    value: salesStats.value.collectedRevenue,
    previousValue: salesStats.value.collectedRevenue * 0.85, // 임시로 15% 증가로 설정
    description: '전월 대비',
    icon: CheckCircle,
    formatType: 'currency' as const,
  },
  {
    title: '미수금',
    value: salesStats.value.outstandingAmount,
    previousValue: salesStats.value.outstandingAmount * 1.2, // 임시로 20% 감소로 설정
    description: '전월 대비',
    icon: AlertCircle,
    formatType: 'currency' as const,
  },
  {
    title: '평균 수금 기간',
    value: salesStats.value.averageCollectionPeriod,
    previousValue: salesStats.value.averageCollectionPeriod + 5, // 임시로 5일 단축으로 설정
    description: '일 단위',
    icon: Clock,
    formatType: 'number' as const,
  },
]);

// Filter options
const yearOptions = [
  { label: '2025', value: '2025', icon: Calendar },
  { label: '2024', value: '2024', icon: Calendar },
  { label: '2023', value: '2023', icon: Calendar },
  { label: '2022', value: '2022', icon: Calendar },
];

const departmentTypeOptions = [
  { label: '팀', value: '팀', icon: Users },
  { label: '담당', value: '담당', icon: User },
  { label: '본부', value: '본부', icon: Building2 },
];

const columns: ColumnDef<SalesSearch>[] = [
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
    accessorKey: '부서이름',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '부서명' }),
    cell: ({ row }) => {
      return h('div', { class: 'flex flex-col w-40' }, [
        h(TruncatedCell, {
          text: String(row.getValue('부서이름') ?? '-'),
          maxWidth: '10rem',
          className: 'font-medium',
        }),
        h(TruncatedCell, {
          text: String(row.original.부서범위 ?? ''),
          maxWidth: '10rem',
          className: 'text-xs text-muted-foreground',
        }),
      ]);
    },
    enableHiding: true,
    enableSorting: true, // 부서명은 정렬 가능
    size: 180,
    meta: { skeleton: 'title-subtitle' },
  },
  {
    accessorKey: '매출합계',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '매출합계', align: 'right' }),
    cell: ({ row }) => {
      const amount = row.getValue('매출합계') as number;
      const formattedAmount = amount ? amount.toLocaleString() + '원' : '-';

      return h(TruncatedCell, {
        text: formattedAmount,
        maxWidth: '8rem',
        className: 'text-right font-medium',
      });
    },
    enableHiding: true,
    enableSorting: true, // 매출합계는 정렬 가능
    size: 140,
  },
  {
    accessorKey: '매출목표',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '매출목표', align: 'right' }),
    cell: ({ row }) => {
      const amount = row.getValue('매출목표') as number;
      const formattedAmount = amount ? amount.toLocaleString() + '원' : '-';

      return h(TruncatedCell, {
        text: formattedAmount,
        maxWidth: '8rem',
        className: 'text-right font-medium',
      });
    },
    enableHiding: true,
    enableSorting: true, // 매출목표는 정렬 가능
    size: 140,
  },
  {
    accessorKey: '달성률',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '달성률', align: 'right' }),
    cell: ({ row }) => {
      const rate = row.getValue('달성률') as number;
      const formattedRate = rate ? rate.toFixed(1) + '%' : '-';

      return h(TruncatedCell, {
        text: formattedRate,
        maxWidth: '6rem',
        className: 'text-right font-semibold text-primary',
      });
    },
    enableHiding: true,
    enableSorting: true, // 달성률은 정렬 가능
    size: 100,
  },
  {
    accessorKey: '영업이익',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업이익', align: 'right' }),
    cell: ({ row }) => {
      const amount = row.getValue('영업이익') as number;
      if (!amount) {
        return h(TruncatedCell, {
          text: '-',
          maxWidth: '8rem',
          className: 'text-right font-medium',
        });
      }

      const isNegative = amount < 0;
      const formattedAmount = amount.toLocaleString() + '원';

      return h(TruncatedCell, {
        text: formattedAmount,
        maxWidth: '8rem',
        className: `text-right font-medium ${isNegative ? 'text-red-600' : 'text-green-600'}`,
      });
    },
    enableHiding: true,
    enableSorting: true, // 영업이익은 정렬 가능
    size: 140,
  },
  {
    accessorKey: '영업이익률',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업이익률', align: 'right' }),
    cell: ({ row }) => {
      const rate = row.getValue('영업이익률') as number;
      if (!rate) {
        return h(TruncatedCell, {
          text: '-',
          maxWidth: '6rem',
          className: 'text-right font-medium',
        });
      }

      const isNegative = rate < 0;
      const formattedRate = rate.toFixed(1) + '%';

      return h(TruncatedCell, {
        text: formattedRate,
        maxWidth: '6rem',
        className: `text-right font-medium ${isNegative ? 'text-red-600' : 'text-green-600'}`,
      });
    },
    enableHiding: true,
    enableSorting: true, // 영업이익률은 정렬 가능
    size: 120,
  },
  {
    accessorKey: '정직원',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '정직원', align: 'center' }),
    cell: ({ row }) => {
      const count = row.getValue('정직원') as number;
      const countText = count?.toString() || '0';

      return h(TruncatedCell, {
        text: countText,
        maxWidth: '4rem',
        className: 'text-center font-medium',
      });
    },
    enableHiding: true,
    enableSorting: true, // 정직원은 정렬 가능
    size: 80,
  },
  {
    accessorKey: '프리랜서',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '프리랜서', align: 'center' }),
    cell: ({ row }) => {
      const count = row.getValue('프리랜서') as number;
      const countText = count?.toString() || '0';

      return h(TruncatedCell, {
        text: countText,
        maxWidth: '5rem',
        className: 'text-center font-medium',
      });
    },
    enableHiding: true,
    enableSorting: true, // 프리랜서는 정렬 가능
    size: 90,
  },
  {
    accessorKey: '외주',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '외주', align: 'center' }),
    cell: ({ row }) => {
      const count = row.getValue('외주') as number;
      const countText = count?.toString() || '0';

      return h(TruncatedCell, {
        text: countText,
        maxWidth: '4rem',
        className: 'text-center font-medium',
      });
    },
    enableHiding: true,
    enableSorting: true, // 외주는 정렬 가능
    size: 70,
  },
  // Virtual columns for filtering (숨김 처리)
  {
    id: 'year',
    header: () => null,
    cell: () => null,
    filterFn: (row, id, value) => {
      return value.includes(new Date().getFullYear().toString());
    },
    enableHiding: false,
    enableSorting: false, // 가상 컬럼은 정렬 불가
    size: 0,
  },
  {
    id: 'departmentType',
    header: () => null,
    cell: () => null,
    filterFn: (row, id, value) => {
      return value.includes('팀');
    },
    enableHiding: false,
    enableSorting: false, // 가상 컬럼은 정렬 불가
    size: 0,
  },
  {
    id: 'projectType',
    header: () => null,
    cell: () => null,
    filterFn: (row, id, value) => {
      return value.includes('SI');
    },
    enableHiding: false,
    enableSorting: false, // 가상 컬럼은 정렬 불가
    size: 0,
  },
  {
    id: 'personnelType',
    header: () => null,
    cell: () => null,
    filterFn: (row, id, value) => {
      return value.includes('정직원');
    },
    enableHiding: false,
    size: 0,
  },
  {
    id: 'actions',
    enableHiding: false,
    size: 44,
    cell: ({ row }) => {
      return h(DataTableRowActions, {
        row: row.original,
        onEdit: (sales) => onEditSales(sales),
        onView: (sales) => onViewSales(sales),
        onDuplicate: (sales) => onDuplicateSales(sales),
        onDelete: (sales) => onDeleteSales(sales),
      });
    },
  },
];

function getColumnLabel(columnId: string): string {
  switch (columnId) {
    case '부서이름':
      return '부서명';
    case '부서범위':
      return '부서범위';
    case '매출합계':
      return '매출합계';
    case '매출목표':
      return '매출목표';
    case '달성률':
      return '달성률';
    case '영업이익':
      return '영업이익';
    case '영업이익률':
      return '영업이익률';
    case '정직원':
      return '정직원';
    case '프리랜서':
      return '프리랜서';
    case '외주':
      return '외주';
    case 'year':
      return '연도';
    case 'departmentType':
      return '부서타입';
    default:
      return columnId;
  }
}

// Function to fetch sales statistics
async function fetchSalesStats() {
  try {
    // 새로운 통계 API 사용
    const stats: SalesStats = await SALES_REPOSITORY.getSalesStats();

    salesStats.value.totalRevenue = stats.totalRevenue;
    salesStats.value.collectedRevenue = stats.collectedRevenue;
    salesStats.value.outstandingAmount = stats.outstandingAmount;
    salesStats.value.averageCollectionPeriod = stats.averageCollectionPeriod;
  } catch (error) {
    console.error('Error loading sales statistics:', error);

    // API 실패 시 가데이터 설정
    salesStats.value.totalRevenue = 125000000; // 가데이터
    salesStats.value.collectedRevenue = 100000000; // 가데이터
    salesStats.value.outstandingAmount = 25000000; // 가데이터
    salesStats.value.averageCollectionPeriod = 30; // 가데이터

    toast.error('매출 통계 로드 실패', {
      description: '매출 통계를 불러오는 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  }
}

// Function to fetch sales data
async function fetchSales(params: Record<string, any>): Promise<PageResponse<SalesSearch>> {
  try {
    console.log('Fetching sales with params:', params);
    const response = await SALES_REPOSITORY.getSales(params);
    console.log('Sales loaded:', response.content);
    return response;
  } catch (error) {
    console.error('Error loading sales:', error);
    toast.error('매출 데이터 로드 실패', {
      description: '매출 데이터를 불러오는 중 오류가 발생했습니다. 다시 시도해주세요.',
      position: 'bottom-right',
    });
    throw error;
  }
}

// 컴포넌트 마운트 시 통계 데이터 로드
onMounted(() => {
  fetchSalesStats();
});

// Action handlers
function onViewSales(sales: SalesSearch) {
  console.log('View sales:', sales);
  toast.info('매출 상세보기', {
    description: `${sales.부서이름}의 상세 정보를 확인합니다.`,
    position: 'bottom-right',
  });
}

function onEditSales(sales: SalesSearch) {
  console.log('Edit sales:', sales);
  toast.info('매출 편집', {
    description: `${sales.부서이름}의 정보를 편집합니다.`,
    position: 'bottom-right',
  });
}

function onDuplicateSales(sales: SalesSearch) {
  console.log('Duplicate sales:', sales);
  toast.info('매출 복제', {
    description: `${sales.부서이름}의 정보를 복제합니다.`,
    position: 'bottom-right',
  });
}

function onDeleteSales(sales: SalesSearch) {
  console.log('Delete sales:', sales);
  toast.warning('매출 삭제', {
    description: `${sales.부서이름}을(를) 삭제하시겠습니까?`,
    position: 'bottom-right',
  });
}
</script>

<style scoped></style>