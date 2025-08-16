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
          storageKey="employee-table-visibility"
          @rowClick="onViewEmployee"
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
          </template>

          <template #actions="{ table }">
            <Button size="sm" class="h-8" @click="onAddEmployee">
              <UserPlus class="mr-2 h-4 w-4" />
              구성원 추가
            </Button>
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
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository.ts';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch.ts';
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
import { Clock, UserCheck, UserPlus, UserX } from 'lucide-vue-next';

const toast = useToast();
const EMPLOYEE_REPOSITORY = container.resolve(EmployeeRepository);

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
    enableHiding: true,
  },
  {
    accessorKey: 'teamName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '부서' }),
    cell: ({ row }) => h('div', {}, row.getValue('teamName') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'rank',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '직급' }),
    cell: ({ row }) => h('div', {}, row.getValue('rank') || '-'),
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id));
    },
    enableHiding: true,
  },
  {
    accessorKey: 'joinDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '입사일' }),
    cell: ({ row }) => h('div', {}, row.getValue('joinDate') || '-'),
    enableHiding: true,
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

// Action handlers
function onAddEmployee() {
  toast.info('구성원 추가', {
    description: '구성원 추가 기능이 곧 제공될 예정입니다.',
    position: 'bottom-right',
  });
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
</script>

<style scoped></style>