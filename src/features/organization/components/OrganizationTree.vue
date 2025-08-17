<template>
  <ul class="space-y-1">
    <OrgTreeNode
      v-for="(node, idx) in nodes"
      :key="nodeKey(node, idx)"
      :node="node"
      :level="node.level || 0"
      :selectable="selectable"
      :expandable="expandable"
      :show-icons="showIcons"
      @toggle="onToggle"
      @select="onSelect"
    />
  </ul>
</template>

<script setup lang="ts">
import type { OrganizationTreeNode } from '@/features/organization/entity/OrganizationTree';
import OrgTreeNode from '@/features/organization/components/TreeNode.vue';

interface Props {
  nodes: OrganizationTreeNode[];
  selectable?: boolean;
  expandable?: boolean;
  showIcons?: boolean;
}

withDefaults(defineProps<Props>(), {
  selectable: true,
  expandable: true,
  showIcons: true,
});

const emit = defineEmits<{
  (e: 'toggle', node: OrganizationTreeNode): void;
  (e: 'select', node: OrganizationTreeNode): void;
}>();

function nodeKey(node: OrganizationTreeNode, idx: number) {
  return `${node.departmentId ?? 'd'}-${node.employeeId ?? 'e'}-${idx}-${node.name}`;
}

function onToggle(node: OrganizationTreeNode) {
  emit('toggle', node);
}

function onSelect(node: OrganizationTreeNode) {
  emit('select', node);
}
</script>

<style scoped></style>
