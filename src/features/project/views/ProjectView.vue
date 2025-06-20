<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <DataTableWithUrl
          :columns="columns"
          :fetchData="fetchProjects"
          searchPlaceholder="프로젝트 검색..."
          searchColumnId="name"
          :getColumnLabel="getColumnLabel"
          emptyMessage="프로젝트가 없습니다"
          emptyDescription="새 프로젝트를 추가하거나 검색 조건을 변경해보세요"
          @rowClick="onRowClick"
        />
      </div>
    </main>
  </SidebarLayout>
</template>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table';
import { ChevronDown } from 'lucide-vue-next';
import { h } from 'vue';
import { useRouter } from 'vue-router';
import { container } from 'tsyringe';
import ProjectRepository from '@/features/project/repository/ProjectRepository.ts';
import ProjectSearch from '@/features/project/entity/ProjectSearch.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/shared/components/sidebar';
import { DataTableWithUrl } from '@/shared/components/table';
import { useToast } from '@/core/composables';

import { Button } from '@/core/components/ui/button';
import { Checkbox } from '@/core/components/ui/checkbox';
import { DataTableColumnHeader } from '@/core/components/ui/data-table';

const router = useRouter();
const toast = useToast();
const PROJECT_REPOSITORY = container.resolve(ProjectRepository);

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
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'font-medium' }, row.getValue('name') || '-'),
        h('span', { class: 'text-xs text-muted-foreground' }, row.original.code || ''),
      ]);
    },
  },
  {
    accessorKey: 'type',
    header: '유형',
    cell: ({ row }) => h('div', {}, row.getValue('type') || '-'),
  },
  {
    accessorKey: 'period',
    header: '기간',
    cell: ({ row }) => {
      const startDate = row.original.startDate || '-';
      const endDate = row.original.endDate || '';
      const separator = startDate !== '-' && endDate ? ' ~ ' : '';

      return h('div', {}, startDate + separator + endDate);
    },
  },
  {
    accessorKey: 'contractDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '계약일' }),
    cell: ({ row }) => h('div', {}, row.getValue('contractDate') || '-'),
  },
  {
    accessorKey: 'contractAmount',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '계약금액' }),
    cell: ({ row }) => {
      const amount = row.getValue('contractAmount') as number;
      if (!amount) return h('div', {}, '-');

      return h('div', {}, amount.toLocaleString() + '원');
    },
  },
  {
    accessorKey: 'mainCompany',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '주관사' }),
    cell: ({ row }) => h('div', {}, row.getValue('mainCompany') || '-'),
  },
  {
    accessorKey: 'clientCompany',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '고객사' }),
    cell: ({ row }) => h('div', {}, row.getValue('clientCompany') || '-'),
  },
  {
    accessorKey: 'status',
    header: '상태',
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
          onClick: () => {
            // Navigate to project detail view
            router.push(`/projects/${row.original.id}`);
          },
        },
        () => [
          '상세',
          h(ChevronDown, {
            class: 'ml-2 h-4 w-4',
          }),
        ]
      );
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

function onRowClick(row: ProjectSearch) {
  if (row && row.id) {
    router.push(`/projects/${row.id}`);
  }
}
</script>

<style scoped></style>
