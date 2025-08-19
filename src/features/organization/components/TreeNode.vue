<template>
  <li>
    <div
      class="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-accent cursor-pointer"
      :class="{ 'bg-accent': node.selected }"
      :style="{ paddingLeft: (level * 12 + 4) + 'px' }"
      @click="handleSelect"
    >
      <button
        class="h-5 w-5 inline-flex items-center justify-center rounded hover:bg-muted"
        :class="{ 'opacity-30 cursor-default': isLeaf || !expandable, 'cursor-pointer': !(isLeaf || !expandable) }"
        @click.stop="handleToggle"
        aria-label="toggle"
      >
        <span v-if="isLeaf || !expandable" class="inline-block w-3"></span>
        <ChevronDown v-else-if="node.expanded" class="h-4 w-4" />
        <ChevronRight v-else class="h-4 w-4" />
      </button>

      <template v-if="showIcons">
        <User v-if="node.employeeId" class="h-4 w-4 text-blue-500" />
        <Building2 v-else class="h-4 w-4 text-emerald-600" />
      </template>

      <span class="text-sm select-none truncate">{{ node.name }}</span>
    </div>

    <ul v-if="node.expanded && node.children && node.children.length" class="mt-1 space-y-1">
      <OrgTreeNode
        v-for="(child, i) in node.children"
        :key="child.name + '-' + i"
        :node="child"
        :level="child.level ?? 0"
        :selectable="selectable"
        :expandable="expandable"
        :show-icons="showIcons"
        @toggle="$emit('toggle', $event)"
        @select="$emit('select', $event)"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { OrganizationTreeNode } from '@/features/organization/entity/OrganizationTree';
import { Building2, ChevronDown, ChevronRight, User } from 'lucide-vue-next';

defineOptions({ name: 'OrgTreeNode' });

const props = defineProps<{
  node: OrganizationTreeNode;
  level: number;
  selectable?: boolean;
  expandable?: boolean;
  showIcons?: boolean;
}>();

const emit = defineEmits<{
  (e: 'toggle', node: OrganizationTreeNode): void;
  (e: 'select', node: OrganizationTreeNode): void;
}>();

const isLeaf = computed(() => !props.node.children || props.node.children.length === 0);

function handleToggle() {
  if (!props.expandable || isLeaf.value) return;
  props.node.expanded = !props.node.expanded;
  emit('toggle', props.node);
}

function handleSelect() {
  if (!props.selectable) return;
  props.node.selected = !props.node.selected;
  emit('select', props.node);
}
</script>

<style scoped></style>

