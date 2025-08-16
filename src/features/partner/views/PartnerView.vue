<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <!-- 요약 카드 -->
        <SummaryCards :cards="summaryCards" />
        
        <!-- 데이터 테이블 -->
        <DataTableWithUrl
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
          </template>

          <template #actions="{ table }">
            <Button size="sm" class="h-8" @click="onAddPartner">
              <Plus class="mr-2 h-4 w-4" />
              협력사 추가
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
import PartnerRepository from '@/features/partner/repository/PartnerRepository.ts';
import PartnerSearch from '@/features/partner/entity/PartnerSearch.ts';
import PartnerStats from '@/features/partner/entity/PartnerStats.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/components/layout';
import {
  DataTableWithUrl,
  DataTableColumnHeader,
  DataTableFacetedFilter,
  DataTableRowActions,
  StatusBadge,
  SummaryCards,
} from '@/components/business';
import { useToast } from '@/core/composables';

import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { 
  Star, 
  Award, 
  Shield, 
  CircleDot, 
  Circle,
  Plus,
  Building2,
  TrendingUp,
  Percent,
  Users
} from 'lucide-vue-next';
import { computed, ref, onMounted } from 'vue';

const toast = useToast();
const PARTNER_REPOSITORY = container.resolve(PartnerRepository);

// 요약 카드 데이터
const partnerStats = ref({
  totalPartners: 0,
  activePartners: 0,
  averageGrade: '',
  revenueContribution: 0,
});

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
    previousValue: 'B+',
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
    enableHiding: true,
  },
  {
    accessorKey: 'ceoName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '대표자' }),
    cell: ({ row }) => h('div', {}, row.getValue('ceoName') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'salesRepName',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업대표' }),
    cell: ({ row }) => h('div', {}, row.getValue('salesRepName') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'salesRepPhone',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업대표 연락처' }),
    cell: ({ row }) => h('div', {}, row.getValue('salesRepPhone') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'salesRepEmail',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '영업대표 이메일' }),
    cell: ({ row }) => h('div', {}, row.getValue('salesRepEmail') || '-'),
    enableHiding: true,
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

// 컴포넌트 마운트 시 통계 데이터 로드
onMounted(() => {
  fetchPartnerStats();
});

// Action handlers
function onAddPartner() {
  toast.info('협력사 추가', {
    description: '협력사 추가 기능이 곧 제공될 예정입니다.',
    position: 'bottom-right',
  });
}

function onViewPartner(partner: PartnerSearch) {
  console.log('View partner:', partner);
  toast.info('협력사 상세보기', {
    description: `${partner.name}의 상세 정보를 확인합니다.`,
    position: 'bottom-right',
  });
}

function onEditPartner(partner: PartnerSearch) {
  console.log('Edit partner:', partner);
  toast.info('협력사 편집', {
    description: `${partner.name}의 정보를 편집합니다.`,
    position: 'bottom-right',
  });
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
  toast.warning('협력사 삭제', {
    description: `${partner.name}을(를) 삭제하시겠습니까?`,
    position: 'bottom-right',
  });
}
</script>

<style scoped></style>
