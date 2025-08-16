<template>
  <SidebarLayout>
    <main class="flex flex-col w-full h-full p-4 overflow-x-hidden">
      <div class="w-full">
        <!-- 요약 카드 -->
        <SummaryCards :cards="summaryCards" />
        
        <!-- 데이터 테이블 -->
        <DataTableWithUrl
          :columns="columns"
          :fetchData="fetchProjects"
          searchPlaceholder="프로젝트 검색..."
          searchColumnId="name"
          :getColumnLabel="getColumnLabel"
          emptyMessage="프로젝트가 없습니다"
          emptyDescription="새 프로젝트를 추가하거나 검색 조건을 변경해보세요"
          storageKey="project-table-visibility"
          @rowClick="onRowClick"
        >
          <template #filters="{ table }">
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
            <Button size="sm" class="h-8" @click="onAddProject">
              <Plus class="mr-2 h-4 w-4" />
              프로젝트 추가
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
import { useRouter } from 'vue-router';
import { container } from 'tsyringe';
import ProjectRepository from '@/features/project/repository/ProjectRepository.ts';
import ProjectSearch from '@/features/project/entity/ProjectSearch.ts';
import ProjectStats from '@/features/project/entity/ProjectStats.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/components/layout';
import {
  DataTableColumnHeader,
  DataTableFacetedFilter,
  DataTableRowActions,
  DataTableWithUrl,
  StatusBadge,
  SummaryCards,
} from '@/components/business';
import { useToast } from '@/core/composables';

import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { 
  Briefcase, 
  CalendarClock, 
  CheckCircle, 
  Clock, 
  Factory, 
  Plus,
  FolderOpen,
  TrendingUp,
  DollarSign
} from 'lucide-vue-next';
import { computed, ref, onMounted } from 'vue';

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
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'font-medium' }, row.getValue('name') || '-'),
        h('span', { class: 'text-xs text-muted-foreground' }, row.original.code || ''),
      ]);
    },
    enableHiding: true,
  },
  {
    accessorKey: 'type',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '유형' }),
    cell: ({ row }) => h('div', { class: 'font-medium' }, row.getValue('type') || '-'),
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id));
    },
    enableHiding: true,
  },
  {
    accessorKey: 'period',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '기간' }),
    cell: ({ row }) => {
      const startDate = row.original.startDate || '-';
      const endDate = row.original.endDate || '';
      const separator = startDate !== '-' && endDate ? ' ~ ' : '';

      return h('div', {}, startDate + separator + endDate);
    },
    enableHiding: true,
  },
  {
    accessorKey: 'contractDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '계약일' }),
    cell: ({ row }) => h('div', {}, row.getValue('contractDate') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'contractAmount',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '계약금액' }),
    cell: ({ row }) => {
      const amount = row.getValue('contractAmount') as number;
      if (!amount) return h('div', {}, '-');

      return h('div', {}, amount.toLocaleString() + '원');
    },
    enableHiding: true,
  },
  {
    accessorKey: 'mainCompany',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '주관사' }),
    cell: ({ row }) => h('div', {}, row.getValue('mainCompany') || '-'),
    enableHiding: true,
  },
  {
    accessorKey: 'clientCompany',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '고객사' }),
    cell: ({ row }) => h('div', {}, row.getValue('clientCompany') || '-'),
    enableHiding: true,
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

// 컴포넌트 마운트 시 통계 데이터 로드
onMounted(() => {
  fetchProjectStats();
});

function onRowClick(row: ProjectSearch) {
  if (row && row.id) {
    router.push(`/projects/${row.id}`);
  }
}

// Action handlers
function onAddProject() {
  toast.info('프로젝트 추가', {
    description: '프로젝트 추가 기능이 곧 제공될 예정입니다.',
    position: 'bottom-right',
  });
}

function onViewProject(project: ProjectSearch) {
  console.log('View project:', project);
  router.push(`/projects/${project.id}`);
}

function onEditProject(project: ProjectSearch) {
  console.log('Edit project:', project);
  toast.info('프로젝트 편집', {
    description: `${project.name}의 정보를 편집합니다.`,
    position: 'bottom-right',
  });
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
  toast.warning('프로젝트 삭제', {
    description: `${project.name}을(를) 삭제하시겠습니까?`,
    position: 'bottom-right',
  });
}
</script>

<style scoped></style>
