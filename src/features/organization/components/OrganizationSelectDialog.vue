<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[560px]">
      <DialogHeader>
        <DialogTitle>부서 선택</DialogTitle>
        <DialogDescription>
          트리에서 부서를 선택하세요. 구성원 포함 전환으로 표시 범위를 조정할 수 있습니다.
        </DialogDescription>
      </DialogHeader>

      <div class="flex items-center justify-between gap-2 mb-3">
        <Input v-model="keyword" placeholder="부서/직원 검색..." class="w-64" />
        <div class="flex items-center gap-2">
          <Switch id="withMembers" v-model:checked="withMembersLocal" />
          <Label for="withMembers">구성원 포함</Label>
          <Button variant="outline" size="sm" @click="loadTree" :disabled="loading">
            새로고침
          </Button>
        </div>
      </div>

      <div class="rounded-md border p-2 max-h-[50vh] overflow-auto">
        <OrganizationTree
          :nodes="filteredTree"
          :expandable="true"
          :selectable="true"
          :show-icons="true"
          @select="handleSelect"
        />
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">닫기</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/core/composables';
import { container } from 'tsyringe';
import OrganizationRepository from '@/features/organization/repository/OrganizationRepository.ts';
import OrganizationTree from '@/features/organization/components/OrganizationTree.vue';
import type { OrganizationTreeNode } from '@/features/organization/entity/OrganizationTree';

interface Props {
  open: boolean;
  withMembers?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  withMembers: true,
});

const emit = defineEmits<{
  (e: 'update:open', v: boolean): void;
  (e: 'select', node: OrganizationTreeNode): void;
}>();

const toast = useToast();
const ORG_REPO = container.resolve(OrganizationRepository);

const loading = ref(false);
const keyword = ref('');
const withMembersLocal = ref<boolean>(props.withMembers);
const tree = ref<OrganizationTreeNode[]>([]);

async function loadTree() {
  loading.value = true;
  try {
    tree.value = withMembersLocal.value
      ? await ORG_REPO.getOrganizationTreeWithMembers()
      : await ORG_REPO.getOrganizationTree();
  } catch (e) {
    console.error(e);
    toast.error('조직도 로드 실패', {
      description: '조직도를 불러오는 중 오류가 발생했습니다.',
      position: 'bottom-right',
    });
  } finally {
    loading.value = false;
  }
}

function nameOf(n: OrganizationTreeNode) {
  return n.name?.toLowerCase?.() || '';
}

function filterTree(nodes: OrganizationTreeNode[], q: string): OrganizationTreeNode[] {
  if (!q) return nodes;
  const res: OrganizationTreeNode[] = [];
  for (const node of nodes) {
    const match = nameOf(node).includes(q);
    const children = node.children ? filterTree(node.children, q) : [];
    if (match || children.length) {
      res.push({ ...node, expanded: !!q || node.expanded, children });
    }
  }
  return res;
}

const filteredTree = computed(() => filterTree(tree.value, keyword.value.trim().toLowerCase()));

function handleSelect(node: OrganizationTreeNode) {
  // 직원 노드가 아닌, 부서 노드만 선택 허용
  if (node.departmentId && !node.employeeId) {
    emit('select', node);
    emit('update:open', false);
  }
}

onMounted(loadTree);
watch(withMembersLocal, loadTree);
watch(() => props.open, (o) => {
  if (o) loadTree();
});
</script>

<style scoped></style>

