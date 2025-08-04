<template>
  <SidebarLayout>
    <main class="flex w-full h-full overflow-hidden">
      <!-- Desktop: Organization Tree Sidebar -->
      <div 
        v-if="!isMobile"
        :class="cn(
          'organization-sidebar relative flex-shrink-0 transition-all duration-300 ease-in-out overflow-hidden',
          showOrgChart ? 'w-80' : 'w-0'
        )"
      >
        <!-- Resize Handle -->
        <div 
          v-if="showOrgChart"
          class="absolute right-0 top-0 bottom-0 w-1 bg-border/40 hover:bg-primary/40 cursor-col-resize transition-colors duration-200 z-10"
          @mousedown="startResize"
        />
        
        <div class="h-full p-4 border-r border-border/40 bg-card/30">
          <OrganizationTree
            :compact="false"
            :with-members="true"
            :selectable="true"
            :multi-select="false"
            :searchable="true"
            @select="handleOrgSelection"
          />
        </div>
      </div>

      <!-- Main Content -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <div class="flex-1 p-2 sm:p-4 overflow-x-hidden">
          <DataTableModernContainer
            ref="tableContainer"
            :columns="columns"
            :fetchData="fetchEmployees"
            searchPlaceholder="구성원 검색..."
            searchColumnId="name"
            :getColumnLabel="getColumnLabel"
            emptyMessage="구성원이 없습니다"
            emptyDescription="새 구성원을 추가하거나 검색 조건을 변경해보세요"
            title="구성원 관리"
            description="회사 구성원들의 정보를 체계적으로 관리하고 효율적으로 검색할 수 있습니다"
          >
            <template #filters="{ table }">
              <DataTableModernFilter
                :column="table.getColumn('status')"
                title="상태"
                :options="statusOptions"
              />
              <DataTableModernFilter
                :column="table.getColumn('rank')"
                title="직급"
                :options="rankOptions"
              />
              <DataTableModernFilter
                :column="table.getColumn('teamName')"
                title="부서"
                :options="departmentOptions"
              />
              <DataTableModernDateRange
                :column="table.getColumn('joinDate')"
                title="입사일"
                placeholder="입사일 범위 선택"
              />
            </template>
            
            <template #actions>
              <!-- Organization Chart Toggle -->
              <Button
                variant="outline"
                :size="isMobile ? 'sm' : 'sm'"
                :class="cn(
                  'gap-2 transition-all duration-200',
                  isMobile ? 'h-8 px-2' : 'h-8',
                  showOrgChart && 'bg-primary/5 border-primary/30 text-primary'
                )"
                @click="toggleOrgChart"
              >
                <component 
                  :is="showOrgChart ? EyeOff : Eye" 
                  :class="cn('w-4 h-4', isMobile && 'w-3.5 h-3.5')" 
                />
                <span :class="cn(isMobile && 'text-xs')">조직도</span>
              </Button>

              <Button :size="isMobile ? 'sm' : 'sm'" :class="cn(isMobile ? 'h-8 px-2' : 'h-8')">
                <Plus :class="cn('mr-1.5 w-4 h-4', isMobile && 'w-3.5 h-3.5 mr-1')" />
                <span :class="cn(isMobile && 'text-xs')">구성원 추가</span>
              </Button>
            </template>
          </DataTableModernContainer>
        </div>
      </div>
    </main>

    <!-- Mobile: Organization Tree Sheet Overlay -->
    <div
      v-if="isMobile && showOrgChart"
      class="fixed inset-0 z-50 lg:hidden"
      @click="showOrgChart = false"
    >
      <!-- Backdrop -->
      <div 
        class="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in-0 duration-300"
      />
      
      <!-- Sheet -->
      <div 
        :class="cn(
          'absolute bottom-0 left-0 right-0 max-h-[85vh] rounded-t-2xl',
          'bg-background border-t border-border/40 shadow-2xl',
          'animate-in slide-in-from-bottom-full duration-300'
        )"
        @click.stop
      >
        <!-- Handle -->
        <div class="flex justify-center p-2">
          <div class="w-12 h-1.5 bg-muted-foreground/20 rounded-full" />
        </div>
        
        <!-- Header -->
        <div class="flex items-center justify-between px-4 pb-3 border-b border-border/20">
          <h2 class="text-lg font-semibold text-foreground/90">조직도</h2>
          <Button
            variant="ghost"
            size="sm"
            class="h-8 w-8 p-0"
            @click="showOrgChart = false"
          >
            <X class="w-4 h-4" />
          </Button>
        </div>
        
        <!-- Organization Tree Content -->
        <div class="p-4 overflow-auto max-h-[calc(85vh-100px)]">
          <OrganizationTree
            :compact="true"
            :with-members="true"
            :selectable="true"
            :multi-select="false"
            :searchable="true"
            @select="handleMobileOrgSelection"
          />
        </div>
      </div>
    </div>

    <!-- Selected Organization Info Overlay -->
    <div 
      v-if="selectedOrganization"
      :class="cn(
        'fixed z-50',
        isMobile ? 'top-2 left-2 right-2 max-w-none' : 'top-4 right-4 max-w-sm',
        'p-3 rounded-lg bg-card/95 backdrop-blur-sm border border-border/60 shadow-lg',
        'animate-in slide-in-from-top-2 fade-in-0 duration-300'
      )"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-2 min-w-0">
          <component 
            :is="selectedOrganization.type === 'employee' ? User : Building2" 
            :class="cn('text-primary flex-shrink-0', isMobile ? 'w-3.5 h-3.5' : 'w-4 h-4')" 
          />
          <div class="min-w-0">
            <div :class="cn('font-medium truncate', isMobile ? 'text-xs' : 'text-sm')">
              {{ selectedOrganization.node.name }}
            </div>
            <div :class="cn('text-muted-foreground', isMobile ? 'text-xs' : 'text-xs')">
              {{ selectedOrganization.type === 'employee' ? '구성원' : '부서' }} 선택됨
            </div>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          :class="cn('p-0 flex-shrink-0', isMobile ? 'h-5 w-5' : 'h-6 w-6')"
          @click="clearOrgSelection"
        >
          <X :class="cn(isMobile ? 'w-2.5 h-2.5' : 'w-3 h-3')" />
        </Button>
      </div>
      
      <!-- Additional filters based on selection -->
      <div 
        v-if="selectedOrganization.type === 'department'" 
        :class="cn('mt-2 text-muted-foreground', isMobile ? 'text-xs' : 'text-xs')"
      >
        해당 부서의 구성원들이 필터링되었습니다
      </div>
    </div>
  </SidebarLayout>
</template>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table';
import { Plus, Eye, EyeOff, User, Building2, X } from 'lucide-vue-next';
import { h, ref, watch, onMounted, onUnmounted } from 'vue';
import { container } from 'tsyringe';
import EmployeeRepository from '@/features/employee/repository/EmployeeRepository.ts';
import EmployeeSearch from '@/features/employee/entity/EmployeeSearch.ts';
import PageResponse from '@/core/common/PageResponse.ts';
import { SidebarLayout } from '@/shared/components/sidebar';
import { DataTableModernContainer } from '@/shared/components/table';
import { useToast } from '@/core/composables';
import { cn } from '@/shared/utils/utils';

import { Button } from '@/core/components/ui/button';
import { Checkbox } from '@/core/components/ui/checkbox';
import { 
  DataTableColumnHeader,
  DataTableModernFilter,
  DataTableModernDateRange 
} from '@/core/components/ui/data-table';

// Organization Tree imports
import { OrganizationTree } from '@/features/organization';
import type { OrganizationSelectEvent } from '@/features/organization';

const toast = useToast();
const EMPLOYEE_REPOSITORY = container.resolve(EmployeeRepository);

// Organization Chart State
const showOrgChart = ref(false);
const selectedOrganization = ref<OrganizationSelectEvent | null>(null);
const tableContainer = ref<any>(null);

// Responsive state
const isMobile = ref(false);

// Check if mobile on mount and resize
function checkMobile() {
  isMobile.value = window.innerWidth < 1024; // lg breakpoint
}

// Initialize mobile check and cleanup
onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
});

// Organization Chart Methods
function toggleOrgChart() {
  showOrgChart.value = !showOrgChart.value;
}

function handleOrgSelection(event: OrganizationSelectEvent) {
  selectedOrganization.value = event;
  applyOrgFilter(event);
}

function handleMobileOrgSelection(event: OrganizationSelectEvent) {
  selectedOrganization.value = event;
  applyOrgFilter(event);
  // Close mobile sheet after selection
  showOrgChart.value = false;
}

function applyOrgFilter(event: OrganizationSelectEvent) {
  // Apply filter to the table based on organization selection
  if (tableContainer.value && tableContainer.value.table) {
    const table = tableContainer.value.table;
    
    if (event.type === 'department' && event.departmentId) {
      // Filter by department - need to get department name from the node
      const departmentName = event.node.name;
      const teamColumn = table.getColumn('teamName');
      if (teamColumn) {
        teamColumn.setFilterValue(departmentName);
      }
    } else if (event.type === 'employee' && event.employeeId) {
      // Filter by specific employee - need to get employee name
      const employeeName = event.node.name.split(' ')[0]; // Remove rank from name
      const nameColumn = table.getColumn('name');
      if (nameColumn) {
        nameColumn.setFilterValue(employeeName);
      }
    }
  }
}

function clearOrgSelection() {
  selectedOrganization.value = null;
  
  // Clear table filters
  if (tableContainer.value && tableContainer.value.table) {
    const table = tableContainer.value.table;
    table.resetColumnFilters();
  }
}

// Resize functionality for organization chart
let isResizing = false;
let startX = 0;
let startWidth = 0;

function startResize(e: MouseEvent) {
  isResizing = true;
  startX = e.clientX;
  startWidth = 320; // Default width of 320px (w-80)
  
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
}

function handleResize(e: MouseEvent) {
  if (!isResizing) return;
  
  const newWidth = startWidth + (e.clientX - startX);
  const minWidth = 280;
  const maxWidth = 600;
  
  if (newWidth >= minWidth && newWidth <= maxWidth) {
    const orgChartElement = document.querySelector('.organization-sidebar') as HTMLElement;
    if (orgChartElement) {
      orgChartElement.style.width = `${newWidth}px`;
    }
  }
}

function stopResize() {
  isResizing = false;
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
}

// Filter options (백엔드 enum과 동기화)
const statusOptions = [
  { label: '재직', value: '재직' },
  { label: '휴직', value: '휴직' },
  { label: '퇴사', value: '퇴사' },
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

// 백엔드 부서 구조에 맞춘 부서 옵션 (InitEmployeeMemberDepartmentRoleData.java 참고)
const departmentOptions = [
  // 최상위
  { label: '애버커스', value: '애버커스' },
  
  // 본부급
  { label: '통신사업본부', value: '통신사업본부' },
  { label: '미래사업본부', value: '미래사업본부' },
  { label: '연구개발본부', value: '연구개발본부' },
  
  // 담당급
  { label: '통신이행담당', value: '통신이행담당' },
  { label: '경영빌링담당', value: '경영빌링담당' },
  
  // 팀급
  { label: '고객정보팀', value: '고객정보팀' },
  { label: '가입정보팀', value: '가입정보팀' },
  { label: '빌링시스템팀', value: '빌링시스템팀' },
  { label: '영업정보팀', value: '영업정보팀' },
  { label: '기반기술팀', value: '기반기술팀' },
  { label: '경영정보팀', value: '경영정보팀' },
  { label: '융합데이터분석팀', value: '융합데이터분석팀' },
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
  },
  {
    accessorKey: 'teamName',
    header: '부서',
    cell: ({ row }) => h('div', {}, row.getValue('teamName') || '-'),
  },
  {
    accessorKey: 'rank',
    header: '직급',
    cell: ({ row }) => h('div', {}, row.getValue('rank') || '-'),
  },
  {
    accessorKey: 'joinDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: '입사일' }),
    cell: ({ row }) => h('div', {}, row.getValue('joinDate') || '-'),
  },
  {
    accessorKey: 'status',
    header: '상태',
    cell: ({ row }) => h('div', { class: 'capitalize' }, row.getValue('status') || '-'),
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
