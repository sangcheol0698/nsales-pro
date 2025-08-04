<template>
  <div 
    :class="cn(
      'relative group transition-all duration-300',
      compact ? 'py-1.5' : 'py-2'
    )"
    :style="{ paddingLeft: `${level * (compact ? 12 : 24)}px` }"
  >
    <!-- Connection Lines (Magic UI Style) -->
    <div 
      v-if="level > 0"
      :class="cn(
        'absolute left-0 top-0 w-px h-full bg-gradient-to-b',
        'from-border via-border/60 to-transparent',
        'group-hover:from-primary/40 group-hover:via-primary/20',
        'transition-all duration-300'
      )"
      :style="{ left: `${(level - 1) * (compact ? 12 : 24) + 6}px` }"
    />
    
    <div 
      v-if="level > 0"
      :class="cn(
        'absolute top-1/2 w-3 h-px bg-gradient-to-r',
        'from-border to-transparent',
        'group-hover:from-primary/40',
        'transition-all duration-300'
      )"
      :style="{ left: `${(level - 1) * (compact ? 12 : 24) + 6}px` }"
    />

    <!-- Node Content -->
    <div 
      :class="cn(
        'relative flex items-center rounded-lg transition-all duration-200',
        'hover:bg-gradient-to-r hover:from-muted/30 hover:via-muted/10 hover:to-transparent',
        'group cursor-pointer',
        compact ? 'gap-2 px-2 py-1.5 text-sm' : 'gap-3 px-3 py-2',
        isSelected && 'bg-primary/5 border border-primary/20',
        isEmployee && (compact ? 'ml-2' : 'ml-4')
      )"
      @click="handleClick"
    >
      <!-- Expand/Collapse Button -->
      <button
        v-if="hasChildren && !isEmployee"
        :class="cn(
          'flex items-center justify-center w-5 h-5 rounded-full',
          'bg-gradient-to-br from-background to-muted border border-border/60',
          'hover:border-primary/40 hover:shadow-sm transition-all duration-200',
          'text-muted-foreground hover:text-primary',
          compact && 'w-4 h-4'
        )"
        @click.stop="toggleExpanded"
      >
        <ChevronRight 
          :class="cn(
            'transition-transform duration-200',
            compact ? 'w-3 h-3' : 'w-3.5 h-3.5',
            isExpanded && 'rotate-90'
          )" 
        />
      </button>
      
      <!-- Icon Placeholder -->
      <div 
        v-else
        :class="cn(
          'w-5 h-5 flex items-center justify-center',
          compact && 'w-4 h-4'
        )"
      >
        <div 
          v-if="!isEmployee"
          :class="cn(
            'w-2 h-2 rounded-full bg-gradient-to-br from-primary/60 to-primary/40',
            compact && 'w-1.5 h-1.5'
          )"
        />
      </div>

      <!-- Node Icon with Magic UI Style -->
      <div 
        :class="cn(
          'relative flex items-center justify-center rounded-lg transition-all duration-200',
          'bg-gradient-to-br shadow-sm border border-border/40',
          compact ? 'w-7 h-7' : 'w-8 h-8',
          isEmployee 
            ? 'from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/50 border-blue-200/60 dark:border-blue-800/60'
            : 'from-emerald-50 to-emerald-100 dark:from-emerald-950/50 dark:to-emerald-900/50 border-emerald-200/60 dark:border-emerald-800/60',
          'group-hover:shadow-md group-hover:scale-105'
        )"
      >
        <!-- Subtle glow effect -->
        <div 
          :class="cn(
            'absolute inset-0 rounded-lg bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300',
            isEmployee 
              ? 'from-blue-200/20 to-blue-300/20 dark:from-blue-400/10 dark:to-blue-500/10'
              : 'from-emerald-200/20 to-emerald-300/20 dark:from-emerald-400/10 dark:to-emerald-500/10'
          )"
        />
        
        <component 
          :is="isEmployee ? User : Building2"
          :class="cn(
            'relative z-10 transition-colors duration-200',
            compact ? 'w-4 h-4' : 'w-4.5 h-4.5',
            isEmployee 
              ? 'text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300'
              : 'text-emerald-600 dark:text-emerald-400 group-hover:text-emerald-700 dark:group-hover:text-emerald-300'
          )" 
        />
      </div>

      <!-- Node Label -->
      <div class="flex-1 min-w-0">
        <div 
          :class="cn(
            'font-medium transition-colors duration-200 truncate',
            compact ? 'text-sm' : 'text-sm',
            isEmployee 
              ? 'text-foreground/80 group-hover:text-foreground' 
              : 'text-foreground/90 group-hover:text-foreground',
            isSelected && 'text-primary font-semibold'
          )"
        >
          {{ node.name }}
        </div>
        
        <!-- Employee Count Badge -->
        <div 
          v-if="!isEmployee && employeeCount > 0"
          :class="cn(
            'inline-flex items-center gap-1 mt-1 px-2 py-0.5 rounded-full text-xs',
            'bg-gradient-to-r from-muted/50 to-muted/30 text-muted-foreground',
            'border border-border/30 transition-all duration-200',
            'group-hover:from-primary/10 group-hover:to-primary/5 group-hover:text-primary group-hover:border-primary/20',
            compact && 'px-1.5 text-xs'
          )"
        >
          <Users :class="cn('w-3 h-3', compact && 'w-2.5 h-2.5')" />
          {{ employeeCount }}명
        </div>
      </div>

      <!-- Selection Indicator -->
      <div 
        v-if="isSelected"
        :class="cn(
          'absolute right-2 w-2 h-2 rounded-full',
          'bg-gradient-to-br from-primary to-primary/80 shadow-sm',
          'animate-pulse'
        )"
      />

      <!-- Hover Beam Effect -->
      <div 
        :class="cn(
          'absolute inset-0 rounded-lg border border-transparent',
          'bg-gradient-to-r from-transparent via-primary/5 to-transparent',
          'opacity-0 group-hover:opacity-100 transition-opacity duration-300',
          'pointer-events-none'
        )"
      />
    </div>

    <!-- Children Nodes with Stagger Animation -->
    <div 
      v-if="isExpanded && hasChildren"
      :class="cn(
        'overflow-hidden transition-all duration-300 ease-out',
        'animate-in slide-in-from-top-2'
      )"
    >
      <OrganizationTreeNode
        v-for="(child, index in node.children || []"
        :key="child.departmentId || child.employeeId || index"
        :node="child"
        :level="level + 1"
        :compact="compact"
        :selectable="selectable"
        :selected-nodes="selectedNodes"
        :style="{ animationDelay: `${index * 50}ms` }"
        @select="$emit('select', $event)"
        @expand="$emit('expand', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ChevronRight, Building2, User, Users } from 'lucide-vue-next';
import { cn } from '@/shared/utils/utils';
import type { OrganizationTreeNode, OrganizationSelectEvent } from '../entity/OrganizationTree';

interface Props {
  node: OrganizationTreeNode;
  level?: number;
  compact?: boolean;
  selectable?: boolean;
  selectedNodes?: Set<string>;
}

const props = withDefaults(defineProps<Props>(), {
  level: 0,
  compact: false,
  selectable: true,
  selectedNodes: () => new Set()
});

const emit = defineEmits<{
  select: [event: OrganizationSelectEvent];
  expand: [node: OrganizationTreeNode];
}>();

// Computed properties
const isEmployee = computed(() => !!props.node.employeeId);
const hasChildren = computed(() => (props.node.children?.length || 0) > 0);
const isExpanded = computed(() => props.node.expanded === true);

const nodeKey = computed(() => 
  props.node.employeeId ? `employee-${props.node.employeeId}` : `department-${props.node.departmentId}`
);

const isSelected = computed(() => 
  props.selectable && props.selectedNodes.has(nodeKey.value)
);

const employeeCount = computed(() => {
  if (isEmployee.value) return 0;
  
  const countEmployees = (node: OrganizationTreeNode): number => {
    let count = 0;
    if (node.children) {
      for (const child of node.children) {
        if (child.employeeId) {
          count++;
        } else {
          count += countEmployees(child);
        }
      }
    }
    return count;
  };
  
  return countEmployees(props.node);
});

// Event handlers
function handleClick() {
  if (props.selectable) {
    const event: OrganizationSelectEvent = {
      node: props.node,
      type: isEmployee.value ? 'employee' : 'department',
      departmentId: props.node.departmentId,
      employeeId: props.node.employeeId
    };
    emit('select', event);
  }
}

function toggleExpanded() {
  if (hasChildren.value) {
    emit('expand', props.node);
  }
}
</script>