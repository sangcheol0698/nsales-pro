<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <DataTableWithUrl
          :columns="columns"
          :fetchData="fetchEmployees"
          searchPlaceholder="구성원 검색..."
          searchColumnId="name"
          :getColumnLabel="getColumnLabel"
          emptyMessage="구성원이 없습니다"
          emptyDescription="새 구성원을 추가하거나 검색 조건을 변경해보세요"
        />
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table';
import { ChevronDown } from 'lucide-vue-next';
import { h } from 'vue';
import { container } from 'tsyringe';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository.ts';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/shared/components/sidebar';
import { DataTableWithUrl } from '@/shared/components/table';
import { useToast } from '@/core/composables';

import { Button } from '@/core/components/ui/button';
import { Checkbox } from '@/core/components/ui/checkbox';
import { DataTableColumnHeader } from '@/core/components/ui/data-table';

const toast = useToast();
const EMPLOYEE_REPOSITORY = container.resolve(EmployeeRepository);

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
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'font-medium' }, row.getValue('name') || '-'),
        h('span', { class: 'text-xs text-muted-foreground' }, row.original.code || ''),
      ]);
    },
  },
  // {
  //   accessorKey: 'email',
  //   header: ({ column }) => h(DataTableColumnHeader, { column, title: '이메일' }),
  //   cell: ({ row }) => h('div', {}, row.getValue('email') || '-'),
  // },
  {
    accessorKey: 'teamName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '부서' }),
    cell: ({ row }) => h('div', {}, row.getValue('teamName') || '-'),
  },
  {
    accessorKey: 'rank',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '직급' }),
    cell: ({ row }) => h('div', {}, row.getValue('rank') || '-'),
  },
  {
    accessorKey: 'joinDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '입사일' }),
    cell: ({ row }) => h('div', {}, row.getValue('joinDate') || '-'),
  },
  {
    accessorKey: 'status',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '상태' }),
    cell: ({ row }) => h('div', { class: 'capitalize' }, row.getValue('status') || '-'),
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      return h(
        Button,
        {
          variant: 'ghost',
          onClick: () => row.toggleExpanded(!row.getIsExpanded()),
        },
        () => [
          '상세',
          h(ChevronDown, {
            class: `ml-2 h-4 w-4 transition-transform ${row.getIsExpanded() ? 'rotate-180' : ''}`,
          }),
        ]
      );
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
    case 'joinDate':
      return '입사일';
    case 'status':
      return '상태';
    default:
      return columnId;
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
</script>

<style scoped></style>
