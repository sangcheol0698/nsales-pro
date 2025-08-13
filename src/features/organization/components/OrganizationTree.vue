<template>
  <div 
    :class="cn(
      'relative overflow-hidden rounded-xl border border-border/40',
      'bg-gradient-to-br from-card/50 via-card/30 to-card/50 backdrop-blur-sm',
      'shadow-lg shadow-black/5',
      compact ? 'p-3' : 'p-4'
    )"
  >
    <!-- Modern Header with Gradient -->
    <div class="relative mb-4">
      <div class="absolute inset-0 bg-gradient-to-r from-primary/5 via-primary/2 to-transparent rounded-lg" />
      
      <div class="relative flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-1 h-6 bg-gradient-to-b from-primary to-primary/60 rounded-full" />
          <h3 :class="cn('font-semibold text-foreground/90', compact ? 'text-base' : 'text-lg')">
            조직도
          </h3>
          
          <!-- Employee Count Badge -->
          <div 
            v-if="totalEmployeeCount > 0"
            :class="cn(
              'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium',
              'bg-gradient-to-r from-primary/10 to-primary/5 text-primary border border-primary/20'
            )"
          >
            <Users class="w-3.5 h-3.5" />
            총 {{ totalEmployeeCount }}명
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-2">
          <!-- Expand All / Collapse All -->
          <Button
            variant="ghost"
            :size="compact ? 'sm' : 'sm'"
            :class="cn(
              'h-8 px-2 text-xs gap-1.5',
              'hover:bg-primary/5 hover:text-primary transition-all duration-200'
            )"
            @click="toggleAllExpanded"
          >
            <component :is="allExpanded ? Minimize2 : Maximize2" class="w-3.5 h-3.5" />
            {{ allExpanded ? '모두 접기' : '모두 펼치기' }}
          </Button>

          <!-- Compact Mode Toggle -->
          <Button
            variant="ghost"
            :size="compact ? 'sm' : 'sm'"
            :class="cn(
              'h-8 px-2 text-xs gap-1.5',
              'hover:bg-primary/5 hover:text-primary transition-all duration-200'
            )"
            @click="$emit('update:compact', !compact)"
          >
            <component :is="compact ? Expand : Shrink" class="w-3.5 h-3.5" />
            {{ compact ? '확장' : '축소' }}
          </Button>

          <!-- Refresh Button -->
          <Button
            variant="ghost"
            :size="compact ? 'sm' : 'sm'"
            :class="cn(
              'h-8 px-2 text-xs gap-1.5',
              'hover:bg-primary/5 hover:text-primary transition-all duration-200',
              loading && 'animate-pulse'
            )"
            @click="refreshData"
            :disabled="loading"
          >
            <RotateCcw :class="cn('w-3.5 h-3.5', loading && 'animate-spin')" />
            새로고침
          </Button>
        </div>
      </div>
    </div>

    <!-- Search and Filter -->
    <div v-if="searchable" class="mb-4 space-y-3">
      <!-- Search Input -->
      <div class="relative">
        <Search :class="cn('absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground', compact ? 'w-3.5 h-3.5' : 'w-4 h-4')" />
        <Input
          v-model="searchQuery"
          :placeholder="compact ? '검색...' : '부서명 또는 구성원명으로 검색...'"
          :class="cn(
            'pr-4 transition-all duration-200',
            'focus:ring-2 focus:ring-primary/20 focus:border-primary/40',
            compact ? 'h-8 text-sm pl-9' : 'h-9 pl-10'
          )"
        />
        
        <!-- Clear Search -->
        <button
          v-if="searchQuery"
          :class="cn(
            'absolute right-3 top-1/2 transform -translate-y-1/2',
            'rounded-full bg-muted-foreground/20 hover:bg-muted-foreground/30',
            'flex items-center justify-center transition-colors duration-200',
            compact ? 'w-3.5 h-3.5' : 'w-4 h-4'
          )"
          @click="searchQuery = ''"
        >
          <X :class="cn('text-muted-foreground', compact ? 'w-2.5 h-2.5' : 'w-3 h-3')" />
        </button>
      </div>

      <!-- Filter Options -->
      <div class="flex items-center gap-2 flex-wrap">
        <Button
          variant="outline"
          size="sm"
          :class="cn(
            'h-7 px-2 text-xs gap-1',
            'border-border/60 hover:border-primary/40 hover:bg-primary/5',
            'transition-all duration-200',
            showEmployeesOnly && 'bg-primary/10 border-primary/30 text-primary'
          )"
          @click="showEmployeesOnly = !showEmployeesOnly"
        >
          <User class="w-3 h-3" />
          구성원만
        </Button>

        <Button
          variant="outline"
          size="sm"
          :class="cn(
            'h-7 px-2 text-xs gap-1',
            'border-border/60 hover:border-primary/40 hover:bg-primary/5',
            'transition-all duration-200',
            showEmptyDepartments && 'bg-primary/10 border-primary/30 text-primary'
          )"
          @click="showEmptyDepartments = !showEmptyDepartments"
        >
          <Building2 class="w-3 h-3" />
          빈 부서 포함
        </Button>
      </div>
    </div>

    <!-- Selection Info -->
    <div 
      v-if="selectable && selectedNodes.size > 0"
      :class="cn(
        'mb-3 p-3 rounded-lg bg-gradient-to-r',
        'from-primary/5 via-primary/2 to-transparent',
        'border border-primary/10'
      )"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2 text-sm">
          <div class="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span class="text-primary font-medium">
            {{ selectedNodes.size }}개 항목 선택됨
          </span>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          class="h-6 px-2 text-xs text-muted-foreground hover:text-destructive"
          @click="clearSelection"
        >
          선택 해제
        </Button>
      </div>
    </div>

    <!-- Tree Content with Modern Scrollbar -->
    <div 
      :class="cn(
        'relative overflow-auto',
        'scrollbar-thin scrollbar-track-transparent scrollbar-thumb-border',
        'hover:scrollbar-thumb-muted-foreground/20',
        compact ? 'max-h-96' : 'max-h-[500px]'
      )"
    >
      <!-- Loading State -->
      <div 
        v-if="loading"
        class="flex items-center justify-center py-12"
      >
        <div class="flex items-center gap-3 text-muted-foreground">
          <div class="w-4 h-4 rounded-full border-2 border-primary/20 border-t-primary animate-spin" />
          <span class="text-sm">조직도를 불러오는 중...</span>
        </div>
      </div>

      <!-- Empty State -->
      <div 
        v-else-if="filteredTreeData.length === 0"
        class="flex flex-col items-center justify-center py-12 space-y-4"
      >
        <div class="relative">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-muted/40 via-muted/20 to-transparent flex items-center justify-center">
            <Building2 class="w-8 h-8 text-muted-foreground/60" />
          </div>
          <div class="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-background border-2 border-border/20" />
        </div>
        
        <div class="text-center space-y-2">
          <h4 class="font-medium text-foreground/80">
            {{ searchQuery ? '검색 결과가 없습니다' : '조직도 데이터가 없습니다' }}
          </h4>
          <p class="text-sm text-muted-foreground">
            {{ searchQuery ? '다른 검색어를 사용해보세요' : '관리자에게 문의하세요' }}
          </p>
        </div>
      </div>

      <!-- Tree Nodes with Stagger Animation -->
      <div 
        v-else
        :class="cn(
          'space-y-1',
          'animate-in fade-in-0 slide-in-from-top-4 duration-500'
        )"
      >
        <OrganizationTreeNode
          v-for="(node, index) in filteredTreeData"
          :key="node.departmentId || node.employeeId || index"
          :node="node"
          :compact="compact"
          :selectable="selectable"
          :selected-nodes="selectedNodes"
          :style="{ animationDelay: `${index * 100}ms` }"
          @select="handleNodeSelect"
          @expand="handleNodeExpand"
        />
      </div>
    </div>

    <!-- Gradient Fade Effects -->
    <div class="absolute top-0 left-0 right-0 h-4 bg-gradient-to-b from-card/80 to-transparent pointer-events-none" />
    <div class="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-card/80 to-transparent pointer-events-none" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { 
  Search, X, Users, Building2, User, RotateCcw, 
  Maximize2, Minimize2, Expand, Shrink 
} from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/shared/utils/utils';
import { container } from 'tsyringe';
import OrganizationRepository from '../repository/OrganizationRepository';
import OrganizationTreeNode from './OrganizationTreeNode.vue';
import type { 
  OrganizationTreeNode as TreeNode, 
  OrganizationSelectEvent,
  OrganizationTreeOptions 
} from '../entity/OrganizationTree';

interface Props extends OrganizationTreeOptions {
  /** 외부에서 제공하는 트리 데이터 */
  treeData?: TreeNode[];
  
  /** 자동 로드 여부 */
  autoLoad?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  withMembers: true,
  expandable: true,
  selectable: true,
  multiSelect: true,
  searchable: true,
  draggable: false,
  compact: false,
  autoLoad: true
});

const emit = defineEmits<{
  'update:compact': [value: boolean];
  'select': [event: OrganizationSelectEvent];
  'multiSelect': [events: OrganizationSelectEvent[]];
}>();

// Repository
const organizationRepository = container.resolve(OrganizationRepository);

// Reactive state
const loading = ref(false);
const treeData = ref<TreeNode[]>([]);
const searchQuery = ref('');
const showEmployeesOnly = ref(false);
const showEmptyDepartments = ref(true);
const selectedNodes = ref<Set<string>>(new Set());

// Computed properties
const totalEmployeeCount = computed(() => {
  const countEmployees = (nodes: TreeNode[]): number => {
    let count = 0;
    for (const node of nodes) {
      if (node.employeeId) {
        count++;
      } else if (node.children) {
        count += countEmployees(node.children);
      }
    }
    return count;
  };
  
  return countEmployees(treeData.value);
});

const allExpanded = computed(() => {
  const checkAllExpanded = (nodes: TreeNode[]): boolean => {
    for (const node of nodes) {
      if (node.children && node.children.length > 0) {
        if (!node.expanded) return false;
        if (!checkAllExpanded(node.children)) return false;
      }
    }
    return true;
  };
  
  return checkAllExpanded(treeData.value);
});

const filteredTreeData = computed(() => {
  if (!searchQuery.value && !showEmployeesOnly.value && showEmptyDepartments.value) {
    return treeData.value;
  }
  
  const filterNodes = (nodes: TreeNode[]): TreeNode[] => {
    return nodes.reduce((filtered: TreeNode[], node) => {
      const matchesSearch = !searchQuery.value || 
        node.name.toLowerCase().includes(searchQuery.value.toLowerCase());
      
      const isEmployee = !!node.employeeId;
      const matchesEmployeeFilter = !showEmployeesOnly.value || isEmployee;
      
      let filteredChildren: TreeNode[] = [];
      if (node.children) {
        filteredChildren = filterNodes(node.children);
      }
      
      const hasEmployees = isEmployee || filteredChildren.some(child => !!child.employeeId);
      const matchesEmptyFilter = showEmptyDepartments.value || hasEmployees || isEmployee;
      
      if ((matchesSearch && matchesEmployeeFilter && matchesEmptyFilter) || filteredChildren.length > 0) {
        filtered.push({
          ...node,
          children: filteredChildren
        });
      }
      
      return filtered;
    }, []);
  };
  
  return filterNodes(treeData.value);
});

// Methods
async function loadData() {
  try {
    loading.value = true;
    
    const data = props.withMembers 
      ? await organizationRepository.getOrganizationTreeWithMembers()
      : await organizationRepository.getOrganizationTree();
    
    treeData.value = data;
  } catch (error) {
    console.error('Failed to load organization tree:', error);
  } finally {
    loading.value = false;
  }
}

async function refreshData() {
  await loadData();
}

function toggleAllExpanded() {
  const newExpandedState = !allExpanded.value;
  
  const updateExpanded = (nodes: TreeNode[]) => {
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        node.expanded = newExpandedState;
        updateExpanded(node.children);
      }
    });
  };
  
  updateExpanded(treeData.value);
}

function handleNodeSelect(event: OrganizationSelectEvent) {
  const nodeKey = event.employeeId ? `employee-${event.employeeId}` : `department-${event.departmentId}`;
  
  if (props.multiSelect) {
    const newSelected = new Set(selectedNodes.value);
    
    if (newSelected.has(nodeKey)) {
      newSelected.delete(nodeKey);
    } else {
      newSelected.add(nodeKey);
    }
    
    selectedNodes.value = newSelected;
    
    // Emit multi-select event
    const selectedEvents = Array.from(selectedNodes.value).map(key => {
      const [type, id] = key.split('-');
      return {
        node: event.node, // This should be updated to find the actual node
        type: type as 'department' | 'employee',
        [type === 'employee' ? 'employeeId' : 'departmentId']: Number(id)
      } as OrganizationSelectEvent;
    });
    
    emit('multiSelect', selectedEvents);
  } else {
    selectedNodes.value = new Set([nodeKey]);
    emit('select', event);
  }
}

function handleNodeExpand(node: TreeNode) {
  node.expanded = !node.expanded;
}

function clearSelection() {
  selectedNodes.value.clear();
}

// Watchers
watch(() => props.treeData, (newData) => {
  if (newData) {
    treeData.value = newData;
  }
}, { immediate: true });

// Lifecycle
onMounted(() => {
  if (props.autoLoad && !props.treeData) {
    loadData();
  }
});

// Expose methods for external use
defineExpose({
  loadData,
  refreshData,
  clearSelection,
  selectedNodes: computed(() => selectedNodes.value)
});
</script>