<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <DataTableWithUrl
          :columns="columns"
          :fetchData="fetchPartners"
          searchPlaceholder="협력사 검색..."
          searchColumnId="name"
          :getColumnLabel="getColumnLabel"
          emptyMessage="협력사가 없습니다"
          emptyDescription="새 협력사를 추가하거나 검색 조건을 변경해보세요"
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
import PartnerRepository from '@/features/partner/repository/PartnerRepository.ts';
import PartnerSearch from '@/features/partner/entity/PartnerSearch.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/shared/components/sidebar';
import { DataTableWithUrl } from '@/shared/components/table';
import { useToast } from '@/core/composables';

import { Button } from '@/core/components/ui/button';
import { Checkbox } from '@/core/components/ui/checkbox';
import { DataTableColumnHeader } from '@/core/components/ui/data-table';

const toast = useToast();
const PARTNER_REPOSITORY = container.resolve(PartnerRepository);

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
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'font-medium' }, row.getValue('name') || '-'),
        h('span', { class: 'text-xs text-muted-foreground' }, row.original.address || ''),
      ]);
    },
  },
  {
    accessorKey: 'ceoName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '대표자' }),
    cell: ({ row }) => h('div', {}, row.getValue('ceoName') || '-'),
  },
  {
    accessorKey: 'salesRepName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업대표' }),
    cell: ({ row }) => h('div', {}, row.getValue('salesRepName') || '-'),
  },
  {
    accessorKey: 'salesRepPhone',
    header: '영업대표 연락처',
    cell: ({ row }) => h('div', {}, row.getValue('salesRepPhone') || '-'),
  },
  {
    accessorKey: 'salesRepEmail',
    header: '영업대표 이메일',
    cell: ({ row }) => h('div', {}, row.getValue('salesRepEmail') || '-'),
  },
  {
    accessorKey: 'grade',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '등급' }),
    cell: ({ row }) => h('div', {}, row.getValue('grade') || '-'),
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

// Function to fetch partners data
async function fetchPartners(params: Record<string, any>): Promise<PageResponse<PartnerSearch>> {
  try {
    console.log('Fetching partners with params:', params);
    const response = await PARTNER_REPOSITORY.getPartners(params);
    console.log('Partners loaded:', response.content);
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
</script>

<style scoped></style>
