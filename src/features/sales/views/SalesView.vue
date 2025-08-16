<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
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
            <DataTableFacetedFilter
              v-if="table.getColumn('projectType')"
              :column="table.getColumn('projectType')"
              title="프로젝트 타입"
              :options="projectTypeOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('personnelType')"
              :column="table.getColumn('personnelType')"
              title="인력 타입"
              :options="personnelTypeOptions"
            />
            <DataTableFacetedFilter
              v-if="table.getColumn('status')"
              :column="table.getColumn('status')"
              title="상태"
              :options="statusOptions"
            />
          </template>

        </DataTableWithUrl>
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table';
import { h } from 'vue';
import { container } from 'tsyringe';
import SalesRepository from '@/features/sales/repository/SalesRepository.ts';
import type { SalesSearch } from '@/features/sales/entity/SalesSearch.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/components/layout';
import {
  DataTableColumnHeader,
  DataTableFacetedFilter,
  DataTableRowActions,
  DataTableWithUrl,
  StatusBadge,
} from '@/components/business';
import { useToast } from '@/core/composables';

import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { 
  Building2, 
  Factory, 
  User, 
  Users, 
  Briefcase,
  Calendar,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-vue-next';

const toast = useToast();
const SALES_REPOSITORY = container.resolve(SalesRepository);

// Filter options
const yearOptions = [
  { label: '2024', value: '2024', icon: Calendar },
  { label: '2023', value: '2023', icon: Calendar },
  { label: '2022', value: '2022', icon: Calendar },
  { label: '2021', value: '2021', icon: Calendar },
];

const departmentTypeOptions = [
  { label: '팀', value: '팀', icon: Users },
  { label: '담당', value: '담당', icon: User },
  { label: '본부', value: '본부', icon: Building2 },
];

const projectTypeOptions = [
  { label: 'SI', value: 'SI', icon: Briefcase },
  { label: 'SM', value: 'SM', icon: Factory },
];

const personnelTypeOptions = [
  { label: '정직원', value: '정직원', icon: User },
  { label: '프리랜서', value: '프리랜서', icon: Users },
  { label: '외주', value: '외주', icon: Building2 },
];

const statusOptions = [
  { label: '미수금', value: '미수금', icon: Clock },
  { label: '수금완료', value: '수금완료', icon: CheckCircle },
  { label: '취소', value: '취소', icon: XCircle },
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
    accessorKey: 'projectName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '프로젝트명' }),
    cell: ({ row }) => {
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'font-medium' }, row.getValue('projectName') || '-'),
        h('span', { class: 'text-xs text-muted-foreground' }, row.original.code || ''),
      ]);
    },
    enableHiding: true,
  },
  {
    accessorKey: 'partnerName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '협력사' }),
    cell: ({ row }) => h('div', {}, row.getValue('partnerName') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'amount',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '금액' }),
    cell: ({ row }) => {
      const amount = row.getValue('amount') as number;
      if (!amount) return h('div', {}, '-');
      return h('div', { class: 'font-medium' }, amount.toLocaleString() + '원');
    },
    enableHiding: true,
  },
  {
    accessorKey: 'totalAmount',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '총액' }),
    cell: ({ row }) => {
      const amount = row.getValue('totalAmount') as number;
      if (!amount) return h('div', {}, '-');
      return h('div', { class: 'font-semibold text-primary' }, amount.toLocaleString() + '원');
    },
    enableHiding: true,
  },
  {
    accessorKey: 'issueDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '발행일' }),
    cell: ({ row }) => h('div', {}, row.getValue('issueDate') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'dueDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '만기일' }),
    cell: ({ row }) => h('div', {}, row.getValue('dueDate') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'paymentDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '결제일' }),
    cell: ({ row }) => h('div', {}, row.getValue('paymentDate') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'status',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '상태' }),
    cell: ({ row }) => {
      const status = row.getValue('status') as string;
      return h(StatusBadge, {
        status: status || '미수금',
        type: 'sales',
      });
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id));
    },
    enableHiding: true,
  },
  // Virtual columns for filtering
  {
    id: 'year',
    header: '연도',
    cell: () => h('div', { style: 'display: none' }),
    filterFn: (row, id, value) => {
      return value.includes(new Date().getFullYear().toString());
    },
    enableHiding: true,
  },
  {
    id: 'departmentType',
    header: '부서타입',
    cell: () => h('div', { style: 'display: none' }),
    filterFn: (row, id, value) => {
      return value.includes('팀');
    },
    enableHiding: true,
  },
  {
    id: 'projectType',
    header: '프로젝트타입',
    cell: () => h('div', { style: 'display: none' }),
    filterFn: (row, id, value) => {
      return value.includes('SI');
    },
    enableHiding: true,
  },
  {
    id: 'personnelType',
    header: '인력타입',
    cell: () => h('div', { style: 'display: none' }),
    filterFn: (row, id, value) => {
      return value.includes('정직원');
    },
    enableHiding: true,
  },
  {
    id: 'actions',
    enableHiding: false,
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
    case 'projectName':
      return '프로젝트명';
    case 'partnerName':
      return '협력사';
    case 'amount':
      return '금액';
    case 'totalAmount':
      return '총액';
    case 'issueDate':
      return '발행일';
    case 'dueDate':
      return '만기일';
    case 'paymentDate':
      return '결제일';
    case 'status':
      return '상태';
    case 'year':
      return '연도';
    case 'departmentType':
      return '부서타입';
    case 'projectType':
      return '프로젝트타입';
    case 'personnelType':
      return '인력타입';
    default:
      return columnId;
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

// Action handlers
function onViewSales(sales: SalesSearch) {
  console.log('View sales:', sales);
  toast.info('매출 상세보기', {
    description: `${sales.projectName}의 상세 정보를 확인합니다.`,
    position: 'bottom-right',
  });
}

function onEditSales(sales: SalesSearch) {
  console.log('Edit sales:', sales);
  toast.info('매출 편집', {
    description: `${sales.projectName}의 정보를 편집합니다.`,
    position: 'bottom-right',
  });
}

function onDuplicateSales(sales: SalesSearch) {
  console.log('Duplicate sales:', sales);
  toast.info('매출 복제', {
    description: `${sales.projectName}의 정보를 복제합니다.`,
    position: 'bottom-right',
  });
}

function onDeleteSales(sales: SalesSearch) {
  console.log('Delete sales:', sales);
  toast.warning('매출 삭제', {
    description: `${sales.projectName}을(를) 삭제하시겠습니까?`,
    position: 'bottom-right',
  });
}
</script>

<style scoped></style>