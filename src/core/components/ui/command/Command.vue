<script setup lang="ts">
import type { ListboxRootEmits, ListboxRootProps } from 'reka-ui';
import { ListboxRoot, useForwardPropsEmits } from 'reka-ui';
import { cn } from '@/shared/utils/utils.ts';
import { computed, type HTMLAttributes, reactive, ref, watch } from 'vue';
import { provideCommandContext } from '.';
import Hangul from 'hangul-js'; // ✅ hangul-js import

const props = withDefaults(defineProps<ListboxRootProps & { class?: HTMLAttributes['class'] }>(), {
  modelValue: '',
});

const emits = defineEmits<ListboxRootEmits>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;
  return delegated;
});

const forwarded = useForwardPropsEmits(delegatedProps, emits);

const allItems = ref<Map<string, string>>(new Map());
const allGroups = ref<Map<string, Set<string>>>(new Map());

// ✅ hangul-js 기반 필터 함수 (case-insensitive for English)
function customContains(text: string, query: string): boolean {
  if (!text || !query) return false;

  // Convert to lowercase for case-insensitive English search
  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();

  // Check if the text contains the query (case-insensitive)
  if (lowerText.includes(lowerQuery)) {
    return true;
  }

  // Use Hangul.js for Korean text search
  const words = text.split(/\s+/);
  for (const word of words) {
    if (Hangul.search(word, query) >= 0) {
      return true;
    }
  }

  return Hangul.search(text, query) >= 0;
}

const filterState = reactive({
  search: '',
  filtered: {
    count: 0,
    items: new Map() as Map<string, number>,
    groups: new Set() as Set<string>,
  },
});

function filterItems() {
  if (!filterState.search) {
    filterState.filtered.count = allItems.value.size;
    return;
  }

  filterState.filtered.items.clear();
  filterState.filtered.groups = new Set();
  let itemCount = 0;

  for (const [id, value] of allItems.value) {
    const match = customContains(value, filterState.search);
    filterState.filtered.items.set(id, match ? 1 : 0);
    if (match) itemCount++;
  }

  for (const [groupId, group] of allGroups.value) {
    for (const itemId of group) {
      if (filterState.filtered.items.get(itemId)! > 0) {
        filterState.filtered.groups.add(groupId);
        break;
      }
    }
  }

  filterState.filtered.count = itemCount;
}

function handleSelect() {
  filterState.search = '';
}

watch(
  () => filterState.search,
  () => {
    filterItems();
  }
);

provideCommandContext({
  allItems,
  allGroups,
  filterState,
});
</script>

<template>
  <ListboxRoot
    data-slot="command"
    v-bind="forwarded"
    :class="
      cn(
        'bg-popover text-popover-foreground flex h-full w-full flex-col overflow-hidden rounded-md',
        props.class
      )
    "
  >
    <slot />
  </ListboxRoot>
</template>
